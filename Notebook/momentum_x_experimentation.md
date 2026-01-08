# Notebook de Conception du Projet Momentum-X

## Objectif du projet

Ce projet visait à concevoir une application Streamlit permettant de générer un portefeuille d'investissement selon une logique Cœur / Satellites, avec sélection dynamique par **momentum** et optimisation basée sur le profil de risque de l’utilisateur.

## Idée initiale

* Créer une interface claire, éducative et fonctionnelle permettant à un investisseur non-expert de construire un portefeuille optimisé en fonction de son appétence au risque.
* Combiner la simplicité des ETFs "cœur" à une sélection dynamique d’actifs satellites plus tactiques.
* L’inspiration est venue des portefeuilles en gestion pilotée proposés par certains robo-advisors, mais en apportant un degré plus élevé de transparence et de personnalisation.

## Étapes de conception

### 1. Profilage utilisateur (KYC simplifié)

* Nous avons conçu un petit questionnaire à 5 questions pour capter rapidement l’appétence au risque de l’utilisateur.
* Ce profil détermine deux paramètres clés :

  * Le poids du **cœur** dans le portefeuille
  * L’**aversion au risque** utilisée dans les optimisations quadratiques.

### 2. ETFs cœur : choix et évolutions

* **Hypothèse initiale** : proposer un unique ETF Euro Stoxx 50 (CSSX5E) comme cœur du portefeuille.
* **Problème identifié** : trop restrictif pour certains utilisateurs souhaitant une exposition plus globale ou américaine.
* **Évolution** : nous avons élargi le choix avec d’autres ETFs cœur comme le MSCI World (SWDA) et le S&P 500 (CSPX).
* **Défi rencontré** : certains suffixes sur Yahoo Finance (.MI, .SW, .L) ne sont pas toujours disponibles selon les périodes, ce qui nous a obligés à tester plusieurs variantes pour chaque ETF cœur.

### 3. Satellites : sélection et complexité

* Plusieurs univers thématiques définis (Tech, Énergie, Défense, Banques, Métaux, Marchés émergents).
* Chaque satellite est constitué d’une liste d’actifs (souvent > 50 tickers).
* **Défi majeur** :

  * Initialement, nous avons essayé d'extraire les composantes des indices thématiques via Bloomberg.
  * Les tickers Bloomberg étant incompatibles avec Yahoo Finance, il a fallu retrouver les correspondances exactes pour chacun d’eux, souvent manuellement.
  * Cette **conversion des tickers** s’est révélée **extrêmement longue et délicate**.

### 4. Sélection par Momentum

* Pour chaque satellite sélectionné, on applique un ranking momentum (performance sur 63, 126 ou 252 jours).
* L’utilisateur peut choisir le nombre d’actifs à retenir (Top K).

### 5. Optimisation intra-satellite

* Les Top K actifs sélectionnés sont pondérés via une optimisation moyenne-variance (maximisation du Sharpe ratio sous contraintes).
* Limitations observées :

  * Certaines périodes avec peu de données entraînent des matrices de covariance peu fiables.
  * Des satellites comme Banques ou Défense ont parfois très peu d’actifs valides (manque de données Yahoo).

### 6. Optimisation inter-satellite

* Une seconde couche d’optimisation moyenne-variance est appliquée pour combiner les satellites sélectionnés.
* La pondération finale est le produit : poids satellite × poids intra-satellite.

### 7. Visualisation et export

* Visualisation des performances (performance cumulée, Sharpe, volatilité).
* Représentation donut cœur/satellites.
* Liste d’achat finale (tickers + poids).
* Export CSV disponible.

## Limitations identifiées

* Dépendance forte à Yahoo Finance (fiabilité variable, tickers manquants).
* Le modèle d’optimisation moyenne-variance reste très simpliste :

  * Hypothèse de normalité des rendements
  * Pas de prise en compte du turnover, ni des coûts de transaction.
* Les pondérations très optimisées peuvent manquer de robustesse hors-échantillon.

## Possibilités futures (non implémentées)

* Ajout d’autres méthodes d’optimisation :

  * Min variance
  * Max diversification
  * Hierarchical Risk Parity
* Backtest rolling avec recalibrage mensuel
* Affichage interactif des positions dans un portefeuille virtuel

## Conclusion

Ce projet nous a permis d'explorer plusieurs dimensions d'un portefeuille quantitatif accessible : profilage utilisateur, sélection algorithmique, et optimisation. Malgré certaines limitations techniques, le résultat est une application éducative et visuellement intuitive, offrant un vrai gain pédagogique pour les utilisateurs novices comme avancés.

---

*Fin du notebook Momentum-X*

