from odoo import fields
from odoo.tests.common import tagged
from .common import FleetDriverJobWageCommon


@tagged('post_install', '-at_install')
class TestFleetHrPayslip(FleetDriverJobWageCommon):

    @classmethod
    def setUpClass(cls):
        super(TestFleetHrPayslip, cls).setUpClass()
        cls.setUP_fuel_price()
        cls.setUP_multiple_trip()
    
    def test_4_compute_vehicle_trip_ids(self):
        self.trip_1.action_confirm()
        self.trip_2.action_confirm()
        self.trip_another_month.action_confirm()
        self.trip_another_partner.action_confirm()
        self.trip_not_done.action_confirm()
        
        self.trip_1.write({'state':'done'})
        self.trip_2.write({'state':'done'})
        self.trip_another_month.write({'state':'done'})
        self.trip_another_partner.write({'state':'done'})
        
        contract_employee = self.user.employee_id.contract_ids[0]
        contract_employee.write({
            'date_start':fields.Date.from_string('1999-6-1'),
            'date_end': False,
            'state':'open'
            })
        payslip = self.env['hr.payslip'].create({
            'employee_id': self.user.employee_id.id,
            'contract_id': contract_employee.id,
            'company_id': self.env.company.id,
            'date_from': fields.Date.from_string('2021-9-1'),
            'date_to': fields.Date.from_string('2021-9-30'),
        })
        self.assertTrue(self.trip_1 in payslip.vehicle_trip_ids, "to_fleet_driver_job_wage: error compute_vehicle_trip_ids")
        self.assertTrue(self.trip_2 in payslip.vehicle_trip_ids, "to_fleet_driver_job_wage: error compute_vehicle_trip_ids")
        self.assertTrue(self.trip_another_month not in payslip.vehicle_trip_ids, "to_fleet_driver_job_wage: error compute_vehicle_trip_ids")
        self.assertTrue(self.trip_another_partner not in payslip.vehicle_trip_ids, "to_fleet_driver_job_wage: error compute_vehicle_trip_ids")
        self.assertTrue(self.trip_not_done not in payslip.vehicle_trip_ids, "to_fleet_driver_job_wage: error compute_vehicle_trip_ids")
        self.check_5_compute_total_job_wage(payslip)
        self.check_6_compute_total_allowance(payslip)

    def check_5_compute_total_job_wage(self, payslip):
        self.assertEqual(payslip.total_job_wage, 505000, "to_fleet_driver_job_wage: error compute_total_job_wage")

    def check_6_compute_total_allowance(self, payslip):
        self.assertEqual(payslip.total_allowance, 300000, "to_fleet_driver_job_wage: error compute_total_allowance")
