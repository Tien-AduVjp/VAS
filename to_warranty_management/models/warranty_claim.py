from dateutil.relativedelta import relativedelta

from odoo import api, models, fields, _
from odoo.exceptions import ValidationError, UserError


class WarrantyClaim(models.Model):
    _name = "warranty.claim"
    _description = "Warranty Claim"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Order Reference', required=True, index=True, copy=False, default='New')
    product_id = fields.Many2one('product.product', string='Products', required=True, readonly=False, states={'investigation': [('readonly', True)],
                                                                                                              'disclaimed': [('readonly', True)],
                                                                                                              'confirmed': [('readonly', True)],
                                                                                                              'done': [('readonly', True)],
                                                                                                              'cancelled': [('readonly', True)]})
    partner_id = fields.Many2one('res.partner', string='Partner', required=True, readonly=False, states={'investigation': [('readonly', True)],
                                                                                                         'disclaimed': [('readonly', True)],
                                                                                                         'confirmed': [('readonly', True)],
                                                                                                         'done': [('readonly', True)],
                                                                                                         'cancelled': [('readonly', True)]})
    description = fields.Text(string='Warranty Reason')
    state = fields.Selection([
        ('draft', "Draft"),
        ('investigation', "Investigated"),
        ('disclaimed', 'Disclaimed'),
        ('confirmed', "Confirmed"),
        ('done', "Done"),
        ('cancelled', "Cancelled"),
    ], default='draft', string='Status', tracking=True)
    warranty_claim_policy_ids = fields.One2many('warranty.claim.policy', 'warranty_claim_id', string="Warranty Policy",
                                                readonly=False, states={'investigation': [('readonly', True)],
                                                                        'disclaimed': [('readonly', True)],
                                                                        'confirmed': [('readonly', True)],
                                                                        'done': [('readonly', True)],
                                                                        'cancelled': [('readonly', True)]}, 
                                                compute='_compute_warranty_claim_policy_ids', store=True, copy=True)
    user_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user, tracking=True)
    type = fields.Selection([('customer', 'Customer'),
                             ('vendor', 'Vendor')], string="Partner Type", required=True, default='customer', readonly=False,
                             states={'investigation': [('readonly', True)],
                                     'disclaimed': [('readonly', True)],
                                     'confirmed': [('readonly', True)],
                                     'done': [('readonly', True)],
                                     'cancelled': [('readonly', True)]})
    warranty_start_date = fields.Date(string='Warranty Start Date', tracking=True,
                                      compute='_compute_warranty_start_date', inverse='_set_warranty_start_date', store=True,
                                      readonly=False, states={'disclaimed': [('readonly', True)],
                                                              'confirmed': [('readonly', True)],
                                                              'done': [('readonly', True)],
                                                              'cancelled': [('readonly', True)]})
    warranty_period = fields.Integer('Warranty period (months)', compute='_compute_warranty_period', inverse='_set_warranty_period',
                                     store=True, tracking=True, readonly=False, states={'investigation': [('readonly', True)],
                                                                                        'disclaimed': [('readonly', True)],
                                                                                        'confirmed': [('readonly', True)],
                                                                                        'done': [('readonly', True)],
                                                                                        'cancelled': [('readonly', True)]})
    warranty_expiration_date = fields.Date(string='Warranty Expiration Date', compute='_compute_warranty_expiration_date', store=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company, readonly=False, states={'investigation': [('readonly', True)],
                                                                                                                              'disclaimed': [('readonly', True)],
                                                                                                                              'confirmed': [('readonly', True)],
                                                                                                                              'done': [('readonly', True)],
                                                                                                                              'cancelled': [('readonly', True)]})
    date_claim = fields.Date(string='Date Claim', default=fields.date.today(), readonly=False, states={'investigation': [('readonly', True)],
                                                                                                       'disclaimed': [('readonly', True)],
                                                                                                       'confirmed': [('readonly', True)],
                                                                                                       'done': [('readonly', True)],
                                                                                                       'cancelled': [('readonly', True)]})

    @api.depends('product_id')
    def _compute_warranty_period(self):
        for r in self:
            if not r.warranty_period:
                r.warranty_period = r.product_id.warranty_period

    def _set_warranty_period(self):
        pass

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('warranty.claim') or '/'
        return super(WarrantyClaim, self).create(vals_list)
    
    def unlink(self):
        for r in self:
            if r.state not in ('draft', 'cancelled'):
                raise UserError(_("You can not delete a warranty claim, which is not in draft or cancelled state."))
        return super(WarrantyClaim, self).unlink()

    @api.constrains('warranty_claim_policy_ids')
    def _check_constrains_milestone(self):
        for r in self:
            policy_for_sale_ids = r.mapped('warranty_claim_policy_ids').filtered(lambda p: p.apply_to == 'sale')
            policy_for_purchase_ids = r.warranty_claim_policy_ids - policy_for_sale_ids
            sale_categ_ids = policy_for_sale_ids.mapped('product_milestone_id.uom_id.category_id')
            purchase_categ_ids = policy_for_purchase_ids.mapped('product_milestone_id.uom_id.category_id')

            if len(policy_for_sale_ids) > len(sale_categ_ids) or len(policy_for_purchase_ids) > len(purchase_categ_ids):
                raise ValidationError(_("You can not create more milestone that have the same category with an existing milestone"))

    def action_draft(self):
        return self.write({'state':'draft'})

    def action_investigation(self):
        return self.write({'state':'investigation'})

    def action_disclaimed(self):
        return self.write({'state':'disclaimed'})

    def action_confirm(self):
        for r in self:
            if not r.warranty_start_date:
                raise UserError(_("You can not confirm a warranty claim, which doesn't have warranty start date."))
            elif r.warranty_expiration_date:
                if any(warranty_claim_policy_id.state == 'not_ok' for warranty_claim_policy_id in r.mapped('warranty_claim_policy_ids')) or \
                fields.Date.from_string(r.warranty_expiration_date) < r.date_claim:
                    if not self._context.get('call_from_wizard', False):
                        view = self.env.ref('to_warranty_management.action_confirm_wizard_form_view')
                        ctx = dict(self._context or {})
                        ctx.update({'default_warranty_claim_id': r.id})
                        return {
                            'type': 'ir.actions.act_window',
                            'view_mode': 'form',
                            'res_model': 'action.confirm.wizard',
                            'views': [(view.id, 'form')],
                            'view_id': view.id,
                            'target': 'new',
                            'context': ctx,
                            }
        self.write({'state':'confirmed'})

    def action_cancelled(self):
        return self.write({'state': 'cancelled'})

    def action_done(self):
        return self.write({'state':'done'})

    @api.depends('product_id', 'type')
    def _compute_warranty_claim_policy_ids(self):
        for r in self:
            warranty_claim_policy_ids = r.env['warranty.claim.policy']
            if r.type == 'vendor':
                warranty_policy_ids = r.product_id.warranty_policy_ids.filtered(lambda l: l.apply_to == 'purchase')
            elif r.type == 'customer':
                warranty_policy_ids = r.product_id.warranty_policy_ids.filtered(lambda l: l.apply_to == 'sale')
            else:
                warranty_policy_ids = False
            if warranty_policy_ids:
                for warranty_policy_id in warranty_policy_ids:
                    warranty_claim_policy_ids += warranty_claim_policy_ids.new(warranty_policy_id._prepare_warranty_claim_policy_data())
            r.warranty_claim_policy_ids = warranty_claim_policy_ids

    @api.depends('warranty_start_date', 'warranty_period')
    def _compute_warranty_expiration_date(self):
        for r in self:
            if r.warranty_start_date and r.warranty_period:
                r.warranty_expiration_date = fields.Date.from_string(r.warranty_start_date) + relativedelta(months=r.warranty_period)

    def _compute_warranty_start_date(self):
        """
        This method is for future inheritance. For example, Warranty Purchase & Warranty Sale could implement this.
        """
        for r in self:
            r.warranty_start_date = False

    def _set_warranty_start_date(self):
        pass
