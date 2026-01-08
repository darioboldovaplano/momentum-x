# 💹 Momentum-X

Application Streamlit de stratégie d’investissement **Cœur-Satellites** avec sélection dynamique par **momentum**.

---

## 📁 Contenu

- Questionnaire KYC pour définir le profil investisseur  
- Allocation cœur ETF + satellites (actions / futures)  
- Sélection momentum Top K par satellite  
- Optimisation intra- et inter-satellite  
- Visualisation des performances  
- Export CSV de la liste d'achat  

---

## ▶️ Installation & Lancement

1. Ouvre un terminal (PowerShell ou Git Bash)
2. Clone ce dépôt ou crée un dossier et place le fichier `main.py` + `requirements.txt` à la racine
3. Dans le terminal :

```bash
pip install -r requirements.txt
streamlit run main.py

```

## 🌐 Mode d’emploi (pas à pas)

### 🧠 1. Onglet “Profil investisseur”

🎯 **Objectif** : Définir ton profil de risque via un mini questionnaire.

- Réponds aux 5 questions (horizon, réaction au risque, etc.)
- Clique sur **“Calculer mon profil de risque”**
- Tu obtiens l’un des profils suivants :
  - Prudent
  - Équilibré
  - Dynamique

➡️ Ce profil influencera automatiquement l’allocation entre le Cœur (ETF) et les Satellites (actions à fort momentum).

---

### 📊 2. Onglet “Stratégie Momentum-X”

🎯 **Objectif** : Construire un portefeuille optimal cœur + satellites.

#### a) Paramètres (à gauche)

- Choisis la date de départ du backtest
- Sélectionne le lookback momentum (63j, 126j, 252j)
- Définis le nombre d’actions (Top K) par satellite
- Ajuste les contraintes de poids (par actif et par satellite)

#### b) Cœur (ETF)

- Choisis un ETF EuroStoxx 50 dans la liste proposée
- Il représentera la base défensive du portefeuille

#### c) Satellites (thématiques)

- Clique sur **Ajouter** les satellites que tu veux inclure
- Un résumé s’affiche sous chaque carte (US Equity, Défense, EM, etc.)

#### d) Sélection momentum & optimisation

- Les meilleurs titres sont automatiquement sélectionnés (Top K)
- Optimisation **intra-satellite** : répartition à l’intérieur d’un thème
- Optimisation **inter-satellites** : poids alloués à chaque satellite
- Données extraites de Yahoo Finance

---

### 📈 3. Résultats

- Graphique donut : répartition cœur / satellites
- Tableau : top titres sélectionnés par momentum
- Détail par satellite : rendement, volatilité, momentum
- ✅ Liste d’achat finale (tickers + poids optimisés)
- 💾 Export CSV disponible
