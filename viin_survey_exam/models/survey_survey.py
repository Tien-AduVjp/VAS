import ast

from odoo import models, api


class Survey(models.Model):
    _inherit = 'survey.survey'

    def action_import_question_bank(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('viin_survey_exam.survey_import_question_wizard_action')
        context = self._context.copy()
        if 'context' in action and type(action['context']) == str:
            context.update(ast.literal_eval(action['context']))
        else:
            context.update(action.get('context', {}))
        context['default_survey_id'] = self.id
        action['context'] = context
        return action

    def import_question_from_question_bank(self, question_ids):
        self.ensure_one()
        if not question_ids:
            return True

        question_values = []
        for question in question_ids:
            question_values.append((0, 0, self._prepare_question_value_to_import(question)))
        return self.write({'question_and_page_ids': question_values})

    def _prepare_question_value_to_import(self, question):
        self.ensure_one()
        sequence = self._get_latest_question_sequence()
        suggested_answer_ids = []
        for answer in question.answer_ids:
            suggested_answer_ids.append((0, 0, answer._prepare_answer_value()))
        res = {
            'sequence': sequence,
            'title': question.name,
            'description': question.description,
            'question_type': question.question_type,
            'constr_mandatory': question.constr_mandatory,
            'constr_error_msg': question.constr_error_msg,
            'column_nb': question.column_nb,
            'comments_allowed': question.comments_allowed,
            'comments_message': question.comments_message,
            'comment_count_as_answer': question.comment_count_as_answer,
            'suggested_answer_ids': suggested_answer_ids,
            'allow_value_image': question.allow_value_image,
            'is_time_limited': question.is_time_limited,
            'time_limit': question.time_limit
        }
        return res

    def _get_latest_question_sequence(self):
        self.ensure_one()
        sequence = 10
        if self.question_and_page_ids:
            sequence = self.question_and_page_ids.sorted('sequence', reverse=True)[0].sequence + 1
        return sequence
