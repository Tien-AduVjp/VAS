from odoo import api, SUPERUSER_ID, _
from odoo.exceptions import ValidationError

REQ_STATE_CHANGES = {
    'draft': 'draft',
    'confirm': 'confirm',
    'validate1': 'confirm',
    'validate': 'validate',
    'done': 'done',
    'refuse': 'refuse',
    }

def _fetch_approval_requests(cr):
    """
        This function: fetch all Approval Requests with approvers list by employee.
        Approvers are direct manager, indirect managers, department manager, parent department manager and responsible approval officer.
    """
    cr.execute(
        """
            WITH RECURSIVE raw_parents_tree AS(
                SELECT
                    department_id,
                    CAST(parent_user_id AS VARCHAR),
                    CAST(parent_id AS VARCHAR),
                    id,
                    1 AS tree_level
                FROM hr_employee_with_parent
                WHERE parent_id IS NOT NULL
                UNION
                SELECT
                    hre.department_id,
                    CAST(hre.parent_user_id as VARCHAR) || '->' || CAST(pt.parent_user_id as VARCHAR),
                    CAST(hre.parent_id as VARCHAR) || '->' || CAST(pt.parent_id as VARCHAR),
                    hre.id,
                    pt.tree_level + 1
                FROM hr_employee_with_parent hre
                JOIN raw_parents_tree pt ON pt.id = hre.parent_id
            ),
            hr_employee_with_parent as (
                SELECT
                    hre1.id,
                    hre1.parent_id,
                    hre1.department_id as department_id,
                    hre2.user_id as parent_user_id
                FROM hr_employee as hre1 LEFT JOIN hr_employee as hre2 ON hre1.parent_id = hre2.id
            ),
            parents_tree as (
                SELECT id, MAX(tree_level) AS tl FROM raw_parents_tree GROUP BY id
            ),
            employee_with_parent_tree as (
                SELECT parents_tree.id,
                    raw_parents_tree.department_id,
                    raw_parents_tree.parent_user_id,
                    raw_parents_tree.parent_id,
                    raw_parents_tree.tree_level
                FROM parents_tree
                JOIN raw_parents_tree ON parents_tree.id = raw_parents_tree.id and raw_parents_tree.tree_level = parents_tree.tl
            ),
            department_manager as(
                SELECT
                    hrd.id as dep_id,
                    hrd.manager_id as manager_id,
                    hre.user_id as manager_user_id
                FROM
                    hr_department hrd LEFT JOIN hr_employee hre ON hrd.manager_id = hre.id
            ),
            parent_department_manager as(
                SELECT
                    hrd.id,
                    hrd.name,
                    hrd_1.manager_id AS parent_dep_manager_id,
                    hrd_1.parent_id, hrd_1.name AS parent_name,
                    hre.user_id as parent_dep_manager_user_id,
                    hre.name as parent_manager_name
                FROM hr_department hrd
                LEFT JOIN hr_department hrd_1 ON hrd.parent_id = hrd_1.id
                LEFT JOIN hr_employee hre ON hrd_1.manager_id = hre.id
            )
            SELECT
                r.id as id,
                r.state as state,
                t.legacy_validation_type as type,
                t.legacy_responsible_id as res_id,
                ep.parent_user_id as parent_user_id,
                dm.manager_user_id as dep_manager_user_id,
                r.employee_id,
                dm.manager_id,
                pdm.parent_dep_manager_user_id,
                pdm.parent_dep_manager_id,
                r.legacy_first_approver_id
            FROM approval_request r
            LEFT JOIN approval_request_type t ON r.approval_type_id = t.id
            LEFT JOIN employee_with_parent_tree ep ON r.employee_id = ep.id
            LEFT JOIN department_manager dm ON r.department_id = dm.dep_id
            LEFT JOIN parent_department_manager pdm ON  r.department_id = pdm.id
        """
    )
    return cr.fetchall()


def _update_approval_request_types(env):
    """
    Replace selection as 'no_validation' with manager_approval as 'required'
    Update list approvers for approval type 'both','hr','leader'
    """
    user_admin = env.ref('base.user_admin')
    env.cr.execute(
        """
        SELECT id, legacy_responsible_id, legacy_validation_type
        FROM approval_request_type
        """)
    req_type_rows = env.cr.dictfetchall()
    for row in req_type_rows:
        request_type = env['approval.request.type'].browse(row['id'])
        if row['legacy_validation_type'] == 'hr':
            request_type.write({
                'manager_approval': 'none',
                'mimimum_approvals': 1,
                'type_approval_user_line_ids': [(0, 0, {
                    'request_type_id': row['id'],
                    'user_id': row['legacy_responsible_id'] or user_admin.id,
                    'required': True
                    })]
                })
        elif row['legacy_validation_type'] == 'leader':
            request_type.write({
                'manager_approval': 'required',
                'mimimum_approvals': 1,
                })
        elif row['legacy_validation_type'] == 'both':
            request_type.write({
                'manager_approval': 'required',
                'mimimum_approvals': 2,
                'type_approval_user_line_ids': [(0, 0, {
                    'request_type_id': row['id'],
                    'user_id': row['legacy_responsible_id'] or user_admin.id,
                    'required': True
                    })]
                })
        else:
            request_type.write({
                'manager_approval': 'required',
                'mimimum_approvals': 1,
                })

def _migrate_approval_requests(env):
    env.cr.execute("""
    UPDATE approval_request
        SET deadline = date + interval '1' day,
            state = CASE
                WHEN legacy_state = 'validate1' THEN 'confirm'
                ELSE legacy_state
                END
    """)
    env.cr.execute("""
    SELECT id, legacy_first_approver_id, legacy_second_approver_id
    FROM approval_request
    ORDER BY id ASC
    """)
    all_request_rows = env.cr.dictfetchall()
    all_requests = env['approval.request'].with_context(active_test=False).search([], order='id ASC')
    all_requests.invalidate_cache(ids=all_requests.ids)
    for request, request_row in zip(all_requests, all_request_rows):
        if request.id != request_row['id']:
            stop = True
        approved_uids = []
        if request_row['legacy_first_approver_id']:
            approved_uids.append(request_row['legacy_first_approver_id'])
        if request_row['legacy_second_approver_id'] and request_row['legacy_second_approver_id'] not in approved_uids:
            approved_uids.append(request_row['legacy_second_approver_id'])

        sql = ""
        for approved_uid in approved_uids:
            sql += """
                INSERT INTO request_approval_user_line (sequence, user_id, required, approval_id, state) VALUES %s;
                """ % (
                    (10, approved_uid, True, request.id, 'approved'),
                    )

        for vals in request._prepare_request_approval_user_line_vals_list():
            if vals['user_id'] in approved_uids:
                continue
            if request.state == 'refuse':
                state = 'refused'
            elif request.state == 'confirm':
                state = 'pending'
            elif request.state == 'validate':
                state = 'approved'
            else:
                state = 'draft'
            sql += """
            INSERT INTO request_approval_user_line (sequence, user_id, required, approval_id, state) VALUES %s;
            """ % (
                tuple(list(vals.values()) + [state]),
                )
        if sql:
            env.cr.execute(sql)

    all_requests.invalidate_cache(ids=all_requests.ids)

    env.cr.execute("""
    UPDATE request_approval_user_line AS l
        SET state = CASE
                WHEN req.legacy_state = 'draft' THEN 'draft'
                WHEN req.legacy_state = 'confirm' THEN 'pending'
                WHEN (req.legacy_state = 'validate1' AND l.user_id = req.legacy_first_approver_id) THEN 'approved'
                WHEN (req.legacy_state = 'validate1' AND l.user_id != req.legacy_first_approver_id) THEN 'pending'
                WHEN req.legacy_state = 'validate' THEN 'approved'
                WHEN req.legacy_state = 'done' THEN 'approved'
                WHEN req.legacy_state = 'cancel' THEN 'draft'
                ELSE 'refused'
            END
        FROM approval_request AS req
        WHERE req.id = l.approval_id;
    """)
    all_requests.invalidate_cache(ids=all_requests.ids)
    all_requests._compute_mimimum_approvals()
    all_requests._compute_approvers()
    all_requests._compute_last_approver_id()
    all_requests._compute_next_approver_id()
    all_requests.activity_update()

def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _update_approval_request_types(env)
    _migrate_approval_requests(env)
