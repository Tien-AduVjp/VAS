from datetime import date

from odoo.tests import SavepointCase, tagged
from odoo import fields


@tagged('post_install','-at_install')
class TestHrProjectTask(SavepointCase):
    
    @classmethod
    def setUpClass(cls):
        super(TestHrProjectTask, cls).setUpClass()
        cls.project_01 = cls.env['project.project'].create({
            'name': 'New Project For Testing'
        })
        cls.task_01 = cls.env.ref('project.project_task_1').copy()
        cls.task_01.project_id = cls.project_01.id
        cls.task_02 = cls.env.ref('project.project_task_2').copy()
        cls.task_02.project_id = cls.project_01.id
        cls.emp_01 = cls.env.ref('hr.employee_mit').copy()
        cls.emp_02= cls.env.ref('hr.employee_stw').copy()
        cls.emp_03 =cls.env.ref('hr.employee_ngh').copy()
    
    def test_01_compute_associated_employees_department_of_task(self):
        """
            Testcase 1 + 2 +3: Kiểm tra tính toán nhân viên liên quan, phòng ban liên quan đến một nhiệm vụ, phòng ban liên quan đến dự án
            Expect
                +) Nhân sự liên quan đến nhiệm vụ dự án sẽ bao gồm tất cả những người đã chấm công vào nhiệm vụ đó. (gồm cả những người thuộc phòng ban khác)
                +) Phòng ban liên quan đến nhiệm vụ dự án sẽ bao phòng ban có nhân sự đã chấm công vào nhiệm vụ đó.
                +) Phòng ban liên quan đến dự án sẽ bao gồm các phòng ban có nhân sự chấm công vào nhiệm vụ thuộc dự án đó.
        """
        self.task_01.update({
            'timesheet_ids':[
                (0, 0, {
                    'name':'Research new project',
                    'employee_id':self.emp_01.id,
                    'date':fields.Date.today(),
                    'time_start':19.0,
                    'unit_amount':1.0,
                    'project_id':self.project_01.id
                }),
                (0, 0, {
                    'name':'Research new project',
                    'employee_id':self.emp_02.id,
                    'date':fields.Date.today(),
                    'time_start':19.0,
                    'unit_amount':1.0,
                    'project_id':self.project_01.id                   
                }),
                (0, 0, {
                    'name':'Research new project',
                    'employee_id':self.emp_03.id,
                    'date':fields.Date.today(),
                    'time_start':19.0,
                    'unit_amount':1.0,
                    'project_id':self.project_01.id                
                })
            ]
        })
        self.assertEqual(self.task_01.employee_ids, self.emp_01 | self.emp_02 | self.emp_03)
        self.assertEqual(self.task_01.associated_department_ids, self.emp_01.department_id | self.emp_03.department_id) 
        self.assertEqual(self.project_01.associated_department_ids, self.emp_01.department_id | self.emp_03.department_id)
        
    def test_02_filter_tasks_associated_to_user_subordinate(self):
        """
            Test case: Kiểm tra chức năng lọc nhiệm vụ dự án theo "Nhiệm vụ liên quan đến nhân viên cấp dưới".
        """
        self.emp_02.parent_id = self.emp_01.id
        self.emp_03.parent_id = self.emp_02.id
        self.task_01.update({
            'timesheet_ids':[
                (0, 0, {
                    'name':'Research new project',
                    'employee_id':self.emp_02.id,
                    'date':fields.Date.today(),
                    'time_start':18.0,
                    'unit_amount':1.0,
                    'project_id':self.project_01.id                   
                })               
            ]
        })
        self.task_02.update({
            'timesheet_ids':[
                (0, 0, {
                    'name':'Research new project',
                    'employee_id':self.emp_03.id,
                    'date':fields.Date.today(),
                    'time_start':19.0,
                    'unit_amount':1.0,
                    'project_id':self.project_01.id                  
                })               
            ]
        })        
        user_subordinate_tasks = self.env['project.task'].search([('employee_ids','in',self.emp_01.subordinate_ids.ids)])
        self.assertEqual(user_subordinate_tasks, self.task_01 | self.task_02)
    
    def test_03_filter_tasks_associated_to_user_department(self):
        """
            Testcase: Kiểm tra chức năng lọc nhiệm vụ dự án theo "Nhiệm vụ liên quan đến phòng"
            Expect: Hiển thị tất cả các dự án mà nhân viên của phòng đã chấm công.
        """
        self.dep_01 = self.env.ref('hr.dep_rd').copy()
        self.emp_02.department_id = self.dep_01
        self.emp_03.department_id = self.dep_01
        self.task_01.update({
            'timesheet_ids':[
                (0, 0, {
                    'name':'Research new project',
                    'employee_id':self.emp_02.id,
                    'date':fields.Date.today(),
                    'time_start':18.0,
                    'unit_amount':1.0,
                    'project_id':self.project_01.id                   
                })               
            ]
        })
        self.task_02.update({
            'timesheet_ids':[
                (0, 0, {
                    'name':'Research new project',
                    'employee_id':self.emp_03.id,
                    'date':fields.Date.today(),
                    'time_start':19.0,
                    'unit_amount':1.0,
                    'project_id':self.project_01.id                  
                })               
            ]
        })       
        user_department_tasks = self.env['project.task'].search([('associated_department_ids','in',[self.emp_02.department_id.id])])
        self.assertEqual(user_department_tasks, self.task_01 | self.task_02)
    
    def test_04_filter_tasks_assigned_to_user_department(self):
        """
            Test case: Kiểm tra chức năng lọc nhiệm vụ dự án theo "Nhiệm vụ của phòng"
            Expect: Hiển thị tất cả các nhiệm vụ thuộc dự án được giao cho phòng.
        """
        self.dep_01 = self.env.ref('hr.dep_rd').copy()
        self.emp_02.department_id = self.dep_01.id
        self.emp_03.department_id = self.dep_01.id
        self.project_01.department_id = self.dep_01.id       
        department_tasks = self.env['project.task'].search([('department_id','=',self.dep_01.id)])
        self.assertEqual(department_tasks, self.task_01 | self.task_02)
    
    def test_05_filter_tasks_assigned_to_user_subordinate(self):
        """
            Testcase: Kiểm tra chức năng lọc nhiệm vụ giao cho nhân viên dưới quyền.
            Expect: Hiển thị tất cả nhiệm vụ được giao cho nhân viên dưới quyền.
        """
        self.emp_02.parent_id = self.emp_01.id
        self.emp_03.parent_id = self.emp_02.id
        self.task_01.update({
            'assign_employee_id':self.emp_02.id
        })
        self.task_02.update({
            'assign_employee_id':self.emp_03.id
        }) 
        user_subordinate_assigned_tasks = self.env['project.task'].search([('assign_employee_id','in',self.emp_01.subordinate_ids.ids)])
        self.assertEqual(user_subordinate_assigned_tasks, self.task_01 | self.task_02)
