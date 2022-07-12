from odoo import fields
import pytz

from odoo.tests.common import SavepointCase


class Common(SavepointCase): 
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        cls.employee_01 = cls.env.ref('hr.employee_qdp')
        cls.contracts_emp_01 = cls.env.ref('hr_contract.hr_contract_qdp')
        cls.contracts_emp_01.date_start = fields.Date.subtract(fields.Date.today(), days=1)
        cls.contracts_emp_01.action_start_contract()    
        cls.user_02, cls.user_03 = cls.env['res.users'].create([
            {
                'name':'Mike OT Bot',
                'login':'mike_ot_bot',
                'email':'mike.ot.test@example.viindoo.com',
                'groups_id':[(6, 0, [cls.env.ref('base.group_user').id])]         
            },
            {
                'name':'Lissa OT Bot',
                'login':'lissa_ot_bot',
                'email':'lissa.ot.test@example.viindoo.com',
                'groups_id':[(6, 0, [cls.env.ref('base.group_user').id])]  
            }
        ])    
        cls.user_02.action_create_employee() 
        cls.user_03.action_create_employee()
        cls.env.user.action_create_employee()
        cls.overtime_reason_general = cls.env.ref('viin_hr_overtime.hr_overtime_reason_general')       
        cls.monday_evening_ot_rule = cls.env['hr.overtime.rule'].search(
            [('weekday', '=', '0'),
            ('code', '=', cls.env.ref('viin_hr_overtime.rule_code_ot1822').name),
            ('company_id', '=', cls.env.company.id)
        ], limit=1)   
        cls.user_01 = cls.employee_01.user_id
        cls.overtime_plan_emp_01, cls.overtime_plan_emp_02 = cls.env['hr.overtime.plan'].create([
            {
                'employee_id':cls.employee_01.id,
                'reason_id':cls.env.ref('viin_hr_overtime.hr_overtime_reason_project').id,
                'recognition_mode':'none'        
            },
            {
                'employee_id':cls.user_02.employee_id.id,
                'reason_id':cls.env.ref('viin_hr_overtime.hr_overtime_reason_project').id,
                'recognition_mode':'none'  
            }
        ])        
        cls.next_monday = cls._generate_overtime_plan_date(0) 
        cls.company_01 = cls.env['res.company'].create({
            'name':'Viin Company'
        })
       
    @classmethod
    def _generate_overtime_plan_date(cls, weekday):
        """
            This function will calculate date by next day in week.
        """
        return cls.env['to.base'].next_weekday(fields.Date.today(), weekday)
    
    def _utcoffset_by_hours(self, user_tz):
        tz = pytz.timezone(user_tz)
        tz_offset = tz.utcoffset(fields.datetime(2021, 6, 6)).total_seconds() / 3600
        user_time = self.env['to.base'].time_to_float_hour(fields.datetime.max) % 1 - 1 + tz_offset   
        return user_time
    
    @classmethod
    def _calculate_overtime_line(cls, ot_plan, day_ot_rules, contract): 
        """
            This function will calculate OT line by OT period time, working time by employee contract and OT rules by employee company
        """
        if(
            ot_plan.time_start > ot_plan.time_end 
            or not day_ot_rules 
            or not contract 
            or contract.state not in ['open', 'close']
            or contract.date_start > ot_plan.date_end.date()           
            or contract.date_end and contract.date_end < ot_plan.date_start.date()
        ):
            return []
        
        day_ot_rules = day_ot_rules.mapped(lambda r: (r.id, (r.hour_from, r.hour_to)))
        periods_rule = [ period for _, period in day_ot_rules]   
        
        working_time = contract.resource_calendar_id.attendance_ids\
                        .filtered(lambda r: r.dayofweek == str(ot_plan.date.weekday()))\
                        .mapped(lambda r: (r.hour_from, r.hour_to))
        
        timeline = sum((
                            sum(periods_rule, ()),
                            sum(working_time, ()),
                            (ot_plan.time_start, ot_plan.time_end)
                    ), ())
        
        # the time of OT rule will change if date start of contract is same with the date OT plan.
        if contract.date_start == ot_plan.date_end.date() != ot_plan.date_start.date():
            timeline = list(timeline)
            tz_offset = cls._utcoffset_by_hours(cls, ot_plan.employee_id.tz) 
            timeline = [time for time in timeline if time > tz_offset]
            timeline.insert(0, tz_offset)   
            timeline = tuple(timeline)
        # the time of OT rule will change if date end of contract is same with the date OT plan.   
        if contract.date_end == ot_plan.date_start.date() != ot_plan.date_end.date():
            timeline = list(timeline)
            tz_offset = cls._utcoffset_by_hours(cls, ot_plan.employee_id.tz)   
            timeline = [time for time in timeline if time < tz_offset]
            timeline.append(tz_offset)   
            timeline = tuple(timeline)
        
        time_inside_ot_period = list(filter(lambda r: r >= ot_plan.time_start and r <= ot_plan.time_end, sorted(set(timeline))))
        intervals = [(time, time_inside_ot_period[pos + 1]) for pos, time in  enumerate(time_inside_ot_period[0:len(time_inside_ot_period) - 1])]
        
        i = 0
        while i < len(intervals):
            (time_start, time_end) = intervals[i]
            for (working_start_time, working_end_time) in working_time: 
                if time_start >= working_start_time and time_end <= working_end_time:
                    del intervals[i]# remove OT interval belong to the working time
                    if i < len(intervals):
                        (time_start, time_end) = intervals[i]
                    break
            for rule_id, (rule_hour_start, rule_hour_end) in day_ot_rules: 
                if i< len(intervals) and time_start >= rule_hour_start and time_end <= rule_hour_end:
                    intervals[i] = (rule_id, (time_start, time_end))# add OT rule_id to OT line.
                    break
            i += 1
        return intervals
