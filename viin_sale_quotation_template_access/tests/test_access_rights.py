from odoo.tests.common import TransactionCase, tagged, Form


@tagged('access_rights')
class TestAccessRights(TransactionCase):
    
    def setUp(self):
        super(TestAccessRights, self).setUp()
        context_no_mail = {'no_reset_password': True, 'mail_create_nosubscribe': True, 'mail_create_nolog': True}
        group_user = self.env.ref('base.group_user')
        group_sale_quotation_template_all = self.env.ref('viin_sale_quotation_template_access.group_sale_quotation_template_all')
        self.user_access_quotation_template = self.env['res.users'].with_context(context_no_mail).create({
            'name': 'User Access Quotation Template',
            'login': 'user_access_quotation_template',
            'email': 'user@example.viindoo.com',
            'notification_type': 'email',
            'groups_id': [(6, 0, [group_user.id, group_sale_quotation_template_all.id])],
        })
        self.product_1 = self.env.ref('product.product_product_5')
        self.product_2 = self.env.ref('product.product_product_6')

    def test_user_access_quotation_template(self):
        # Create quotation template
        quotation_template_form = Form(self.env['sale.order.template'].with_user(self.user_access_quotation_template))
        quotation_template_form.name = 'Quotation Template'
        with quotation_template_form.sale_order_template_line_ids.new() as template_line:
            template_line.product_id = self.product_1
        with quotation_template_form.sale_order_template_option_ids.new() as template_option:
            template_option.product_id = self.product_2
        quotation_template_test = quotation_template_form.save()
        
        # Read quotation template
        quotation_template_test.with_user(self.user_access_quotation_template).read()
        # Update quotation, template line, template option
        quotation_template_test.write({'name': 'Quotation Template Test'})
        quotation_template_test.sale_order_template_line_ids.write({'product_uom_qty': 2.0})
        quotation_template_test.sale_order_template_option_ids.write({'quantity': 2.0})
        # Remove template lines, template options, quotation template 
        quotation_template_test.sale_order_template_line_ids.unlink()
        quotation_template_test.sale_order_template_option_ids.unlink()
        quotation_template_test.unlink()
