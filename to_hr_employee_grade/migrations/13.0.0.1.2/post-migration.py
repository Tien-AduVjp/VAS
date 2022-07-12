def _remove_no_of_employee(cr):
    cr.execute("ALTER TABLE hr_employee_grade DROP COLUMN no_of_employee;")


def migrate(cr, version):
    _remove_no_of_employee(cr)

