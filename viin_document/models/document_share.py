from odoo import fields, models, api, _

class DocumentShare(models.Model):
    _name = "document.share"
    _inherit = 'rotating.token.mixin'
    _description = "Share Document"
    _rec_name = 'url'

    url = fields.Char(string="Share URL", compute="_compute_url")
    token = fields.Char(readonly=True)
    expire_date = fields.Datetime(string="Expire Date", related='rotating_token_id.expiration')
    document_ids = fields.Many2many('document.document', string="Documents", readonly=True)
    document_count = fields.Integer("Total shared documents", compute="_compute_document_count")
    workspace_ids = fields.Many2many('document.workspace', string="Workspaces", compute="_compute_workspace_ids")
    status = fields.Boolean(string='Hidden Status', compute="_compute_status", help="The technical field used to set decoration on treeview")
    show_status = fields.Char(string="Status", compute="_compute_status")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('access_token', 'unique (access_token)', 'The token must be unique!')
    ]

    @api.depends('access_token')
    def _compute_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('report.url') or self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for r in self:
            if r.access_token:
                r.url = base_url + '/document/share/' + r.access_token
            else:
                r.url = False

    @api.depends('document_ids')
    def _compute_document_count(self):
        for r in self:
            r.document_count = len(r.document_ids)

    @api.depends('document_ids.workspace_id')
    def _compute_workspace_ids(self):
        for r in self:
            workspace_ids = self.env['document.workspace']
            for d in r.document_ids:
                workspace_ids |= d.workspace_id
            r.workspace_ids = workspace_ids

    @api.depends('expire_date')
    def _compute_status(self):
        for r in self:
            if not r.rotating_token_id.is_expired():
                r.status = True
                r.show_status = _('Actived')
            else:
                r.status = False
                r.show_status = _('Expired')

    def update_share_url(self):
        return True

    def generate_url(self):
        return True
