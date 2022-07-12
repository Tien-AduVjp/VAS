odoo.define('to_mrp_mps.MPSClientAction', function (require) {
    'use strict';

    var AbstractAction = require('web.AbstractAction');
    var Dialog = require('web.Dialog');
    var concurrency = require('web.concurrency');
    var field_utils = require('web.field_utils');
    var session = require('web.session');

    var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;

    var MPSClientAction = AbstractAction.extend({
        contentTemplate: 'to_mrp_mps',
        events: {
            'click .o_mps_automatic_mode': '_onClickAutomaticMode',
            'click .o_mps_create': '_onClickCreate',
            'click .o_mps_edit': '_onClickEdit',
            'click .o_mps_open_details': '_onClickOpenDetails',
            'click .o_mps_replenish': '_onClickReplenish',
            'click .o_mps_open_product': '_onClickOpenProduct',
            'click .o_mps_unlink': '_onClickUnlink',
            'change .o_mps_input_forcasted_qty': '_onChangeForcastedQty',
            'change .o_mps_input_to_replenish_qty': '_onChangeToReplenishQty',
        },
        custom_events: {
            search: '_onSearch',
        },
        hasControlPanel: true,
        loadControlPanel: true,
        withSearchBar: true,

        /**
         * @override
         */
        init: function (parent, action) {
            this._super.apply(this, arguments);

            this.actionManager = parent;
            this.action = action;
            this.context = action.context;
            this.domain = [];

            this.companyId = false;
            this.groups = false;
            this.state = false;
            this.period = false;
            this.date_range = [];
            this.formatFloat = field_utils.format.float;
            this.manufacturingPeriods = [];

            this.mutex = new concurrency.Mutex();
            this.controlPanelParams.modelName = 'mrp.production.schedule';
        },

        /**
         * @override
         */
        willStart: function () {
            var self = this;
            var _super = this._super.bind(this);
            var defs = [this._getMpsViewState()];
            defs.push(this._rpc({
                model: 'ir.model.data',
                method: 'get_object_reference',
                args: ['to_mrp_mps', 'mrp_production_schedule_search'],
                kwargs: {context: session.user_context},
            })
                .then(function (viewId) {
                    self.controlPanelParams.viewId = viewId[1];
                }));

            return Promise.all(defs).then(function () {
                return _super.apply(self, arguments);
            });
        },

        /**
         * @override
         */
        start: function () {
            return this._super.apply(this, arguments)
                .then(this._updateCustomControlPanel.bind(this));
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * Add 'Replenish' button and the 'Rows' dropdown button to toggle the display of rows
         */
        _updateCustomControlPanel: function () {
            this.$buttons = $(QWeb.render('mps_control_panel_buttons'));
            this._updateControlPanelButtons();

            this.$searchview_buttons = $(QWeb.render('mps_control_panel_rows_buttons', {
                period: this.period,
                groups: this.groups
            }));
            this.$searchview_buttons.find('.o_mps_show_line').on('click', this._onToggleLine.bind(this));
            this.$searchview_buttons.find('.o_mps_change_period').on('click', this._onChangePeriod.bind(this));

            this.updateControlPanel({
                title: _t('Master Production Schedule'),
                cp_content: {
                    $buttons: this.$buttons,
                    $searchview_buttons: this.$searchview_buttons
                },
            });
        },

        _backToState: function (scheduleId) {
            var state = _.where(_.flatten(_.values(this.state)), {id: scheduleId});
            return this._renderSchedule(state);
        },

        _selectNextInput: function (scheduleId, dateIndex, inputName) {
            var tableSelector = '.table-responsive[data-id=' + scheduleId + ']';
            var rowSelector = 'tr[name=' + inputName + ']';
            var inputSelector = 'input[data-date_index=' + (dateIndex + 1) + ']';
            return this.$el.find(tableSelector + ' ' + rowSelector + ' ' + inputSelector).select();
        },

        _getMpsViewState: function () {
            var self = this;
            return this._rpc({
                model: 'mrp.production.schedule',
                method: 'get_mps_view_state_by_domain',
                args: [this.domain],
            }).then(function (state) {
                self.state = state.schedule_states;
                self.groups = state.groups[0];
                self.period = state.period;
                self.companyId = state.company_id;
                self.manufacturingPeriods = state.dates;
                return state;
            });
        },

        /**
         * Get states and reload all the production schedules.
         *
         * @private
         * @return {Promise}
         */
        _reloadView: function () {
            var self = this;
            return this._getMpsViewState().then(function () {
                self.$el.find('.o_mrp_mps').replaceWith($(QWeb.render('to_mrp_mps', {
                    widget: {
                        manufacturingPeriods: self.manufacturingPeriods,
                        state: self.state,
                        groups: self.groups,
                        formatFloat: self.formatFloat
                    }
                })));
                self._updateControlPanelButtons();
            });
        },

        /**
         * Get the state with rpc call and render production schedule.
         */
        _renderProductionSchedule: function (scheduleId) {
            var self = this;
            return self._rpc({
                model: 'mrp.production.schedule',
                method: 'get_impacted_mps_ids',
                args: [scheduleId, self.domain],
            })
                .then(function (scheduleIds) {
                    scheduleIds.push(scheduleId);
                    return self._rpc({
                        model: 'mrp.production.schedule',
                        method: 'get_mps_view_state',
                        args: [scheduleIds],
                    })
                        .then(function (datas) {
                            _.each(datas, function (data) {
                                var index = _.findIndex(self.state, {id: data.id});
                                if (index >= 0) {
                                    self.state[index] = data;
                                } else {
                                    self.state.push(data);
                                }
                            });
                            return self._renderSchedule(datas);
                        });
                });
        },

        _renderSchedule: function (schedules) {
            var self = this;
            _.each(schedules, function (schedule) {
                var $newTable = $(QWeb.render('mrp_mps_production_schedule', {
                    productionSchedule: schedule,
                    manufacturingPeriods: self.manufacturingPeriods,
                    groups: self.groups,
                    formatFloat: self.formatFloat,
                }));
                var $table = self.$el.find('.table-responsive[data-id=' + schedule.id + ']');
                if ($table.length) {
                    $table.replaceWith($newTable);
                } else {
                    var $warehouse;
                    if ('warehouse_id' in schedule) {
                        $warehouse = self.$el.find('.table-responsive[data-warehouse_id=' + schedule.warehouse_id[0] + ']');
                    }
                    if ($warehouse && $warehouse.length) {
                        $warehouse.last().append($newTable);
                    } else {
                        self.$el.find('.o_mrp_mps').append($newTable);
                    }
                }
            });
            this._updateControlPanelButtons();
            return Promise.resolve();
        },

        _afterSaveQty: function (scheduleId, dateIndex, inputName) {
            var self = this;
            return this._renderProductionSchedule(scheduleId)
                .then(function () {
                    return self._selectNextInput(scheduleId, dateIndex, inputName);
                })
        },

        _saveForecast: function (scheduleId, dateIndex, forecastQty) {
            var self = this;
            this.mutex.exec(function () {
                return self._rpc({
                    model: 'mrp.production.schedule',
                    method: 'update_forecast_qty',
                    args: [scheduleId, dateIndex, forecastQty],
                }).then(self._afterSaveQty.bind(self, scheduleId, dateIndex, 'demand_forecast'));
            });
        },

        _saveToReplenish: function (scheduleId, dateIndex, replenishQty) {
            var self = this;
            this.mutex.exec(function () {
                return self._rpc({
                    model: 'mrp.production.schedule',
                    method: 'update_replenish_qty',
                    args: [scheduleId, dateIndex, replenishQty],
                }).then(
                    self._afterSaveQty.bind(self, scheduleId, dateIndex, 'to_replenish'),
                    self._backToState.bind(self, scheduleId)
                );
            });
        },

        _updateControlPanelButtons: function () {
            var recordsLen = Object.keys(this.state).length;
            if (recordsLen) {
                this.$buttons.find('.o_mps_create').addClass('btn-secondary').removeClass('btn-primary');
            } else {
                this.$buttons.find('.o_mps_create').addClass('btn-primary').removeClass('btn-secondary');
            }
            var toReplenish = _.filter(_.flatten(_.values(this.state)), function (mps) {
                return !!_.where(mps.mrp_product_forecast_ids, {'to_replenish': true}).length;
            });
            if (toReplenish.length) {
                this.$buttons.find('.o_mps_replenish').removeClass('o_hidden');
            } else {
                this.$buttons.find('.o_mps_replenish').addClass('o_hidden');
            }
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        _onSearch: function (e) {
            e.stopPropagation();
            this.domain = e.data.domain;
            this._reloadView();
        },

        _getEventTargetData: function ($target) {
            var dateIndex = $target.data('date_index');
            var scheduleId = $target.closest('.table-responsive').data('id');
            return {
                dateIndex: dateIndex,
                scheduleId: scheduleId
            }
        },

        _onChangeForcastedQty: function (e) {
            e.stopPropagation();
            var targetData = this._getEventTargetData($(e.target));
            var forecastQty = parseFloat($(e.target).val());
            if (isNaN(forecastQty)) {
                this._backToState(targetData.scheduleId);
            } else {
                this._saveForecast(targetData.scheduleId, targetData.dateIndex, forecastQty);
            }
        },

        _onChangeToReplenishQty: function (e) {
            e.stopPropagation();
            var targetData = this._getEventTargetData($(e.target));
            var replenishQty = parseFloat($(e.target).val());
            if (isNaN(replenishQty)) {
                this._backToState(targetData.scheduleId);
            } else {
                this._saveToReplenish(targetData.scheduleId, targetData.dateIndex, replenishQty);
            }
        },

        _onClickAutomaticMode: function (e) {
            e.stopPropagation();
            var targetData = this._getEventTargetData($(e.target));
            var self = this;
            this.mutex.exec(function () {
                return self._rpc({
                    model: 'mrp.production.schedule',
                    method: 'remove_replenish_qty',
                    args: [targetData.scheduleId, targetData.dateIndex],
                }).then(self._renderProductionSchedule.bind(self, targetData.scheduleId));
            });
        },

        _onClickReplenish: function (e) {
            e.stopPropagation();
            var scheduleIds = [];
            var $table = $(e.target).closest('.table-responsive');
            if ($table.length) {
                scheduleIds = [$table.data('id')];
            }
            var self = this;
            var ids = scheduleIds.length ? scheduleIds : _.map(self.state, (s) => s.id);
            var basedOnLeadTime = scheduleIds.length ? false : true;
            this.mutex.exec(function () {
                return self._rpc({
                    model: 'mrp.production.schedule',
                    method: 'action_replenish',
                    args: [ids, basedOnLeadTime]
                }).then(self._reloadView.bind(self));
            });
        },

        /**
         * Handles hide/show related rows, save rows settings to company
         * and then reload content.
         */
        _onToggleLine: function (e) {
            e.stopPropagation();
            var $target = $(e.target);
            var vals = {};
            vals[$target.data('value')] = $target.prop('checked');
            var self = this;
            this.mutex.exec(function () {
                return self._rpc({
                    model: 'res.company',
                    method: 'write',
                    args: [[self.companyId], vals],
                }).then(self._reloadView.bind(self));
            });
        },

        /**
         * Save current period setting to res.company and reload view
         */
        _onChangePeriod: function (e) {
            var self = this;
            this.period = $(e.target).data('value');
            var vals = {'manufacturing_period': this.period};
            this.mutex.exec(function () {
                return self._rpc({
                    model: 'res.company',
                    method: 'write',
                    args: [[self.companyId], vals],
                }).then(function () {
                    self._updateCustomControlPanel();
                    self._reloadView();
                });
            });
        },

        _onClickCreate: function (e) {
            e.stopPropagation();
            var self = this;
            this.mutex.exec(function () {
                return self.do_action('to_mrp_mps.mps_add_product_action', {
                    on_close: function () {
                        return self._rpc({
                            model: 'mrp.production.schedule',
                            method: 'search_read',
                            args: [[], ['id']],
                            orderBy: [{name: 'id', asc: false}],
                            limit: 1,
                        }).then(function (result) {
                            if (result.length) {
                                return self._renderProductionSchedule(result[0].id);
                            }
                        });
                    }
                });
            });
        },

        _onClickEdit: function (e) {
            e.stopPropagation();
            var scheduleId = this._getEventTargetData($(e.target)).scheduleId;
            var self = this;
            this.mutex.exec(function () {
                return self.do_action({
                    name: 'Edit Production Schedule',
                    type: 'ir.actions.act_window',
                    res_model: 'mrp.production.schedule',
                    res_id: scheduleId,
                    views: [[false, 'form']],
                    target: 'new',
                }, {
                    on_close: self._renderProductionSchedule.bind(self, scheduleId)
                });
            });
        },

        _onClickUnlink: function (e) {
            e.preventDefault();
            var scheduleId = this._getEventTargetData($(e.target)).scheduleId;
            var self = this;
            Dialog.confirm(this, _t("Are you sure you want to delete this record?"), {
                confirm_callback: function () {
                    self.mutex.exec(function () {
                        return self._rpc({
                            model: 'mrp.production.schedule',
                            method: 'unlink',
                            args: [scheduleId],
                        }).then(self._reloadView.bind(self));
                    });
                }
            });
        },

        _onClickOpenDetails: function (e) {
            e.preventDefault();
            var $target = $(e.target);
            var targetData = this._getEventTargetData($target);
            var self = this;
            this.mutex.exec(function () {
                return self._rpc({
                    model: 'mrp.production.schedule',
                    method: $target.data('action'),
                    args: [
                        targetData.scheduleId,
                        self.manufacturingPeriods[targetData.dateIndex],
                        $target.data('date_start'),
                        $target.data('date_stop'),
                    ]
                }).then(function (action) {
                    return self.do_action(action);
                });
            });
        },

        _onClickOpenProduct: function (e) {
            e.preventDefault();
            return this.do_action({
                type: 'ir.actions.act_window',
                res_model: 'product.product',
                res_id: $(e.currentTarget).data('res-id'),
                views: [[false, 'form']],
                target: 'current'
            });
        },
    });

    core.action_registry.add('to_mps_client_action', MPSClientAction);

    return MPSClientAction;

});
