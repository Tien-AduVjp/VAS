from odoo.tests.common import TransactionCase
from odoo import fields
from dateutil.relativedelta import relativedelta

class Common(TransactionCase):
    def setUp(self):
        super(Common, self).setUp()

        self.vehicle_a = self.env.ref('fleet.vehicle_1')
        self.vehicle_b = self.env.ref('fleet.vehicle_2')
        self.insurance_type_public_liability_insurance = self.env.ref('to_fleet_insurance_basic.fleet_public_liability_insurance')
        self.vehicle_insurance = self.create_new_fleet_vehicle_insurance()

        self.cron_set_expired = self.env.ref('to_fleet_insurance_basic.ir_cron_find_to_set_expire')
        self.cron_send_expire_notice = self.env.ref('to_fleet_insurance_basic.ir_cron_send_expire_notice')

        #Create users
        self.fleet_group_user = self.env.ref('base.user_admin')
        self.fleet_group_user.write({
            'groups_id': [(6, 0, [self.env.ref('fleet.fleet_group_user').id])]
        })

    def create_new_fleet_vehicle_insurance(self):
        self.fleet_vehicle_insurance = self.env['fleet.vehicle.insurance'].create({
            'name': 'Vehicle Insurance for vehicle A',
            'vehicle_id': self.vehicle_a.id,
            'fleet_insurance_type_id': self.insurance_type_public_liability_insurance.id,
            'date_start': fields.Date.today() + relativedelta(days=-15),
            'date_end': fields.Date.today() + relativedelta(days=-2),
            'days_to_notify': 7
        })
        return self.fleet_vehicle_insurance
