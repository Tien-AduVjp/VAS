from . import models
from odoo.tools.sql import column_exists, create_column


def _pre_init_hook(cr): 
    _update_project(cr)    
    _update_project_task(cr)


def _update_project(cr):
    """ Allow installing module in database with large project table.
        - Creating the computed+stored field project.department_id.
    """
    if not column_exists(cr, 'project_project', 'department_id'):
        create_column(cr, 'project_project', 'department_id', 'integer')   
    cr.execute("""UPDATE project_project
                  SET 
                  department_id=hre.department_id
                  FROM hr_employee as hre
                  WHERE project_project.user_id = hre.user_id;
               """)


def _update_project_task(cr): 
    """ Allow installing module in database with large project.task table.
        - Creating the related+stored field project_task.assign_employee_id.
        - Creating the related+stored field project_task.department_id.  
    """   
  
    if not column_exists(cr, 'project_task', 'department_id'):
        create_column(cr, 'project_task', 'department_id', 'integer')
    if not column_exists(cr, 'project_task', 'assign_employee_id'):
        create_column(cr, 'project_task', 'assign_employee_id', 'integer')
    cr.execute("""
                WITH task_employee_project AS (
                    SELECT t.id AS task_id, emp.id AS emp_id, pj.department_id AS dep_id
                    FROM project_task AS t
                    LEFT JOIN res_users AS u ON t.user_id = u.id
                    LEFT JOIN hr_employee AS emp ON u.id = emp.user_id AND (emp.company_id = t.company_id OR emp.company_id IS NULL)
                    LEFT JOIN project_project AS pj ON t.project_id = pj.id
                )
                UPDATE project_task as pjt
                SET
                    assign_employee_id= tep.emp_id,
                    department_id= tep.dep_id
                FROM task_employee_project AS tep
                WHERE pjt.id = tep.task_id;
            """)
