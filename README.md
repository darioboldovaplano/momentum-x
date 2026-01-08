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

## 🌐 Mode d’emploi (pas à pas)
🧠 1. Onglet “Profil investisseur”

🎯 Objectif : Définir ton profil de risque via un mini questionnaire.

Réponds aux 5 questions (horizon, réaction au risque, etc.)

Clique sur “Calculer mon profil de risque”

Tu obtiens un des profils suivants :

🟢 Prudent

🔵 Équilibré

🔴 Dynamique

👉 Ce profil ajuste automatiquement :

L’allocation entre cœur (ETF) et satellites (actions)

Le niveau d’aversion au risque pour l’optimisation

📊 2. Onglet “Stratégie Momentum-X”

🎯 Objectif : Construire ton portefeuille optimal.

a. Paramètres à gauche (sidebar)

Date de départ du backtest

Lookback momentum (63 / 126 / 252 jours)

Top K : nombre d’actions sélectionnées par satellite

Contraintes de poids :

par actif (intra-satellite)

par satellite (inter-satellites)

b. Cœur ETF

Choisis ton ETF principal (ex : MSCI World, S&P500, etc.)

Active (ou non) la gestion automatique selon ton profil

c. Satellites

Clique sur "Ajouter" sous les thèmes qui t'intéressent :

Tech / IA

Banques

Énergie

Défense

Matières premières (futures)

Marchés émergents

Chaque thème contient plusieurs actions sélectionnables

d. Sélection & Optimisation

Les meilleurs actifs sont sélectionnés automatiquement (Top K momentum)

L’optimisation moyenne-variance est effectuée :

Intra-satellite : pondération des actions d’un thème

Inter-satellites : pondération entre les thèmes choisis

Données récupérées depuis Yahoo Finance

📈 3. Résultats

Graphique de répartition : cœur vs satellites

Courbe de performance cumulée

Tableau des performances :

Bloc Cœur

Bloc Satellites

Portefeuille global

✅ Liste d'achat finale :

Tickers des actifs sélectionnés

Poids de chaque actif

Téléchargement du fichier CSV prêt à l’emploi
