from odoo import api, fields, models


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    @api.model
    def _get_rendering_context(self, docids, data):
        res = super(IrActionsReport, self)._get_rendering_context(docids, data)
        if self.model == 'account.asset.asset' and docids:
            assets = self.env['account.asset.asset'].browse(docids)

            res['assets'] = {}

            for asset in assets:
                lines = [self._prepare_report_line(date=asset.date, value=asset.value, year=asset.year)]
                revaluation_lines = asset.revaluation_line_ids.filtered(
                    lambda l: l.revaluation_date < fields.Date.context_today(asset) and l.move_id.state == 'posted'
                    ).sorted(key='revaluation_date')

                value = asset.value
                for depr in asset.depreciation_line_ids:
                    ignore_this_depr_line = False

                    if depr.depreciation_date >= fields.Date.context_today(asset):
                        continue
                    for revl in revaluation_lines:
                        if revl.revaluation_date < depr.depreciation_date:
                            value += revl.value if revl.method == 'increase' else -revl.value
                            lines.append(
                                self._prepare_report_line(
                                    date=revl.revaluation_date,
                                    reason=revl.name,
                                    value=value,
                                    year=revl.year
                                    )
                                )

                            revaluation_lines -= revl

                        elif revl.revaluation_date == depr.depreciation_date:
                            value += revl.value if revl.method == 'increase' else -revl.value
                            lines.append(
                                self._prepare_report_line(
                                    date=revl.revaluation_date,
                                    reason=revl.name,
                                    value=value,
                                    year=revl.year,
                                    current_depreciation=depr.amount,
                                    cumulative_depreciation=depr.depreciated_value
                                    )
                                )

                            ignore_this_depr_line = True
                            revaluation_lines -= revl

                    if not ignore_this_depr_line:
                        lines.append(
                            self._prepare_report_line(
                                date=depr.depreciation_date,
                                year=depr.year,
                                current_depreciation=depr.amount,
                                cumulative_depreciation=depr.depreciated_value
                                )
                            )

                for revl in revaluation_lines:
                    value += revl.value if revl.method == 'increase' else -revl.value
                    lines.append(
                        self._prepare_report_line(
                            date=revl.revaluation_date,
                            reason=revl.name,
                            value=value,
                            year=revl.year
                            )
                        )

                res['assets'][asset.id] = lines
        return res

    @api.model
    def _prepare_report_line(self, **values):
        return {
            'ref': values.get('ref', ''),
            'date': values.get('date', ''),
            'reason': values.get('reason', ''),
            'value': values.get('value', ''),
            'year': values.get('year', ''),
            'current_depreciation': values.get('current_depreciation', ''),
            'cumulative_depreciation': values.get('cumulative_depreciation', ''),
            }
