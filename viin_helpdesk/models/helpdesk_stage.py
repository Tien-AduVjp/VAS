from odoo import fields, models, _
from odoo.exceptions import UserError


class HelpdeskStage(models.Model):
    _name = 'helpdesk.stage'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Helpdesk Stage"
    _order = 'sequence, id'

    def _get_default_team_ids(self):
        team_id = self.env.context.get('default_team_id', False)
        if team_id:
            return [team_id]
        return False

    name = fields.Char(string='Name', required=True, translate=True)
    description = fields.Text(string='Description', translate=True)
    sequence = fields.Integer(string='Sequence', help="Gives the sequence order when displaying a list of Stages.")
    mail_template_id = fields.Many2one('mail.template', string='Email Template', domain=[('model', '=', 'helpdesk.ticket')],
                                       help="If set an email will be sent to the customer when the ticket reaches this step")
    team_ids = fields.Many2many('helpdesk.team', 'helpdesk_stage_rel', 'stage_id', 'team_id', string='Teams',
                                default=_get_default_team_ids,
                                help="Specific team that ticket in stage. Other team will not be able to see or use this stage")
    fold = fields.Boolean(string='Folded in Kanban',
                          help="This stage is folded in the kanban view when there are no records in that stage to display.")
    rating_template_id = fields.Many2one('mail.template', string='Rating Email Template', domain=[('model', '=', 'helpdesk.ticket')],
                                         help="If set and if the ticket's rating configuration is 'Rating when changing stage',"
                                         "then an email will be sent to the customer when the ticket reaches this step.")
    is_final_stage = fields.Boolean(string='Is Final Stage', groups='viin_helpdesk.group_helpdesk_user',
                                    help="Specific whenever this stage is final stage or not. "
                                    "Any ticket moved into this stage will be considering as resolved.")
    legend_blocked = fields.Char(string='Red Kanban Label', default=lambda s: _('Blocked'), translate=True, required=True,
                                 help="Override the default value displayed for the blocked state for kanban selection, when the ticket is in that stage.")
    legend_done = fields.Char(string='Green Kanban Label', default=lambda s: _('Ready for Next Stage'), translate=True, required=True,
                              help="Override the default value displayed for the done state for kanban selection, when the ticket is in that stage.")
    legend_normal = fields.Char(string='Grey Kanban Label', default=lambda s: _('In Progress'), translate=True, required=True,
                                help="Override the default value displayed for the normal state for kanban selection, when the ticket is in that stage.")
    auto_validation_kanban_state = fields.Boolean(string='Automatic kanban status', default=False,
                                                  help="Automatically modify the kanban state when the customer replies to the feedback for this stage.\n"
                                                " * A good feedback from the customer will update the kanban state to 'ready for the new stage' (green bullet).\n"
                                                " * A medium or a bad feedback will set the kanban state to 'blocked' (red bullet).\n")

    def unlink(self):
        for r in self:
            if r.team_ids:
                raise UserError(_("You cannot delete a Stage containing Teams or first you can delete all of its Teams."))
        return super(HelpdeskStage, self).unlink()
