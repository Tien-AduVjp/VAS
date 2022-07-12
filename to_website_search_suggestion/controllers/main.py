import json
from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import Website

class Website(Website):

    @http.route(
        '/website/field_suggestion/<string:model>',
        type='http',
        auth='public',
        methods=['GET'],
        website=True,
    )
    def _get_field_suggestion(self, model, **kwargs):
        """ Return json suggestion data """
        domain = json.loads(kwargs.get('domain', "[]"))
        fields = json.loads(kwargs.get('fields', "[]"))
        limit = kwargs.get('limit', None)
        res = self._get_suggestion_data(model, domain, fields, limit)
        return json.dumps(res)

    def _get_suggestion_data(self, model, domain, fields, limit=None):
        """ Gets and returns raw record data"""
        if limit:
            limit = int(limit)
        res = request.env[model].search_read(
            domain, fields, limit=limit
        )
            
        return {r['id']: r for r in res}
