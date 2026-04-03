/** @odoo-module **/

import { Component, useState, onWillStart, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";

class SaleDashboard extends Component {
    static template = "sale_dashboard.SaleDashboard";
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            loading: true,
            data: {
                state_counts: {},
                to_invoice_count: 0,
                late_count: 0,
                ca_month: 0,
                daily_sales: [],
                active_orders: [],
                recent_order_count: 0,
                recent_ca: 0,
                top_products: [],
            },
            // Filtres dynamiques
            filters: {
                chart_days: 7,
                recent_days: 30,
                active_order_limit: 50,
                date_from: '',
                date_to: '',
                user_id: 0,
                partner_id: 0,
            },
            // Données des listes déroulantes
            salespersons: [],
            partners: [],
            // Panneau filtres visible/masqué
            showFilters: false,
            // Auto-refresh
            autoRefreshInterval: 0,
            // Dernière mise à jour
            lastUpdate: '',
        });
        this._refreshTimer = null;

        onWillStart(async () => {
            await this.loadFiltersData();
            await this.loadConfig();
            await this.loadData();
        });

        onMounted(() => {
            this._startAutoRefresh();
        });

        onWillUnmount(() => {
            this._stopAutoRefresh();
        });
    }

    async loadConfig() {
        try {
            const config = await this.orm.call(
                'sale.dashboard.config', 'get_config', []
            );
            this.state.filters.chart_days = config.chart_days;
            this.state.filters.recent_days = config.recent_days;
            this.state.filters.active_order_limit = config.active_order_limit;
            this.state.autoRefreshInterval = config.auto_refresh_interval;
        } catch (e) {
            console.warn("Config non disponible, valeurs par défaut utilisées");
        }
    }

    async loadFiltersData() {
        try {
            const data = await rpc("/sale_dashboard/filters_data", {});
            this.state.salespersons = data.salespersons || [];
            this.state.partners = data.partners || [];
        } catch (e) {
            console.error("Sale Dashboard - Erreur chargement filtres:", e);
        }
    }

    async loadData() {
        this.state.loading = true;
        try {
            const filters = { ...this.state.filters };
            // Nettoyer les filtres vides
            if (!filters.user_id) delete filters.user_id;
            if (!filters.partner_id) delete filters.partner_id;
            if (!filters.date_from) delete filters.date_from;
            if (!filters.date_to) delete filters.date_to;

            this.state.data = await rpc("/sale_dashboard/data", { filters });
            this.state.lastUpdate = new Date().toLocaleTimeString("fr-FR");
        } catch (e) {
            console.error("Sale Dashboard error:", e);
            this.state.data = {
                state_counts: {},
                to_invoice_count: 0,
                late_count: 0,
                ca_month: 0,
                daily_sales: [],
                active_orders: [],
                recent_order_count: 0,
                recent_ca: 0,
                top_products: [],
            };
        }
        this.state.loading = false;
    }

    // --- Gestion des filtres ---

    toggleFilters() {
        this.state.showFilters = !this.state.showFilters;
    }

    onFilterChange(field, ev) {
        const value = ev.target.value;
        if (['chart_days', 'recent_days', 'active_order_limit',
             'user_id', 'partner_id'].includes(field)) {
            this.state.filters[field] = parseInt(value) || 0;
        } else {
            this.state.filters[field] = value;
        }
    }

    applyFilters() {
        this.loadData();
    }

    resetFilters() {
        this.state.filters = {
            chart_days: 7,
            recent_days: 30,
            active_order_limit: 50,
            date_from: '',
            date_to: '',
            user_id: 0,
            partner_id: 0,
        };
        this.loadData();
    }

    // --- Auto-refresh ---

    onRefreshIntervalChange(ev) {
        this.state.autoRefreshInterval = parseInt(ev.target.value) || 0;
        this._startAutoRefresh();
    }

    _startAutoRefresh() {
        this._stopAutoRefresh();
        const interval = this.state.autoRefreshInterval;
        if (interval > 0) {
            this._refreshTimer = setInterval(() => this.loadData(), interval * 1000);
        }
    }

    _stopAutoRefresh() {
        if (this._refreshTimer) {
            clearInterval(this._refreshTimer);
            this._refreshTimer = null;
        }
    }

    // --- Formatage et helpers ---

    formatAmount(amount) {
        if (!amount && amount !== 0) return "0,00";
        return Number(amount).toLocaleString("fr-FR", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        });
    }

    formatQty(qty) {
        if (!qty) return "0";
        return Math.round(qty).toLocaleString("fr-FR");
    }

    getBarHeight(amount) {
        const maxAmount = Math.max(
            ...this.state.data.daily_sales.map((d) => d.amount),
            1
        );
        return Math.max((amount / maxAmount) * 150, 4);
    }

    getStateLabel(state) {
        const labels = {
            draft: "Devis",
            sent: "Envoyé",
            sale: "Confirmée",
            done: "Verrouillée",
            cancel: "Annulée",
        };
        return labels[state] || state;
    }

    getInvoiceStatusLabel(status) {
        const labels = {
            upselling: "Opportunité",
            invoiced: "Facturée",
            "to invoice": "A facturer",
            no: "Rien à facturer",
        };
        return labels[status] || status || "N/A";
    }

    getInvoiceStatusClass(status) {
        if (status === "to invoice") return "to_invoice";
        if (status === "invoiced") return "invoiced";
        if (status === "upselling") return "upselling";
        return "no_invoice";
    }

    hasActiveFilters() {
        const f = this.state.filters;
        return f.date_from || f.date_to || f.user_id || f.partner_id
            || f.chart_days !== 7 || f.recent_days !== 30;
    }

    openOrders(state) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: `Commandes - ${this.getStateLabel(state)}`,
            res_model: "sale.order",
            views: [
                [false, "list"],
                [false, "form"],
            ],
            domain: [["state", "=", state]],
            target: "current",
        });
    }

    openToInvoice() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Commandes à facturer",
            res_model: "sale.order",
            views: [
                [false, "list"],
                [false, "form"],
            ],
            domain: [
                ["state", "=", "sale"],
                ["invoice_status", "=", "to invoice"],
            ],
            target: "current",
        });
    }

    openLateOrders() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Commandes en retard",
            res_model: "sale.order",
            views: [
                [false, "list"],
                [false, "form"],
            ],
            domain: [
                ["state", "=", "sale"],
                ["commitment_date", "<", new Date().toISOString()],
            ],
            target: "current",
        });
    }

    openOrder(orderId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "sale.order",
            res_id: orderId,
            views: [[false, "form"]],
            target: "current",
        });
    }
}

registry.category("actions").add("sale_dashboard.SaleDashboard", SaleDashboard);
