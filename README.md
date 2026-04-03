# Tableau de bord Ventes (Sale Dashboard)

Module Odoo 18 — Dashboard Ventes dynamique avec KPI en temps réel, filtres interactifs et configuration par societe.

**Auteur :** SOPROMER  
**Version :** 18.0.2.0.0  
**Licence :** LGPL-3  
**Dependance :** `sale_management`

---

## Fonctionnalites

### KPI en temps reel (8 indicateurs)

| Indicateur | Description |
|---|---|
| **Devis** | Nombre de commandes en etat brouillon |
| **Envoyes** | Devis envoyes au client, en attente de confirmation |
| **Confirmees** | Commandes de vente confirmees |
| **A facturer** | Commandes confirmees dont la facturation est en attente |
| **Verrouillees** | Commandes verrouillees (terminees) |
| **Annulees** | Commandes annulees |
| **En retard** | Commandes confirmees dont la date d'engagement est depassee |
| **CA ce mois** | Chiffre d'affaires total du mois en cours (commandes confirmees et verrouillees) |

Chaque carte KPI est **cliquable** et ouvre la liste filtree des commandes correspondantes.

### Graphique des ventes

- Graphique en barres du chiffre d'affaires quotidien
- Periode configurable : **7, 14 ou 30 jours**
- Resume en haut a droite : total commandes et CA sur la periode stats

### Top 10 produits vendus

- Classement des 10 produits les plus vendus sur la periode stats
- Colonnes : Rang, Produit, Quantite, Montant, Nombre de lignes
- Periode alignee sur le filtre "Periode stats"

### Tableau des commandes actives

- Liste des commandes non terminees (brouillon, envoye, confirme)
- Colonnes : Reference, Client, Montant, Etat, Statut facturation
- Cliquer sur une ligne ouvre le formulaire de la commande
- Nombre d'enregistrements configurable (par defaut : 50)

---

## Filtres dynamiques

Le panneau de filtres s'ouvre via le bouton **Filtres** dans l'en-tete du dashboard.

| Filtre | Description |
|---|---|
| **Date debut** | Filtrer les commandes a partir de cette date |
| **Date fin** | Filtrer les commandes jusqu'a cette date |
| **Commercial** | Filtrer par vendeur assigne (liste dynamique) |
| **Client** | Filtrer par client (liste dynamique, top 200) |
| **Jours graphique** | Nombre de jours affiches dans le graphique (7/14/30) |
| **Periode stats** | Periode pour les statistiques recentes (7/30/60/90 jours) |

- Un **point bleu** apparait sur le bouton Filtres quand des filtres sont actifs
- Bouton **Appliquer** pour lancer la recherche
- Bouton **Reinitialiser** pour revenir aux valeurs par defaut

---

## Rafraichissement automatique

Le selecteur dans l'en-tete permet de configurer le rafraichissement automatique :

- **Off** -- rafraichissement manuel uniquement
- **30 secondes**
- **1 minute**
- **2 minutes**
- **5 minutes**

L'heure de la derniere mise a jour est affichee a cote des controles.

---

## Installation

### Prerequis

- Odoo 18 Community ou Enterprise
- Module `sale_management` (Gestion des ventes) installe et configure

### Etapes

1. Copier le dossier `sale_dashboard` dans le repertoire des addons personnalises :

   ```
   cp -r sale_dashboard /chemin/vers/odoo18/custom-addons/
   ```

2. Mettre a jour la liste des modules dans Odoo :

   **Applications > Mettre a jour la liste des applications**

3. Rechercher et installer le module :

   **Applications > Rechercher "Tableau de bord Ventes" > Installer**

4. Ou via la ligne de commande :

   ```bash
   python odoo-bin -d ma_base -u sale_dashboard --stop-after-init
   ```

### Mise a jour

Pour mettre a jour apres modification :

```bash
python odoo-bin -d ma_base -u sale_dashboard --stop-after-init
```

---

## Configuration

### Acceder a la configuration

**Ventes > Configuration > Config. Dashboard**

> Seuls les **Responsables Dashboard Vente** (groupe `sale_dashboard.group_sale_dashboard_manager`) peuvent modifier la configuration.

### Parametres disponibles

| Parametre | Par defaut | Description |
|---|---|---|
| Jours graphique ventes | 7 | Nombre de jours dans le graphique en barres |
| Jours statistiques recentes | 30 | Periode pour le calcul des totaux et du top produits |
| Limite commandes actives | 50 | Nombre max de commandes affichees dans le tableau |
| Rafraichissement auto | Desactive | Intervalle de mise a jour automatique |
| Societe | Societe courante | Configuration par societe (multi-societe) |

### Multi-societe

Chaque societe peut avoir sa propre configuration. Le dashboard charge automatiquement la configuration de la societe active de l'utilisateur.

---

## Droits d'acces

Le module definit ses propres groupes de securite dans la categorie **Dashboard Vente** :

| Groupe | Voir le dashboard | Voir la config | Modifier la config |
|---|---|---|---|
| Utilisateur Dashboard Vente | Oui | Oui (lecture) | Non |
| Responsable Dashboard Vente | Oui | Oui | Oui |

Le groupe **Responsable Dashboard Vente** herite automatiquement du groupe **Utilisateur Dashboard Vente**.

Les **Responsables des ventes** (`sales_team.group_sale_manager`) obtiennent automatiquement le role **Responsable Dashboard Vente**.

> Pour qu'un utilisateur accede au dashboard, il doit avoir au minimum le groupe **Utilisateur Dashboard Vente** assigne dans ses parametres utilisateur, sous la categorie "Dashboard Vente".

---

## Architecture technique

```
sale_dashboard/
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   └── main.py                    # Endpoints RPC
├── models/
│   ├── __init__.py
│   └── sale_dashboard_config.py   # Modele de configuration
├── security/
│   ├── sale_dashboard_groups.xml  # Groupes de securite
│   └── ir.model.access.csv       # Droits d'acces
├── static/src/
│   ├── css/sale_dashboard.css     # Styles
│   ├── js/sale_dashboard.js       # Composant OWL
│   └── xml/sale_dashboard.xml     # Template OWL
├── views/
│   ├── sale_dashboard_views.xml        # Menu + Action client
│   └── sale_dashboard_config_views.xml # Vues configuration
├── doc/
│   └── guide_utilisation.md       # Guide detaille
└── README.md
```

### Endpoints API

| Route | Type | Description |
|---|---|---|
| `/sale_dashboard/data` | JSON (POST) | Donnees du dashboard avec filtres |
| `/sale_dashboard/filters_data` | JSON (POST) | Listes pour les selecteurs de filtres (commerciaux, clients) |

### Parametres de `/sale_dashboard/data`

```json
{
  "filters": {
    "chart_days": 7,
    "recent_days": 30,
    "active_order_limit": 50,
    "date_from": "2026-01-01",
    "date_to": "2026-03-31",
    "user_id": 2,
    "partner_id": 15
  }
}
```

### Reponse de `/sale_dashboard/data`

```json
{
  "state_counts": { "draft": 12, "sent": 5, "sale": 30, "done": 8, "cancel": 2 },
  "to_invoice_count": 7,
  "late_count": 3,
  "ca_month": 125000.50,
  "daily_sales": [
    { "date": "28/03", "count": 4, "amount": 15200.00 }
  ],
  "active_orders": [ ... ],
  "recent_order_count": 45,
  "recent_ca": 350000.00,
  "top_products": [
    { "product_id": 1, "product_name": "Produit A", "qty": 120, "amount": 50000.00, "count": 25 }
  ],
  "config": { "chart_days": 7, "recent_days": 30, "active_order_limit": 50, "auto_refresh_interval": 0 }
}
```

### Reponse de `/sale_dashboard/filters_data`

```json
{
  "salespersons": [
    { "id": 2, "name": "Ahmed Commercial" }
  ],
  "partners": [
    { "id": 15, "name": "Client SARL" }
  ]
}
```

### Technologies

- **Frontend :** OWL 2 (framework reactif Odoo), Bootstrap 5
- **Backend :** Odoo 18 HTTP Controllers, ORM
- **Modeles interroges :** `sale.order`, `sale.order.line`, `sale.dashboard.config`

---

## Depannage

| Probleme | Solution |
|---|---|
| Le dashboard ne s'affiche pas | Verifier que le module `sale_management` est installe. Vider le cache navigateur (Ctrl+Maj+Suppr). |
| Erreur "Acces non autorise au dashboard vente" | Verifier que l'utilisateur a le groupe "Utilisateur Dashboard Vente" au minimum dans ses parametres. |
| Les filtres commercial/client sont vides | Normal si aucune commande de vente n'existe encore dans le systeme. |
| L'auto-refresh ne fonctionne pas | Verifier que la valeur est differente de "Off" dans le selecteur de l'en-tete. |
| Les donnees ne correspondent pas | Cliquer sur "Actualiser" pour forcer un rechargement. Verifier les filtres actifs (point bleu). |
| Le menu "Config. Dashboard" n'apparait pas | Seuls les Responsables Dashboard Vente y ont acces. Verifier les groupes de l'utilisateur. |
| Le CA ce mois affiche 0 | Verifier qu'il existe des commandes confirmees ou verrouillees avec une date de commande dans le mois en cours. |

---

## Licence

Ce module est distribue sous licence [LGPL-3](https://www.gnu.org/licenses/lgpl-3.0.html).
