from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SuppliferInfo(models.Model):
    _name = "product.supplierinfo"
    _inherit = ['product.supplierinfo', 'mail.thread', 'mail.activity.mixin']

    STATES = [
        ('confirmed', 'Confirmed'),
        ('locked', 'Locked'),
        ]

    name = fields.Many2one(tracking=True)
    product_name = fields.Char(tracking=True)
    product_code = fields.Char(tracking=True)
    sequence = fields.Integer(tracking=True)
    product_uom = fields.Many2one(tracking=True)
    min_qty = fields.Float(tracking=True)
    price = fields.Float(tracking=True)
    currency_id = fields.Many2one(tracking=True)
    date_start = fields.Date(tracking=True)
    date_end = fields.Date(tracking=True)
    product_id = fields.Many2one(tracking=True)
    product_tmpl_id = fields.Many2one(tracking=True)
    delay = fields.Integer(tracking=True)
    state = fields.Selection(STATES, string='Status', default='confirmed', index=True, readonly=True, copy=False, required=True, tracking=True,
                             help='Confirmed: The pricelist is confirmed and active. The price will be loaded into purchase order lines but still can be changed on the lines\n'
                             'Locked: the pricelist is locked and cannot be changed on purchase order lines if the user is not a purchase manager')

    def action_lock(self):
        self.write({'state':'locked'})

    def action_unlock(self):
        self.write({'state':'confirmed'})

    def unlink(self):
        for r in self:
            if r.state == 'locked':
                raise UserError(_('You are not allowed to delete a pricelist which is in locked state.'
                                  ' Here are some information for the pricelist that cannot be deleted:\n'
                                  'Vendor: %s\n'
                                  'Product: %s\n') % (r.name.name, r.product_tmpl_id.name))
        return super(SuppliferInfo, self).unlink()

    def write(self, vals):
        for r in self:
            if r.state == 'locked' and not r.env.user.has_group('purchase.group_purchase_manager'):
                raise UserError(_('Only Purchase Manager can edit locked vendor pricelist'))
        return super(SuppliferInfo, self).write(vals)

    @api.model
    def create(self, vals):
        if not self.env.user.has_group('purchase.group_purchase_manager'):
            if vals['name'] and vals['product_tmpl_id']:
                existing_locked_pricelist = self.search([
                    ('product_tmpl_id', '=', vals['product_tmpl_id']),
                    ('name', '=', vals['name']),
                    ('state', '=', 'locked')
                    ], limit=1)

                if existing_locked_pricelist:
                    input_prod_tmpl_id = self.env['product.template'].search([('id', '=', vals['product_tmpl_id'])])
                    vendor_id = self.env['res.partner'].search([('id', '=', vals['name'])])
                    raise UserError(_('Creating a new vendor pricelist for product \'%s\' from the vendor \'%s\' is'
                                      ' forbidden while such an existing record is locked.\n'
                                      ' Please contact your Purchase Manager to ask him to unlock all records corresponding'
                                      ' to the product and the vendor before you can create a new one.'
                                      ' Or just ask him to do the job for you!')
                                    % (input_prod_tmpl_id.name, vendor_id.name))

        return super(SuppliferInfo, self).create(vals)

