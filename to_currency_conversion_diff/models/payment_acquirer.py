from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountPaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    supported_currency_map_ids = fields.One2many('payment.acquirer.supported.currency.map', 'acquirer_id',
                                                 string='Supported Currency Map')
    supported_currency_ids = fields.Many2many('res.currency', compute='_compute_supported_currency_ids', string='Supported Currencies')
    default_converted_currency_id = fields.Many2one('res.currency', string='Default Converted Currency',
                                                    default=lambda self: self._default_currency(),
                                                    help="The currency supported by the acquirer that will be used for payment conversion"
                                                    " for currencies that are not supported by the acquirer.\n"
                                                    "For example, your invoice is in VND (Vietnam Dong) which is not supported by the acquirer."
                                                    " During online payment, Odoo will convert the amount in VND to the amount in the"
                                                    " currency specified here before processing payment.")

    @api.constrains('supported_currency_map_ids', 'default_converted_currency_id')
    def _check_default_converted_currency(self):
        for r in self:
            if r.default_converted_currency_id and r.supported_currency_map_ids and r.default_converted_currency_id not in r.supported_currency_map_ids.currency_id:
                raise ValidationError(_("The default currency '%s' does not in the list of supported currencies of the acquirer '%s'."
                                        " Please consult the payment acquirer to have its full list of the supported currencies.")
                                      % (r.default_converted_currency_id.display_name, r.display_name))

    @api.model
    def _default_currency(self):
        return self.env.ref('base.USD', raise_if_not_found=False) or self.env['res.currency'].with_context(active_test=False).search([('name', '=', 'USD')], limit=1)

    def _compute_supported_currency_ids(self):
        for r in self:
            r.supported_currency_ids = r.mapped('supported_currency_map_ids.currency_id')

    def render(self, reference, amount, currency_id, partner_id=False, values=None):
        """
        Override to modify the transaction of the given reference for wallet params.
        Others that extend this just need to implement the method `payment.transaction._prepare_converted_vals()`
        """
        if not bool(values):
            values = {}
        transaction = self.env['payment.transaction'].search([('reference', '=', reference), ('currency_id', '=', currency_id)])
        # there should be no chance of multiple transaction here but it's better to test this
        if len(transaction) > 1:
            raise ValidationError(_("Programming error! There were more than one transactions of the same"
                                  " reference '%s' found in the database which are %s. Please let our"
                                  " administrator know about this for fixing this issue as soon as possible.")
                                    % (reference, ", ".join(transaction.mapped('reference')))
                                    )
        elif len(transaction) == 1:
            vals = transaction._prepare_converted_vals()
            if bool(vals):
                transaction.write(vals)
                values.update(vals)
        return super(AccountPaymentAcquirer, self).render(reference, amount, currency_id, partner_id, values)
