from datetime import datetime

from odoo import models, fields, api


class UserAssignment(models.Model):
    _name = 'user.assignment'
    _description = "User Assignment"

    @api.model
    def _selection_target_model(self):
        models = self.env['ir.model'].search([])
        return [(model.model, model.name) for model in models]

    model_id = fields.Many2one('ir.model', string='Model', readonly=True, index=True)
    res_model = fields.Char(string='Resource Model Name', related='model_id.model', store=True, index=True)
    res_id = fields.Integer(string='Record ID', readonly=True, required=True, index=True)
    res_name = fields.Char(
        'Document Name', compute='_compute_res_name', compute_sudo=True, search="_search_res_name",
        help="Display name of the related document.", readonly=True)
    resource_ref = fields.Reference(string='Record reference', selection='_selection_target_model',
                                    compute='_compute_resource_ref', inverse='_inverse_resource_ref', readonly=True,
                                    compute_sudo=True)
    date_start = fields.Datetime(string='Assigned Date', required=True, readonly=True, index=True)
    date_end = fields.Datetime(string='Unassigned Date', readonly=True, index=True)
    duration = fields.Float(string='Duration', compute='_compute_duration',
                            help="The duration (in hours) counting from the assigned date to the unassigned date or"
                            " the current date if the unassigned date is not specified.")
    user_id = fields.Many2one('res.users', string='Responsible', readonly=True, required=True, index=True)
    assigned_by_user_id = fields.Many2one('res.users', string='Assigned by', default=lambda self: self.env.user,
                                          readonly=True, required=True)
    unassigned_by_user_id = fields.Many2one('res.users', string='Unassigned by', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True, index=True)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        # overrides the default read_group in order to compute the computed fields manually for the group
        fields_list = {'duration', }

        # remove all the aggregate functions of non-stored fields to avoid error on pivot view
        def truncate_aggr(field):
            field_no_aggr = field.split(':', 1)[0]
            if field_no_aggr in fields_list:
                return field_no_aggr
            return field

        fields = {truncate_aggr(field) for field in fields}

        result = super(UserAssignment, self).read_group(
            domain,
            list(fields - fields_list),
            groupby,
            offset=offset,
            limit=limit,
            orderby=orderby,
            lazy=lazy
            )

        now = datetime.now().replace(microsecond=0)
        if any(x in fields for x in fields_list):
            for group_line in result:

                # initialize fields to compute to 0 if they are requested
                if 'duration' in fields:
                    group_line['duration'] = 0

                if group_line.get('__domain'):
                    all_lines_that_compose_group = self.search(group_line['__domain'])
                else:
                    all_lines_that_compose_group = self.search([])
                for line_of_group in all_lines_that_compose_group:
                    date_end = line_of_group.date_end or now
                    if 'duration' in fields or 'percentage' in fields:
                        group_line['duration'] += (date_end - line_of_group.date_start).total_seconds() / 3600

        return result

    def _compute_res_name(self):
        model_dict = {}
        for r in self:
            if r.res_model and r.res_model in r.env and r.res_id:
                model_dict.setdefault(r.res_model, [])
                model_dict[r.res_model].append(r.res_id)
        for res_model, ids in model_dict.items():
            model_dict[res_model] = {rec.id:rec.display_name for rec in self.env[res_model].browse(ids)}
        for r in self:
            if r.res_model and r.res_model in r.env and r.res_id:
                r.res_name = model_dict[r.res_model][r.res_id]
            else:
                r.res_name = ''

    @api.depends('model_id', 'res_id')
    def _compute_resource_ref(self):
        for r in self:
            if r.model_id:
                r.resource_ref = '%s,%s' % (r.model_id.model, r.res_id or 0)
            else:
                r.resource_ref = False
                
    def _inverse_resource_ref(self):
        for r in self:
            if r.resource_ref:
                r.res_id = r.resource_ref.id

    def _compute_duration(self):
        now = fields.Datetime.now()
        for r in self:
            date_end = r.date_end or now
            r.duration = (date_end - r.date_start).total_seconds() / 3600

    def _search_res_name(self, operator, operand):
        assignment_list = self.env['user.assignment'].search_read([], ['res_name'])
        if operator == '=':
            if operand:  # equal
                list_ids = [vals['id'] for vals in assignment_list if operand == vals['res_name']]
            else:  # is not set, equal = ""
                list_ids = [vals['id'] for vals in assignment_list if not vals['res_name']]
        elif operator == '!=':
            if operand:  # not equal
                list_ids = [vals['id'] for vals in assignment_list if operand != vals['res_name']]
            else:  # is set
                list_ids = [vals['id'] for vals in assignment_list if vals['res_name']]
        elif operator == 'not ilike':
            list_ids = [vals['id'] for vals in assignment_list if operand.lower() not in vals['res_name'].lower()]
        elif operator == 'ilike':  # 'ilike'
            list_ids = [vals['id'] for vals in assignment_list if operand.lower() in vals['res_name'].lower()]
        else:
            return []
        return [('id', 'in', list_ids)]
