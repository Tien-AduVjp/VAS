from odoo.tests.common import SavepointCase


class TestDocumentCommon(SavepointCase):

    def setUp(self):
        super(TestDocumentCommon, self).setUp()
        self.employeea = self.env.ref('hr.employee_admin')
        self.identification_card_type = self.env.ref('to_employee_documents.employee_document_type_national_id')
        self.labor_contract_type = self.env.ref('to_employee_documents.employee_document_type_hr_contract')
