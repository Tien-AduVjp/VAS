import re
import ast

from urllib.parse import urlparse, parse_qs
from dateutil.relativedelta import relativedelta
try:
    # try to use UniqueViolation if psycopg2's version >= 2.8
    from psycopg2 import errors
    UniqueViolation = errors.UniqueViolation
except Exception:
    import psycopg2
    UniqueViolation = psycopg2.IntegrityError

from odoo import fields, models, api, _


class DocumentDocument(models.Model):
    _name = 'document.document'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Document"

    attachment_id = fields.Many2one('ir.attachment', string='Attachment', ondelete='cascade',
                                    copy=False, index=True, auto_join=True)
    res_model = fields.Char(related='attachment_id.res_model')
    res_id = fields.Many2oneReference(related='attachment_id.res_id', model_field='res_model')
    name = fields.Char(related='attachment_id.name', readonly=False, store=True, tracking=True, required=True)
    type = fields.Selection([('url', 'URL'), ('binary', 'File')], string='Type', compute='_compute_type', store=True)
    mimetype = fields.Char(related='attachment_id.mimetype',
                           help="A media type (also known as a Multipurpose Internet Mail Extensions or MIME type) "
                                "indicates the nature and format of a document, file, or assortment of bytes "
                                "(e.g. audio/aac, application/x-bzip, etc)")
    datas = fields.Binary(related='attachment_id.datas', related_sudo=True, readonly=False)
    workspace_id = fields.Many2one('document.workspace', string='Workspace', required=True, tracking=True)
    tag_ids = fields.Many2many('document.tag', string='Tags')
    action_ids = fields.Many2many('document.action', string='Actions', compute='_compute_action_ids')
    owner_id = fields.Many2one('res.users', string='Owner', required=True, default=lambda self: self.env.user, tracking=True)
    url = fields.Char(string='URL', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', related='workspace_id.company_id')
    favorited_user_ids = fields.Many2many('res.users', string='Favorited Users')
    active = fields.Boolean(string='Active', default=True)
    ytb_video_id = fields.Char(string='Youtube Video ID', compute='_compute_ytb_video_id')

    @api.depends('attachment_id.type', 'url')
    def _compute_type(self):
        for r in self:
            if r.url:
                r.type = 'url'
            elif r.attachment_id:
                r.type = r.attachment_id.type
            else:
                r.type = False

    @api.depends('workspace_id.action_ids')
    def _compute_action_ids(self):
        for r in self:
            r.action_ids = r.workspace_id.action_ids.filtered(
                lambda a:
                (not a.included_tag_ids or any([tag in a.included_tag_ids for tag in r.tag_ids]))
                and (not a.excluded_tag_ids or all([tag not in a.excluded_tag_ids for tag in r.tag_ids]))
                and (not a.owner_id or r.owner_id == a.owner_id)
                and (not a.condition_type == 'domain' or not a.domain or (a.domain and r in self.search(ast.literal_eval(a.domain))))
            )

    @api.depends('type', 'url')
    def _compute_ytb_video_id(self):
        for r in self:
            if r.type == 'url' and r.url:
                r.ytb_video_id = self._extract_youtube_video_id(r.url)
            else:
                r.ytb_video_id = None

    @api.model_create_multi
    def create(self, vals_list):
        """
        We need create attachment before create document. So datas in vals_list must be included some information
        to create attachment, Ex.: datas, name, mimetype.
        """
        for vals in vals_list:
            if not vals.get('attachment_id', False) and 'datas' in vals:
                attachment_vals = self._prepare_attachment_vals(vals)
                if bool(attachment_vals):
                    attachment = self.env['ir.attachment'].create(attachment_vals)
                    vals['attachment_id'] = attachment.id
                    # remove datas and mimetype from vals to avoid inverse that slowdown the creation
                    vals.pop('datas')
                    if 'mimetype' in vals:
                        vals.pop('mimetype')

        documents = super(DocumentDocument, self).create(vals_list)

        # attachments that are not link to any other model record should have the document as their res_id
        for document in documents:
            if not document.attachment_id.res_id:
                document.attachment_id.res_id = document.id
        return documents

    @api.constrains('name', 'workspace_id')
    def _check_unique_name(self):
        existing_vals_list = self.with_context(active_test=False).search_read(
            [
                ('id', 'not in', self.ids),
                ('workspace_id', 'in', self.workspace_id.filtered(lambda wsp: wsp.unique_doc_name).ids)
                ],
            ['name', 'workspace_id']
            )
        for r in self:
            if r.workspace_id.unique_doc_name:
                overlap = list(
                    filter(
                        lambda vals: vals['name'] == r.name and vals['workspace_id'][0] == r.workspace_id.id,
                        existing_vals_list
                        )
                    )
                if overlap:
                    raise UniqueViolation(
                        _("Document name unique violation. The workspace '%s' already contains a document named '%s'")
                        %(r.workspace_id.display_name, r.name)
                        )
                else:
                    existing_vals_list.append({
                        'name': r.name,
                        'workspace_id': (r.workspace_id.id, r.workspace_id.name)
                        })

    @api.model
    def _prepare_attachment_vals(self, vals):
        """
        Hook method to prepare attachment values
        """
        if not vals.get('datas'):
            return {}
        res = {
            'name': vals.get('name', 'unnamed'),
            'mimetype': vals.get('mimetype', 'application/octet-stream'),
            'datas': vals['datas'],
            'res_model': self._name,
        }
        return res

    def _prepare_upload_document_value(self, name, mimetype, datas, workspace_id, kwargs=None):
        """
        Hook method to prepare document value from upload view. It called from controller
        """
        res = {
            'name': name,
            'mimetype': mimetype,
            'datas': datas,
            'workspace_id': workspace_id,
        }
        return res

    def update_schedule_activity(self, action):
        if not action.document_activity_due_date_type or not action.document_activity_due_date:
            due_date = None
        if action.document_activity_due_date_type == 'day':
            due_date = relativedelta(days=action.document_activity_due_date)
        elif action.document_activity_due_date_type == 'week':
            due_date = relativedelta(weeks=action.document_activity_due_date)
        elif action.document_activity_due_date_type == 'month':
            due_date = relativedelta(months=action.document_activity_due_date)

        for r in self:
            activity = r.sudo().activity_schedule(
                summary=action.document_activity_summary,
                date_deadline=fields.Datetime.today() + due_date if due_date else None,
                activity_type_id=action.document_activity_type_id.id,
                note=action.document_activity_note,
                user_id=action.document_activity_user_id.id,
            )
            if action.done_document_activity:
                activity.action_done()

    @api.model
    def _extract_youtube_video_id(self, url):
            """
                Returns Video_ID extracting from the given url of Youtube
                Examples:
                - http://youtu.be/SnM0X3VpUBU
                - http://www.youtube.com/watch?v=SnM0X3VpUBU&feature=feedu
                - http://www.youtube.com/embed/SnM0X3VpUBU
                - http://www.youtube.com/v/SnM0X3VpUBU?version=3&amp;hl=en_US
            """
            regex = r'^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$'
            match = re.match(regex, url)
            if not match:
                return None
            if url.startswith(('youtu', 'www')):
                url = 'http://' + url
            query = urlparse(url)
            if 'youtube' in query.hostname:
                if query.path == '/watch':
                    return parse_qs(query.query)['v'][0]
                elif query.path.startswith(('/embed/', '/v/')):
                    return query.path.split('/')[2]
            elif 'youtu.be' in query.hostname:
                return query.path[1:]
            else:
                return None
