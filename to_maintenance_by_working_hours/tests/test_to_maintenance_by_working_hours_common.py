
from datetime import datetime
from unittest.mock import patch
from odoo import fields

from odoo.tests.common import TransactionCase


class TestMaintenanceWorkingHoursCommon(TransactionCase):
    def setUp(self):
        super(TestMaintenanceWorkingHoursCommon, self).setUp()
        self.equipment = self.env['maintenance.equipment']
        self.hp_laptop = self.env.ref('maintenance.equipment_computer11')

        self.maintenance_request_todo = self.env.ref('maintenance.m_request_8')
        self.maintenance_request_done = self.env.ref('maintenance.m_request_3')
        self.maintenance_team = self.env.ref('maintenance.equipment_team_maintenance')
        
        self.maintenance_request_todo.update({'equipment_id': False})
        self.maintenance_request_done.update({'equipment_id': False})
        
    def _update_equipment(self, equipment, ave_daily_working_hours = 0, working_hour_period = 0):
        equipment.write({
            'maintenance_team_id': self.maintenance_team.id,
            'ave_daily_working_hours': ave_daily_working_hours,
            'working_hour_period': working_hour_period
            })
        equipment.flush()


