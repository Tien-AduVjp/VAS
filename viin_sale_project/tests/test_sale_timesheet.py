from odoo.tests import tagged

from odoo.addons.sale_timesheet.tests.test_project_billing import TestProjectBilling
from odoo.addons.sale_timesheet.tests.test_project_billing_multicompany import TestProjectBillingMulticompany
from odoo.addons.sale_timesheet.tests.test_reinvoice import TestReInvoice
from odoo.addons.sale_timesheet.tests.test_reporting import TestReporting
from odoo.addons.sale_timesheet.tests.test_sale_service import TestSaleService
from odoo.addons.sale_timesheet.tests.test_sale_timesheet import TestSaleTimesheet

@tagged('post_install', '-at_install')
class TestProjectBillingReTest(TestProjectBilling):
    pass

@tagged('post_install', '-at_install')
class TestProjectBillingMulticompanyReTest(TestProjectBillingMulticompany):
    pass

@tagged('post_install', '-at_install')
class TestReInvoiceReTest(TestReInvoice):
    pass

@tagged('post_install', '-at_install')
class TestReportingReTest(TestReporting):
    pass

@tagged('post_install', '-at_install')
class TestSaleServiceReTest(TestSaleService):
    pass

@tagged('post_install', '-at_install')
class TestSaleTimesheetReTest(TestSaleTimesheet):
    pass
