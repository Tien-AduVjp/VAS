from odoo import api, fields, models


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    sale_order_id = fields.Many2one('sale.order', string='Sale Order', check_company=True)

    @api.onchange('sale_order_id')
    def _onchange_sale_order_id(self):
        if self.sale_order_id:
            self.team_id = self.env['helpdesk.team'].with_context(lang='en_US').search(
                [('name', '=', 'Customer Support'), ('company_id', 'in', self.env.companies.ids)], limit=1).id \
                           or self.env.company.default_helpdesk_team_id.id
