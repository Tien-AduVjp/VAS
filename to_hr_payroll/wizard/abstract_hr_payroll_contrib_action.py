from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class AbstractHrPayrollContribAction(models.AbstractModel):
    _name = 'abstract.hr.payroll.contrib.act'
    _description = "Share business logics between hr.payroll.contrib.action models"

    date = fields.Date(string='Date', required=True, default=fields.Date.today())

    def process(self):
        raise ValidationError(_("The method `process` has not been implemented for the model `%s`") % (self._name,))
