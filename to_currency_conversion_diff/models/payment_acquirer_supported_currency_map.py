from odoo import models, fields, api


class AcquirerSupportedCurrencyMap(models.Model):
    _name = 'payment.acquirer.supported.currency.map'
    _rec_name = 'currency_id'
    _description = 'Acquirer Supported Currency Map'
 
    acquirer_id = fields.Many2one('payment.acquirer', string='Acquirer', required=True, ondelete='cascade')
    currency_id = fields.Many2one('res.currency', string='Supported Currency', required=True, ondelete='cascade')
    
    _sql_constraints = [
        ('acquirer_currency_unique',
         'UNIQUE(acquirer_id,currency_id)',
         "Currency must be Unique per acquirer! Please specify another currency."),
    ]

    def name_get(self):
        result = []
        for r in self:
            result.append((r.id, '%s - %s' % (r.acquirer_id.name, r.currency_id.name)))
        return result
