from odoo.tests import tagged
from odoo.exceptions import ValidationError

from .test_to_hr_training_common import TestTrainingCommon

@tagged('post_install','-at_install')
class TestGradeFunction(TestTrainingCommon):
# Test functional
    """
        Case 1: Check data synchronize between e-learning courses and HR required training
    """
    def test_01_edit_course(self): 
        slides_channel_ids = (self.garden_basic | self.garden_advance).ids
        search_requires_training = self.env['slide.channel'].search([])
        filter_requires_training_ids = search_requires_training.filtered(
                        lambda l: l.id in slides_channel_ids
                        ).ids
        self.assertEqual(
                    slides_channel_ids, 
                    filter_requires_training_ids, 
                    'the {} is equal to {}'.format(slides_channel_ids, filter_requires_training_ids)
                    )
        
    def test_02_edit_grade(self):
        courses = (self.garden_course1 | self.tree_course1)
        filter_courses_ids = courses.slide_channel_id.ids
        self.intern.update({
                'require_training_ids': [(4,x) for x in courses.ids]
                })
        self.employeea.update({'grade_id': self.intern.id})
        search_training_courses = self.env['hr.employee.training.line'].search([
            ('employee_id', '=', self.employeea.id)])
        filter_training_courses_ids = search_training_courses.slide_channel_id.ids
        self.assertEqual(
                    filter_courses_ids, 
                    filter_training_courses_ids, 
                    'the {} is equal to {}'.format(filter_courses_ids, filter_training_courses_ids)
                    )
        
    """
        Case 3: Courses and require hours will be calculated by the course according to
        that employee's grade/job and all below grade of an employee.
    """
    def test_03_edit_grade(self):
        self.intern.update({
                        'require_training_ids': [
                                        (4, self.garden_course1.id),
                                        (4, self.tree_course1.id)
                                        ], 
                        'parent_id':self.junior.id
                        })
        self.junior.update({
                        'require_training_ids': [
                                    (4, self.garden_course2.id), 
                                    (4, self.tree_course2.id)
                                    ]
                            })
        self.job_position.update({
                        'require_training_ids': [
                                    (4,self.garden_course3.id), 
                                    (4,self.tree_course3.id)
                                    ]
                                })
        self.employeea.update({
                        'job_id': self.job_position.id, 
                        'grade_id': self.junior.id
                        })
        search_garden_course = self.employeea.training_line_ids.filtered(
                        lambda l: l.slide_channel_id == self.garden_basic
                        )
        search_tree_course = self.employeea.training_line_ids.filtered(
                        lambda l: l.slide_channel_id == self.tree_basic
                        )
        self.assertEqual(
                    search_garden_course.require_hour, 9, 
                    'the {} not equal to {}'.format(search_garden_course.require_hour, 9)
                    )
        self.assertEqual(
                    search_tree_course.require_hour, 9,
                    'the {} not equal to {}'.format(search_tree_course.require_hour, 9)
                    )
        
    """ 
        Case 4: Unlink a grade, require hours will be recalculated by the course according to
        that employee's grade/job and all below grade of an employee.
    """
    def test_04_unlink_grade(self):
        self.intern.update({
                    'require_training_ids': [(4,self.garden_course1.id)],
                    'parent_id':self.junior.id
                    })
        self.junior.update({
                    'require_training_ids': [
                                    (4,self.garden_course2.id), 
                                    (4,self.tree_course1.id)
                                    ]
                    })
        self.job_position.update({
                        'require_training_ids': [
                                    (4,self.garden_course3.id), 
                                    (4,self.tree_course2.id)]
                        })
        self.employeea.update({
                        'job_id': self.job_position.id, 
                        'grade_id': self.junior.id
                        })
        self.intern.unlink()
        search_garden_course = self.employeea.training_line_ids.filtered(
                        lambda l: l.slide_channel_id == self.garden_basic
                        )
        search_tree_course = self.employeea.training_line_ids.filtered(
                        lambda l: l.slide_channel_id == self.tree_basic
                        )
        self.assertEqual(
                search_garden_course[0].require_hour,
                4, 
                'the {} not equal to {}'.format(search_garden_course.require_hour, 4)
                )
        self.assertEqual(
                search_tree_course[0].require_hour,
                8,
                'the {} not equal to {}'.format(search_tree_course.require_hour, 8)
                )
         
    """
        Case 5: Archive a course
    """
    def test_05_archive_course(self):
        python_beginer = self.env['slide.channel'].create({
                                'name':'python beginner'
                                    })
        python_beginer.active = False
        python_in_course = self.env['hr.require.training'].search([
                                ('slide_channel_id', '=',python_beginer.id)
                                ])
        self.assertEqual(
                python_in_course.id, 
                False, 
                'the {} not equal to {}'.format(python_in_course.id, False)
                )
        

