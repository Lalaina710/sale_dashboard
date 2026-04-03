# Guide d'utilisation -- Tableau de bord Ventes

## Table des matieres

1. [Acceder au dashboard](#1-accéder-au-dashboard)
2. [Comprendre les KPI](#2-comprendre-les-kpi)
3. [Utiliser les filtres](#3-utiliser-les-filtres)
4. [Configurer le rafraichissement automatique](#4-configurer-le-rafraîchissement-automatique)
5. [Naviguer vers les commandes](#5-naviguer-vers-les-commandes)
6. [Lire le graphique des ventes](#6-lire-le-graphique-des-ventes)
7. [Consulter le top 10 produits](#7-consulter-le-top-10-produits)
8. [Configurer les parametres par defaut](#8-configurer-les-paramètres-par-défaut)
9. [Droits d'acces et groupes](#9-droits-daccès-et-groupes)
10. [Cas d'usage courants](#10-cas-dusage-courants)

---

## 1. Acceder au dashboard

1. Ouvrir le menu principal **Ventes**
2. Cliquer sur **Tableau de bord** (premier element du menu)

Le dashboard se charge et affiche les donnees en temps reel.

> **Note :** L'acces au dashboard necessite le groupe "Utilisateur Dashboard Vente" au minimum. Si le menu n'apparait pas, contactez votre administrateur.

---

## 2. Comprendre les KPI

Les 8 cartes en haut du dashboard affichent les indicateurs principaux :

### Cartes d'etat des commandes

- **Devis** (gris) -- Commandes en etat brouillon, pas encore envoyees au client
- **Envoyes** (bleu) -- Devis envoyes au client, en attente de confirmation
- **Confirmees** (vert) -- Commandes de vente confirmees par le client
- **Verrouillees** (sombre) -- Commandes terminees et verrouillees, aucune modification possible

### Cartes d'alerte et suivi

- **A facturer** (orange) -- Commandes confirmees dont le statut de facturation est "A facturer". Ce sont les commandes pour lesquelles une facture doit etre creee.
- **Annulees** (rouge) -- Commandes annulees
- **En retard** (rouge vif) -- Commandes confirmees dont la **date d'engagement** est depassee. Ce sont les urgences a traiter en priorite.
- **CA ce mois** (turquoise) -- Chiffre d'affaires total du mois en cours, calcule sur les commandes confirmees et verrouillees. Le montant est affiche en format monetaire.

### Interaction

Cliquer sur n'importe quelle carte ouvre la **liste filtree** des commandes correspondantes dans une vue standard Odoo, ou vous pouvez trier, exporter, ou ouvrir chaque commande.

> **Exception :** La carte "CA ce mois" est informative et n'est pas cliquable.

---

## 3. Utiliser les filtres

### Ouvrir le panneau

Cliquer sur le bouton **Filtres** dans l'en-tete du dashboard. Un panneau apparait avec les options suivantes :

### Filtres disponibles

#### Date debut / Date fin
- Permet de restreindre les donnees a une **periode precise**
- Filtre sur la date de commande (`date_order`)
- Exemple : voir uniquement les commandes de mars 2026

#### Commercial
- Liste deroulante contenant tous les vendeurs ayant des commandes assignees
- Permet de voir le dashboard **du point de vue d'un commercial**
- "-- Tous --" affiche les donnees de tous les commerciaux

#### Client
- Liste deroulante des clients ayant des commandes (jusqu'a 200 clients)
- Permet de suivre les ventes pour un **client specifique**
- "-- Tous --" affiche tous les clients

#### Jours graphique
- **7 jours** -- vue courte, ideale pour le suivi quotidien
- **14 jours** -- vue bi-hebdomadaire
- **30 jours** -- vue mensuelle

#### Periode stats
- Determine la periode pour le calcul affiche en haut du graphique ("30j: X cmd / Y DH")
- Determine aussi la periode du classement Top 10 produits
- **7 jours** -- cette semaine
- **30 jours** -- ce mois (par defaut)
- **60 jours** -- 2 mois
- **90 jours** -- trimestre

### Appliquer les filtres

1. Configurer les filtres souhaites
2. Cliquer sur **Appliquer**
3. Le dashboard se recharge avec les donnees filtrees
4. Un **point bleu** apparait sur le bouton Filtres pour indiquer que des filtres sont actifs

### Reinitialiser

Cliquer sur **Reinitialiser** pour revenir aux valeurs par defaut et recharger toutes les donnees.

---

## 4. Configurer le rafraichissement automatique

### Depuis le dashboard

Le selecteur **Auto** dans l'en-tete permet de choisir l'intervalle :

| Option | Usage recommande |
|---|---|
| **Off** | Travail ponctuel, consultation rapide |
| **30 secondes** | Suivi en temps reel sur ecran de vente |
| **1 minute** | Supervision active |
| **2 minutes** | Suivi regulier |
| **5 minutes** | Affichage permanent sur ecran mural |

### Depuis la configuration

Le responsable peut definir l'intervalle par defaut dans la configuration (voir section 8).

### Rafraichissement manuel

Le bouton **Actualiser** (icone de rafraichissement) force un rechargement immediat a tout moment.

L'heure de la derniere mise a jour est affichee a gauche des controles.

---

## 5. Naviguer vers les commandes

### Depuis les cartes KPI

Cliquer sur une carte ouvre la **vue liste** des commandes filtrees par cet etat :

| Carte | Filtre applique |
|---|---|
| Devis | `state = draft` |
| Envoyes | `state = sent` |
| Confirmees | `state = sale` |
| A facturer | `state = sale` et `invoice_status = to invoice` |
| Verrouillees | `state = done` |
| Annulees | `state = cancel` |
| En retard | `state = sale` et `commitment_date < maintenant` |

### Depuis le tableau des commandes actives

Cliquer sur une **ligne du tableau** ouvre le **formulaire** de la commande directement. Vous pouvez alors modifier la commande, creer une facture, ou effectuer toute action standard.

---

## 6. Lire le graphique des ventes

### Les barres

- Chaque barre represente un jour
- La hauteur indique le **chiffre d'affaires total** de ce jour (commandes confirmees et verrouillees)
- La valeur exacte est affichee au-dessus de chaque barre (format monetaire)
- La date est affichee en dessous (format jj/mm)

### Le resume

En haut a droite du graphique :
- **X cmd** -- nombre total de commandes sur la periode stats
- **Y DH** -- chiffre d'affaires total sur la periode stats

### Interpreter

- Des barres regulieres indiquent des ventes stables
- Des barres a zero signalent des jours sans vente (weekend, jour ferie, etc.)
- Une tendance a la hausse indique une croissance commerciale
- Une tendance a la baisse peut signaler un ralentissement a investiguer

---

## 7. Consulter le top 10 produits

La section **Top 10 produits vendus** affiche le classement des articles les plus vendus sur la periode stats.

### Colonnes du tableau

| Colonne | Description |
|---|---|
| **#** | Rang du produit (1 a 10) |
| **Produit** | Nom du produit |
| **Qte** | Quantite totale vendue |
| **Montant** | Chiffre d'affaires genere (sous-total des lignes) |
| **Lignes** | Nombre de lignes de commande concernees |

### Parametres influents

- La periode est definie par le filtre **Periode stats** (7/30/60/90 jours)
- Les filtres **Commercial** et **Client** s'appliquent aussi au classement
- Le classement est ordonne par montant decroissant

### Cas ou le tableau est vide

Le message "Aucune vente sur la periode" apparait si aucune commande confirmee ou verrouilllee n'existe dans la periode selectionnee.

---

## 8. Configurer les parametres par defaut

> Reserve aux **Responsables Dashboard Vente**

### Acceder a la configuration

**Ventes > Configuration > Config. Dashboard**

### Creer une configuration

1. Cliquer sur **Nouveau**
2. Remplir les parametres :
   - **Jours graphique ventes** -- nombre de jours par defaut dans le graphique (defaut : 7)
   - **Jours statistiques recentes** -- periode de calcul des totaux et du top produits (defaut : 30)
   - **Limite commandes actives** -- combien de commandes afficher dans le tableau (defaut : 50)
   - **Rafraichissement auto** -- intervalle par defaut (Desactive, 30s, 1min, 2min, 5min)
   - **Societe** -- la societe concernee (visible uniquement en multi-societe)
3. Cliquer sur **Enregistrer**

### Multi-societe

Si vous gerez plusieurs societes, creez une configuration distincte pour chacune. Le dashboard chargera automatiquement la configuration correspondant a la societe active de l'utilisateur.

### Pas de configuration ?

Si aucune configuration n'existe pour la societe, le dashboard utilise les valeurs par defaut :
- 7 jours pour le graphique
- 30 jours pour les stats et le top produits
- 50 commandes actives max
- Pas d'auto-refresh

---

## 9. Droits d'acces et groupes

Le module definit sa propre categorie de securite **Dashboard Vente** avec deux groupes :

### Utilisateur Dashboard Vente

- **Acces au dashboard** : Oui
- **Lecture de la configuration** : Oui
- **Modification de la configuration** : Non

Ce groupe doit etre assigne manuellement a chaque utilisateur devant acceder au dashboard.

### Responsable Dashboard Vente

- **Acces au dashboard** : Oui
- **Lecture de la configuration** : Oui
- **Modification de la configuration** : Oui (creation, modification, suppression)

Ce groupe herite automatiquement du groupe Utilisateur.

### Attribution automatique

Les utilisateurs ayant le groupe **Responsable des ventes** (`sales_team.group_sale_manager`) recoivent automatiquement le role **Responsable Dashboard Vente**. Aucune action manuelle n'est necessaire pour eux.

### Assigner les groupes manuellement

1. Aller dans **Parametres > Utilisateurs > Utilisateurs**
2. Ouvrir la fiche de l'utilisateur
3. Dans l'onglet **Droits d'acces**, section **Dashboard Vente**
4. Selectionner le niveau : Utilisateur ou Responsable
5. Enregistrer

---

## 10. Cas d'usage courants

### Reunion commerciale

1. Ouvrir le dashboard
2. Verifier les cartes **En retard** et **A facturer** en priorite
3. Consulter le graphique pour voir l'evolution des ventes de la semaine
4. Parcourir le tableau des commandes actives pour identifier les devis en attente
5. Consulter le Top 10 produits pour identifier les articles les plus demandes

### Suivi commercial

1. Ouvrir le dashboard sur un ecran dedie
2. Configurer l'auto-refresh a **30 secondes** ou **1 minute**
3. Le dashboard se met a jour en continu sans intervention
4. Les commerciaux voient en temps reel les nouvelles commandes et les alertes

### Analyse par client

1. Ouvrir les filtres
2. Selectionner le client dans la liste deroulante
3. Etendre la periode stats a **90 jours**
4. Cliquer sur **Appliquer**
5. Le dashboard affiche uniquement les donnees de ce client : CA, commandes actives, produits achetes

### Suivi d'un commercial

1. Ouvrir les filtres
2. Selectionner le commercial
3. Appliquer
4. Voir les KPI et commandes assignes a ce vendeur
5. Comparer avec d'autres commerciaux en changeant le filtre

### Analyse mensuelle

1. Ouvrir les filtres
2. Definir **Date debut** = 01/03/2026, **Date fin** = 31/03/2026
3. Mettre **Jours graphique** a 30
4. Mettre **Periode stats** a 30 jours
5. Appliquer
6. Le dashboard affiche la vue complete du mois de mars : CA quotidien, top produits, commandes actives

### Preparation de facturation

1. Ouvrir le dashboard
2. Verifier la carte **A facturer** pour connaitre le nombre de commandes en attente
3. Cliquer sur la carte pour ouvrir la liste des commandes a facturer
4. Traiter les factures directement depuis la vue liste

---

## Raccourcis clavier

Le dashboard utilise les interactions souris standard d'Odoo :
- **Clic** sur une carte KPI -- liste filtree des commandes
- **Clic** sur une ligne du tableau -- formulaire de la commande
- **F5** ou bouton Actualiser -- rafraichir les donnees
