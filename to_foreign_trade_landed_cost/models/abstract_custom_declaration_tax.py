from odoo import models


class CustomDeclarationTax(models.AbstractModel):
    _inherit = "abstract.custom.declaration.tax"
    
    def _prepare_landed_cost_line_data(self, landed_cost):
        import_tax_cost_product = self.env.ref('to_foreign_trade_landed_cost.to_product_product_import_tax_cost')
        accounts_data = import_tax_cost_product.product_tmpl_id.sudo().get_product_accounts()
        account = accounts_data['stock_input']
        return {
                'product_id': import_tax_cost_product.id,
                'name': self.name + ': ' + self.product_id.name,
                'split_method': 'by_quantity',
                'price_unit': self.amount,
                'cost_id': landed_cost.id,
                'account_id': account.id
            }
    
    def _prepare_landed_cost_adjustment_line_data(self, landed_cost_line):
        move = self.custom_declaration_line_id.stock_move_id
        vals = {
                'product_id': self.product_id.id,
                'name': self.name + ': ' + self.product_id.name,
                'quantity': self.qty,
                'additional_landed_cost': self.amount,
                'cost_id': landed_cost_line.cost_id.id,
                'cost_line_id': landed_cost_line.id,
                'weight': 0,
                'volume': 0,
            }
        if move:
            vals.update({
                'move_id': move.id,
                'quantity': move.product_qty,
                'former_cost': sum(move.stock_valuation_layer_ids.mapped('value')),
                'weight': move.product_id.weight * move.product_qty,
                'volume': move.product_id.volume * move.product_qty,
                })
        return vals
    
