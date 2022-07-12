from odoo.tests.common import Form, tagged
from odoo.exceptions import UserError, ValidationError
from odoo.addons.to_loan_management.tests.common import TestLoanCommon


@tagged('post_install', '-at_install')
class TestLoanProduct(TestLoanCommon):

    def test_product_form(self):
        product_form = Form(self.env['product.product'])
        product_form.name = 'khaihoan'
        product_form.type = 'consu'
        product_form.is_loan = True
        product_consu = product_form.save()
        self.assertRecordValues(product_consu,
                                [{'type': 'service', 'categ_id': self.product_category_loan_interest.id}])

    def test_set_loan_product_to_consu(self):
        with self.assertRaises(UserError):
            self.product_loan.write({'type': 'consu'})

    def test_set_loan_product(self):
        product_loan = Form(self.product_loan).save()
        with self.assertRaises(ValidationError):
            product_loan.write({'is_loan': False})
