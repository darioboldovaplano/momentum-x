# 💹 Momentum-X

Application Streamlit de stratégie d’investissement **Cœur-Satellites** avec sélection dynamique par **momentum**.

## 📁 Contenu

- Questionnaire KYC pour définir le profil investisseur
- Allocation cœur ETF + satellites (actions / futures)
- Sélection momentum Top K par satellite
- Optimisation intra- et inter-satellite
- Visualisation des performances
- Export CSV de la liste d'achat

## ▶️ Lancer l'application

```bash
pip install -r requirements.txt
streamlit run main.py

##🌐 Utilisation de l’application web

Une fois l'application Streamlit lancée, voici comment l’utiliser pas à pas :

1. Onglet “Profil investisseur”

Objectif : Définir ton profil de risque via un mini questionnaire.

Réponds aux 5 questions (horizon, réaction au risque, etc.).

Clique sur “Calculer mon profil de risque”.

Un profil te sera attribué automatiquement :
Prudent, Équilibré, ou Dynamique.

Ce profil influencera l’allocation entre le Cœur (ETF) et les Satellites (actions à fort momentum).

2. Onglet “Stratégie Momentum-X”

Objectif : Construire un portefeuille optimal cœur + satellites.

a. Paramètres dans la sidebar (gauche) :

Choisis la date de départ du backtest.

Sélectionne le lookback momentum (63j, 126j, 252j).

Choisis le nombre d’actions (Top K) à sélectionner par satellite.

Ajuste les contraintes de poids :
poids max par actif et par satellite.

b. Cœur :

Sélectionne ton ETF principal (S&P500, MSCI World, etc.).

Sois libre de laisser l’application gérer automatiquement l’allocation (selon ton profil) ou la régler manuellement.

c. Satellites :

Clique sur “Ajouter” sous les thèmes qui t'intéressent (Tech, Défense, Énergie...).

Un résumé des actifs disponibles est affiché sous chaque carte.

Tu peux en choisir plusieurs.

d. Sélection momentum et optimisation :

Les actions à plus fort momentum sont sélectionnées automatiquement (Top K).

Une optimisation est faite intra-satellite puis entre satellites pour maximiser le couple rendement/risque.

Tous les calculs sont faits à partir des données Yahoo Finance.

3. Résultats

Affichage du portefeuille final avec graphique de répartition.

Courbe de performance cumulée.

Tableau comparatif des performances :

Cœur

Satellites

Portefeuille global

Liste d'achat finale : tickers + poids

Possibilité de télécharger un fichier CSV.
