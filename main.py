import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.optimize import minimize
import yfinance as yf

# ============================================================
# CONFIG
# ============================================================
st.set_page_config(page_title="Momentum-X", page_icon="💹", layout="wide")

if "selected_sats" not in st.session_state:
    st.session_state["selected_sats"] = set()
if "risk_score" not in st.session_state:
    st.session_state["risk_score"] = None
if "risk_profile" not in st.session_state:
    st.session_state["risk_profile"] = None

# ============================================================
# CSS
# ============================================================

CUSTOM_CSS = """
<style>
body { background-color: #F5F7FB; font-family: "Segoe UI", sans-serif; }

.risk-card {
  padding: 1rem 1.2rem;
  border-radius: 12px;
  border: 1px solid #D0D6E6;
  background-color: #FFFFFF;
  margin-bottom: 1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

/* FIX visibilité texte dans les cartes (dark mode / thème streamlit) */
.risk-card, .risk-card * { color: #111827 !important; }
.risk-level, .muted, .small-note { color: #7A869A !important; }

.risk-title { font-weight: 600; font-size: 1.1rem; margin-bottom: 0.25rem; }
.risk-level { font-size: 0.9rem; margin-bottom: 0.6rem; }
.muted { font-size: 0.85rem; }
.small-note { font-size: 0.8rem; }
.hr { border-top: 1px solid #EAECEF; margin: 0.8rem 0; }

/* Thèmes par profil */
.risk-card--prudent {
  border-left: 6px solid #16A34A;
  background: linear-gradient(135deg, #ECFDF5 0%, #FFFFFF 70%);
}

.risk-card--equilibre {
  border-left: 6px solid #2563EB;
  background: linear-gradient(135deg, #EFF6FF 0%, #FFFFFF 70%);
}

.risk-card--dynamique {
  border-left: 6px solid #991B1B;
  background: linear-gradient(135deg, #FEF2F2 0%, #FFFFFF 70%);
}

/* Active (sélectionnée) */
.risk-card--active {
  border: 2px solid #1C3C78;
  box-shadow: 0 6px 16px rgba(0,0,0,0.08);
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ============================================================
# Fonctions qu'on utilise dans le code
# ============================================================
def pct_returns(prices: pd.DataFrame) -> pd.DataFrame:
    return prices.pct_change().replace([np.inf, -np.inf], np.nan).dropna(how="all")

def momentum_score(prices: pd.DataFrame, lookback_days: int = 126) -> pd.Series: #fonction plus solide on ajuste le momentum au risque
    """
    Risk-adjusted momentum:
    score = cumulative return over lookback / annualized volatility over lookback
    """
    prices = prices.dropna(how="all")
    if prices.empty or len(prices) <= lookback_days:
        return pd.Series(index=prices.columns, dtype=float)

    # returns for vol
    r = pct_returns(prices).dropna(how="all")
    r_lb = r.tail(lookback_days)

    # annualized vol over lookback
    vol = r_lb.std() * np.sqrt(252)
    
    # cumulative return over lookback
    mom = (prices.iloc[-1] / prices.iloc[-1 - lookback_days] - 1.0) / vol.replace(0, np.nan)

    return mom.replace([np.inf, -np.inf], np.nan)


def annualize_stats(daily_returns: pd.Series) -> dict:
    daily_returns = daily_returns.dropna()
    if daily_returns.empty:
        return {"ret": np.nan, "vol": np.nan, "sharpe": np.nan}
    mu = daily_returns.mean() * 252
    vol = daily_returns.std() * np.sqrt(252)
    sharpe = (mu / vol) if vol and vol > 0 else np.nan
    return {"ret": mu, "vol": vol, "sharpe": sharpe}

def clamp_weights(w: np.ndarray) -> np.ndarray:
    # Nettoie les petits artefacts numériques (ex: -1e-12) et renormalise
    w = np.maximum(w, 0.0)
    s = w.sum()
    return (w / s) if s > 0 else w

def optimize_mean_variance(mu: np.ndarray, cov: np.ndarray, risk_aversion: float, max_weight: float = 0.40, min_weight: float = 0.0, ridge: float = 1e-6
) -> np.ndarray:
    """
    Maximise: mu^T w - risk_aversion * (w^T cov w)
    s.c. sum(w)=1, min_weight <= w_i <= max_weight
    """

    n = len(mu)
    if n == 0:
        return np.array([])
    if n == 1:
        return np.array([1.0])

    # Nettoyage NaN
    mu = np.nan_to_num(mu, nan=0.0, posinf=0.0, neginf=0.0)
    cov = np.nan_to_num(cov, nan=0.0, posinf=0.0, neginf=0.0)

    # Stabilise la covariance (utile si cov bruitée / presque singulière)
    cov = cov + ridge * np.eye(n)

    # Sanitize bornes
    min_w = max(0.0, float(min_weight))
    max_w = float(max_weight)

    # Si min > max, on écrase min au max (sinon impossible)
    if min_w > max_w:
        min_w = max_w

    # Faisabilité : n*min <= 1 et n*max >= 1
    # Si min trop haut, on le réduit au maximum faisable
    if n * min_w > 1.0:
        min_w = 1.0 / n

    # Si max trop bas, on ne peut pas sommer à 1 -> fallback equal-weight
    if n * max_w < 1.0:
        return np.ones(n) / n

    def obj(w):
        # minimize négatif de l'utilité (équivalent à maximiser utilité)
        return -(mu @ w - risk_aversion * (w @ cov @ w))

    cons = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]
    bounds = [(min_w, max_w) for _ in range(n)]

    # point initial: équipondéré, puis clip dans les bornes et renormalise
    x0 = np.ones(n) / n
    x0 = np.clip(x0, min_w, max_w)
    x0 = x0 / x0.sum()

    res = minimize(obj, x0, bounds=bounds, constraints=cons, method="SLSQP")

    if not res.success or res.x is None:
        return x0

    # Nettoyage final
    w = res.x
    w = np.clip(w, min_w, max_w)
    w = w / w.sum()

    return clamp_weights(w)

@st.cache_data
def fetch_adjclose(tickers, start="2015-01-01") -> pd.DataFrame: #start est un paramètre on voudrait que ça soit une variable ici
    tickers = [t.strip() for t in tickers if t and str(t).strip()]
    if not tickers:
        return pd.DataFrame()

    data = yf.download(
        tickers=tickers,
        start=start,
        progress=False,
        auto_adjust=False,
        group_by="column",
        threads=True
    )

    if data is None or len(data) == 0:
        return pd.DataFrame()

    if isinstance(data.columns, pd.MultiIndex):
        if "Adj Close" in data.columns.get_level_values(0):
            adj = data["Adj Close"].copy()
        else:
            adj = data["Close"].copy()
    else:
        if "Adj Close" in data.columns:
            adj = data[["Adj Close"]].rename(columns={"Adj Close": tickers[0]})
        elif "Close" in data.columns:
            adj = data[["Close"]].rename(columns={"Close": tickers[0]})
        else:
            adj = pd.DataFrame()

    adj = adj.dropna(how="all")
    adj.index = pd.to_datetime(adj.index)
    return adj

def get_names(ticker_list):
    return [yf.Ticker(t).info.get("longName", t) for t in ticker_list]
# ============================================================
# CORE ETFs (Yahoo tickers)
# ============================================================
CORE_MAP = {
    "S&P 500 (CSPX)": ["CSPX.L", "CSPX.AS"],
    "Euro Stoxx 50 (CSSX5E)": ["CSSX5E.MI", "CSSX5E.SW"],
    "MSCI World (SWDA)": ["SWDA.L", "SWDA.MI", "SWDA.SW"],
}

# ============================================================
# SATELLITES
# ============================================================
SATELLITES = [
    {"name": "Emerging Markets (stocks)", "key": "EM", "geo": "Global EM", "desc": "Sélection momentum sur gros EM (actions/ADR)"},
    {"name": "Commodities (futures)", "key": "METALS", "geo": "Global", "desc": "Sélection momentum sur futures matières premières"},
    {"name": "Banks", "key": "BANKS", "geo": "Global", "desc": "Sélection momentum sur banques (US/Europe/Asie)"},
    {"name": "Tech / IA", "key": "TECH", "geo": "Global", "desc": "Sélection momentum sur Big Tech / Semi / Software"},
    {"name": "Defense", "key": "DEF", "geo": "Global", "desc": "Sélection momentum sur défense/aérospatial"},
    {"name": "Energy", "key": "ENERGY", "geo": "Global", "desc": "Sélection momentum sur oil & gas (US/Europe/Canada/Asie)"},
]

SAT_UNIVERSE = {
    "EM": ["2330.TW","2317.TW","2454.TW","2881.TW","2882.TW","2891.TW","2303.TW","3711.TW","2884.TW","3231.TW","2327.TW","2601.TW","1216.TW","1109.TW","2880.TW","0700.HK","9988.HK","0939.HK","1810.HK","2318.HK","0999.HK","1211.HK","9961.HK","3988.HK","0386.HK","2628.HK","1398.HK","9618.HK","3690.HK","2899.HK","0883.HK","0688.HK","0669.HK","2388.HK","0288.HK","1928.HK","1378.HK","005930.KS","000660.KS","051910.KS","035420.KS","012450.KS","005935.KS","068270.KS","000270.KS","105560.KS","HDFCBANK.NS","RELIANCE.NS","INFY.NS","BHARTIARTL.NS","ICICIBANK.NS","LT.NS","TCS.NS","AXISBANK.NS","BAJFINANCE.NS","MARUTI.NS","HINDUNILVR.NS","SUNPHARMA.NS","WIPRO.NS","ITC.NS","TITAN.NS","ULTRACEMCO.NS","NTPC.NS","ONGC.NS","ADANIENT.NS","VALE3.SA","PETR4.SA","ITSA4.SA","BBDC4.SA","ABEV3.SA","WEGE3.SA","HAPV3.SA","SBSP3.SA","AMXB.MX","FEMSAUBD.MX","WALMEX.MX","GMEXICOB.MX","PE&OLES.MX","GAPB.MX","NPN.JO","ANG.JO","MTN.JO","SBK.JO","2222.SR","1120.SR","1180.SR","2010.SR","2020.SR","EMIRATESDU.AE","PKO.WA","OTP.BD","CEZ.PR"],
    "METALS": ["GC=F","SI=F","NG=F","HG=F","BZ=F","ZS=F","CL=F","ZC=F","ALI=F","LE=F","ZL=F","ZM=F","KC=F","ZW=F","SB=F","HO=F","RB=F","HE=F","KE=F","CT=F"],
    "BANKS": ["JPM","BAC","WFC","C","GS","MS","PNC","USB","TFC","SCHW","BK","STT","NTRS","FITB","HBAN","CFG","CMA","MTB","KEY","RF","RY.TO","TD.TO","BNS.TO","BMO.TO","CM.TO","NA.TO","CIBC.TO","HSBA.L","LLOY.L","NWG.L","STAN.L","BARC.L","BNP.PA","GLE.PA","ACA.PA","SAN.MC","BBVA.MC","INGA.AS","DBK.DE","CBK.DE","UCG.MI","ISP.MI","BAMI.MI","SAB.MC","ABN.AS","KBC.BR","SWED-A.ST","SEB-A.ST","DANSKE.CO","NDA-FI.HE","NDA-SE.ST","UBSG.SW","BCVN.SW","MFG","SMFG","MUFG","DBS.SI","UOB.SI","OCBC.SI","8306.T","8316.T","8411.T","ITUB","BBD","BBAS","SAN","IBN","HDFC","KB","BBCA.JK","BMRI.JK"],
    "TECH": ["NVDA","AAPL","MSFT","AVGO","PLTR","AMD","ORCL","MU","CSCO","IBM","CRM","INTC","ADBE","TXN","ANET","ADI","PANW","CRWD","SNPS","CDNS","QCOM","ACN","NOW","INTU","WDAY","MRVL","DELL","MSTR","KEYS","NET","DDOG","MDB","HPE","TER","ASML.AS","SAP.DE","STM.PA","IFX.DE","NOKIA.HE","ERIC-B.ST","CAP.PA","DSY.PA","ATE.PA","RNE.PA","8035.T","6857.T","6723.T","6702.T","6701.T","6762.T","7751.T","8056.T","4307.T","4704.T","4684.T","7735.T","4709.T","4768.T","4716.T","2330.TW","2303.TW","3711.TW","3034.TW","005930.KS","000660.KS","BABA","BIDU","TCEHY","LOGN.SW","SGE.L","NICE","NEM.DE"],
    "DEF": ["GE","RTX","BA","AIR.PA","RR.L","SAF.PA","LMT","RHM.DE","HWM","NOC","GD","TDG","BA.L","LHX","AXON","RKLB","HO.PA","LDO.MI","MTX.DfE","HEI","SAAB-B.ST","ESLT","TXT","BBD-B.TO","HEI.A","KOG.OL","S63.SI","MRO.L","CAE.TO","AM.PA","HAG.DE"],
    "ENERGY": ["XOM","CVX","COP","EOG","OXY","SLB","HAL","KMI","WMB","PSX","MPC","VLO","OKE","DVN","HES","FANG","APA","SHEL.L","BP.L","TTE","EQNR","REP.MC","ENI.MI","GALP.LS","CNQ.TO","SU.TO","TRP.TO","IMO.TO","PETRONAS.KL","PTT.BK","STO.AX","Santos.AX","YPF","PBR","AKRBP.OL","OMV.VI","KEY.TO"],
} #on voudrait avoir les noms associés à chaque tickers

# ============================================================
# HEADER
# ============================================================
st.markdown("<h1 style='text-align:center;'>Momentum-X</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center; color:#555;'>Core ETF + Satellites (stocks/futures sélectionnés par momentum)</h3>", unsafe_allow_html=True) #ptet changer cette ligne pour que ce soit plus stylé le nom
st.markdown("---")

tab_kyc, tab_strategy = st.tabs(["Profil investisseur", "Stratégie Momentum-X"])

# ============================================================
# TAB 1: KYC On créée le questionnaire KYC
# ============================================================
with tab_kyc:
    st.subheader("Questionnaire de profil de risque")
    st.write("Le profil ajuste automatiquement l’allocation cœur vs satellites et l’aversion au risque.")
    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

    st.markdown("#### 1. Horizon d'investissement")
    q1_options = {"Moins de 1 an": 1, "1 à 3 ans": 2, "3 à 5 ans": 3, "5 à 10 ans": 4, "Plus de 10 ans": 5}
    q1_choice = st.radio("Combien de temps souhaitez-vous investir ?", list(q1_options.keys()))
    q1_score = q1_options[q1_choice]

    st.markdown("#### 2. Réaction à une baisse de 15% en 1 mois")
    q2_options = {
        "Je vends immédiatement pour couper la perte": 1,
        "Je réduis un peu l'exposition": 2,
        "Je garde la position": 4,
        "Je renforce car c'est une opportunité": 5,
    }
    q2_choice = st.radio("Que faites-vous ?", list(q2_options.keys()))
    q2_score = q2_options[q2_choice]

    st.markdown("#### 3. Stabilité vs performance")
    q3_options = {
        "Je privilégie avant tout la stabilité du capital": 1,
        "Je suis prêt à accepter un peu de volatilité": 3,
        "Je cherche surtout la performance, même volatile": 5,
    }
    q3_choice = st.radio("Quel est votre point de vue ?", list(q3_options.keys()))
    q3_score = q3_options[q3_choice]

    st.markdown("#### 4. Expérience en investissement")
    q4_options = {
        "Aucune": 1,
        "Faible (Livret, PEA simple...)": 2,
        "Moyenne (fonds, ETF...)": 3,
        "Bonne (actions, suivi régulier)": 4,
        "Très avancée (dérivés, gestion active...)": 5,
    }
    q4_choice = st.radio("Comment évaluez-vous votre expérience ?", list(q4_options.keys()))
    q4_score = q4_options[q4_choice]

    st.markdown("#### 5. Volatilité")
    q5_options = {
        "La volatilité me stresse beaucoup": 1,
        "Elle me met un peu mal à l'aise": 2,
        "Je reste plutôt neutre": 3,
        "Je suis à l'aise": 4,
        "Je vois cela comme une opportunité": 5,
    }
    q5_choice = st.radio("Comment vous sentez-vous face aux fluctuations de marché ?", list(q5_options.keys()))
    q5_score = q5_options[q5_choice]

    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

    if st.button("Calculer mon profil de risque"):
        score_total = q1_score + q2_score + q3_score + q4_score + q5_score
        if score_total <= 12:
            risk_profile = "Prudent"
        elif score_total <= 18:
            risk_profile = "Équilibré"
        else:
            risk_profile = "Dynamique"

        st.session_state["risk_score"] = score_total
        st.session_state["risk_profile"] = risk_profile
        st.success(f"Votre Profil est: **{risk_profile}**")

    prof = st.session_state.get("risk_profile", None)

    c1, c2, c3 = st.columns(3)
    
    def card(title, subtitle, desc, theme="neutral", active=False):
        cls = f"risk-card risk-card--{theme}"
        if active:
            cls += " risk-card--active"

        return f"""
        <div class="{cls}">
            <div class="risk-title">{title}</div>
            <div class="risk-level">{subtitle}</div>
            <p class="muted">{desc}</p>
        </div>
        """
    
    with c1:
        st.markdown(card("Prudent","Risque limité",
                         "Cœur dominant, satellites limités, optimisation défensive.",
                         theme="prudent", active=(prof=="Prudent")),
                    unsafe_allow_html=True)

    with c2:
        st.markdown(card("Équilibré","Compromis",
                         "Cœur important + satellites diversifiés, optimisation modérée.",
                         theme="equilibre", active=(prof=="Équilibré")),
                    unsafe_allow_html=True)

    with c3:
        st.markdown(card("Dynamique","Performance",
                         "Satellites plus importants, optimisation plus agressive.",
                         theme="dynamique", active=(prof=="Dynamique")),
                    unsafe_allow_html=True)

    if prof:
        st.info("Ton profil sera utilisé dans l’onglet Stratégie.")
    else:
        st.warning("Clique sur « Calculer mon profil » pour activer l’auto-paramétrage.")

# ============================================================
# TAB 2: STRATEGY
# ============================================================
with tab_strategy:
    st.subheader("Core ETF + Satellites (momentum sélection Top K)")

    st.sidebar.header("Paramètres")
    start_date = st.sidebar.text_input("Start date (YYYY-MM-DD)", "2015-01-01")
    lookback = st.sidebar.selectbox("Lookback momentum (jours)", [63, 126, 252], index=1)
    top_k = st.sidebar.selectbox("Top K par satellite (momentum)", [3, 4, 5, 6, 7,  8, 9, 10, 11, 12, 13, 14, 15], index=2)
    max_w_stock = st.sidebar.slider("Poids max par actif (intra-satellite)", 0.10, 1.00, 0.40, 0.01)
    max_w_sat = st.sidebar.slider("Poids max par satellite (inter-satellites)", 0.10, 1.00, 0.60, 0.01)
    #min_w_stock = st.sidebar.slider("Poids max par actif (intra-satellite)", 0.05, 1.00, 0.40, 0.01) #raajout pour min sur opti oui mais le min est fonction du nombre d'actifs ....donc 0.05 pas tjrs possible....
    #min_w_sat = st.sidebar.slider("Poids max par actif (intra-satellite)", 0.05, 1.00, 0.40, 0.01)
    min_w_stock = 0.5 / top_k   # min dynamique: 50% du equal-weight

    risk_profile = st.session_state.get("risk_profile", "Non défini")
    if risk_profile == "Prudent":
        core_default, risk_aversion = 0.80, 12.0
    elif risk_profile == "Équilibré":
        core_default, risk_aversion = 0.65, 6.0
    elif risk_profile == "Dynamique":
        core_default, risk_aversion = 0.50, 2.5
    else:
        core_default, risk_aversion = 0.70, 7.0

    st.markdown("### 1) Choix du cœur ETF et de la répartition Coeur/Satellites") #la répartition coeur/satellite ne se fait pas dans lopti ? si oui, on enleve la partie sur la répartition...
    core_choice = st.selectbox("Core ETF :", list(CORE_MAP.keys()))
    
    st.caption(f"Préférez-vous conserver la répartition Coeur/Satellite associé à votre profil investisseur ? (Vous pourrez dans le cas inverse, effectuer manuellement cette répartition.)")

    use_auto = st.toggle("Sélection automatique selon votre profil investisseur.", value=True)
    if use_auto:
        core_weight = core_default
    else:
        core_weight = st.slider("Poids du cœur", 0.0, 1.0, float(core_default), 0.05)
    sats_weight = 1.0 - core_weight

    st.caption(f"Profil: {risk_profile} | risk_aversion={risk_aversion} | Core={core_weight:.0%} / Satellites={sats_weight:.0%}") # c'est moche ptet qu'il faut garder que "Prudent et la répartition" donc enlever le risk aversion truc

    core_prices = pd.DataFrame()
    core_ticker_used = None
    for t in CORE_MAP[core_choice]:
        p = fetch_adjclose([t], start=start_date)
        if not p.empty:
            core_prices = p.rename(columns={p.columns[0]: t}) # pas compris cette lin
            core_ticker_used = t
            break

    if core_prices.empty:
        st.error("Impossible de télécharger le core via Yahoo Finance (suffix).")
        st.stop()

    st.markdown("### 2) Satellites (thèmes)")
    cols = st.columns(3)

    def toggle_satellite(sat_key: str):
        s = {k.strip().upper() for k in st.session_state["selected_sats"]}
        if sat_key in s:
            s.remove(sat_key)
        else:
            s.add(sat_key)
        st.session_state["selected_sats"] = s

    cols = st.columns(3)

    for i, sat in enumerate(SATELLITES):
        col = cols[i % 3]
        with col:
            sat_key = sat["key"].strip().upper()
            selected_set = {k.strip().upper() for k in st.session_state["selected_sats"]}
            selected = sat_key in selected_set

            # couleurs premium B
            border = "#60A5FA" if selected else "#334155"
            bg = "#E0F2FE" if selected else "#0F172A"
            text = "#0F172A" if selected else "#F8FAFC"
            muted = "#334155" if selected else "#CBD5E1"

            # 1) carte d'abord
            st.markdown(
                f"""
                <div style="border:2px solid {border}; background:{bg}; border-radius:12px;
                            padding:0.75rem 0.85rem; margin-bottom:0.5rem;">
                    <div style="font-weight:700; font-size:1.05rem; color:{text};">
                        {sat["name"]}
                    </div>
                    <div style="font-size:0.95rem; color:{muted};">
                        Géo : {sat["geo"]}
                    </div>
                    <div style="color:{muted}; margin-top:0.35rem;">
                        {sat["desc"]}
                    </div>
                    <div style="font-size:0.85rem; color:{muted}; margin-top:0.35rem;">
                        Univers: {len(SAT_UNIVERSE.get(sat_key, []))} actifs
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # 2) bouton ensuite (sous la carte)
            st.button(
                "✅ Sélectionné" if selected else "➕ Ajouter",
                key=f"sat_btn_{sat_key}",
                type="primary" if selected else "secondary",
                on_click=toggle_satellite,
                args=(sat_key,),
            )


    selected_sats = list(st.session_state["selected_sats"])
    if not selected_sats:
        st.info("Sélectionne au moins 1 satellite.")
        df_donut = pd.DataFrame({"Bloc":["Cœur"], "Poids":[1.0]})
        st.plotly_chart(px.pie(df_donut, names="Bloc", values="Poids", hole=0.55), use_container_width=True)
        st.stop()

    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
    st.markdown("### 3) Momentum → sélection Top K → optimisation intra-satellite")
    st.caption(f"Min weight auto (intra) = {min_w_stock:.2%} (≈ 50% de 1/K)")

    ###################################################################################
    ## Cette section est le “cœur quant” du projet. Elle fait, pour chaque satellite sélectionné :
    ## 1) Télécharger les prix des titres composant son univers
    ## 2) Calculer les scores momentum de chacun des ses constituants
    ## 3) Garder les Top K titres
    ## 4) Optimiser les poids des Top K (avec un optimisateur mean–variance)
    ## 5) Produire une série de rendement “satellite” et un résumé
    ###################################################################################

    sat_stock_weights = {}
    sat_returns_series = {}
    sat_summary_rows = []

    for sat_key in selected_sats:
        universe = SAT_UNIVERSE.get(sat_key, [])
        prices = fetch_adjclose(universe, start=start_date)

        prices = prices.dropna(axis=1, how="all")
        if prices.empty or prices.shape[1] < 2:
            sat_summary_rows.append([sat_key, "NO DATA", 0, np.nan, np.nan, np.nan])
            sat_returns_series[sat_key] = pd.Series(dtype=float)
            continue

        mom = momentum_score(prices, lookback_days=lookback).dropna().sort_values(ascending=False)
        top = mom.head(top_k).index.tolist()

        if len(top) == 0:
            sat_summary_rows.append([sat_key, "NO TOP", 0, np.nan, np.nan, np.nan])
            sat_returns_series[sat_key] = pd.Series(dtype=float)
            continue

        p_sel = prices[top].dropna(how="all")
        r_sel = pct_returns(p_sel).dropna(how="any")

        if r_sel.empty:
            sat_summary_rows.append([sat_key, ", ".join(get_names(top)), len(top), np.nan, np.nan, np.nan])
            sat_returns_series[sat_key] = pd.Series(dtype=float)
            continue

        mu = mom.reindex(top).fillna(0.0).values
        r_last = r_sel.tail(252)
        cov = r_last.cov().values if len(r_last) > 5 else np.eye(len(top)) * 1e-6

        w_intra = optimize_mean_variance(mu=mu, cov=cov, risk_aversion=risk_aversion, max_weight=max_w_stock, min_weight=min_w_stock)
        w_intra_ser = pd.Series(w_intra, index=top).sort_values(ascending=False)

        sat_ret = (r_sel @ w_intra_ser.reindex(top).values)
        sat_returns_series[sat_key] = sat_ret

        stats = annualize_stats(sat_ret)
        sat_mom_avg = float(np.average(mom.reindex(top).values, weights=w_intra_ser.reindex(top).values)) if w_intra_ser.sum() > 0 else float(mom.reindex(top).mean())
        sat_summary_rows.append([sat_key, ", ".join(get_names(top)), len(top), sat_mom_avg, stats["ret"], stats["vol"]])

        sat_stock_weights[sat_key] = w_intra_ser

    df_sat_summary = pd.DataFrame(
        sat_summary_rows,
        columns=["Satellite", f"Top {top_k}", "K", f"Momentum({lookback}j)", "Return ann.", "Vol ann."]
    )
    st.dataframe(df_sat_summary, use_container_width=True, hide_index=True)

    with st.expander("Détail poids intra-satellite"):
        for sat_key in selected_sats:
            w = sat_stock_weights.get(sat_key)
            if w is None or w.empty:
                st.write(f"**{sat_key}** : pas de données.")
                continue
            st.write(f"**{sat_key}**")
            w_named = w.copy()
            w_named.index = get_names(w_named.index.tolist())
            st.dataframe(w_named.reset_index().rename(columns={"index":"Titre", 0:"Poids"}), use_container_width=True, hide_index=True)


    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
    st.markdown("### 4) Optimisation inter-satellites")

    valid = [k for k in selected_sats if not sat_returns_series.get(k, pd.Series(dtype=float)).dropna().empty]
    if len(valid) == 0:
        st.error("Aucun satellite exploitable (données Yahoo manquantes).")
        st.stop()

    rets_df = pd.concat([sat_returns_series[k].rename(k) for k in valid], axis=1).dropna(how="any")

    mu_sats = []
    for k in valid:
        row = df_sat_summary[df_sat_summary["Satellite"] == k]
        mu_sats.append(float(row[f"Momentum({lookback}j)"].iloc[0]) if not row.empty else 0.0)
    mu_sats = np.array([0.0 if not np.isfinite(x) else x for x in mu_sats])

    cov_sats = rets_df.cov().values if rets_df.shape[0] > 5 else np.eye(len(valid)) * 1e-6
    
    # Min inter-satellites dynamique (ex: 50% de l'équipondération)
    n_sat = len(valid)
    min_w_sat = 0.5 / n_sat
    st.caption(f"Min weight auto (inter) = {min_w_sat:.2%} (≈ 50% de 1/N)")

    w_sats = optimize_mean_variance(mu=mu_sats, cov=cov_sats, risk_aversion=risk_aversion, max_weight=max_w_sat, min_weight=min_w_sat)
    w_sats_ser = pd.Series(w_sats, index=valid).sort_values(ascending=False)

    st.dataframe(w_sats_ser.reset_index().rename(columns={"index":"Satellite", 0:"Poids"}), use_container_width=True, hide_index=True)

    sat_port_ret = rets_df @ w_sats_ser.reindex(valid).values

    core_ret = pct_returns(core_prices).iloc[:, 0].dropna()
    common = core_ret.index.intersection(sat_port_ret.index)
    core_ret = core_ret.loc[common]
    sat_port_ret = sat_port_ret.loc[common]

    port_ret = core_weight * core_ret + sats_weight * sat_port_ret
    
    
    # ============================================================
    # BUY LIST (final weights)
    # ============================================================
    final_positions = {}

    # 1) Core ETF
    final_positions[core_ticker_used] = float(core_weight)

    # 2) Satellites -> stocks
    for sat_key in valid:
        sat_w = float(w_sats_ser.get(sat_key, 0.0))
        if sat_w <= 0:
            continue

        intra = sat_stock_weights.get(sat_key)
        if intra is None or intra.empty:
            continue

        for ticker, w_intra in intra.items():
            w_final = float(sats_weight) * sat_w * float(w_intra)
            if w_final > 0:
                final_positions[ticker] = final_positions.get(ticker, 0.0) + w_final

    tickers_final = list(final_positions.keys())
    names_final = get_names(tickers_final)
    df_buy = (
        pd.DataFrame({"Titre": names_final, "Ticker": tickers_final, "Poids": list(final_positions.values())})
        .sort_values("Poids", ascending=False)
        .reset_index(drop=True)
).set_index("Titre")


    # ============================================================
    # DISPLAY RESULTS
    # ============================================================
    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
    st.markdown("## Résultats")

    donut = pd.DataFrame({"Bloc":["Cœur", "Satellites"], "Poids":[core_weight, sats_weight]})
    st.plotly_chart(px.pie(donut, names="Bloc", values="Poids", hole=0.55), use_container_width=True)

    cum = (1 + port_ret.fillna(0)).cumprod()
    df_cum = cum.to_frame("Portfolio").reset_index().rename(columns={"index":"Date"})
    st.plotly_chart(px.line(df_cum, x="Date", y="Portfolio"), use_container_width=True)

    s_core = annualize_stats(core_ret)
    s_sat = annualize_stats(sat_port_ret)
    s_all = annualize_stats(port_ret)

    summary = pd.DataFrame([
        [f"Cœur ({core_ticker_used})", s_core["ret"], s_core["vol"], s_core["sharpe"]],
        ["Satellites (momentum+opti)", s_sat["ret"], s_sat["vol"], s_sat["sharpe"]],
        ["Portefeuille final", s_all["ret"], s_all["vol"], s_all["sharpe"]],
    ], columns=["Bloc", "Return", "Vol", "Sharpe"]).set_index("Bloc")

    st.dataframe(summary.style.format({"Return":"{:.2%}", "Vol":"{:.2%}", "Sharpe":"{:.2f}"}), use_container_width=True)

    st.markdown("## 🧾 Liste d'achat (poids finaux)")
    st.dataframe(df_buy.style.format({"Poids": "{:.2%}"}), use_container_width=True)


    df_export = df_buy.copy()
    df_export["Poids"] = (df_export["Poids"] * 100).round(2).astype(str) + "%"

    st.download_button(
        "⬇️ Télécharger la liste d'achat (CSV)",
        data=df_export.to_csv(index=False).encode("utf-8"),
        file_name="buy_list_momentumx.csv",
        mime="text/csv"
    )

    st.caption(f"Somme totale des poids = {df_buy['Poids'].sum():.2%}")
