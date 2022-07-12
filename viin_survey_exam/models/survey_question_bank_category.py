from odoo import fields, models, api


class SurveyQuestionBankCategory(models.Model):
    _name = 'survey.question.bank.category'
    _description = 'Category of Survey Question Bank'
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'complete_name'
    
    name = fields.Char(string="Name", required=True)
    complete_name = fields.Char(string='Complete Name', compute='_compute_complete_name', store=True)
    parent_id = fields.Many2one('survey.question.bank.category', string='Parent Category', index=True, ondelete='cascade',
                                domain="[('id', '!=', id)]")
    parent_path = fields.Char(index=True)
    child_id = fields.One2many('survey.question.bank.category', 'parent_id', 'Child Categories')
    question_count = fields.Integer(string='# Questions', compute='_compute_question_count',
        help="The number of questions under this category (Does not consider the children categories)")
    question_bank_ids = fields.One2many('survey.question.bank', 'category_id', string='Bank Survey Questions')
    
    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = '%s / %s' % (category.parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name
                
    def _compute_question_count(self):
        for r in self:
            question_count = 0
            for categ in r + r.child_id:
                question_count += len(categ.question_bank_ids)
            r.question_count = question_count
            
    def open_questions_bank(self):
        self.ensure_one()
        action = self.env.ref('viin_survey_exam.survey_question_bank_action').read()[0]
        context = self._context.copy()
        context['default_category_id'] = self.id
        action['context'] = context
        action['domain'] = [('id', 'in', (self + self.child_id).question_bank_ids.ids)]
        return action
