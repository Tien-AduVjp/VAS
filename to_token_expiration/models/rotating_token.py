import uuid
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class RotatingToken(models.Model):
    _name = 'rotating.token'
    _description = "Rotating Token"

    def _default_token(self):
        return str(uuid.uuid4())

    name = fields.Char('Security Token', copy=False, default=_default_token, required=True, index=True)
    expiration = fields.Datetime(string='Expiry Date',
                                 help="The date and time at which this token will become expired.")
    model = fields.Char(string='Model Name', required=True)
    res_id = fields.Integer(string='Record ID', required=True)
    reference = fields.Char(string='Reference', compute='_compute_reference', readonly=True, store=False)

    # -------------------------------------------------------------------------
    # CRUD
    # -------------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = vals.get('name', self._default_token())
        records = super(RotatingToken, self).create(vals_list)
        to_delete = self.env['rotating.token']
        for rec in records:
            ref_object = rec.get_object(raise_if_not_found=False)
            if ref_object:
                if ref_object.rotating_token_id:
                    to_delete |= ref_object.rotating_token_id
                ref_object.write({
                    'rotating_token_id': rec.id
                })
        if to_delete:
            to_delete.unlink()
        return records

    def write(self, vals):
        if not self._context.get('allow_update_model_and_res_id', False):
            if 'model' in vals or 'res_id' in vals:
                raise UserError(_("Modifying either Model Name or Record ID is not allowed."))
        return super(RotatingToken, self).write(vals)

    def copy(self, default=None):
        raise UserError(_("Rotating Tokens are not allowed to copy!"))

    @api.depends('model', 'res_id')
    def _compute_reference(self):
        for res in self:
            res.reference = "%s,%s" % (res.model, res.res_id)

    def get_object(self, raise_if_not_found=True):
        if self.model not in self.env:
            raise UserError(_("Model `%s` not found. It may not installed.")
                            % (self.model))
        record = self.env[self.model].browse(self.res_id)
        if record.exists():
            return record
        if raise_if_not_found:
            raise UserError(_("No record found for unique ID %s of the model `%s`. It may have been deleted.")
                            % (self.res_id, self.model))
        return None

    def is_expired(self):
        self.ensure_one()
        if (self.expiration and self.expiration < fields.Datetime.now()) or not self.get_object(
                raise_if_not_found=False):
            return True
        else:
            return False

    @api.model
    def cron_rotate_tokens(self):
        expired_tokens = self.env['rotating.token'].search(
            [('expiration', '!=', False), ('expiration', '<', fields.Datetime.now())])
        todo = {}
        for model in set(expired_tokens.mapped('model')):
            todo[model] = expired_tokens.filtered(lambda t: t.model == model).mapped('res_id') or False

        for model, res_ids in todo.items():
            records = self.env[model].browse(res_ids)
            # ensure we are working on the records that do exist in the database
            records = records.exists()

            to_remove_ids = list(set(res_ids) - set(records.ids))
            #remove tokens linked to records not exist
            self.search([('model', '=', model), ('res_id', 'in', to_remove_ids)]).unlink()

            if records:
                records.rotate_token()
                _logger.debug("Refreshed tokens for model %s: %s", records._name, records.ids)
