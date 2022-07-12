from odoo import fields, models, api, _


class SurveyQuestionBank(models.Model):
    _name = 'survey.question.bank'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Survey Question Bank'

    name = fields.Char(string="Question", required=True, translate=True)
    description = fields.Html('Description', help="Use this field to add additional explanations about your question", translate=True)
    category_id = fields.Many2one('survey.question.bank.category', string="Category", required=True)
    question_type = fields.Selection([
        ('simple_choice', 'Multiple choice: only one answer'),
        ('multiple_choice', 'Multiple choice: multiple answers allowed'),
    ], string='Question Type', default='simple_choice', required=True)
    constr_mandatory = fields.Boolean('Mandatory Answer', default=True)
    constr_error_msg = fields.Char('Error message', translate=True, default=lambda self: _("This question requires an answer."))
    column_nb = fields.Selection([
        ('12', '1'), ('6', '2'), ('4', '3'), ('3', '4'), ('2', '6')],
        string='Number of columns', default='12',
        help='These options refer to col-xx-[12|6|4|3|2] classes in Bootstrap for dropdown-based simple and multiple choice questions.')
    comments_allowed = fields.Boolean('Show Comments Field')
    comments_message = fields.Char('Comment Message', translate=True, default=lambda self: _("If other, please specify:"))
    comment_count_as_answer = fields.Boolean('Comment Field is an Answer Choice')
    answer_ids = fields.One2many('survey.question.bank.answer', 'question_id', string="Answers", copy=True)
    allow_value_image = fields.Boolean('Images on answers', help='Display images in addition to answer label. Valid only for simple / multiple choice questions.')

    is_time_limited = fields.Boolean('The question is limited in time',
        help="Currently only supported for live sessions.")
    time_limit = fields.Integer('Time limit (seconds)')
