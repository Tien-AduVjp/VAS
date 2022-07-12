# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountFullReconcile(models.Model):
    _inherit = 'account.full.reconcile'
    _description = "Full Reconcile"

    reconciliation_date = fields.Date(string='Reconciliation Date', default=fields.Date.today)

    @api.model_create_multi
    @api.returns('self', lambda value:value.id)
    def create(self, vals_list):
        records = super(AccountFullReconcile, self).create(vals_list)
        for record in records:
            # update reconciled journal items for reconciliation date
            record.reconciled_line_ids.write({
                'reconciliation_date': record.reconciliation_date
                })
        return records

