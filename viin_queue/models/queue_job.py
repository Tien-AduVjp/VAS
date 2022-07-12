import html
import traceback

from odoo import models, fields
from odoo.exceptions import except_orm


class QueueJob(models.Model):
    _name = 'queue.job'
    _inherit = 'mail.thread'
    _description = 'Queue Job'
    _order = 'id DESC'

    queue_id = fields.Many2one('queue', string='Queue', required=True)
    method_call_id = fields.Many2one('method.call', string='Method Call', required=True, delegate=True)
    state = fields.Selection([
        ('queued', 'Queued'),
        ('done', 'Done'),
        ('failed', 'Failed')
    ], string='Status', default='queued', required=True, readonly=True)
    error = fields.Text(string='Error', readonly=True)
    exception = fields.Text(string='Exception', readonly=True)
    active = fields.Boolean(string='Active', default=True, readonly=True)
    last_execution = fields.Datetime(string='Last Execution')
    depend_keys = fields.Text(string='Depend Keys', help="Comma-separated depend keys. Jobs which have same depend key will be ensured to execute sequently.\n"
                                                         "This means that a job must be done before the later jobs with the same depend key are executed.")

    def _execute(self):
        jobs = self._select_for_update_skip_locked()
        for r in jobs:
            r.last_execution = fields.Datetime.now()
            try:
                with self.env.cr.savepoint():
                    r.method_call_id._execute()
            except Exception as e:
                if isinstance(e, except_orm):
                    r.error = e.name
                else:
                    r.error = str(e)
                r.exception = traceback.format_exc()
                r.state = 'failed'
                r.message_post(body='<pre>%s</pre>' % html.escape(r.exception))
            else:
                r.error = False
                r.exception = False
                r.state = 'done'

    def _get_depend_keys(self):
        self.ensure_one()
        if self.depend_keys:
            return set(self.depend_keys.split(','))
        return set()
