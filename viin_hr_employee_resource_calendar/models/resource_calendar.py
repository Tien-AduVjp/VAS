from odoo import models


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    def _get_leave_intervals(self, start_dt, end_dt, resource, domain=None, tz=None):
        """ Return the leave intervals in the given datetime range that excluded by global leaves
            The returned intervals are expressed in specified tz or in the calendar's timezone.

        :param start_dt: timezone aware start datetime for the datetime range beginning
        :param end_dt: timezone aware end datetime for the datetime range ending
        :param resource: the resource to get leave intervals in the given datetime range
        :param domain: controls the way leaves are recognized. None means default value ('time_type', '=', 'leave')
        :param tz: The returned intervals are expressed in specified tz or in the calendar's timezone.

        :return: collection of ordered disjoint intervals with some associated resource.calendar.leaves records
        :rtype: Intervals collection of ordered disjoint intervals with some associated resource.calendar.leaves records.
            Each interval is a triple ``(start, stop, leaves)``, where ``leaves`` is a recordset of resource.calendar.leaves records.
        """
        self.ensure_one()
        leave_intervals_batch = self._leave_intervals_batch(
                        start_dt,
                        end_dt,
                        resources=resource,
                        domain=domain,
                        tz=tz
                        )
        intervals = leave_intervals_batch[resource.id] \
            -leave_intervals_batch[False]  # Substract Global Leaves to avoid duplication
        return intervals
