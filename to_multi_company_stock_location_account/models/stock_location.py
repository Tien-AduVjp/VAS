from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class StockLocation(models.Model):
    _inherit = 'stock.location'

    # override label to avoid warning that have the same label
    valuation_in_account_id = fields.Many2one(string='Default Stock Valuation Account (Incoming)')
    valuation_out_account_id = fields.Many2one(string='Default Stock Valuation Account (Outgoing)')

    property_valuation_in_account_id = fields.Many2one(
        'account.account', 'Stock Valuation Account (Incoming)',
        domain=[('internal_type', '=', 'other'), ('deprecated', '=', False)], company_dependent=True,
        help="Used for real-time inventory valuation. When set on a virtual location (non internal type), "
             "this account will be used to hold the value of products being moved from an internal location "
             "into this location, instead of the generic Stock Output Account set on the product. "
             "This has no effect for internal locations.")
    property_valuation_out_account_id = fields.Many2one(
        'account.account', 'Stock Valuation Account (Outgoing)',
        domain=[('internal_type', '=', 'other'), ('deprecated', '=', False)], company_dependent=True,
        help="Used for real-time inventory valuation. When set on a virtual location (non internal type), "
             "this account will be used to hold the value of products being moved out of this location "
             "and into an internal location, instead of the generic Stock Output Account set on the product. "
             "This has no effect for internal locations.")

    @api.model
    def _update_exist_location(self):
        AccountAccount = self.env['account.account']
        PropertyObj = self.env['ir.property']
        IrModelField = self.env['ir.model.fields']
        company_ids = self.env['res.company'].search([('chart_template_id', '!=', False)])

        for localtion in self.search([('usage', 'in', ('inventory','production'))]):
            if localtion.valuation_in_account_id:
                for company_id in company_ids:
                    fields_id = IrModelField.search([
                        ('name', '=', 'property_valuation_in_account_id'),
                        ('model', '=', 'stock.location'),
                        ('relation', '=', 'account.account')], limit=1)
                    properties = PropertyObj.search([
                        ('name', '=', 'property_valuation_in_account_id'),
                        ('fields_id', '=', fields_id.id),
                        ('company_id', '=', company_id.id)])
                    if not properties:
                        account_id = AccountAccount.search([
                            ('company_id', '=', company_id.id),
                            ('code', '=', localtion.valuation_in_account_id.code)], limit=1)
                        if account_id:
                            vals = {'name': 'property_valuation_in_account_id',
                                  'fields_id': fields_id.id,
                                  'company_id': company_id.id,
                                  'value': 'account.account,' + str(account_id.id)}
                            property_id = PropertyObj.create(vals)
                            _logger.info("Property %s (ID: %s) has been created for the company %s", property_id.name, property_id.id, company_id.name)
            if localtion.valuation_out_account_id:
                for company_id in company_ids:
                    fields_id = IrModelField.search([
                        ('name', '=', 'property_valuation_out_account_id'),
                        ('model', '=', 'stock.location'),
                        ('relation', '=', 'account.account')], limit=1)
                    properties = PropertyObj.search([
                        ('name', '=', 'property_valuation_out_account_id'),
                        ('fields_id', '=', fields_id.id),
                        ('company_id', '=', company_id.id)])
                    if not properties:
                        account_id = AccountAccount.search([
                            ('company_id', '=', company_id.id),
                            ('code', '=', localtion.valuation_out_account_id.code)], limit=1)
                        if account_id:
                            vals = {'name': 'property_valuation_out_account_id',
                                  'fields_id': fields_id.id,
                                  'company_id': company_id.id,
                                  'value': 'account.account,' + str(account_id.id)}
                            property_id = PropertyObj.create(vals)
                            _logger.info("Property %s (ID: %s) has been created for the company %s", property_id.name, property_id.id, company_id.name)
