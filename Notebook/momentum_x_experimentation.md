# 📓 Notebook - Momentum-X

Ce document retrace les étapes clés, les essais, erreurs et décisions prises lors du développement de l'application Momentum-X.

---

## ✅ Objectif du projet

Concevoir une application Streamlit permettant de créer un portefeuille dynamique ETF (cœur) + actions thématiques (satellites) en fonction :

* Du **profil de risque** utilisateur (via questionnaire KYC)
* D'une **sélection momentum Top K**
* D'une **optimisation moyenne-variance**

---

## ⚖️ Structure initiale envisagée

### Modules principaux prévus :

1. **KYC / Questionnaire** → profil de risque
2. **Sélection ETF cœur** → 1 ETF via Yahoo Finance
3. **Choix satellites thématiques** (Tech, Banques, etc.)
4. **Filtrage momentum Top K**
5. **Optimisation intra- et inter-satellite**
6. **Visualisation + export liste achat**

---

## ❌ Problèmes rencontrés et ajustements

### 1. **Récupération des prix (Yahoo Finance)**

* **Problème :** De nombreux tickers renvoient des NaN / données vides
* **Solutions essayées :**

  * Multiples suffixes (.SW, .MI, .L, .NS...) pour ETF internationaux
  * Nettoyage des colonnes vides à chaque fetch
* **Décision :** filtrer systématiquement les colonnes vides, fallback sur autre ticker si le principal échoue

### 2. **Manque de profondeur sur certains satellites**

* **Ex :** certains satellites comme “Defense” ou “Energy” ont peu de titres exploitables (données manquantes ou incohérentes)
* **Décision :** Ne garder que les satellites avec au moins 2 titres exploitables (Top K minimum = 2)

### 3. **Optimisation moyenne-variance trop sensible**

* **Problème :** Risque de surajustement si la covariance est mal estimée (matrice singulière)
* **Tentatives :**

  * Ajout d'une élévation diagonale (ridge-like)
  * Nettoyage via `np.nan_to_num`
  * Simplification avec matrice identité si trop peu de data

### 4. **Cumul des poids incorrect**

* **Problème :** Somme finale des poids différait de 1 (problèmes d'arrondis ou poids négatifs)
* **Fix :** Utilisation d'une fonction `clamp_weights` pour assurer la somme à 1 et forcer positivité

### 5. **Visualisation incomplète**

* **Souci initial :** noms de tickers peu explicites
* **Solution :** ajout d'une fonction `get_names()` pour récupérer les noms longs via API Yahoo
* **Limite :** trop lent si appel massif, on l’a limité à la vue finale

---

## 📊 Choix finaux retenus

* KYC → calcule un score [5–25] → associe à un profil : Prudent / Équilibré / Dynamique
* Ce profil ajuste :

  * Aversion au risque pour optimisation
  * Répartition Cœur / Satellites
* Satellite : Top K par momentum → optim intragroupe → optim intergroupe
* Cumul final → poids à 2 décimales, exportable en CSV

---

## 🔄 Idées non retenues ou postposées

* Backtesting Rolling (non nécessaire ici)
* Optimisation à plusieurs objectifs (Sharpe, Max Diversification...)
* Intégration dynamique du min weight (complexité)

---

## 📔 Lessons Learned

* Yahoo Finance a beaucoup de limites : vérifier chaque ticker
* Moins de thématiques mais plus robustes = meilleur résultat
* Une bonne visualisation aide à valider les résultats
* Le KYC amène une vraie personnalisation utile

---

## 🔍 Pistes futures

* Backtest rolling + rebalance mensuel
* Amélioration UX : sauvegarde préférences, plus de thèmes visuels
* Version API ou télégram bot ?
* Ajout de règles ESG ou contraintes thématiques

---

*Fin du notebook Momentum-X*

