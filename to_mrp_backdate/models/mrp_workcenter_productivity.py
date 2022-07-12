from odoo import api, fields, models, _
from odoo.exceptions import UserError


class MrpWorkcenterProductivity(models.Model):
    _inherit = 'mrp.workcenter.productivity'

    backdate = fields.Datetime(string='Backdate', help="If filled, this date and time will be used instead"
                               " of the current date and time")

    @api.constrains('backdate')
    def _check_backdate(self):
        for r in self.filtered(lambda r: r.backdate):
            if r.backdate > fields.Datetime.now():
                raise UserError(_("You may not be able to specify a date in the future!"))

    def button_block(self):
        self.ensure_one()
        if self.backdate:
            self.date_start = self.backdate
            super(MrpWorkcenterProductivity, self.with_context(manual_validate_date_time=self.backdate)).button_block()
        else:
            super(MrpWorkcenterProductivity, self).button_block()
