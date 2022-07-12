from datetime import date

from unittest.mock import patch
from odoo import fields
from odoo.tests import TransactionCase, tagged

NOW = date(2021, 8, 12)


@tagged('post_install', '-at_install')
@patch.object(fields.Date, 'today', lambda: NOW)
class TestHrEmployeeSeniority(TransactionCase):

    def setUp(self):
        super(TestHrEmployeeSeniority, self).setUp()

        self.user = self.env['res.users'].with_context(no_reset_password=True, tracking_disable=True).create({
            'name': 'Test User',
            'login': 'user',
            'groups_id': [(6, 0, self.env.ref('base.group_user').ids)]
        })
        self.user.action_create_employee()
        self.employee = self.user.employee_id

        self.contract_create_val = {
            'name': 'Contract for Test User',
            'employee_id': self.employee.id,
            'wage': 5000.0,
        }

    def test_hr_employee_seniority_1(self):
        """Input: Contract with start date and end date are smaller than current date, there is a trial end date.
        """
        date_start = date(2019, 8, 11)
        date_end = date(2020, 8, 11)
        trial_date_end = date(2019, 9, 11)
        first_non_trial_date = date(2019, 9, 12)

        contract_create_val = self.contract_create_val.copy()
        contract_create_val['date_start'] = date_start
        contract_create_val['date_end'] = date_end
        contract_create_val['trial_date_end'] = trial_date_end
        contract = self.env['hr.contract'].create(contract_create_val)

        """ Case 1: The state of the contract is draft
                Expectation: Seniority is not counted
        """
        self.assertEqual(self.employee.seniority_message, '0')

        """ Case 2: The state of the contract is open
        """
        self.employee.invalidate_cache()
        contract.action_start_contract()
        self.assertEqual(contract.years, 1.0)
        self.assertEqual(contract.months, 12.0)
        self.assertEqual(self.employee.termination_date, date_end)
        self.assertEqual(self.employee.first_non_trial_contract_date, first_non_trial_date)
        self.assertEqual(self.employee.seniority_message, '1 year')
        self.assertEqual(len(self.employee.employee_seniority_ids), 2)

        employee_seniority_trial = self.employee.employee_seniority_ids.filtered(lambda x: x.is_trial)
        self.assertEqual(employee_seniority_trial.date_start, date_start)
        self.assertEqual(employee_seniority_trial.date_end, trial_date_end)
        self.assertAlmostEqual(employee_seniority_trial.service_years, 0.083333333, 9)

        employee_seniority = self.employee.employee_seniority_ids.filtered(lambda x: not x.is_trial)
        self.assertEqual(employee_seniority.date_start, first_non_trial_date)
        self.assertEqual(employee_seniority.date_end, date_end)
        self.assertAlmostEqual(employee_seniority.service_years, 0.916666667, 9)

        """ Case 3: The state of the contract is close
        """
        self.employee.invalidate_cache()
        contract.set_as_close()
        self.assertEqual(contract.years, 1.0)
        self.assertEqual(contract.months, 12.0)
        self.assertEqual(self.employee.termination_date, contract.date_end)
        self.assertEqual(self.employee.first_non_trial_contract_date, first_non_trial_date)
        self.assertEqual(self.employee.seniority_message, '1 year')
        self.assertEqual(len(self.employee.employee_seniority_ids), 2)

        employee_seniority_trial = self.employee.employee_seniority_ids.filtered(lambda x: x.is_trial)
        self.assertEqual(employee_seniority_trial.date_start, date_start)
        self.assertEqual(employee_seniority_trial.date_end, trial_date_end)
        self.assertAlmostEqual(employee_seniority_trial.service_years, 0.083333333, 9)

        employee_seniority = self.employee.employee_seniority_ids.filtered(lambda x: not x.is_trial)
        self.assertEqual(employee_seniority.date_start, first_non_trial_date)
        self.assertEqual(employee_seniority.date_end, date_end)
        self.assertAlmostEqual(employee_seniority.service_years, 0.916666667, 9)

        """ Case 4: The state of the contract is cancel
                Expectation: Seniority is not counted
        """
        self.employee.invalidate_cache()
        contract.action_cancel()
        self.assertEqual(self.employee.seniority_message, '0')

    def test_hr_employee_seniority_2(self):
        """Input: Contract with start date is smaller than current date, trial end date is smaller than start date, end date is greater than current date.
        """
        date_start = date(2019, 8, 12)
        date_end = date(2022, 8, 12)
        trial_date_end = date(2018, 9, 12)

        contract_create_val = self.contract_create_val.copy()
        contract_create_val['date_start'] = date_start
        contract_create_val['date_end'] = date_end
        contract_create_val['trial_date_end'] = trial_date_end
        contract = self.env['hr.contract'].create(contract_create_val)

        """ Case 1: The state of the contract is open
        """
        self.employee.invalidate_cache()
        contract.action_start_contract()
        self.assertEqual(contract.years, 2.0)
        self.assertEqual(contract.months, 24.0)
        self.assertEqual(len(self.employee.employee_seniority_ids), 1)
        self.assertEqual(self.employee.employee_seniority_ids.service_years, 2.0)

    def test_hr_employee_seniority_3(self):
        """Input: Contract with start date and end date are greater than current date, there isn't trial end date.
        """
        date_start = date(2022, 8, 12)
        date_end = date(2023, 8, 12)

        contract_create_val = self.contract_create_val.copy()
        contract_create_val['date_start'] = date_start
        contract_create_val['date_end'] = date_end
        contract = self.env['hr.contract'].create(contract_create_val)

        """ Case 1: The state of the contract is open
        """
        self.employee.invalidate_cache()
        contract.action_start_contract()
        self.assertEqual(contract.years, 0.0)
        self.assertEqual(contract.months, 0.0)
        self.assertEqual(len(self.employee.employee_seniority_ids), 1)
        self.assertEqual(self.employee.employee_seniority_ids.service_years, 0.0)

    def test_hr_employee_seniority_4(self):
        """Input: Contract with start date and trial end date, there isn't end date
        """
        date_start = date(2019, 8, 12)
        trial_date_end = date(2019, 8, 22)

        contract_create_val = self.contract_create_val.copy()
        contract_create_val['date_start'] = date_start
        contract_create_val['trial_date_end'] = trial_date_end
        contract = self.env['hr.contract'].create(contract_create_val)

        """ Case 1: The state of the contract is open
        """
        self.employee.invalidate_cache()
        contract.action_start_contract()
        self.assertFalse(self.employee.termination_date)

        self.assertEqual(len(self.employee.employee_seniority_ids), 2)

        employee_seniority = self.employee.employee_seniority_ids.filtered(lambda x: x.is_trial)
        self.assertAlmostEqual(employee_seniority.service_years, 0.027397260, 9)

        employee_seniority = self.employee.employee_seniority_ids.filtered(lambda x: not x.is_trial)
        self.assertFalse(employee_seniority.date_end)
        self.assertAlmostEqual(employee_seniority.service_years, 1.974200913, 9)

    def test_hr_employee_seniority_5(self):
        """Input: User in multiple contracts
        """
        contract_create_val = self.contract_create_val.copy()
        contract_create_val['date_start'] = date(2021, 2, 12)
        contract_create_val['date_end'] = date(2021, 5, 12)
        contractA = self.env['hr.contract'].create(contract_create_val)

        contractB = contractA.copy()
        contractC = contractA.copy()
        contractD = contractA.copy()

        self.employee.invalidate_cache()
        contractA.action_start_contract()
        contractA.set_as_close()

        contractB.date_start = date(2020, 8, 15)
        contractB.date_end = date(2021, 2, 11)
        self.employee.invalidate_cache()
        contractB.action_start_contract()
        contractB.set_as_close()

        contractC.date_start = date(2020, 6, 15)
        contractC.date_end = date(2020, 8, 14)
        contractC.trial_date_end = date(2020, 8, 14)
        self.employee.invalidate_cache()
        contractC.action_start_contract()
        contractC.set_as_close()

        contractD.date_end = date(2022, 6, 11)
        contractD.date_start = date(2021, 6, 12)
        self.employee.invalidate_cache()
        contractD.action_start_contract()

        self.assertEqual(self.employee.termination_date, date(2022, 6, 11))
        self.assertEqual(self.employee.first_non_trial_contract_date, date(2020, 8, 15))

        employee_seniority = self.employee.employee_seniority_ids.sorted(lambda x: x.date_start)
        self.assertAlmostEqual(employee_seniority[0].service_years, 0.165300546, 9)
        self.assertAlmostEqual(employee_seniority[1].service_years, 0.490437158, 9)
        self.assertAlmostEqual(employee_seniority[2].service_years, 0.25, 9)
        self.assertAlmostEqual(employee_seniority[3].service_years, 0.166666667, 9)

    def test_hr_employee_seniority_6(self):
        "Input: compare seniority months, years of employee with months, years of contract "
        "Expected: contract's seniority must be the same as the employee's seniority"
        date_start = date(2020, 1, 13)
        date_end = date(2021, 3, 17)
        trial_date_end = date(2021, 3, 17)
        contract_create_val = self.contract_create_val.copy()
        contract_create_val['date_start'] = date_start
        contract_create_val['date_end'] = date_end
        contract_create_val['trial_date_end'] = trial_date_end
        contract = self.env['hr.contract'].create(contract_create_val)

        self.employee.invalidate_cache()
        contract.action_start_contract()
        self.assertAlmostEqual(self.employee.seniority_months, contract.months, 9)
        self.assertAlmostEqual(self.employee.seniority_years, contract.years, 9)
