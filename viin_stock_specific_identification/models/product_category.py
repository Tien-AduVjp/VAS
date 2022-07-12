from odoo import fields, models, _
from odoo.exceptions import UserError


class ProductCategory(models.Model):
    _inherit = 'product.category'

    property_cost_method = fields.Selection(
        selection_add=[('specific_identification', 'Specific Identification')],
        ondelete={'specific_identification': lambda recs: recs.write({'property_cost_method': 'fifo'})},
        help="""Standard Price: The products are valued at their standard cost defined on the product.
        Average Cost (AVCO): The products are valued at weighted average cost.
        First In First Out (FIFO): The products are valued supposing those that enter the company first will also leave it first.
        Specific Identification: The products are valued at their identified cost.
        """)

    def write(self, vals):
        if vals.get('property_cost_method', '') == 'specific_identification':
            self._can_change_cost_method()
        return super(ProductCategory, self).write(vals)

    def _can_change_cost_method(self):
        """To prevent to change the property_cost_method to specific_identification if:
        any product that has not been enabled tracking by lot/serial
        or any product that has quantity_svl > 0.
        """
        product = self.env['product.product'].search([('type', '=', 'product'),
                                                      ('categ_id', 'in', self.ids),
                                                      ('tracking', '=', 'none')], limit=1)
        if product:
            raise UserError(_("Tracking by a lot/serial number must be applied for product '%s' that "
                              "belongs to category '%s'!") % (product.name, product.categ_id.name))

        products = self.env['product.product'].search([('type', '=', 'product'),
                                                       ('categ_id', 'in', self.ids)])\
                                              .filtered(lambda p: p.quantity_svl > 0)

        for r in self:
            for product in products.filtered(lambda prd: prd.categ_id == r):
                raise UserError(_("You cannot change costing method of product category '%s' to 'Specific Identification'.\n"
                                  "Because quantity of product '%s' still in stock.\n"
                                  "Please follow the instructions below: \n"
                                  "1. Set inventory valuation as Manual in this product category to avoid recording your inventory valuation in your accounting books.\n"
                                  "2. Using the inventory adjustment to set product quantity to zero before changing.\n"
                                  "3. Changing costing method to 'Specific Identification'.\n"
                                  "4. Using the inventory adjustment to recreate product quantity.\n"
                                  "5. Set inventory valuation as Automated in this product category if you need.")
                                  % (r.name, product.name))
