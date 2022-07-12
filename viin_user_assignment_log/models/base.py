from odoo import models, api, fields
from odoo.tools import config


class Base(models.AbstractModel):
    _inherit = 'base'

    @api.model_create_multi
    @api.returns('self', lambda value:value.id)
    def create(self, vals_list):
        records = super(Base, self).create(vals_list)
        records._generate_user_assignment_logs()
        return records

    def write(self, vals):
        user_assignment_vals_list = []
        if self._can_log_user_assignment():
            current_user = self.env.user
            responsible_user_field_name = self._get_responsible_user_field_name()
            if responsible_user_field_name and responsible_user_field_name in vals:
                last_assignments_dict = self._get_last_user_assignment_dict()
                for r in self:
                    last_assignment = last_assignments_dict.get(r.id, False)
                    if last_assignment:
                        last_assignment.sudo().write({
                            'date_end': fields.Datetime.now(),
                            'unassigned_by_user_id': current_user,
                        })

                    if vals[responsible_user_field_name]:
                        user_assignment_vals = r.with_context(
                            assigned_user_id=vals[responsible_user_field_name]
                            )._prepare_user_assignment_vals(date_start=fields.Datetime.now())
                        if bool(user_assignment_vals):
                            user_assignment_vals_list.append(user_assignment_vals)
        res = super(Base, self).write(vals)
        if user_assignment_vals_list:
            self.env['user.assignment'].sudo().create(user_assignment_vals_list)
        return res

    def unlink(self):
        related_user_assignments = self.sudo()._get_user_assignments()
        if related_user_assignments:
            related_user_assignments.unlink()
        return super(Base, self).unlink()

    def _generate_user_assignment_logs(self):
        if self._can_log_user_assignment():
            responsible_user_field_name = self._get_responsible_user_field_name()
            if responsible_user_field_name:
                user_assignment_vals_list = []
                for r in self:
                    responsible_user = getattr(r, responsible_user_field_name)
                    if responsible_user and not responsible_user.share and responsible_user.active: 
                        user_assignment_vals = r.with_context(
                            assigned_user_id=responsible_user.id
                            )._prepare_user_assignment_vals()
                        if bool(user_assignment_vals):
                            user_assignment_vals_list.append(user_assignment_vals)
                if user_assignment_vals_list:
                    return self.env['user.assignment'].sudo().create(user_assignment_vals_list)
        return self.env['user.assignment']
        
    @api.model
    def _get_user_assignment_backlisted_models(self):
        return ['web_tour.tour', 'bus.presence']

    @api.model
    def _can_log_user_assignment(self):
        return not isinstance(self, self.env['user.assignment'].__class__) \
            and not isinstance(self, models.TransientModel) \
            and self._name not in self._get_user_assignment_backlisted_models() \
            and self._name in config.options.get('track_user_assignment_whitelisted_models', []) \
            and self._auto == True

    @api.model
    def _get_responsible_user_field_name(self):
        if not self._can_log_user_assignment():
            return False
        if self._name == 'account.move':
            return 'invoice_user_id'
        else:
            # the user_id of attendance.device.user is char type which is not a relation field
            # the user_id of user.attendance is relation field but the target model is not res.users
            # we only need relation field and the target model is res.users
            return 'user_id' if self.fields_get('user_id', 'relation').get('user_id', {}).get('relation', '') == 'res.users' else False
        
    def _get_real_id_for_asignment_res_id(self):
        self.ensure_one()
        if self._name == 'calendar.event':
            # the id of calendar.event is in the format of 'id-date' (e.g. '2143-20210426033000')
            # which is not a real id (i.e. 2143)
            # we need to convert it to real id
            from odoo.addons.calendar.models import calendar
            real_id = calendar.calendar_id2real_id(self.id, with_date=False)
        else:
            real_id = self.id
        return real_id

    def _prepare_user_assignment_vals(self, date_start=None):
        self.ensure_one()
        responsible_user_field_name = self._get_responsible_user_field_name()
        if not responsible_user_field_name:
            return {}
        model_record = self.env['ir.model'].sudo().search([('model', '=', self._name)], limit=1)
        if not model_record:
            return {}

        user_id = self._context.get('assigned_user_id', False) or False
        if not user_id:
            assigned_user = getattr(self, responsible_user_field_name)
            if assigned_user and not assigned_user.share and assigned_user.active:
                users_obj = self.env['res.users']
                if isinstance(assigned_user, str) and assigned_user.isnumeric():
                    assigned_user = users_obj.browse(int(assigned_user)).exists()
                elif isinstance(assigned_user, int):
                    assigned_user = users_obj.browse(assigned_user).exists()

                if isinstance(assigned_user, users_obj.__class__):
                    user_id = assigned_user.id

        if not user_id:
            return {}

        if not date_start:
            if hasattr(self, 'create_date'):
                date_start = self.create_date
            else:
                date_start = fields.Datetime.now()
        company_id = self._context.get('force_company') or (self.company_id.id if hasattr(self, 'company_id') and self.company_id else self.env.company.id)

        return {
            'date_start': date_start,
            'model_id': model_record.id,
            'res_model': self._name,
            'res_id': self._get_real_id_for_asignment_res_id(),
            'user_id': user_id,
            'assigned_by_user_id': self.env.user.id,
            'company_id': company_id
            }

    def _get_user_assignments_domain(self):
        """
        Hooking method for others to extend
        """
        return [
            ('res_model', '=', self._name),
            ('res_id', 'in', self.ids)
            ]

    def _get_user_assignments(self, order='create_date desc'):
        return self.env['user.assignment'].search(self._get_user_assignments_domain(), order=order)

    def _get_last_user_assignment_dict(self):
        """
        :return: {
                    id: user.assignment(),
                    id: user.assignment(),
                    ...
                    }
        """
        res = {}
        all_assignment_log_records = self._get_user_assignments(order='create_date desc')
        for r in self:
            assignment_log_records = all_assignment_log_records.filtered(lambda l: l.res_id == r._get_real_id_for_asignment_res_id())
            if assignment_log_records:
                res[r.id] = assignment_log_records[0]
        return res

    def action_view_assignment_logs(self):
        assignments = self._get_user_assignments()
        action = self.env.ref('viin_user_assignment_log.action_user_assignment')
        result = action.read()[0]
        result['context'] = {}
        result['domain'] = "[('id', 'in', %s)]" % str(assignments.ids)
        return result
