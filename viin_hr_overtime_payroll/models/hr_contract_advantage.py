from odoo import fields, models


class HrContractAdvandage(models.Model):
    _inherit = 'hr.contract.advantage'

    overtime_base_factor = fields.Boolean(related='template_id.overtime_base_factor',
                                          help="If enabled, This advantage amount will be added into the contract's"
                                          " Overtime Base Amount for overtime calculation.")

