from odoo import models, api, fields
from datetime import timedelta


class SaleDashboard(models.Model):
    _name = 'sale.dashboard'
    _description = 'Sales Dashboard'

    @api.model
    def get_sales_data(self, date_from=None, date_to=None):
        domain = []

        # Default last 15 days
        if not date_from and not date_to:
            date_from = fields.Datetime.now() - timedelta(days=15)

        if date_from:
            domain.append(('date_order', '>=', date_from))
        if date_to:
            domain.append(('date_order', '<=', date_to))

        orders = self.env['sale.order'].search(domain, order='date_order desc')

        return [{
            'id': o.id,
            'name': o.name,
            'customer': o.partner_id.name,
            'total': o.amount_total,
            'date': o.date_order,
        } for o in orders]
