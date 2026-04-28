# Modified by: odoo-backend agent — 2026-04-13 — Fix bc_month, timezone, perf, currency
from odoo import fields, http
from odoo.http import request
from datetime import timedelta, datetime
import pytz
from werkzeug.exceptions import Forbidden


class SaleDashboardController(http.Controller):

    @http.route('/sale_dashboard/data', type='json', auth='user')
    def get_dashboard_data(self, **kwargs):
        if not request.env.user.has_group('sale_dashboard.group_sale_dashboard_user'):
            raise Forbidden("Accès non autorisé au dashboard vente")
        SO = request.env['sale.order']

        # Récupérer les paramètres dynamiques (filtres du frontend)
        filters = kwargs.get('filters', {})
        chart_days = filters.get('chart_days', 7)
        recent_days = filters.get('recent_days', 30)
        active_order_limit = filters.get('active_order_limit', 50)
        date_from = filters.get('date_from')
        date_to = filters.get('date_to')

        # Keep original date strings for Date fields (invoice_date)
        date_from_date = date_from
        date_to_date = date_to

        # Convert date_from/date_to to UTC boundaries for Datetime fields (date_order)
        _ftz = pytz.timezone(request.env.user.tz or 'Indian/Antananarivo')
        if date_from and len(date_from) == 10:
            _df_local = _ftz.localize(datetime.strptime(date_from, '%Y-%m-%d'))
            date_from = _df_local.astimezone(pytz.utc).strftime('%Y-%m-%d %H:%M:%S')
        if date_to and len(date_to) == 10:
            _dt_local = _ftz.localize(datetime.strptime(date_to, '%Y-%m-%d').replace(hour=23, minute=59, second=59))
            date_to = _dt_local.astimezone(pytz.utc).strftime('%Y-%m-%d %H:%M:%S')
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
            ('commitment_date', '<', fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ])

        # Total BC (Bons de Commande)
        _tz_sale = pytz.timezone(request.env.user.tz or "Indian/Antananarivo")
        today = fields.Datetime.now()
        today_local = today.replace(tzinfo=pytz.utc).astimezone(_tz_sale)
        month_start = today_local.replace(day=1, hour=0, minute=0, second=0, microsecond=0).astimezone(pytz.utc)
        bc_date_domain = date_domain if date_domain else [('date_order', '>=', month_start.strftime('%Y-%m-%d %H:%M:%S'))]
        bc_domain = base_domain + bc_date_domain + [
            ('state', 'in', ['sale', 'done']),
        ]
        bc_groups = SO.read_group(bc_domain, fields=['amount_total:sum'], groupby=[])
        bc_month = bc_groups[0].get('amount_total', 0) if bc_groups else 0

        # Quantite totale du mois (somme product_uom_qty sur les memes SO que bc_month)
        bc_so_ids = SO.search(bc_domain).ids
        if bc_so_ids:
            qty_month_groups = request.env['sale.order.line'].read_group(
                [('order_id', 'in', bc_so_ids)],
                fields=['product_uom_qty:sum'],
                groupby=[],
            )
            qty_month = qty_month_groups[0].get('product_uom_qty', 0) if qty_month_groups else 0
        else:
            qty_month = 0

        # Facturation Vente ce mois (factures clients hors POS, payé et non payé)
        Invoice = request.env['account.move']
        invoice_domain = [
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('pos_order_ids', '=', False),
        ]
        if date_from_date:
            invoice_domain.append(('invoice_date', '>=', date_from_date))
        else:
            invoice_domain.append(('invoice_date', '>=', month_start.strftime('%Y-%m-%d')))
        if date_to_date:
            invoice_domain.append(('invoice_date', '<=', date_to_date))
        if user_id:
            invoice_domain.append(('invoice_user_id', '=', user_id))
        if partner_id:
            invoice_domain.append(('partner_id', '=', partner_id))
        all_invoices = Invoice.search_read(
            invoice_domain,
            fields=['amount_total', 'payment_state'],
        )
        sale_paid = sum(inv['amount_total'] for inv in all_invoices if inv['payment_state'] in ('paid', 'in_payment'))
        sale_unpaid = sum(inv['amount_total'] for inv in all_invoices if inv['payment_state'] not in ('paid', 'in_payment'))

        # Ventes des N derniers jours (pour stats récapitulatives)
        date_n_ago = fields.Datetime.now() - timedelta(days=recent_days)
        recent_orders = SO.search_read(
            base_domain + [
                ('state', 'in', ['sale', 'done']),
                ('date_order', '>=', date_n_ago.strftime('%Y-%m-%d')),
            ],
            fields=['amount_total'],
        )
        recent_order_count = len(recent_orders)
        recent_ca = sum(o['amount_total'] for o in recent_orders)

        # CA quotidien (factures clients par jour) - graphique
        now = fields.Datetime.now()
        user_tz = pytz.timezone(request.env.user.tz or 'Indian/Antananarivo')
        now_local = now.replace(tzinfo=pytz.utc).astimezone(user_tz)
        chart_start_date = (now_local - timedelta(days=chart_days - 1)).strftime('%Y-%m-%d')
        chart_inv_domain = [
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('pos_order_ids', '=', False),
            ('invoice_date', '>=', chart_start_date),
        ]
        if user_id:
            chart_inv_domain.append(('invoice_user_id', '=', user_id))
        if partner_id:
            chart_inv_domain.append(('partner_id', '=', partner_id))
        chart_groups = Invoice.read_group(
            chart_inv_domain,
            fields=['amount_total:sum', 'invoice_date'],
            groupby=['invoice_date:day'],
        )
        chart_by_date = {}
        for g in chart_groups:
            rng = g.get('__range', {}).get('invoice_date:day', {})
            from_str = rng.get('from', '')
            if from_str:
                day_key = from_str[:10]  # invoice_date is a Date field, no TZ conversion needed
                chart_by_date[day_key] = {'amount': round(g.get('amount_total', 0), 2), 'count': g.get('__count', 0)}
        daily_sales = []
        for i in range(chart_days - 1, -1, -1):
            day = now_local - timedelta(days=i)
            day_key = day.strftime('%Y-%m-%d')
            data = chart_by_date.get(day_key, {})
            daily_sales.append({
                'date': day.strftime('%d/%m'),
                'count': data.get('count', 0),
                'amount': data.get('amount', 0),
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
        top_products = []
        recent_so_ids = SO.search(base_domain + [
            ('state', 'in', ['sale', 'done']),
            ('date_order', '>=', date_n_ago.strftime('%Y-%m-%d')),
        ]).ids
        if recent_so_ids:
            top_products_data = SOL.read_group(
                [('order_id', 'in', recent_so_ids)],
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
                    'count': p.get('__count', p.get('product_id_count', 0)),
                }
                for p in top_products_data if p['product_id']
            ]

        # Factures du jour (par défaut) ou de la période filtrée
        today_date = now_local.strftime('%Y-%m-%d')
        inv_list_domain = [
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('pos_order_ids', '=', False),
        ]
        if date_from_date:
            inv_list_domain.append(('invoice_date', '>=', date_from_date))
        else:
            inv_list_domain.append(('invoice_date', '=', today_date))
        if date_to_date:
            inv_list_domain.append(('invoice_date', '<=', date_to_date))
        if user_id:
            inv_list_domain.append(('invoice_user_id', '=', user_id))
        if partner_id:
            inv_list_domain.append(('partner_id', '=', partner_id))
        daily_invoices = Invoice.search_read(
            inv_list_domain,
            fields=[
                'name', 'partner_id', 'invoice_date', 'amount_untaxed',
                'amount_total', 'payment_state', 'invoice_user_id',
            ],
            order='invoice_date desc, name desc',
        )

        # Config pour le frontend
        config = request.env['sale.dashboard.config'].get_config()

        # Devise de la société
        currency = request.env.company.currency_id
        currency_info = {
            'symbol': currency.symbol or '',
            'position': currency.position or 'after',
        }

        return {
            'currency': currency_info,
            'state_counts': state_counts,
            'to_invoice_count': to_invoice_count,
            'late_count': late_count,
            'bc_month': round(bc_month, 2),
            'qty_month': round(qty_month, 2),
            'invoice_sale': {
                'total': round(sale_paid + sale_unpaid, 2),
                'paid': round(sale_paid, 2),
                'unpaid': round(sale_unpaid, 2),
            },
            'daily_sales': daily_sales,
            'active_orders': active_orders,
            'recent_order_count': recent_order_count,
            'recent_ca': round(recent_ca, 2),
            'top_products': top_products,
            'daily_invoices': daily_invoices,
            'config': config,
        }

    @http.route('/sale_dashboard/filters_data', type='json', auth='user')
    def get_filters_data(self):
        """Retourne les données pour les listes déroulantes des filtres."""
        if not request.env.user.has_group('sale_dashboard.group_sale_dashboard_user'):
            raise Forbidden("Accès non autorisé au dashboard vente")
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
