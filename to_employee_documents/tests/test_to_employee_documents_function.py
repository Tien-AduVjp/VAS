from datetime import date

from odoo.tests import tagged
from odoo.tests.common import Form
from odoo.exceptions import ValidationError
from odoo.tools.misc import mute_logger

from .test_to_employee_documents_common import TestDocumentCommon

try:
    # try to use UniqueViolation if psycopg2's version >= 2.8
    from psycopg2 import errors
    UniqueViolation = errors.UniqueViolation
except Exception:
    import psycopg2
    UniqueViolation = psycopg2.IntegrityError


@tagged('post_install','-at_install')
class TestDocumentFunction(TestDocumentCommon):   

    def test_01_edit_documents(self):
        '''
            Check document dates, document types, employee documents
        ''' 
        self.identification_card_type.update({
            'description': '12 - number chipset identification card',
            'return_upon_termination': True,
            'days_to_notify': 15
            })
        self.labor_contract_type.update({
            'description': '1 year labor contract',
            'return_upon_termination': True,
            'days_to_notify': 30
            })        
        
        # Create 2 documents for employee "employeea"
        self.identification_card_a = self.env['employee.document'].create({
            'name': '100694419',
            'expire_date': date(2021, 8, 31),
            'type_id': self.identification_card_type.id,
            'employee_id': self.employeea.id
        })        
        self.labor_contract_a = self.env['employee.document'].create({
            'name': 'labor contract no.11111',
            'expire_date': date(2022, 8, 31),
            'type_id': self.labor_contract_type.id,
            'employee_id': self.employeea.id
        })
        
        # Edit to change the ID card a from identification type to labor contract type
        with Form(self.identification_card_a) as id_card_form:
            # Change type
            id_card_form.type_id = self.labor_contract_type
            self.assertEqual(
                id_card_form.days_to_notify,
                30, 
                "Expect: number of days to notify == 30."
            )
            self.assertEqual(
                id_card_form.date_to_notify, 
                date(2021, 8, 1),
                "Expect: Date to notify is 01-08-2021."
            )
            self.assertEqual(
                id_card_form.expire_date,
                '2021-08-31',
                "Expect: Expired Date is 31-08-2021"
            )
            # Change expired date with another value
            id_card_form.expire_date = date(2021, 7, 31)
            self.assertEqual(
                id_card_form.date_to_notify,
                date(2021, 7, 1),
                ("Expect: after changing the Expired Date, "
                 "the Date to Notify should be compute correspondingly.")
            )
            # Not assign any value to Expired Date
            # Expect: field Date To Notify will be invisible
            id_card_form.expire_date = False
            self.assertTrue(
                id_card_form._get_modifier('date_to_notify', 'invisible'),
            )
            
        self.assertEqual(
            self.employeea.document_count, 
            2, 
            "Expect: The 'employeea'the amount of document is 2."
        )
        self.assertTrue(self.identification_card_a.id in self.employeea.document_ids.ids)
        self.assertTrue(self.labor_contract_a.id in self.employeea.document_ids.ids)
 
    @mute_logger('odoo.sql_db')
    def test_02_check_data_contraints(self):
        '''
            Check sql constraints on the name at creating document
        '''
        document_a = self.env['employee.document'].create({
            'name': '100694419',
            'expire_date': date(2021, 7, 31),
            'type_id': self.identification_card_type.id,
            'employee_id': self.employeea.id
        })
        
        # Not allowed
        with self.assertRaises(UniqueViolation):
            self.env['employee.document'].create({
                'name': '100694419',
                'expire_date': date(2021, 8, 31),
                'type_id': self.identification_card_type.id,
                'employee_id': self.employeea.id
            })
        
    @mute_logger('odoo.sql_db')
    def test_02_01_check_data_contraints(self):
        '''
            Check sql constraints on the name at creating document
        '''
        document_a = self.env['employee.document'].create({
            'name': '100694419',
            'expire_date': date(2021, 7, 31),
            'type_id': self.identification_card_type.id,
            'employee_id': self.employeea.id
        })

        # Allowed
        self.env['employee.document'].create({
            'name': '100694419',
            'expire_date': date(2021, 8, 31),
            'type_id': self.identification_card_type.id,
            'employee_id': self.env.ref('hr.employee_qdp').id
        })
