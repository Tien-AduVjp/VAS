odoo.define('viin_web_dashboard.ViinDashboardController', function (require) {
    "use strict";

    var core = require('web.core');

    var AbstractController = require('web.AbstractController');
    var BasicController = require('web.BasicController');
    var Domain = require('web.Domain');

    var _t = core._t;

    /**
     * Viin Dashboard Controller
     */
    var ViinDashboardController = AbstractController.extend({
    	className: 'o_viin_dashboard_view',
        custom_events: _.extend({}, BasicController.prototype.custom_events, {
            open_fullscreen: '_onOpenFullscreen',
        }),

        init: function (parent, model, renderer, params) {
            this._super.apply(this, arguments);
            // info on current action
            this.actionDomain = params.actionDomain || [];
        },

        getViewName: function (viewType) {
            viewType = viewType === 'viin_cohort' ? 'Cohort' : viewType;
            return _.str.sprintf(_t('%s Analysis'), _.str.capitalize(viewType));
        },

        getOwnedQueryParams: function () {
            return {
                    context: _.mapObject(
                        this.renderer.viinDashboardSubControllers,
                        (controller) => controller.getOwnedQueryParams().context
                        )
            };
        },

        /**
         * Rebuild domain on search view whenever a field with domain is clicked.
         */
        _onReload: function (e) {
            e.stopPropagation();
            if (!this.withControlPanel) {
                return this.do_warn(
                    _t("Incorrect Operation!"),
                    _t("You cannot apply filters for this view.")
                );
            }

            let data = e && e.data || {};
            if (data.domain && data.domain.length) {
                var new_filter = {
                    type: 'filter',
                    domain: Domain.prototype.arrayToString(data.domain),
                    description: data.domainLabel
                }
                if (!this.filterToToggleIDs) {
                    this.filterToToggleIDs = []
                }
                var filterIDs = this.searchModel.get('filters').map(item => item.id);
                this.searchModel.dispatch('createNewFilters', [new_filter]);
                var newFilterIDs = this.searchModel.get('filters').map(item => item.id);
                this.filterToToggleIDs.map(filterId => this.searchModel.dispatch('toggleFilter', filterId));
                this.filterToToggleIDs = newFilterIDs.filter(value => filterIDs.indexOf(value) === -1);
            }
        },

        /**
         * Opens a view in another fullscreen action.
         */
        _onOpenFullscreen: function (e) {
            e.stopPropagation();
            let data = e && e.data || {};
            let action = {
                type: 'ir.actions.act_window',
                name: this.getViewName(data.viewType),
                res_model: this.modelName,
                domain: this.actionDomain,
                context: _.omit(data.context, ['timeRangeMenuData']),
                views: [[false, data.viewType]],
            };
            if (!_.isEmpty(data.additionalMeasures)) {
                action.flags = {additionalMeasures: data.additionalMeasures};
            }

            this.do_action(action, {controllerState: this.exportState()});
        },
    });

    return ViinDashboardController;

});
