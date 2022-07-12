from datetime import date

from odoo.tests import tagged
from odoo.tests.common import Form
from odoo.exceptions import AccessError

from .test_to_employee_documents_common import TestDocumentCommon


@tagged('post_install','-at_install')
class TestEmployeeDucomentSecurityRule(TestDocumentCommon):
    
    def setUp(self):
        super().setUp()
        
        self.employee_manager = self.env.ref('hr.employee_admin')
        self.user_manager = self.env.user
        self.employee_employee = self.env.ref('hr.employee_qdp')
        self.user_employee = self.env.ref('base.user_demo')
        
        # Admin creates a document type
        self.test_document_type = self.env['employee.document.type'].create({
            'name': 'Test Document Type',
            'type': 'others',
            'kept_by': 'employee',
            'return_upon_termination': True,
            'description': 'Other type of document',
            'days_to_notify': 30
        })
        # Admin creates a document for employee
        self.test_employee_document = self.env['employee.document'].create({
            'name': 'Document Employee',
            'expire_date': date(2024, 8, 31),
            'type_id': self.test_document_type.id,
            'employee_id': self.employee_employee.id
        })
        # Admin creates a document for manager
        self.test_manager_document = self.env['employee.document'].create({
            'name': 'Document Admin',
            'expire_date': date(2025, 8, 31),
            'type_id': self.test_document_type.id,
            'employee_id': self.employee_manager.id
        })

    def test_01_security_rule_document_type(self):
        """
            Test security rule on group 'base.group_user'
            1) Access rights:
                Model            Read    Create    Update    Unlink
                Document Type      1        0        0        0
                Document           1        1        1        1
            2) Access rules:
                model:            employee.document
                domain_force:   ('employee_id.user_id.id','=',user.id)
                perm_read:        eval="1"
                perm_create       eval="1"
                perm_write        eval="1"
                perm_unlink       eval="0"
        """
        
        self.user_employee.write({'groups_id': [(6, 0, [self.env.ref('base.group_user').id])]})
        
        # ----------------------> Test access on DOCUMENT TYPE <----------------------- #

        # Read: yes
        employee_document_type_list = self.env['employee.document.type'].with_user(self.user_employee).search([])
        self.assertEqual(
            len(employee_document_type_list),
            5,
            "Expect: employee can read all 5 document types: 4 from demo + 1 just created."
        )
        # Create: no
        with self.assertRaises(AccessError):
            self.env['employee.document.type'].with_user(self.user_employee).create({
                'name': 'Test Document Type Failed Case',
                'type': 'others',
                'kept_by': 'employee',
                'return_upon_termination': True,
                'description': 'Other type of document',
                'days_to_notify': 30
            })
        # Write: no
        with self.assertRaises(AccessError):
            self.test_document_type.with_user(self.user_employee).write({'days_to_notify': 10})
        # unlink: no
        with self.assertRaises(AccessError):
            self.test_document_type.with_user(self.user_employee).unlink()

    def test_01_security_rule_document(self):
        """
            Test security rule on group 'base.group_user'
            1) Access rights:
                Model            Read    Create    Update    Unlink
                Document Type      1        0        0        0
                Document           1        1        1        1
            2) Access rules:
                model:            employee.document
                domain_force:   ('employee_id.user_id.id','=',user.id)
                perm_read:        eval="1"
                perm_create       eval="1"
                perm_write        eval="1"
                perm_unlink       eval="0"
        """
        
        self.user_employee.write({'groups_id': [(6, 0, [self.env.ref('base.group_user').id])]})
        
        # -------------------------> Test access on DOCUMENT <------------------------- #
        
        # Create
        self.env['employee.document'].with_user(self.user_employee).create({
            'name': 'Employee can only create document for himself / herself.',
            'expire_date': date(2025, 8, 31),
            'type_id': self.test_document_type.id,
            'employee_id': self.employee_employee.id,
        })
        with self.assertRaises(AccessError):
            self.env['employee.document'].with_user(self.user_employee).create({
                'name': 'Employee cannot create document for other.',
                'expire_date': date(2025, 8, 31),
                'type_id': self.test_document_type.id,
                'employee_id': self.employee_manager.id,
            })
        # Read
        employee_document_list = self.env['employee.document'].with_user(self.user_employee).search([])
        self.assertEqual(
            len(employee_document_list),
            2,
            "Expect: employee can read all 2 documents: 1 of admin + 1 of employee"
        )
        # Write
        self.test_employee_document.with_user(self.user_employee).write({'return_upon_termination': False})
        with self.assertRaises(AccessError):
            self.test_manager_document.with_user(self.user_employee).write({'return_upon_termination': False})
        # Unlink
        with self.assertRaises(AccessError):
            self.test_employee_document.with_user(self.user_employee).unlink()
            self.test_manager_document.with_user(self.user_employee).unlink()
        
    def test_02_security_rule_document_type(self):
        """
            Test security rule on group 'hr.group_hr_user'
            1) Access rights:
                Model            Read    Write    Update    Unlink
                Document Type      1        1        1        0
                Document           1        1        1        1
            2) Access rules:
                Can read, create, update, unlink any document
                Can read, create, update any document type, but not unlink
        """
        self.user_employee.write({'groups_id': [(6, 0, [self.env.ref('hr.group_hr_user').id])]})
        
        # ----------------------> Test access on DOCUMENT TYPE <----------------------- #

        # Create: yes
        new_type_01 = self.env['employee.document.type'].with_user(self.user_employee).create({
            'name': 'Test Document Type Case 01',
            'type': 'others',
            'kept_by': 'employee',
            'return_upon_termination': True,
            'description': 'Test Document Type Create Successfully Case',
            'days_to_notify': 30
        })
        # Read: yes
        employee_document_type_list = self.env['employee.document.type'].with_user(self.user_employee).search([])
        self.assertEqual(
            len(employee_document_type_list),
            6,
            "Expect: employee can read all 6 document types: 4 from demo + 2 just created."
        )
        # Write: yes
        self.test_document_type.with_user(self.user_employee).write({'days_to_notify': 10})
        new_type_01.with_user(self.user_employee).write({'days_to_notify': 10})
        # unlink: no
        with self.assertRaises(AccessError):
            new_type_01.with_user(self.user_employee).unlink()
            self.test_document_type.with_user(self.user_employee).unlink()
        
    def test_02_security_rule_document(self):
        """
            Test security rule on group 'hr.group_hr_user'
            1) Access rights:
                Model            Read    Write    Update    Unlink
                Document Type      1        1        1        0
                Document           1        1        1        1
            2) Access rules:
                Can read, create, update, unlink any document
                Can read, create, update any document type, but not unlink
        """
        self.user_employee.write({'groups_id': [(6, 0, [self.env.ref('hr.group_hr_user').id])]})
            
        # -------------------------> Test access on DOCUMENT <------------------------- #
        
        # Create
        self.env['employee.document'].with_user(self.user_employee).create({
            'name': 'HR Employee can create document for himself / herself.',
            'expire_date': date(2025, 8, 31),
            'type_id': self.test_document_type.id,
            'employee_id': self.employee_employee.id,
        })
        self.env['employee.document'].with_user(self.user_employee).create({
            'name': 'HR Employee can also create document for other.',
            'expire_date': date(2025, 8, 31),
            'type_id': self.test_document_type.id,
            'employee_id': self.employee_manager.id,
        })
        # Read
        employee_document_list = self.env['employee.document'].with_user(self.user_employee).search([])
        self.assertEqual(
            len(employee_document_list),
            4,
            "Expect: employee can read all 2 documents: 2 of admin + 2 of employee"
        )
        # Write
        self.test_employee_document.with_user(self.user_employee).write({'return_upon_termination': False})
        self.test_manager_document.with_user(self.user_employee).write({'return_upon_termination': False})
        # Unlink
        self.test_employee_document.with_user(self.user_employee).unlink()
        self.test_manager_document.with_user(self.user_employee).unlink()
        
    def test_03_security_rule_document_type(self):
        """
            Test security rule on group 'hr.group_hr_manager'
            1) Access rights:
                Model            Read    Write    Update    Unlink
                Document Type      1        1        1        1
                Document           1        1        1        1
            2) Access rules:
                Can everything
        """
        
        self.user_employee.write({'groups_id': [(6, 0, [self.env.ref('hr.group_hr_manager').id])]})
        
        # ----------------------> Test access on DOCUMENT TYPE <----------------------- #

        # Create
        # By himself/herself
        new_type_01 = self.env['employee.document.type'].with_user(self.user_employee).create({
            'name': 'Test Document Type Case 0101',
            'type': 'others',
            'kept_by': 'employee',
            'return_upon_termination': True,
            'description': 'Test Document Type Create Successfully Case',
            'days_to_notify': 30
        })
        # By other
        new_type_02 = self.env['employee.document.type'].create({
            'name': 'Test Document Type Case 0102',
            'type': 'others',
            'kept_by': 'employee',
            'return_upon_termination': True,
            'description': 'Test Document Type Create Successfully Case',
            'days_to_notify': 30
        })
        # Read
        employee_document_type_list = self.env['employee.document.type'].with_user(self.user_employee).search([])
        self.assertEqual(
            len(employee_document_type_list),
            7,
            "Expect: employee can read all 6 document types: 4 from demo + 2 just created."
        )
        # Write
        self.test_document_type.with_user(self.user_employee).write({'days_to_notify': 10})
        new_type_01.with_user(self.user_employee).write({'days_to_notify': 10})
        # unlink:
        new_type_01.with_user(self.user_employee).unlink()
        new_type_02.with_user(self.user_employee).unlink()

    def test_03_security_rule_document(self):
        """
            Test security rule on group 'hr.group_hr_manager'
            1) Access rights:
                Model            Read    Write    Update    Unlink
                Document Type      1        1        1        1
                Document           1        1        1        1
            2) Access rules:
                Can everything
        """
        
        self.user_employee.write({'groups_id': [(6, 0, [self.env.ref('hr.group_hr_manager').id])]})

        # -------------------------> Test access on DOCUMENT <------------------------- #
        
        # Create
        self.env['employee.document'].with_user(self.user_employee).create({
            'name': 'HR Employee can create document for himself / herself.',
            'expire_date': date(2025, 8, 31),
            'type_id': self.test_document_type.id,
            'employee_id': self.employee_employee.id,
        })
        self.env['employee.document'].with_user(self.user_employee).create({
            'name': 'HR Employee can also create document for other.',
            'expire_date': date(2025, 8, 31),
            'type_id': self.test_document_type.id,
            'employee_id': self.employee_manager.id,
        })
        # Read
        employee_document_list = self.env['employee.document'].with_user(self.user_employee).search([])
        self.assertEqual(
            len(employee_document_list),
            4,
            "Expect: employee can read all 2 documents: 2 of admin + 2 of employee"
        )
        # Write
        self.test_employee_document.with_user(self.user_employee).write({'return_upon_termination': False})
        self.test_manager_document.with_user(self.user_employee).write({'return_upon_termination': False})
        # Unlink
        self.test_employee_document.with_user(self.user_employee).unlink()
        self.test_manager_document.with_user(self.user_employee).unlink()
