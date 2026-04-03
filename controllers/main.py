from odoo import http
from odoo.http import request
from datetime import datetime, timedelta


class SaleDashboardController(http.Controller):

    @http.route('/sale_dashboard/data', type='json', auth='user')
    def get_dashboard_data(self, **kwargs):
        SO = request.env['sale.order']

        # Récupérer les paramètres dynamiques (filtres du frontend)
        filters = kwargs.get('filters', {})
        chart_days = filters.get('chart_days', 7)
        recent_days = filters.get('recent_days', 30)
        active_order_limit = filters.get('active_order_limit', 50)
        date_from = filters.get('date_from')
        date_to = filters.get('date_to')
        user_id = filters.get('user_id')
        partner_id = filters.get('partner_id')

        # Construire le domaine de base à partir des filtres
        base_domain = []
        if user_id:
            base_domain.append(('user_id', '=', user_id))
        if partner_id:
            base_domain.append(('partner_id', '=', partner_id))

        # Domaine temporel pour les filtres date
        date_domain = []
        if date_from:
            date_domain.append(('date_order', '>=', date_from))
        if date_to:
            date_domain.append(('date_order', '<=', date_to))

        # Compteurs par état
        states = ['draft', 'sent', 'sale', 'done', 'cancel']
        state_counts = {}
        for state in states:
            domain = base_domain + date_domain + [('state', '=', state)]
            state_counts[state] = SO.search_count(domain)

        # A facturer
        to_invoice_count = SO.search_count(
            base_domain + date_domain + [
                ('state', '=', 'sale'),
                ('invoice_status', '=', 'to invoice'),
            ]
        )

        # Commandes en retard (confirmées mais date d'engagement dépassée)
        late_count = SO.search_count(base_domain + [
            ('state', '=', 'sale'),
            ('commitment_date', '!=', False),
            ('commitment_date', '<', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ])

        # CA ce mois
        today = datetime.now()
        month_start = today.replace(day=1, hour=0, minute=0, second=0)
        month_orders = SO.search_read(
            base_domain + [
                ('state', 'in', ['sale', 'done']),
                ('date_order', '>=', month_start.strftime('%Y-%m-%d %H:%M:%S')),
            ],
            fields=['amount_total'],
        )
        ca_month = sum(o['amount_total'] for o in month_orders)

        # Ventes des N derniers jours (pour stats récapitulatives)
        date_n_ago = datetime.now() - timedelta(days=recent_days)
        recent_orders = SO.search_read(
            base_domain + [
                ('state', 'in', ['sale', 'done']),
                ('date_order', '>=', date_n_ago.strftime('%Y-%m-%d')),
            ],
            fields=['amount_total'],
        )
        recent_order_count = len(recent_orders)
        recent_ca = sum(o['amount_total'] for o in recent_orders)

        # Ventes par jour (N derniers jours) - graphique
        daily_sales = []
        for i in range(chart_days - 1, -1, -1):
            day = datetime.now() - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0).strftime('%Y-%m-%d %H:%M:%S')
            day_end = day.replace(hour=23, minute=59, second=59).strftime('%Y-%m-%d %H:%M:%S')
            domain = base_domain + [
                ('state', 'in', ['sale', 'done']),
                ('date_order', '>=', day_start),
                ('date_order', '<=', day_end),
            ]
            orders = SO.search_read(domain, fields=['amount_total'])
            amount = sum(o['amount_total'] for o in orders)
            daily_sales.append({
                'date': day.strftime('%d/%m'),
                'count': len(orders),
                'amount': round(amount, 2),
            })

        # Commandes actives (brouillon, envoyé, confirmé)
        active_domain = base_domain + [
            ('state', 'in', ['draft', 'sent', 'sale']),
        ]
        if date_from:
            active_domain.append(('date_order', '>=', date_from))
        if date_to:
            active_domain.append(('date_order', '<=', date_to))

        active_orders = SO.search_read(
            active_domain,
            fields=[
                'name', 'partner_id', 'amount_total',
                'state', 'invoice_status', 'date_order',
                'user_id', 'commitment_date',
            ],
            order='date_order desc',
            limit=active_order_limit,
        )

        # Top 10 produits vendus (période récente)
        SOL = request.env['sale.order.line']
        top_products_data = SOL.read_group(
            [
                ('order_id.state', 'in', ['sale', 'done']),
                ('order_id.date_order', '>=', date_n_ago.strftime('%Y-%m-%d')),
            ] + (
                [('order_id.user_id', '=', user_id)] if user_id else []
            ) + (
                [('order_id.partner_id', '=', partner_id)] if partner_id else []
            ),
            fields=['product_id', 'product_uom_qty', 'price_subtotal'],
            groupby=['product_id'],
            orderby='price_subtotal desc',
            limit=10,
        )
        top_products = [
            {
                'product_id': p['product_id'][0],
                'product_name': p['product_id'][1],
                'qty': p['product_uom_qty'],
                'amount': round(p['price_subtotal'], 2),
                'count': p['__count'],
            }
            for p in top_products_data if p['product_id']
        ]

        # Config pour le frontend
        config = request.env['sale.dashboard.config'].get_config()

        return {
            'state_counts': state_counts,
            'to_invoice_count': to_invoice_count,
            'late_count': late_count,
            'ca_month': round(ca_month, 2),
            'daily_sales': daily_sales,
            'active_orders': active_orders,
            'recent_order_count': recent_order_count,
            'recent_ca': round(recent_ca, 2),
            'top_products': top_products,
            'config': config,
        }

    @http.route('/sale_dashboard/filters_data', type='json', auth='user')
    def get_filters_data(self):
        """Retourne les données pour les listes déroulantes des filtres."""
        # Commerciaux ayant des commandes
        users = request.env['sale.order'].read_group(
            [('user_id', '!=', False)],
            fields=['user_id'],
            groupby=['user_id'],
        )
        salesperson_list = [
            {'id': u['user_id'][0], 'name': u['user_id'][1]}
            for u in users if u['user_id']
        ]

        # Clients avec des commandes (top 200)
        partners = request.env['sale.order'].read_group(
            [('partner_id', '!=', False)],
            fields=['partner_id'],
            groupby=['partner_id'],
            limit=200,
        )
        partner_list = [
            {'id': p['partner_id'][0], 'name': p['partner_id'][1]}
            for p in partners if p['partner_id']
        ]

        return {
            'salespersons': salesperson_list,
            'partners': partner_list,
        }
