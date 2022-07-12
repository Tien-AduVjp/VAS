# -*- coding: utf-8 -*-

from odoo.addons.hr_contract.tests.test_auto_status import TestHrContracts
from odoo.addons.hr_contract.tests.test_calendar_sync import TestContractCalendars
from odoo.addons.hr_contract.tests.test_contract import TestHrContracts as TestHrContracts2

# RE-TEST hr_contract
class TestHrContractsRetest1(TestHrContracts):

    def setUp(self):
        super(TestHrContractsRetest1, self).setUp()


class TestContractCalendarsRetest(TestContractCalendars):

    def setUp(self):
        super(TestContractCalendarsRetest, self).setUp()


class TestHrContractsRetest2(TestHrContracts2):

    def setUp(self):
        super(TestHrContractsRetest2, self).setUp()
