from odoo import fields, models, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError


class WizardStockReportCommon(models.AbstractModel):
    _name = 'wizard.stock.report.common'
    _description = 'Stock Report Common Wizard'

    @api.model
    def _get_location_domain(self):
        return [('usage', 'in', ('view', 'internal'))]

    def _default_date_from(self):
        """
        Return the first of the current month
        """
        first_of_month = fields.Datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        first_of_month = self.env['to.base'].convert_time_to_utc(first_of_month)
        # convert timezone aware datetime to naive
        first_of_month = first_of_month.replace(tzinfo=None)
        return first_of_month

    date_from = fields.Datetime(string="Date From", required=True, default=_default_date_from)
    date_to = fields.Datetime(string="Date To", required=True, default=fields.Datetime.now, help="Extract the data upto this date (not including this date)")
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', compute='_compute_warehouse_id', readonly=False, store=True,
                                   domain="[('company_id', '=', company_id)]", help="Leave empty for the whole data of the"
                                   " inventory system, no matter which the warehouse is.")
    location_id = fields.Many2one('stock.location', string="Stock Location", compute='_compute_location_id', readonly=False, store=True,
                                  domain="[('usage', 'in', ('view', 'internal')),('warehouse_id', '=', warehouse_id)]",
                                  help="Only stock locations in types of view and internal are available for report."
                                  " The data in the report also include the data corresponding to the sub-locations of the selected location")
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)

    @api.constrains('date_from', 'date_to')
    def _check_date_constrain(self):
        for r in self:
            if r.date_to < r.date_from:
                raise UserError(_("The Date To must be later than the Date From"))

    @api.depends('company_id')
    def _compute_warehouse_id(self):
        for r in self:
            if r.warehouse_id.company_id.id != r.company_id.id:
                r.warehouse_id = False
            else:
                r.warehouse_id = r.warehouse_id

    @api.depends('warehouse_id')
    def _compute_location_id(self):
        for r in self:
            r.location_id = r.warehouse_id.view_location_id

    def _print_report(self, data):
        raise ValidationError(_("The method `_print_report` has not been implemted for the model '%s'") % self._name)

    def _build_contexts(self, data):
        result = {}
        result['date_from'] = data['form']['date_from'] or False
        result['date_to'] = data['form']['date_to'] or False
        result['company_id'] = data['form']['company_id'] or False
        result['warehouse_id'] = data['form']['warehouse_id'] or False
        return result

    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'company_id', 'warehouse_id', 'location_id'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang', 'en_US'))
        res = self._print_report(data)
        return res
