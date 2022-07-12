odoo.define('viin_web_dashboard.ViinDashboardRenderer', function (require) {
    "use strict";

    var FormRenderer = require('web.FormRenderer');
    var viewRegistry = require('web.view_registry');
    var Domain = require('web.Domain');
    var config = require('web.config');
    var dataComparisonUtils = require('web.dataComparisonUtils');
    var fieldUtils = require('web.field_utils');
    var pyUtils = require('web.py_utils');

    var renderComparison = dataComparisonUtils.renderComparison;
    var renderVariation = dataComparisonUtils.renderVariation;

    var core = require('web.core');
    var QWeb = core.qweb;

    var ViinDashboardRenderer = FormRenderer.extend({
        className: "o_viin_dashboard_view",
        events: {
            'click .o_viin_aggregate.o_clickable': '_onClickAggregate',
        },
        OUTER_GROUP_COL: 6,

        /**
         * @override
         */
        init: function (parent, state, params) {
            this._super.apply(this, arguments);

            this.mode = 'readonly';
            this.additionalMeasures = params.additionalMeasures;
            this.subFieldsViews = params.subFieldsViews;

            this.viinDashboardSubControllers = {};
            this.viinDashboardSubControllersContext = _.pick(state.context || {}, 'pivot', 'graph', 'viin_cohort');
            this.subcontrollersNextMeasures = {pivot: {}, graph: {}, viin_cohort: {}};

            var session = this.getSession();
            this.formatOptions = {
                currency_id: session.company_currency_id,
                minDigits: 1,
                decimals: session.decimal_places_of_currency,
    			// allow to decide if utils.human_number should be used
                // if absolute value of number is greater than 10000, then format it, depends on decimal places of currency
    			// e.g. 1234 => 1234
    			// // e.g. 12345 and USD => 12.34k; 12345 and VND => 12k
                humanReadable: (num) => Math.abs(num) >= 10000,
                // avoid comma separators for thousands in numbers when human_number is used
                formatterCallback: (str) => str,
            };
        },

        /**
    	 * * Call `on_attach_callback` for each subview
         * @override
         */
        on_attach_callback: function () {
            this._super.apply(this, arguments);
            this.isInDOM = true;

    		_.each(this.viinDashboardSubControllers, function (controller) {
                if ('on_attach_callback' in controller) {
                    controller.on_attach_callback();
                }
            });

    		_.each(this.widgets, function (widget) {
                if ('on_attach_callback' in widget) {
                    widget.on_attach_callback();
                }
            });

        },

        /**
         * @override
         */
        on_detach_callback: function () {
            this._super.apply(this, arguments);
            this.isInDOM = false;

    		_.each(this.viinDashboardSubControllers, function (controller) {
                if ('on_detach_callback' in controller) {
                    controller.on_detach_callback();
                }
            });

    		_.each(this.widgets, function (widget) {
                if ('on_detach_callback' in widget) {
                    widget.on_detach_callback();
                }
            });
        },

        //--------------------------------------------------------------------------
        // Public
        //--------------------------------------------------------------------------

        /**
         * @override
         */
        updateState: function (state, params) {
            var self = this;
            _.each(self.viinDashboardSubControllers, function (data, viewType) {
                self.viinDashboardSubControllersContext[viewType] = self.viinDashboardSubControllers[viewType].getOwnedQueryParams().context;
            });
            var viinDashboardSubControllersContext = _.pick(params.context || {}, ['pivot', 'graph', 'viin_cohort']);
            _.extend(self.viinDashboardSubControllersContext, viinDashboardSubControllersContext);
            _.each(self.viinDashboardSubControllers, function (data, viewType) {
                _.extend(self.viinDashboardSubControllersContext[viewType], self.subcontrollersNextMeasures[viewType]);
                self.subcontrollersNextMeasures[viewType] = {};
            });
            return self._super.apply(self, arguments);
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * @override
         */
        _renderView: function () {
            var self = this;
            var oldControllers = _.values(this.viinDashboardSubControllers);
            return this._super.apply(this, arguments)
                .then(function () {
    				_.each(oldControllers, function (controller) {
    		            if ('destroy' in controller) {
    		                controller.destroy();
    		            }
    		        });

    				if (self.isInDOM) {
    					_.each(self.viinDashboardSubControllers, function (controller) {
    			            if ('on_attach_callback' in controller) {
    			                controller.on_attach_callback();
    			            }
    			        });

    					_.each(self.widgets, function (widget) {
    			            if ('on_attach_callback' in widget) {
    			                widget.on_attach_callback();
    			            }
    			        });
    				}
                });
        },

        /**
         * @override
         */
        _renderTagGroup: function (node) {
            var $outerGroup = this._renderOuterGroup(node);
            if (node.children.length && node.children[0].tag === 'widget') {
                $outerGroup.addClass('o_has_widget');
            }
            return $outerGroup;
        },

        /**
    	 * Updates the Viin Dashboard's $el with new content.
         * @override
         */
        _updateView: function ($view) {
            return this.$el.html($view);
        },

        _attachTooltip: function ($el, node) {
            $el.tooltip({
                delay: {show: 2000, hide: 0},
                title: () => QWeb.render('viin_web_dashboard.Tooltip', {debug: config.isDebug(), node: node}),
    			trigger: 'manual',
            });
        },

        _renderLabel: (node) => $('<label>', {text: 'string' in node.attrs ? node.attrs.string : node.attrs.name}),

        /**
         * Render a aggregate or formula statistic
         * with its label, and widget if available.
         */
        _renderStatisticElement: function (node) {
            var self = this;
            var $label = this._renderLabel(node);

            var $el = $('<div>').attr('name', node.attrs.name).append($label);
            var stat = node.attrs.name;
            var variation = this.state.variationData[stat] || false;
            var statistic = self.state.fieldsInfo.viin_dashboard[stat];

            if (!node.attrs.widget || (node.attrs.widget in fieldUtils.format)) {
                var valueLabel = statistic.value_label ? (' ' + statistic.value_label) : '';
                var fieldValue = self.state.data[stat];
                fieldValue = self._getfieldDateValue(statistic, fieldValue);
                var formatType = node.attrs.widget || statistic.type;
                var formatter = fieldUtils.format[formatType];
                if (this.state.comparison) {
                    var compareValue = this.state.comparisonData[stat];
                    compareValue = self._getfieldDateValue(statistic, compareValue);
                    renderComparison($el, fieldValue, compareValue, variation, formatter, statistic, this.formatOptions);
                    $('.o_comparison', $el).append(valueLabel);
                } else {
                    fieldValue = isNaN(fieldValue) ? '-' : formatter(fieldValue, statistic, this.formatOptions);
                    $el.append($('<div>', {class: 'o_value', html: fieldValue + valueLabel}));
                }

            } else if (this.state.comparison) {
                var $originalValue = this._renderFieldWidget(node, this.state);
                var comparisonState = _.extend({}, this.state, {data: this.state.comparisonData});
                var $comparisonValue = this._renderFieldWidget(node, comparisonState);
                var $comparison = $('<div>', {class: 'o_comparison'}).append($originalValue, $('<span>', {html: " vs "}), $comparisonValue);
                $el.append(renderVariation(variation, statistic)).append($comparison);

            } else {
                $el.append(this._renderFieldWidget(node, this.state).addClass('o_value'));
            }

            switch(variation) {
              case variation > 0:
                $el.addClass('border-success');
                break;
              case variation < 0:
                $el.addClass('border-danger');
                break;
              case variation == 0:
                $el.addClass('border-info');
                break;
            }

            this._registerModifiers(node, this.state, $el);
            if (config.isDebug() || node.attrs.help) {
                this._attachTooltip($el, node);
            }
            return $el;
        },

    	_getfieldDateValue: function(statistic, fieldValue){
    		return _.contains(['date', 'datetime'], statistic.type) ? (fieldValue === 0 ? NaN : moment(fieldValue)) : fieldValue;
    	},

        /**
         * Renders buttons of a sub view, with an extra fullscreen button.
         */
        _renderSubViewButtons: function (controller) {
            var $buttons = $('<div>', {class: 'o_' + controller.viewType + '_buttons o_viin_dashboard_subview_buttons'});
            controller.renderButtons($buttons);

            // create a buttons group
            var $buttonGroup = $('<div class="btn-group">');
            $buttonGroup
                .append($buttons.find('[aria-label="Main actions"]'))
                .append($buttons.find('.o_dropdown:has(.o_group_by_menu)'));
            $buttonGroup.prependTo($buttons);

            // render the fullscreen mode button
            var $fullscreenButton = $('<button>')
                .addClass("btn btn-outline-secondary fa fa-arrows-alt float-right o_button_switch")
                .attr({title: 'Fullscreen View', viewType: controller.viewType})
                .on('click', this._onOpenFullscreenMode.bind(this));
            $fullscreenButton.appendTo($buttons);

            // select primary and interval buttons and alter their style
            $buttons.find('.btn-primary, .btn-secondary')
                .removeClass('btn-primary btn-secondary o_dropdown_toggler_btn')
                .addClass("btn-outline-secondary");
            $buttons.find('[class*=interval_button]')
                .addClass('text-muted text-capitalize');

            return $buttons;
        },

        _renderTagAggregate: function (node) {
            var $aggregate = this._renderStatisticElement(node).addClass('o_viin_aggregate');
            var clickable = node.attrs.clickable === undefined || pyUtils.py_eval(node.attrs.clickable);
            $aggregate.toggleClass('o_clickable', clickable);

            var $tag = $('<div>').addClass('o_viin_aggregate_col').append($aggregate);
            this._registerModifiers(node, this.state, $tag);
            return $tag;
        },

        _renderTagFormula: function (node) {
            var $el = this._renderStatisticElement(node);
            if (!$el.hasClass('o_viin_formula')) {
                $el.addClass('o_viin_formula');
            }
            return $el;

        },

        /**
         * Render requested sub view with tag name 'view'
         */
        _renderTagView: function (node) {
            var self = this;
            var viewType = node.attrs.type;
            var subViewParams = {
                modelName: this.state.model,
                searchQuery: {
    	            domain: this.state.domain,
    	            groupBy: [],
    	            context: _.extend({}, this.state.context, this.viinDashboardSubControllersContext[viewType]),
                    timeRanges: this.state.timeRanges,
    	        },
                additionalMeasures: this.additionalMeasures,
                withControlPanel: false,
                hasSwitchButton: true,
                isEmbedded: true,
                useSampleModel: false
            };
            var SubViewRegistry = viewRegistry.get(viewType);
            var subView = new SubViewRegistry(this.subFieldsViews[viewType], subViewParams);
            var $view = $('<div>', {class: 'o_viin_dashboard_subview', type: viewType});
            var def = subView.getController(this)
                .then(function (controller) {
                    return controller.appendTo($view)
                        .then(function () {
                            self._renderSubViewButtons(controller).prependTo($view);
                            self.viinDashboardSubControllers[viewType] = controller;
                        });
                });
            this.defs.push(def);
            return $view;
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * Handle clicks on a aggregate (measure). Activates this measure on subviews.
         * If there is a domain specified, apply this domain on whole dashboard.
         */
        _onClickAggregate: function (e) {
            var agg = e.currentTarget.getAttribute('name');
            var aggInfo = this.state.fieldsInfo.viin_dashboard[agg];
            var measure = aggInfo.measure !== undefined ? aggInfo.measure : aggInfo.field;
            if (this.viinDashboardSubControllers.pivot) {
                this.subcontrollersNextMeasures.pivot.pivot_measures = [measure];
            }
            if (this.viinDashboardSubControllers.graph) {
                this.subcontrollersNextMeasures.graph.graph_measure = measure;
            }
            if (this.viinDashboardSubControllers.viin_cohort) {
                this.subcontrollersNextMeasures.viin_cohort.cohort_measure = measure;
            }
            this.trigger_up('reload', {
                domain: new Domain(aggInfo.domain).toArray(),
                domainLabel: aggInfo.domain_label || aggInfo.string || aggInfo.name,
            });
        },

        _onOpenFullscreenMode: function (e) {
            e.stopPropagation();
            var viewType = $(e.currentTarget).attr('viewType');
            var controller = this.viinDashboardSubControllers[viewType];
            this.trigger_up('open_fullscreen', {
                viewType: viewType,
                context: _.extend({}, this.state.context, controller.getOwnedQueryParams().context),
                additionalMeasures: this.additionalMeasures,
            });
        },
    });

    return ViinDashboardRenderer;

});
