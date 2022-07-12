from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class CustomDeclarationLineExtraExpense(models.Model):
    _name = 'custom.declaration.line.extra.expense'
    _description = 'Custom Clearance Request Line Extra Expense'

    custom_declaration_import_id = fields.Many2one('custom.declaration.import', string="Custom Clearance Request (Import)", ondelete='cascade')
    currency_id = fields.Many2one('res.currency', string='Currency on Custom Declaration',
                                  related='custom_declaration_import_id.currency_id', store=True)
    expense_value = fields.Monetary(string='Expense Value', currency_field='currency_id', required=True)
    product_id = fields.Many2one('product.product', string='Expense', required=True,
                                 domain=[('type', '=', 'service')])
    applied_product_ids = fields.Many2many('product.product', string='Applied Products',
                                   domain="[('id', 'in', available_product_ids)]",
                                   help="Leave empty if you want apply for all product on custom declaration.")
    split_method = fields.Selection([
        ('equal', 'Equal'),
        ('by_quantity', 'By Quantity'),
        ('by_cost', 'By Taxable Value')],
        string='Split Method',
        required=True,
        help="Equal : Expense will be equally divided.\n"
             "By Quantity : Expense will be divided according to product's quantity.\n"
             "By Taxable Value : Expense will be divided according to product's currency taxable value.")
    available_product_ids = fields.Many2many('product.product', compute='_compute_available_products',
                                             string='Available Products',
                                             help="Technical field to filter products based on products of custom declaration line")

    @api.constrains('applied_product_ids', 'split_method')
    def _check_applied_product_ids(self):
        for r in self:
            if r.split_method == 'by_quantity' and len(r.applied_product_ids.uom_id.category_id) > 1:
                raise ValidationError(_("You can't select applied products, which has different UoM categories."))

    @api.constrains('expense_value')
    def _check_expense_value(self):
        for r in self:
            if r.expense_value < 0:
                raise ValidationError(_("You can't set expense value as negative."))

    @api.depends('custom_declaration_import_id.custom_declaration_line_ids')
    def _compute_available_products(self):
        for r in self:
            r.available_product_ids = r.custom_declaration_import_id.custom_declaration_line_ids.product_id

    @api.onchange('applied_product_ids', 'split_method')
    def _onchange_applied_product_ids(self):
        if self.split_method == 'by_quantity':
            returned_msg = {}
            if len(self.applied_product_ids.uom_id.category_id) > 1:
                returned_msg = {
                    'warning': {
                        'message': _("You can't select split method is `By Quantity`, "
                                     "while applied products has different UoM categories.")
                    }
                }
            elif not self.applied_product_ids and len(self.available_product_ids.uom_id.category_id) > 1:
                returned_msg = {
                    'warning': {
                        'message': _("You can't select split method is `By Quantity`, "
                                     "while products on declaration lines has different UoM categories.")
                    }
                }
            if returned_msg:
                self.split_method = self._origin.split_method

            return returned_msg

    @api.onchange('expense_value')
    def _onchange_expense_value(self):
        if self.expense_value < 0:
            self.expense_value = self._origin.expense_value
            return {
                'warning': {
                    'message': _("You can't set expense value as negative.")
                }
            }

    def _check_valid_expense(self):
        for r in self:
            if r.split_method == 'by_quantity':
                if len(r.applied_product_ids.uom_id.category_id) > 1 or \
                        (not r.applied_product_ids and len(r.available_product_ids.uom_id.category_id) > 1):
                    return False

            if r.expense_value < 0:
                return False

        return True
