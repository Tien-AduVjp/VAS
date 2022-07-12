from odoo import fields, models


class Task(models.Model):
    _inherit = "project.task"

    okr_node_id = fields.Many2one('okr.node', string="OKR Key Result", help="The OKR key result for which this task is.")
