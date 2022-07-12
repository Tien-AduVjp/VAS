from odoo.tests.common import TransactionCase, Form


class Common(TransactionCase):

    def setUp(self):
        super(Common, self).setUp()
        self.team_maintenance = self.env.ref('maintenance.equipment_team_maintenance')
        form_equipment = Form(self.env.ref('maintenance.equipment_computer5'))
        form_equipment.effective_date = '2021-12-08'
        form_equipment.preventive_maintenance_mode = 'hour'
        form_equipment.maintenance_team_id = self.team_maintenance
        self.equipment = form_equipment.save()
