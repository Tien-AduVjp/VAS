from odoo import models, fields, api
from odoo.addons.viin_queue.helpers import multi_async
from odoo.models import BaseModel


class Queue(models.Model):
    _name = 'queue'
    _inherit = 'mail.thread'
    _description = 'Queue'

    name = fields.Char(string='Name', required=True)
    scheduling_method = fields.Selection([
        ('fifo', 'FIFO')
    ], default='fifo', required=True)
    job_ids = fields.One2many('queue.job', 'queue_id', string='Jobs')
    undone_job_ids = fields.One2many('queue.job', 'queue_id', string='Undone Jobs', readonly=True,
                                     domain=[('state', '!=', 'done')])
    undone_job_count = fields.Integer(string='Undone Job Count', compute='_compute_undone_job_count')

    @api.depends('undone_job_ids')
    def _compute_undone_job_count(self):
        for r in self:
            r.undone_job_count = len(r.undone_job_ids)

    def _enqueue(self, method, args=None, kwargs=None, depend_keys=None):
        """
        Enqueue a job.

        Jobs which have same depend key will be ensured to execute sequently.
        This means that a job must be done before the later jobs with the same depend key are executed.

        :param method: a method of a model.
        :param list args: the method's positional arguments.
        :param dict kwargs: the method's keyword arguments.
        :param depend_keys: a comma-separated string of depend keys or a recordset,...
            Examples:
                * 'a,b' => ['a', 'b']
                * sale.order() => ["sale.order()"]
                * sale.order(1,2) => ["sale.order(1)", "sale.order(2)"]
                * [sale.order(1,2), purchase.order(1)] => ["sale.order(1)", "sale.order(2)", "purchase.order(1)"]
        :return: queue job
        """
        self.ensure_one()
        values = self._prepare_job_values(method, args=args, kwargs=kwargs, depend_keys=depend_keys)
        job = self.env['queue.job'].sudo().create(values)

        def process():
            with api.Environment.manage():
                with self.pool.cursor() as cr:
                    self.with_env(self.env(cr=cr)).sudo()._process_async()

        self.env.cr.after('commit', process)
        return job

    def _prepare_job_values(self, method, args=None, kwargs=None, depend_keys=None):
        self.ensure_one()
        method_call = self.env['method.call'].sudo()._serialize(method, args, kwargs)
        values = {
            'queue_id': self.id,
            'method_call_id': method_call.id,
            'depend_keys': self._stringify_depend_keys(depend_keys)
        }
        return values

    def _stringify_depend_keys(self, depend_keys=None):
        if not depend_keys:
            return None
        if isinstance(depend_keys, (list, tuple)):
            return ','.join(self._stringify_depend_keys(key) for key in depend_keys if key)
        if isinstance(depend_keys, BaseModel):
            return ','.join(str(key) for key in depend_keys)
        return str(depend_keys)

    def _process(self):
        undone_queues = self.filtered(lambda queue: queue.undone_job_ids)
        queues = undone_queues._select_for_update_skip_locked()
        for r in queues:
            jobs = getattr(r, '_schedule_jobs_%s' % r.scheduling_method)()
            queue_depend_keys = set()
            for job in jobs:
                job_depend_keys = job._get_depend_keys()
                if job.state != 'done' and job_depend_keys.isdisjoint(queue_depend_keys):
                    job._execute()
                if job.state != 'done' and job_depend_keys:
                    queue_depend_keys.update(job_depend_keys)

    def _process_async(self, max_workers=10, wait=False):
        undone_queues = self.filtered(lambda queue: queue.undone_job_ids)
        multi_async(undone_queues._process, max_workers=max_workers, wait=wait)

    def action_process(self):
        self._process_async(wait=True)

    def _schedule_jobs_fifo(self):
        self.ensure_one()
        return self.undone_job_ids.sorted('id')

    def _cron_process(self):
        queues = self.sudo().search([])
        queues._process_async()

    def action_view_undone_jobs(self):
        action = self.env['ir.actions.act_window']._for_xml_id('viin_queue.queue_job_action')
        action['domain'] = [('queue_id', 'in', self.ids)]
        return action
