from odoo import fields, models, api, _

OVERTIME_RECOGNITION_MODE = [('none', 'By Plan')]


class ResCompany(models.Model):
    _inherit = 'res.company'

    overtime_recognition_mode = fields.Selection(OVERTIME_RECOGNITION_MODE, string='Overtime Recognition Mode', default='none', required=True,
                                            help="This indicates mode to recognize actual overtime against the plan which could be either"
                                            " By Plan or Attendance or Timesheet. Bridging modules will be required to have full"
                                            " options accordingly.")

    @api.model_create_multi
    @api.returns('self', lambda value:value.id)
    def create(self, vals_list):
        companies = super(ResCompany, self).create(vals_list)
        companies.sudo()._generate_overtime_rules()
        return companies

    def _prepare_overtime_rule_vals_list(self):
        self.ensure_one()

        vals_list = []

        all_rules = self.env['hr.overtime.rule'].search([('company_id', '=', self.id)])
        for rule in [
            {'name': _('Monday Early Morning'), 'weekday': '0', 'hour_from': 0, 'hour_to': 6, 'code_id': self.env.ref('viin_hr_overtime.rule_code_ot0006').id, 'holiday': False, 'company_id': self.id},
            {'name': _('Monday Daytime'), 'weekday': '0', 'hour_from': 6, 'hour_to': 18, 'code_id': self.env.ref('viin_hr_overtime.rule_code_ot0618').id, 'holiday': False, 'company_id': self.id},
            {'name': _('Monday Evening'), 'weekday': '0', 'hour_from': 18, 'hour_to': 22, 'code_id': self.env.ref('viin_hr_overtime.rule_code_ot1822').id, 'holiday': False, 'company_id': self.id},
            {'name': _('Monday Night'), 'weekday': '0', 'hour_from': 22, 'hour_to': 24, 'code_id': self.env.ref('viin_hr_overtime.rule_code_ot2224').id, 'holiday': False, 'company_id': self.id},
            
            {'name': _('Tuesday Early Morning'), 'weekday': '1', 'hour_from': 0, 'hour_to': 6, 'code_id': self.env.ref('viin_hr_overtime.rule_code_ot0006').id, 'holiday': False, 'company_id': self.id},
            {'name': _('Tuesday Daytime'), 'weekday': '1', 'hour_from': 6, 'hour_to': 18, 'code_id': self.env.ref('viin_hr_overtime.rule_code_ot0618').id, 'holiday': False, 'company_id': self.id},
            {'name': _('Tuesday Evening'), 'weekday': '1', 'hour_from': 18, 'hour_to': 22, 'code_id': self.env.ref('viin_hr_overtime.rule_code_ot1822').id, 'holiday': False, 'company_id': self.id},
            {'name': _('Tuesday Night'), 'weekday': '1', 'hour_from': 22, 'hour_to': 24, 'code_id': self.env.ref('viin_hr_overtime.rule_code_ot2224').id, 'holiday': False, 'company_id': self.id},
            
            {'name': _('Wednesday Early Morning'), 'weekday': '2', 'hour_from': 0, 'hour_to': 6, 'code_id': self.env.ref('viin_hr_overtime.rule_code_ot0006').id, 'holiday': False, 'company_id': self.id},
            {'name': _('Wednesday Daytime'), 'weekday': '2', 'hour_from': 6, 'hour_to': 18, 'code_id': self.env.ref('viin_hr_overtime.rule_code_ot0618').id, 'holiday': False, 'company_id': self.id},
            {'name': _('Wednesday Evening'), 'weekday': '2', 'hour_from': 18, 'hour_to': 22, 'code_id': self.env.ref('viin_hr_overtime.rule_code_ot1822').id, 'holiday': False, 'company_id': self.id},
            {'name': _('Wednesday Night'), 'weekday': '2', 'hour_from': 22, 'hour_to': 24, 'code_id': self.env.ref('viin_hr_overtime.rule_code_ot2224').id, 'holiday': False, 'company_id': self.id},

            {'name': _('Thursday Early Morning'), 'weekday': '3', 'hour_from': 0, 'hour_to': 6, 'code_id': self.env.ref('viin_hr_overtime.rule_code_ot0006').id, 'holiday': False, 'company_id': self.id},
            {'name': _('Thursday Daytime'), 'weekday': '3', 'hour_from': 6, 'hour_to': 18, 'code_id': self.env.ref('viin_hr_overtime.rule_code_ot0618').id, 'holiday': False, 'company_id': self.id},
            {'name': _('Thursday Evening'), 'weekday': '3', 'hour_from': 18, 'hour_to': 22, 'code_id': self.env.ref('viin_hr_overtime.rule_code_ot1822').id, 'holiday': False, 'company_id': self.id},
            {'name': _('Thursday Night'), 'weekday': '3', 'hour_from': 22, 'hour_to': 24, 'code_id': self.env.ref('viin_hr_overtime.rule_code_ot2224').id, 'holiday': False, 'company_id': self.id},
            
            {'name': _('Friday Early Morning'), 'weekday': '4', 'hour_from': 0, 'hour_to': 6, 'code_id': self.env.ref('viin_hr_overtime.rule_code_ot0006').id, 'holiday': False, 'company_id': self.id},
            {'name': _('Friday Daytime'), 'weekday': '4', 'hour_from': 6, 'hour_to': 18, 'code_id': self.env.ref('viin_hr_overtime.rule_code_ot0618').id, 'holiday': False, 'company_id': self.id},
            {'name': _('Friday Evening'), 'weekday': '4', 'hour_from': 18, 'hour_to': 22, 'code_id': self.env.ref('viin_hr_overtime.rule_code_ot1822').id, 'holiday': False, 'company_id': self.id},
            {'name': _('Friday Night'), 'weekday': '4', 'hour_from': 22, 'hour_to': 24, 'code_id': self.env.ref('viin_hr_overtime.rule_code_ot2224').id, 'holiday': False, 'company_id': self.id},
            
            {'name': _('Saturday Early Morning'), 'weekday': '5', 'hour_from': 0, 'hour_to': 6, 'code_id': self.env.ref('viin_hr_overtime.rule_code_otsat0006').id, 'holiday': False, 'company_id': self.id},
            {'name': _('Saturday Morning'), 'weekday': '5', 'hour_from': 6, 'hour_to': 12, 'code_id': self.env.ref('viin_hr_overtime.rule_code_otsat0612').id, 'holiday': False, 'company_id': self.id},
            {'name': _('Saturday Afternoon'), 'weekday': '5', 'hour_from': 12, 'hour_to': 18, 'code_id': self.env.ref('viin_hr_overtime.rule_code_otsat1218').id, 'holiday': False, 'company_id': self.id},
            {'name': _('Saturday Evening'), 'weekday': '5', 'hour_from': 18, 'hour_to': 22, 'code_id': self.env.ref('viin_hr_overtime.rule_code_otsat1822').id, 'holiday': False, 'company_id': self.id},
            {'name': _('Saturday Night'), 'weekday': '5', 'hour_from': 22, 'hour_to': 24, 'code_id': self.env.ref('viin_hr_overtime.rule_code_otsat2224').id, 'holiday': False, 'company_id': self.id},
            
            {'name': _('Sunday Early Morning'), 'weekday': '6', 'hour_from': 0, 'hour_to': 6, 'code_id': self.env.ref('viin_hr_overtime.rule_code_otsun0006').id, 'holiday': False, 'company_id': self.id},
            {'name': _('Sunday Morning'), 'weekday': '6', 'hour_from': 6, 'hour_to': 12, 'code_id': self.env.ref('viin_hr_overtime.rule_code_otsun0612').id, 'holiday': False, 'company_id': self.id},
            {'name': _('Sunday Afternoon'), 'weekday': '6', 'hour_from': 12, 'hour_to': 18, 'code_id': self.env.ref('viin_hr_overtime.rule_code_otsun1218').id, 'holiday': False, 'company_id': self.id},
            {'name': _('Sunday Evening'), 'weekday': '6', 'hour_from': 18, 'hour_to': 22, 'code_id': self.env.ref('viin_hr_overtime.rule_code_otsun1822').id, 'holiday': False, 'company_id': self.id},
            {'name': _('Sunday Night'), 'weekday': '6', 'hour_from': 22, 'hour_to': 24, 'code_id': self.env.ref('viin_hr_overtime.rule_code_otsun2224').id, 'holiday': False, 'company_id': self.id},
            ]:
            is_existing = False
            for r in all_rules:
                if rule['weekday'] == r.weekday and rule['holiday'] == r.holiday and rule['hour_from'] == r.hour_from and rule['hour_to'] == r.hour_to:
                    is_existing = True
                    break
            if not is_existing:
                vals_list.append(rule)
        return vals_list

    def _prepare_holiday_overtime_rule_vals_list(self):
        self.ensure_one()

        vals_list = []

        all_rules = self.env['hr.overtime.rule'].search([('company_id', '=', self.id)])
        for rule in [
            {'name': _('Holiday - Monday Early Morning'), 'weekday': '0', 'hour_from': 0, 'hour_to': 6, 'code_id': self.env.ref('viin_hr_overtime.rule_code_othol0006').id, 'holiday': True, 'company_id': self.id},
            {'name': _('Holiday - Monday Daytime'), 'weekday': '0', 'hour_from': 6, 'hour_to': 18, 'code_id': self.env.ref('viin_hr_overtime.rule_code_othol0618').id, 'holiday': True, 'company_id': self.id},
            {'name': _('Holiday - Monday Evening'), 'weekday': '0', 'hour_from': 18, 'hour_to': 22, 'code_id': self.env.ref('viin_hr_overtime.rule_code_othol1822').id, 'holiday': True, 'company_id': self.id},
            {'name': _('Holiday - Monday Night'), 'weekday': '0', 'hour_from': 22, 'hour_to': 24, 'code_id': self.env.ref('viin_hr_overtime.rule_code_othol2224').id, 'holiday': True, 'company_id': self.id},
            
            {'name': _('Holiday - Tuesday Early Morning'), 'weekday': '1', 'hour_from': 0, 'hour_to': 6, 'code_id': self.env.ref('viin_hr_overtime.rule_code_othol0006').id, 'holiday': True, 'company_id': self.id},
            {'name': _('Holiday - Tuesday Daytime'), 'weekday': '1', 'hour_from': 6, 'hour_to': 18, 'code_id': self.env.ref('viin_hr_overtime.rule_code_othol0618').id, 'holiday': True, 'company_id': self.id},
            {'name': _('Holiday - Tuesday Evening'), 'weekday': '1', 'hour_from': 18, 'hour_to': 22, 'code_id': self.env.ref('viin_hr_overtime.rule_code_othol1822').id, 'holiday': True, 'company_id': self.id},
            {'name': _('Holiday - Tuesday Night'), 'weekday': '1', 'hour_from': 22, 'hour_to': 24, 'code_id': self.env.ref('viin_hr_overtime.rule_code_othol2224').id, 'holiday': True, 'company_id': self.id},
            
            {'name': _('Holiday - Wednesday Early Morning'), 'weekday': '2', 'hour_from': 0, 'hour_to': 6, 'code_id': self.env.ref('viin_hr_overtime.rule_code_othol0006').id, 'holiday': True, 'company_id': self.id},
            {'name': _('Holiday - Wednesday Daytime'), 'weekday': '2', 'hour_from': 6, 'hour_to': 18, 'code_id': self.env.ref('viin_hr_overtime.rule_code_othol0618').id, 'holiday': True, 'company_id': self.id},
            {'name': _('Holiday - Wednesday Evening'), 'weekday': '2', 'hour_from': 18, 'hour_to': 22, 'code_id': self.env.ref('viin_hr_overtime.rule_code_othol1822').id, 'holiday': True, 'company_id': self.id},
            {'name': _('Holiday - Wednesday Night'), 'weekday': '2', 'hour_from': 22, 'hour_to': 24, 'code_id': self.env.ref('viin_hr_overtime.rule_code_othol2224').id, 'holiday': True, 'company_id': self.id},

            {'name': _('Holiday - Thursday Early Morning'), 'weekday': '3', 'hour_from': 0, 'hour_to': 6, 'code_id': self.env.ref('viin_hr_overtime.rule_code_othol0006').id, 'holiday': True, 'company_id': self.id},
            {'name': _('Holiday - Thursday Daytime'), 'weekday': '3', 'hour_from': 6, 'hour_to': 18, 'code_id': self.env.ref('viin_hr_overtime.rule_code_othol0618').id, 'holiday': True, 'company_id': self.id},
            {'name': _('Holiday - Thursday Evening'), 'weekday': '3', 'hour_from': 18, 'hour_to': 22, 'code_id': self.env.ref('viin_hr_overtime.rule_code_othol1822').id, 'holiday': True, 'company_id': self.id},
            {'name': _('Holiday - Thursday Night'), 'weekday': '3', 'hour_from': 22, 'hour_to': 24, 'code_id': self.env.ref('viin_hr_overtime.rule_code_othol2224').id, 'holiday': True, 'company_id': self.id},
            
            {'name': _('Holiday - Friday Early Morning'), 'weekday': '4', 'hour_from': 0, 'hour_to': 6, 'code_id': self.env.ref('viin_hr_overtime.rule_code_othol0006').id, 'holiday': True, 'company_id': self.id},
            {'name': _('Holiday - Friday Daytime'), 'weekday': '4', 'hour_from': 6, 'hour_to': 18, 'code_id': self.env.ref('viin_hr_overtime.rule_code_othol0618').id, 'holiday': True, 'company_id': self.id},
            {'name': _('Holiday - Friday Evening'), 'weekday': '4', 'hour_from': 18, 'hour_to': 22, 'code_id': self.env.ref('viin_hr_overtime.rule_code_othol1822').id, 'holiday': True, 'company_id': self.id},
            {'name': _('Holiday - Friday Night'), 'weekday': '4', 'hour_from': 22, 'hour_to': 24, 'code_id': self.env.ref('viin_hr_overtime.rule_code_othol2224').id, 'holiday': True, 'company_id': self.id},
            
            {'name': _('Holiday - Saturday Early Morning'), 'weekday': '5', 'hour_from': 0, 'hour_to': 6, 'code_id': self.env.ref('viin_hr_overtime.rule_code_otholsat0006').id, 'holiday': True, 'company_id': self.id},
            {'name': _('Holiday - Saturday Morning'), 'weekday': '5', 'hour_from': 6, 'hour_to': 12, 'code_id': self.env.ref('viin_hr_overtime.rule_code_otholsat0612').id, 'holiday': True, 'company_id': self.id},
            {'name': _('Holiday - Saturday Afternoon'), 'weekday': '5', 'hour_from': 12, 'hour_to': 18, 'code_id': self.env.ref('viin_hr_overtime.rule_code_otholsat1218').id, 'holiday': True, 'company_id': self.id},
            {'name': _('Holiday - Saturday Evening'), 'weekday': '5', 'hour_from': 18, 'hour_to': 22, 'code_id': self.env.ref('viin_hr_overtime.rule_code_otholsat1822').id, 'holiday': True, 'company_id': self.id},
            {'name': _('Holiday - Saturday Night'), 'weekday': '5', 'hour_from': 22, 'hour_to': 24, 'code_id': self.env.ref('viin_hr_overtime.rule_code_otholsat2224').id, 'holiday': True, 'company_id': self.id},
            
            {'name': _('Holiday - Sunday Early Morning'), 'weekday': '6', 'hour_from': 0, 'hour_to': 6, 'code_id': self.env.ref('viin_hr_overtime.rule_code_otholsun0006').id, 'holiday': True, 'company_id': self.id},
            {'name': _('Holiday - Sunday Morning'), 'weekday': '6', 'hour_from': 6, 'hour_to': 12, 'code_id': self.env.ref('viin_hr_overtime.rule_code_otholsun0612').id, 'holiday': True, 'company_id': self.id},
            {'name': _('Holiday - Sunday Afternoon'), 'weekday': '6', 'hour_from': 12, 'hour_to': 18, 'code_id': self.env.ref('viin_hr_overtime.rule_code_otholsun1218').id, 'holiday': True, 'company_id': self.id},
            {'name': _('Holiday - Sunday Evening'), 'weekday': '6', 'hour_from': 18, 'hour_to': 22, 'code_id': self.env.ref('viin_hr_overtime.rule_code_otholsun1822').id, 'holiday': True, 'company_id': self.id},
            {'name': _('Holiday - Sunday Night'), 'weekday': '6', 'hour_from': 22, 'hour_to': 24, 'code_id': self.env.ref('viin_hr_overtime.rule_code_otholsun2224').id, 'holiday': True, 'company_id': self.id},
            ]:
            is_existing = False
            for r in all_rules:
                if rule['weekday'] == r.weekday and rule['holiday'] == r.holiday and rule['hour_from'] == r.hour_from and rule['hour_to'] == r.hour_to:
                    is_existing = True
                    break
            if not is_existing:
                vals_list.append(rule)
        return vals_list

    def _generate_overtime_rules(self):
        vals_list = []
        for r in self:
            vals_list += r._prepare_overtime_rule_vals_list() + r._prepare_holiday_overtime_rule_vals_list()
        return self.env['hr.overtime.rule'].create(vals_list)
    
