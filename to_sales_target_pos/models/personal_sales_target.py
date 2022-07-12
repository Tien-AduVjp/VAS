from odoo import models, api, fields
from datetime import datetime


class PersonalSalesTarget(models.Model):
    _inherit = 'personal.sales.target'

    non_invoiced_pos_order_ids = fields.Many2many(relation='non_invoiced_pos_order_personal_target')
    invoiced_pos_order_ids = fields.Many2many(relation='invoiced_pos_order_personal_target')

    def _get_pos_orders(self):
        self.ensure_one()
        start_date = datetime.combine(self.start_date, datetime.min.time())
        end_date = datetime.combine(self.end_date, datetime.max.time())
        non_invoiced_pos_order_ids = self.sale_person_id.st_pos_order_ids.filtered(lambda o: o.date_order >= start_date \
                                                                                   and o.date_order <= end_date \
                                                                                   and o.state in ('paid', 'done'))
        invoiced_pos_order_ids = self.sale_person_id.st_pos_order_ids.filtered(lambda o: o.date_order >= start_date \
                                                                               and o.date_order <= end_date \
                                                                               and o.state == 'invoiced')
        return non_invoiced_pos_order_ids, invoiced_pos_order_ids

    @api.depends('sale_person_id.st_pos_order_ids', 'sale_person_id.st_pos_order_ids.state', 'state')
    def _compute_pos_order_ids(self):
        super(PersonalSalesTarget, self)._compute_pos_order_ids()

