import json
from datetime import datetime, date

from odoo import fields
from odoo.models import BaseModel


class JsonEncoder(json.JSONEncoder):
    """A json encoder that supports recordset type."""

    def default(self, obj):
        if isinstance(obj, BaseModel):
            return {'__recordset__': [obj._name, obj.ids]}
        if isinstance(obj, datetime):
            return {'__datetime__': fields.Datetime.to_string(obj)}
        if isinstance(obj, date):
            return {'__date__': fields.Date.to_string(obj)}
        return super(JsonEncoder, self).default(obj)


class JsonDecoder(json.JSONDecoder):
    """A json decoder that supports recordset type."""

    def __init__(self, *args, **kwargs):
        self.env = kwargs.pop('env')
        super(JsonDecoder, self).__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if '__recordset__' in obj:
            vals = obj['__recordset__']
            return self.env[vals[0]].browse(vals[1])
        if '__datetime__' in obj:
            return fields.Datetime.to_datetime(obj['__datetime__'])
        if '__date__' in obj:
            return fields.Date.to_date(obj['__date__'])
        return obj
