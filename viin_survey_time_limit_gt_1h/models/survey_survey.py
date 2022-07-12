from odoo import models
from odoo.http import request


class Survey(models.Model):
    _inherit = 'survey.survey'

    def get_csrf_token(self):
        self.ensure_one()
        if self.time_limit > 60:
            time_limit = int(self.time_limit * 60)
            return request.csrf_token(time_limit=time_limit)
        return request.csrf_token()
