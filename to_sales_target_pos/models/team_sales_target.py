from odoo import models, api, fields
from datetime import datetime


class TeamSalesTarget(models.Model):
    _inherit = 'team.sales.target'

    non_invoiced_pos_order_ids = fields.Many2many(relation='non_invoiced_pos_order_team_target')
    invoiced_pos_order_ids = fields.Many2many(relation='invoiced_pos_order_team_target')

    def _get_pos_orders(self):
        start_date = datetime.combine(self.start_date, datetime.min.time())
        end_date = datetime.combine(self.end_date, datetime.max.time())
        non_invoiced_pos_order_ids = self.crm_team_id.st_pos_order_ids.filtered(lambda o: o.date_order >= start_date \
                                                                                and o.date_order <= end_date \
                                                                                and o.state in ('paid', 'done'))
        invoiced_pos_order_ids = self.crm_team_id.st_pos_order_ids.filtered(lambda o: o.date_order >= start_date \
                                                                            and o.date_order <= end_date \
                                                                            and o.state == 'invoiced')
        return non_invoiced_pos_order_ids, invoiced_pos_order_ids

    @api.depends('crm_team_id.st_pos_order_ids', 'crm_team_id.st_pos_order_ids.state', 'state')
    def _compute_pos_order_ids(self):
        super(TeamSalesTarget, self)._compute_pos_order_ids()

