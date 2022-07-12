from odoo import models, fields, api, _


class Authenticate(models.TransientModel):
    _name = 'git.authenticate'
    _description = 'Git Remote Authenticate'

    username = fields.Char()
    password = fields.Char()

    def try_again(self):
        self.ensure_one()
        origin_call = self.env.context['origin_call']
        action_name = origin_call['name']
        action_model = origin_call['model']
        record_ids = origin_call['ids']
        records = self.env[action_model].browse(record_ids)
        records = records.with_context(username=self.username,
                                       password=self.password,
                                       with_credential=True)
        action = getattr(records, action_name)
        action()
