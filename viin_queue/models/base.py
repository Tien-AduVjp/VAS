from odoo import models


class BaseModel(models.AbstractModel):
    _inherit = 'base'

    def _select_for_update_skip_locked(self):
        if not self or not self._table:
            return self
        self.env.cr.execute("SELECT id FROM %s WHERE id IN %%s FOR UPDATE SKIP LOCKED" % self._table, [tuple(self.ids)])
        ids = set(row[0] for row in self.env.cr.fetchall())
        return self.filtered(lambda r: r.id in ids)
