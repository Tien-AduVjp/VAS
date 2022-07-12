import json

from odoo import models, fields, api
from odoo.addons.viin_queue.json import JsonEncoder, JsonDecoder
from odoo.models import BaseModel


class MethodCall(models.Model):
    _name = 'method.call'
    _description = 'Method Call'

    name = fields.Char(string='Name', compute='_compute_name')
    model = fields.Char(string='Model', required=True)
    record_ids = fields.Text(string='Record IDs', required=True)
    method = fields.Char(string='Method', required=True)
    args = fields.Text(string='Method Args')
    kwargs = fields.Text(string='Method Kwargs')
    context = fields.Text(string='Context')
    user_id = fields.Many2one('res.users', required=True, default=lambda self: self.env.user)
    su = fields.Boolean(string='Sudo')

    @api.depends('model', 'method')
    def _compute_name(self):
        for r in self:
            r.name = '%s.%s' % (r.model, r.method)

    @api.model
    def _json_serialize(self, value, indent=2):
        return json.dumps(value, cls=JsonEncoder, indent=indent)

    @api.model
    def _json_deserialize(self, value):
        return json.loads(value, cls=JsonDecoder, env=self.env) if value else None

    @api.model
    def _prepare_values(self, method, args=None, kwargs=None):
        records = method.__self__
        if not isinstance(records, BaseModel):
            raise Exception("The method %s must be a method of a model!" % method.__name__)
        values = {
            'model': records._name,
            'record_ids': self._json_serialize(records.ids, indent=None),
            'method': method.__name__,
            'args': self._json_serialize(args or []),
            'kwargs': self._json_serialize(kwargs or {}),
            'context': self._json_serialize(records.env.context),
            'user_id': records.env.user.id,
            'su': records.env.su
        }
        return values

    @api.model
    def _serialize(self, method, args=None, kwargs=None):
        values = self._prepare_values(method, args, kwargs)
        call = self.sudo().create(values)
        return call

    def _deserialize(self):
        self.ensure_one()
        env = self.env(context=self._json_deserialize(self.context), su=self.su, user=self.user_id.id)
        records = env[self.model].browse(self._json_deserialize(self.record_ids))
        method = getattr(records, self.method)
        args = self._json_deserialize(self.with_env(env).args) or []
        kwargs = self._json_deserialize(self.with_env(env).kwargs) or {}
        return method, args, kwargs

    def _execute(self):
        self.ensure_one()
        method, args, kwargs = self._deserialize()
        res = method(*args, **kwargs)
        return res
