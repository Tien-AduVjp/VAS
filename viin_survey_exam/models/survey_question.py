from odoo import models, _
from odoo.exceptions import UserError


class SurveyQuestion(models.Model):
    _inherit = 'survey.question'
    
    def create_question_bank(self, category):
        vals_list = []
        for r in self.filtered(lambda q: q.is_page == False):
            if r.question_type not in ('simple_choice', 'multiple_choice'):
                raise UserError(_("Cannot create question bank from question '%s'.\nYou can only create with question type is Multiple choice: only one answer or Multiple choice: multiple answers allowed")
                    % r.title)
            vals_list.append(r._prepare_question_bank_values(category))
        return self.env['survey.question.bank'].create(vals_list)
            
    def _prepare_question_bank_values(self, category):
        self.ensure_one()
        answer_ids = []
        for answer in self.labels_ids:
            answer_ids.append((0, 0, answer._prepare_answer_value()))
        res = {
            'name': self.title,
            'description': self.description,
            'category_id': category.id,
            'question_type': self.question_type,
            'constr_mandatory': self.constr_mandatory,
            'constr_error_msg': self.constr_error_msg,
            'display_mode': self.display_mode,
            'column_nb': self.column_nb,
            'comments_allowed': self.comments_allowed,
            'comments_message': self.comments_message,
            'comment_count_as_answer': self.comment_count_as_answer,
            'answer_ids': answer_ids
        }
        return res
