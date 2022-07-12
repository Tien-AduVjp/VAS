from odoo.tests import TransactionCase
from odoo.tests.common import tagged
from odoo.exceptions import UserError

@tagged('post_install', '-at_install')
class TestCheckUniqueVatSettingsTrue(TransactionCase):

    def setUp(self):
        TransactionCase.setUp(self)
        # super(TestCheckUniqueVatSettingsTrue, self).setUp()

        self.env.company.check_unique_vat = True

        self.partner_individual_1 = self.env['res.partner'].create({
            'name': 'Monkey D. Minhky',
            'company_type': 'person',
            'vat': 'P_VT1',
        })
        self.partner_company_1 = self.env['res.partner'].create({
            'name': 'One Piece A/S',
            'company_type': 'company',
            'vat': 'C_VT1',
        })

    def test_02_create_partner_different_vat(self):
        partner_individual_2 = self.env['res.partner'].create({
            'name': 'Monkey D. Minhky 2',
            'company_type': 'person',
            'vat': 'P_VT2',
        })
        partner_company_2 = self.env['res.partner'].create({
            'name': 'Leaf Company',
            'company_type': 'company',
            'vat': 'C_VT2',
        })

        self.assertTrue(bool(partner_individual_2))
        self.assertTrue(bool(partner_company_2))

    def test_03_create_partner_duplicated_vat(self):
        self.assertEqual(self.partner_individual_1.vat, 'P_VT1')

        with self.assertRaises(UserError):
            self.env['res.partner'].create({
                'name': 'Monkey D. Minhky 3',
                'company_type': 'person',
                'vat': 'P_VT1',
            })

        with self.assertRaises(UserError):
            self.env['res.partner'].create({
                'name': 'Leaf Company',
                'company_type': 'company',
                'vat': 'C_VT1',
            })


    def test_04_duplicate_partner_individual_not_has_company(self):
        # don't copy vat
        partner = self.partner_individual_1.copy()
        self.assertFalse(partner.vat)

    def test_05_duplicate_partner_individual_has_company(self):
        partner_individual_5 = self.env['res.partner'].create({
            'name': 'Monkey D. Minhky 5',
            'company_type': 'person',
            'parent_id': self.partner_company_1.id,
        })
        duplicated_partner = partner_individual_5.copy()

        self.assertTrue(bool(duplicated_partner))

    def test_06_create_partner_existed_vat_already_archived(self):
        # archive partner company 1
        self.partner_company_1.toggle_active()
        self.assertFalse(self.partner_company_1.active)

        with self.assertRaises(UserError):
            self.env['res.partner'].create({
                'name': 'Monkey D. Minhky 6',
                'company_type': 'person',
                'vat': 'P_VT1',
            })

    def test_07_update_partner_individual(self):
        """
            Create a partner and assign to a company
            On editing this partner:
                If remove company but not remove tax code, an UserError will be raised
        """

        partner_individual_7 = self.env['res.partner'].create({
            'name': 'Monkey D. Minhky 5',
            'company_type': 'person',
            'parent_id': self.partner_company_1.id,
        })

        self.assertEqual(
            partner_individual_7.vat,
            self.partner_company_1.vat,
            "Error testing: partner 7 should have the same VAT as company 1.",
        )

        with self.assertRaises(UserError):
            partner_individual_7.write({'parent_id': False})

    def test_09_create_multi_partners_with_no_existed_vat(self):
        """
            Create multi partners using code, not on the User Interface
        """
        partners = self.env['res.partner'].create([
            {'name': 'Monkey D. Minhky 9 1', 'company_type': 'person', 'vat': 'P_VT001'},
            {'name': 'Monkey D. Minhky 9 2', 'company_type': 'person', 'vat': 'P_VT002'},
            {'name': 'Monkey D. Minhky 9 3', 'company_type': 'company', 'vat': 'P_VT003'},
        ])

        self.assertEqual(len(partners), 3, "Error testing: recordset 'partners' should consist of 3 records.")

    def test_10_create_multi_partners_same_company_with_duplicated_vat(self):
        """
            Create multi partners using code, not on the User Interface
        """

        partners = self.env['res.partner'].create([
            {'name': 'Monkey D. Minhky 10 1', 'vat': 'P_VT001', 'parent_id': self.partner_company_1.id},
            {'name': 'Monkey D. Minhky 10 2', 'vat': 'P_VT001', 'parent_id': self.partner_company_1.id},
            {'name': 'Monkey D. Minhky 10 3', 'vat': 'P_VT001', 'parent_id': self.partner_company_1.id},
        ])

        self.assertEqual(len(partners), 3, "Error testing: recordset 'partners' should consist of 3 records.")

    def test_11_create_multi_partners_exeptional_case(self):
        """
            Create multi partners using code, not on the User Interface
            Purpose:
                create multi partners with VATs, which all are identical, but all are not found in the Database yet
        """
        with self.assertRaises(UserError):
            self.env['res.partner'].create([
                {'name': 'Monkey D. Minhky 11 1', 'vat': 'P_VT001'},
                {'name': 'Monkey D. Minhky 11 2', 'vat': 'P_VT001'},
                {'name': 'Monkey D. Minhky 11 3', 'vat': 'P_VTT'},
            ])
