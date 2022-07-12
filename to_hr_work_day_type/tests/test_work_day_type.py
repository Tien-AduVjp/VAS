from odoo.tests import HttpCase, tagged
from odoo.exceptions import ValidationError, UserError
from odoo.addons.mail.models.mail_template import format_date

@tagged('post_install', '-at_install')
class TestWorkDayType(HttpCase):
    
    def setUp(self):
        super(TestWorkDayType, self).setUp()
        self.work_day_type1 = self.env['work.day.type'].create({
            'name': 'Overtime 01',
            'rate': '200',
            'date_from': '2020-01-01',
            'date_to': '2020-01-15',
            })
        self.work_day_type2 = self.env['work.day.type'].create({
            'name': 'Overtime 02',
            'rate': '300',
            'date_from': '2020-01-15',
            'date_to': '2020-01-20',
            })

    def test_constrains_dates(self):
        with self.assertRaises(ValidationError):
            self.work_day_type2.date_to = '2020-01-14'
        
    def test_check_overlap(self):
        #Test create new work day type overlap with work_day_type1, ValidationError exceptions is occurred
        with self.assertRaises(ValidationError, msn="ValidationError not raised"):
            self.work_day_type2.write({'date_from': '2020-01-14'})
    
    def test_name_get(self):
        display_name = '%s [%s - %s]' % (self.work_day_type1.name, format_date(self.env, self.work_day_type1.date_from), format_date(self.env, self.work_day_type1.date_to)) 
        self.assertEqual(self.work_day_type1.display_name, display_name, "No matching record found")
        
    def test_name_search(self):
        work_day_type = self.env['work.day.type']
        #Test search with date_from
        search_date_from = work_day_type.name_search('2020-01-01')
        self.assertEqual({self.work_day_type1.id}, set([r[0] for r in search_date_from]), "name_search ilike date from have returned incorrect")
        #Test search with date_to
        search_date_to = work_day_type.name_search('2020-01-20')
        self.assertEqual({self.work_day_type2.id}, set([r[0] for r in search_date_to]), "name_search ilike date to have returned incorrect")
        #Test search with name
        search_name = work_day_type.name_search('Overtime 02')
        self.assertEqual({self.work_day_type2.id}, set([r[0] for r in search_name]), "name_search ilike name have returned incorrect")
    
    def test_unlink(self):
        normal_work_day = self.env.ref('to_hr_work_day_type.normal_work_day')
        #Test delete non-normal_work_day record
        self.work_day_type1.unlink()

        #Test delete normal_work_day record
        with self.assertRaises(UserError, msn="UserError not raised"):
            normal_work_day.unlink()
