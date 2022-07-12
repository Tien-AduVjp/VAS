from odoo import models, _
from odoo.exceptions import UserError


class stock_move(models.Model):
    _inherit = 'stock.move'

    def _action_done(self, cancel_backorder=False):
        for record in self:
            if record.location_id.is_custom_clearance:
                # Do not stop return to vendors
                if record.location_id.id in record.move_orig_ids.mapped('location_dest_id').ids and record.location_dest_id.usage == 'supplier':
                    continue

                # We just need to consider "done oringal moves" only
                # This will help not stop users from receiving partially fron the custom zones
                for org_move in record.move_orig_ids.filtered(lambda m: m.state=='done'):

                    if not org_move.picking_id.custom_declaration_import_ids and not org_move.picking_id.custom_declaration_export_ids:
                        raise UserError(_('You cannot process the transfer %s while its original transfer %s requires a custom declaration document.'
                                          ' Please create a custom declaration document for that transfer.')
                                        % (record.picking_id.name, org_move.picking_id.name))
                    else:
                        if org_move.picking_id.custom_declaration_import_ids:
                            for custom_dec in org_move.picking_id.custom_declaration_import_ids:
                                if custom_dec.state not in ['confirm', 'done']:
                                    raise UserError(_('You cannot process the transfer %s while its original transfer %s \'s custom declaration document %s'
                                                      ' has not been confirmed by the custom authority. Please get it confirmed first!')
                                                    % (record.picking_id.name, org_move.picking_id.name, custom_dec.name))
                        elif org_move.picking_id.custom_declaration_export_ids:
                            for custom_dec in org_move.picking_id.custom_declaration_export_ids:
                                if custom_dec.state not in ['confirm', 'done']:
                                    raise UserError(_('You cannot process the transfer %s while its original transfer %s \'s custom declaration document %s'
                                                      ' has not been confirmed by the custom authority. Please get it confirmed first!')
                                                    % (record.picking_id.name, org_move.picking_id.name, custom_dec.name))

        res = super(stock_move, self)._action_done(cancel_backorder)
        return res

    def _prepare_custom_declaration_import_line_data(self, total_cost, total_cost_currency, qty):
        return {
            'product_id': self.product_id.id,
            'qty': qty,
            'tax_ids': [(6, 0, [x.id for x in self.product_id.import_tax_ids])],
            'stock_move_id': self.id,
            'account_analytic_id': self.purchase_line_id.account_analytic_id.id,
            'analytic_tag_ids': [(6, 0, self.purchase_line_id.analytic_tag_ids.ids)],
            'total_cost_currency': total_cost_currency,
            'total_cost': total_cost
        }
        
    def _prepare_custom_declaration_export_line_data(self, total_cost, total_cost_currency, qty, sale_line_id):
        return {
            'product_id': self.product_id.id,
            'qty': qty,
            'tax_ids': [(6, 0, self.product_id.export_tax_ids.ids)],
            'sale_order_line_id': sale_line_id.id,
            'account_analytic_id': sale_line_id.order_id.analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, sale_line_id.analytic_tag_ids.ids)],
            'total_cost_currency': total_cost_currency,
            'total_cost': total_cost
        }
