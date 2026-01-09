# 📑 Momentum-X — Analyse académique

> Projet de recherche appliquée en finance de marché  
> Analyse critique d’une stratégie d’allocation dynamique fondée sur le momentum

---

## ▸ Objectif du projet

Momentum-X est un projet de recherche visant à étudier la pertinence d’une approche d’investissement systématique exploitant la prime de **momentum** et **l'optimisation** de portefeuille dans un cadre d’allocation contrôlé par le risque.

L’objectif est d’évaluer dans quelle mesure une structuration de portefeuille combinant sélection momentum, diversification thématique et contraintes d’optimisation permet d’améliorer le couple rendement/risque par rapport à des allocations plus simples.

Ce travail s’inscrit dans la continuité des travaux fondateurs de **Jegadeesh & Titman (1993)** sur le momentum, étendus aux marchés globaux par **Asness, Moskowitz & Pedersen (2013)**, et dans la littérature plus récente sur les risques structurels du facteur momentum (**Daniel & Moskowitz, 2016**).

---

## ▸ Éclairage de la littérature financière

La recherche académique met en évidence plusieurs caractéristiques fondamentales du facteur momentum :

- robustesse empirique à travers les marchés et les classes d’actifs  
  (Jegadeesh & Titman, 1993 ; Asness et al., 2013) ;
- dépendance marquée aux **régimes de marché** ;
- exposition à des **crashes violents** lors de retournements soudains  
  (Daniel & Moskowitz, 2016) ;
- sensibilité extrême aux **coûts de transaction et au turnover**.

Par ailleurs, **Barroso & Santa-Clara (2015)** montrent qu’un contrôle explicite de la volatilité permet de réduire fortement les drawdowns et d’améliorer la stabilité des stratégies momentum, ce qui ouvre des perspectives d’amélioration importantes pour ce type d’approche.

---

## ▸ Limites et biais potentiels

### 1. Qualité et disponibilité des données

L’utilisation de données issues de Yahoo Finance introduit des risques non négligeables :

- historiques incomplets, en particulier sur les marchés émergents ;
- hétérogénéité des calendriers de cotation ;
- qualité variable des prix ajustés.

Ces problèmes réduisent la taille effective des échantillons et fragilisent l’estimation des paramètres statistiques, ce qui peut altérer la robustesse des résultats empiriques.  

**Dans le cadre de Momentum-X, ces limites se traduisent concrètement par une réduction du nombre d’actifs exploitables dans certains univers thématiques et par une instabilité accrue des signaux de sélection.**

---

### 2. Biais de temporalité (look-ahead bias)

Toute absence de séparation stricte entre la date de calcul du signal et la date d’exécution peut générer un biais de regard vers l’avant, conduisant à une surestimation artificielle des performances observées et à une invalidation des résultats empiriques.

---

### 3. Biais de survie et biais de sélection

Les univers d’actifs disponibles aujourd’hui ne reflètent pas nécessairement l’ensemble des opportunités passées.  
L’exclusion d’actifs disparus ou peu liquides conduit à un biais de survie qui surestime la performance historique.

---

### 4. Coûts de transaction et rotation de portefeuille

Les stratégies momentum impliquent un turnover élevé, particulièrement en période de stress de marché.  
En l’absence d’une modélisation réaliste des frais de transaction, des spreads bid-ask et de l’impact de marché, les performances restent largement optimistes. 

**Dans une implémentation réelle, ce point constitue l’un des principaux déterminants de la viabilité économique de la stratégie.**

---

### 5. Risque de change

Pour un investisseur européen, la performance est affectée par la composante devise (USD, devises émergentes).  
Sans politique de couverture explicite, il devient difficile d’isoler la performance propre de la stratégie.

---

### 6. Fragilité de l’optimisation moyenne-variance

Comme le démontrent **DeMiguel, Garlappi & Uppal (2009)**, l’optimisation moyenne-variance est extrêmement sensible aux erreurs d’estimation et peut conduire à des allocations instables ou économiquement sous-optimales malgré son élégance théorique.  

Dans Momentum-X, cette fragilité se manifeste par une forte sensibilité des poids optimisés aux fenêtres d’estimation, aux contraintes imposées et aux variations du régime de marché, ce qui justifie l’introduction de bornes strictes et de mécanismes de stabilisation des allocations.

---

### 7. Concentration et risque de crowding

Les stratégies momentum sont sujettes à des phénomènes d’encombrement et à des corrélations élevées en période de crise.
**Daniel & Moskowitz (2016)** montrent que les stratégies momentum subissent des pertes extrêmes lors des phases de retournement brutal des marchés, en particulier après des périodes prolongées de baisse, lorsque les actifs précédemment gagnants deviennent soudainement les principaux perdants.

Ce risque de crash est structurel : il est amplifié par la similarité des positions détenues par les investisseurs et par l’usage fréquent du levier, ce qui déclenche des ventes forcées et engendre une dynamique d’amplification systémique des pertes.

---

## ▸ Pistes d’amélioration et travaux futurs

Plusieurs axes de recherche peuvent améliorer la robustesse de ce type de stratégie :

- intégration d’un ciblage de volatilité (Barroso & Santa-Clara, 2015) ;
- ajout de filtres de tendance macroéconomique ;
- recours à des méthodes d’allocation plus robustes  
  (risk parity, shrinkage covariance, minimum variance) ;
- modélisation explicite des coûts de transaction et du slippage ;
- validation hors échantillon et analyses de sensibilité approfondies.

**En pratique, toute mise en production nécessiterait également un cadre de gouvernance du modèle, incluant le suivi continu des performances, le contrôle des dérives de risque et la révision périodique des hypothèses de construction du portefeuille.**

---

## ▸Publications professionnelles et exemples de mise en œuvre

Le monde professionnel de la gestion d’actifs a également largement documenté et adopté l’intégration du facteur momentum dans des architectures de portefeuille de type cœur–satellites, confirmant la cohérence économique de l’approche étudiée dans ce projet.

**Symmetry Partners / Panoramic Funds (2025)**  
Dans une note de stratégie publiée par sa filiale Panoramic Funds, la société de gestion américaine Symmetry Partners présente l’utilisation de son ETF sectoriel momentum *(ticker : SMOM)* comme composante satellite d’un portefeuille diversifié.  
Ils recommandent qu’une allocation cœur–satellite typique consacre environ 10 % à 30 % du portefeuille à une stratégie momentum sectorielle, le reste constituant le cœur diversifié.  
L’objectif explicite est d’ajouter une **surcouche dynamique et disciplinée** autour d’un cœur indiciel large afin de rechercher un excès de rendement sans altérer l’allocation stratégique globale.  
En pratique, cela revient à adosser un sleeve” momentum autour d’un cœur passif (par exemple un indice actions mondial) pour capter la rotation des secteurs les plus porteurs, tout en conservant une structure principale stable.  
Source : panoramicfunds.com

**Invesco / Analyse Morningstar relayée par Kiplinger (2024)**  
Nick Kalivas, responsable de la stratégie factorielle et des portefeuilles noyau chez Invesco, souligne que le momentum doit être considéré comme une stratégie satellite et non comme le cœur d’un portefeuille diversifié.  
Les fonds momentum présentent des profils de performance souvent décorrélés, alternant périodes de forte surperformance et phases de sous-performance marquées, notamment face aux styles value.  
Une allocation modérée au momentum permet ainsi d’améliorer la diversification globale et de bénéficier des tendances favorables, tout en limitant l’exposition aux retournements brutaux.  
Source : kiplinger.com

**Guide Dual Momentum – Approche francophone (2023)**  
Dans la littérature francophone, un guide d’investissement momentum décrit une mise en œuvre fréquente combinant un cœur passif mondial (par exemple un ETF MSCI World) avec un satellite géré en Dual Momentum ou Accelerated Dual Momentum, dans le but « d’améliorer le profil rendement/drawdown » du portefeuille.  
Le guide suggère généralement une taille de satellite momentum comprise entre 10 % et 40 % de l’exposition actions, selon la tolérance de l’investisseur aux rotations et à la discipline nécessaire.  
Cette combinaison vise à associer la stabilité structurelle du cœur indiciel avec la réactivité tactique du satellite momentum, capable d’ajuster rapidement l’allocation ou de passer en liquidités lors de phases de marché défavorables.  
Source : dual-momentum.fr

**Nagelmackers – Philosophie d’investissement (2023)**  
La banque privée belge Nagelmackers intègre explicitement l’approche cœur–satellite** et l’investissement factoriel, incluant le facteur Momentum, comme piliers complémentaires de sa gestion de portefeuille.  
Le cœur-satellite permet d’arbitrer entre stabilité et opportunité, tandis que l’investissement factoriel vise à améliorer le rendement ajusté du risque par la sélection de caractéristiques éprouvées *(momentum, value, qualité, etc.)*.  
Cette articulation illustre la place du momentum dans la gestion professionnelle moderne : il est principalement utilisé comme composante satellite pour renforcer la performance et la diversification, plutôt que comme stratégie isolée autonome.

---

## ▸ Conclusion

Ce projet confirme l’intérêt théorique et empirique du facteur momentum, tout en mettant en lumière les risques structurels et opérationnels associés à son implémentation réelle.

Toute exploitation sérieuse de cette anomalie de marché nécessite une discipline méthodologique rigoureuse, une gestion prudente du risque et une évaluation empirique robuste avant toute application en conditions réelles.  

La validité économique de la stratégie demeure conditionnée à sa capacité à maintenir ses propriétés hors échantillon et sous différents régimes de marché, ce qui constitue un critère de falsification essentiel de son intérêt réel.
