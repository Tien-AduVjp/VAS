from odoo import  fields, models, _, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    warranty_ids = fields.One2many('warranty.claim', 'lot_id', string='Warranty', groups='to_warranty_management.group_warranty_user')
    warranty_count = fields.Integer(string='Warranty count', compute='_computte_warranty_count', groups='to_warranty_management.group_warranty_user')
    warranty_start_date = fields.Date(string='Warranry Start Date', tracking=True)
    warranty_period = fields.Integer('Warranty period (months)', compute='_get_warranty_period',
                                     store=True, readonly=False, tracking=True)
    warranty_expiration_date = fields.Date(string='Warranty Expiration Date', compute='_compute_warranty_expiration_date', readonly=True)
    warranty_claim_policy_ids = fields.One2many('warranty.claim.policy', 'stock_production_lot_id', string='Warranty Policy', readonly=False,
                                                groups='to_warranty_management.group_warranty_user')
    supplier_warranty_start_date = fields.Date(string='Supplier Warranry Start Date', tracking=True)
    supplier_warranty_expiration_date = fields.Date(string='Supplier Warranty Expiration Date', compute='_compute_supplier_warranty_expiration_date', readonly=True)

    _sql_constraints = [
        (
            'check_warranty_period_not_negative',
            'CHECK(warranty_period >= 0)',
            "The warranty period cannot be a negative number",
        ),
    ]

    @api.depends('warranty_ids')
    def _computte_warranty_count(self):
        for r in self.sudo():
            r.warranty_count = len(self.warranty_ids)

    def action_view_warranty_history(self):
        warranty_ids = self.mapped('warranty_ids')
        action = self.env['ir.actions.act_window']._for_xml_id('to_warranty_stock.action_warranty_claim_history')
        if len(warranty_ids) > 1:
            action['domain'] = [('id', 'in', warranty_ids.ids)]
        elif len(warranty_ids) == 1:
            action['views'] = [(self.env.ref('to_warranty_management.warranty_claim_form_view').id, 'form')]
            action['res_id'] = warranty_ids.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.depends('product_id')
    def _get_warranty_period(self):
        for r in self:
            if not r.warranty_period:
                r.warranty_period = r.product_id.warranty_period

    @api.depends('warranty_period', 'warranty_start_date')
    def _compute_warranty_expiration_date(self):
        for r in self:
            r.warranty_expiration_date = False
            if r.warranty_period and r.warranty_start_date:
                r.warranty_expiration_date = fields.Date.from_string(r.warranty_start_date) + relativedelta(months=r.warranty_period)

    @api.depends('warranty_period', 'supplier_warranty_start_date')
    def _compute_supplier_warranty_expiration_date(self):
        for r in self:
            r.supplier_warranty_expiration_date = False
            if r.warranty_period and r.supplier_warranty_start_date:
                r.supplier_warranty_expiration_date = fields.Date.from_string(r.supplier_warranty_start_date) + relativedelta(months=r.warranty_period)

    def write(self, values):
        for r in self:
            warranty_start_date = values.get('warranty_start_date', False)
            warranty_period = values.get('warranty_period', False)

            if warranty_start_date or warranty_period:
                if r.warranty_ids.filtered(lambda wcl: wcl.state not in ['draft', 'cancelled']):
                    raise ValidationError(_("You cannot change warranty information of lot/serial, which already had processed warranty claim."))
        return super(ProductionLot, self).write(values)
