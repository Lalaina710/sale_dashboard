{
    'name': 'Tableau de bord Ventes',
    'version': '18.0.2.0.0',
    'category': 'Sales',
    'summary': 'Dashboard Ventes dynamique avec KPI, filtres et configuration',
    'description': 'Tableau de bord interactif pour le suivi des ventes avec filtres dynamiques, rafraîchissement auto et configuration.',
    'author': 'MadaWebZone MWZ',
    'depends': ['sale_management'],
    'data': [
        'security/sale_dashboard_groups.xml',
        'security/ir.model.access.csv',
        'views/sale_dashboard_config_views.xml',
        'views/sale_dashboard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sale_dashboard/static/src/css/sale_dashboard.css',
            'sale_dashboard/static/src/xml/sale_dashboard.xml',
            'sale_dashboard/static/src/js/sale_dashboard.js',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
}
