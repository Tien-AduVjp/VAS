from dateutil.relativedelta import relativedelta

from odoo import fields, models, _


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    workcenter_id = fields.Many2one('mrp.workcenter', string='Work Center')
    mttr = fields.Integer(string='Mean Time To Repair', compute='_compute_maintenance_request')
    expected_mtbf = fields.Integer(string='Expected Mean Time Between Failure', help="It is the mean time expected until the first failure of a piece of equipment.")
    mtbf = fields.Integer(string='Mean Time Between Failure', compute='_compute_maintenance_request', help="Can be calculated based on done corrective maintenances.")
    estimated_next_failure = fields.Date(string='Estimated time before next failure (in days)', compute='_compute_maintenance_request', help="Can be calculated as Latest Failure Date + MTBF")
    latest_failure_date = fields.Date(string='Latest Failure Date', compute='_compute_maintenance_request')

    def _compute_maintenance_request(self):
        requests = self.env['maintenance.request'].search([('equipment_id', 'in', self.ids), ('maintenance_type', '=', 'corrective'), ('stage_id.done', '=', True)])

        def calculate_mttr_days(req):
            if req.close_date:
                start_date = req.schedule_date and req.schedule_date.date() or req.request_date
                return (req.close_date - start_date).days
            return 0

        for r in self:
            requests_ftr = requests.filtered(lambda req: req.equipment_id.id == r.id)
            requests_ftr_count = len(requests_ftr)
            mttr_days = sum(requests_ftr.filtered(lambda req: req.close_date).mapped(calculate_mttr_days))
            r.mttr = len(requests_ftr) and (mttr_days / requests_ftr_count) or 0

            maintenance = requests_ftr.sorted()
            if requests_ftr_count >= 1:
                r.mtbf = (maintenance[0].request_date - r.effective_date).days / (requests_ftr_count)
            else:
                r.mtbf = 0

            r.latest_failure_date = maintenance and maintenance[0].request_date or False

            r.estimated_next_failure = r.latest_failure_date + relativedelta(days=r.mtbf) if (r.mtbf and r.latest_failure_date) else False

    def action_view_workcenter(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Work Center'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mrp.workcenter',
            'view_id': self.env.ref('mrp.mrp_workcenter_view').id,
            'res_id': self.workcenter_id.id,
        }
