# -*- coding: utf-8 -*-

from odoo.addons.stock_account.tests.test_stockvaluationlayer import TestStockValuationStandard
from odoo.addons.stock_account.tests.test_stockvaluationlayer import TestStockValuationAVCO
from odoo.addons.stock_account.tests.test_stockvaluationlayer import TestStockValuationFIFO
from odoo.addons.stock_account.tests.test_stockvaluationlayer import TestStockValuationChangeCostMethod
from odoo.addons.stock_account.tests.test_stockvaluationlayer import TestStockValuationChangeValuation


class TestStockValuationStandardRetest(TestStockValuationStandard):

    def setUp(self):
        super(TestStockValuationStandardRetest, self).setUp()


class TestStockValuationAVCORetest(TestStockValuationAVCO):

    def setUp(self):
        super(TestStockValuationAVCORetest, self).setUp()


class TestStockValuationFIFORetest(TestStockValuationFIFO):

    def setUp(self):
        super(TestStockValuationFIFORetest, self).setUp()


class TestStockValuationChangeCostMethodRetest(TestStockValuationChangeCostMethod):

    def setUp(self):
        super(TestStockValuationChangeCostMethodRetest, self).setUp()


class TestStockValuationChangeValuationRetest(TestStockValuationChangeValuation):

    def setUp(self):
        super(TestStockValuationChangeValuationRetest, self).setUp()
