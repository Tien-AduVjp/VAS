def migrate(cr, version):
    # ========================================= #
    # - Create new column to table project_task #
    # - Fetch all relationship data             #
    # - Update old data to new field            #
    # - DROP OLD TABLE                          #
    # ========================================= #
    cr.execute("""
ALTER TABLE project_task ADD COLUMN odoo_module_version_id INTEGER;

UPDATE project_task
SET odoo_module_version_id = task_omv_rel.odoo_module_version_id
FROM odoo_module_version_project_task_rel AS task_omv_rel
WHERE project_task.id = task_omv_rel.task_id;

DROP TABLE odoo_module_version_project_task_rel;
    """)
