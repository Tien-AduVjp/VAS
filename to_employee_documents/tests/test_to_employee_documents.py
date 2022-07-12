from datetime import date, timedelta

from odoo import fields
from odoo.tests import tagged, Form
from odoo.exceptions import UserError, ValidationError

from .test_to_employee_documents_common import TestDocumentCommon


@tagged('post_install','-at_install')
class TestEmployeeDocuments(TestDocumentCommon):

    def setUp(self):
        super().setUp()

        self.identification_card_type.write({
            'description': '12 - number chipset identification card',
            'kept_by': 'company',
            'return_upon_termination': True,
            'days_to_notify': 15
            })
        self.labor_contract_type.write({
            'description': '1 year labor contract',
            'kept_by': 'company',
            'return_upon_termination': True,
            'days_to_notify': 30
            })

        # Create 2 documents for employee "employeea"
        form_id_card = Form(self.env['employee.document'])
        form_id_card.name = '100694419'
        form_id_card.expire_date = '2021-08-31'
        form_id_card.type_id = self.identification_card_type
        form_id_card.employee_id = self.employeea
        self.identification_card_a = form_id_card.save()

        form_contract= Form(self.env['employee.document'])
        form_contract.name = 'labor contract no.11111'
        form_contract.expire_date = '2022-08-31'
        form_contract.type_id = self.labor_contract_type
        form_contract.employee_id = self.employeea
        self.labor_contract_a = form_contract.save()

    def test_03_form_test(self):
        """
            Test on change
            Input:
                1) Enter value on Expire Date
            Expect:
                1) Date To Notify will be computed based on Expire Date
                2) Days to notify will be set according to the Document Type
                   Return Upon Termination will be set according to the Document Type
        """
        self.labor_contract_type.write({'days_to_notify': 20})
        with Form(self.env['employee.document']) as id_card_form:
            id_card_form.name = '100694419111'
            id_card_form.expire_date = '2021-08-31'
            id_card_form.type_id = self.labor_contract_type
            id_card_form.employee_id = self.employeea

            self.assertEqual(id_card_form.days_to_notify, 20)
            self.assertEqual(id_card_form.date_to_notify, date(2021, 8, 11))

            self.assertTrue(
                id_card_form.return_upon_termination,
                "Expect: True according to the 'labor_contract_type' type"
            )

        self.labor_contract_type.write({'days_to_notify': 0})
        with Form(self.env['employee.document']) as id_card_form:
            id_card_form.name = '10069441989'
            id_card_form.expire_date = '2021-08-31'
            id_card_form.type_id = self.labor_contract_type
            id_card_form.employee_id = self.employeea

            self.assertEqual(id_card_form.date_to_notify, False)

    def test_01_functional(self):
        """
            Input:
                Create a new document
            Expect:
                Creating successfully
        """
        test_saved_document = self.env['employee.document'].search([('id', 'in', self.identification_card_a.ids)])

        self.assertEqual(len(test_saved_document), 1)

    def test_02_functional(self):
        """
            Input:
                Create 2 documents for employee A
            Expect:
                Employee A will have data of:
                    counting number of created documents
                    records of created documents
        """
        self.employeea._compute_document_count()

        self.assertEqual(len(self.employeea.document_ids), 2)
        self.assertEqual(self.employeea.document_count, 2)

    def test_03_functional_expire_notification(self):
        """
            Test cron job: Notify when the document is about to be expired
            Input:
                Set today as expired date on a document
            Expect:
                After the cron job has run, the date of last notification will be updated correspondingly.
        """
        today = fields.Date.today()
        date_to_notify = today - timedelta(days=self.identification_card_a.days_to_notify)
        test_date = today + timedelta(days=2)

        self.identification_card_a.write({'expire_date': today})

        self.identification_card_a.cron_notify_expire_docs()
        if self.identification_card_a.employee_id.address_id.lang == 'en_US':
            self.assertEqual(
                self.identification_card_a.message_ids[0].subject,
                "National ID '100694419' is about to expire"
            )
        elif self.identification_card_a.employee_id.address_id.lang == 'vi_VN':
            self.assertEqual(
                self.identification_card_a.message_ids[0].subject,
                "Chứng minh Nhân dân '100694419' sắp hết hạn"
            )

    def test_03_functional_extension(self):
        """
            Test the case:
            the cron job still runs even if the expire date is the day before yesterday
        """
        new_expire_date = fields.Date.today() - timedelta(days=2)
        self.identification_card_a.write({'expire_date': new_expire_date})

        self.identification_card_a.cron_notify_expire_docs()
        if self.identification_card_a.employee_id.address_id.lang == 'en_US':
            self.assertEqual(
                self.identification_card_a.message_ids[0].subject,
                "National ID '100694419' is about to expire"
            )
        elif self.identification_card_a.employee_id.address_id.lang == 'vi_VN':
            self.assertEqual(
                self.identification_card_a.message_ids[0].subject,
                "Chứng minh Nhân dân '100694419' sắp hết hạn"
            )

    def test_04_functional(self):
        """
            Test api.contrains:
            If
                - a document is set to be kept by company
                - but doesn't need to be returned to the owner
            then
                raise UserError
        """
        self.identification_card_a.write({
            'kept_by': 'company',
            'return_upon_termination': False
        })
        with self.assertRaises(UserError):
            self.identification_card_a.action_return_to_owner()

    def test_04_functional_main(self):
        """
            Test api.contrains:
            If
                - a document is set to be kept by company
                - but doesn't need to be returned to the owner
            then
                Action done successfully
        """
        self.identification_card_a.write({
            'kept_by': 'company',
            'return_upon_termination': True
        })
        self.identification_card_a.action_return_to_owner()
        self.assertEqual(self.identification_card_a.kept_by, 'employee')

    def test_05_function_api_contrains(self):
        """
            Test api.constrains
            On a document:
                Expired date must be after Issued Date
        """
        with self.assertRaises(ValidationError):
            self.identification_card_a.write({
                'issue_date': date(2021, 10, 10),
                'expire_date': date(2021, 10, 9)
            })

    def test_08_function(self):
        """
            Test Data Input
        """
        with self.assertRaises(ValueError):
            self.identification_card_a.write({'days_to_notify': 'string'})

        self.identification_card_a.write({'days_to_notify': -1})
        self.assertFalse(bool(self.identification_card_a.date_to_notify))
        self.identification_card_a.write({'days_to_notify': 0})
        self.assertFalse(bool(self.identification_card_a.date_to_notify))

    def test_09_document_type(self):
        """
            Test create document type
        """
        doc_type_form = Form(self.env['employee.document.type'])
        doc_type_form.kept_by = 'employee'
        self.assertTrue(
            doc_type_form._get_modifier('return_upon_termination', 'invisible'),
        )

        doc_type_form.kept_by = 'company'
        self.assertFalse(
            doc_type_form._get_modifier('return_upon_termination', 'invisible'),
        )

    def test_10_create_document_type(self):
        with self.assertRaises(UserError):
            self.env['employee.document.type'].create({
                'name': 'Donation certificate',
                'type': 'others',
                'description': 'Failed test',
                'kept_by': 'employee',
                'return_upon_termination': True
            })
