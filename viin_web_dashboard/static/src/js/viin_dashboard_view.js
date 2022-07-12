odoo.define('viin_web_dashboard.ViinDashboardView', function(require) {
    "use strict";
    
    var BasicView = require('web.BasicView');
    var core = require('web.core');
    
    var ViinDashboardModel = require('viin_web_dashboard.ViinDashboardModel');
    var ViinDashboardRenderer = require('viin_web_dashboard.ViinDashboardRenderer');
    var ViinDashboardController = require('viin_web_dashboard.ViinDashboardController');
    
    var _lt = core._lt;
    
    var view_registry = require('web.view_registry');
    
    var ViinDashboardView = BasicView.extend({
        display_name: _lt('Dashboard'),
        icon: 'fa-tachometer',
        multi_record: false,
        searchMenuTypes: ['filter', 'timeRange', 'favorite'],
        config: _.extend({}, BasicView.prototype.config, {
            Model: ViinDashboardModel,
            Controller: ViinDashboardController,
            Renderer: ViinDashboardRenderer,
        }),
        jsLibs: [],
        viewType: 'viin_dashboard',
        
        /**
         * @override
         */
        init: function(viewInfo, params) {
            this._super.apply(this, arguments);
            this.load(params);
        },
    
        /**
         * Initial loading.
         */
        load: function (params) {
            this.modelName = params.modelName;
            
            let additionalMeasures = _.pluck(_.filter(this.fieldsInfo.viin_dashboard, { realType: 'many2one' }), 'field');
            this.rendererParams.additionalMeasures = additionalMeasures;
            this.rendererParams.subFieldsViews = {};
            
            this.loadParams.aggregates = this.fieldsView.aggregates;
            this.loadParams.formulas = this.fieldsView.formulas;
            
            this.controllerParams.actionDomain = params.action && params.action.domain || [];
            this.controllerParams.currentFilterIDs = [];
        },
        
        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------
        
        /**
         * @override
         */
        _loadData: async function(model) {
            var self = this;
            var defSubViews;
            if (this.fieldsView.subViews) {
                defSubViews = model.loadViews(this.modelName, this.loadParams.context, this.fieldsView.subViews)
                                .then(function(fieldsViews) {
                                    _.extend(self.rendererParams.subFieldsViews, fieldsViews);
                                    });
            }
            return Promise.all([this._super.apply(this, arguments), defSubViews]).then(function (results) {
                if (results[1] !== undefined){
                    return results[1];
                }
                return results[0];
            });
        },
        
        /**
         * @override
         */
        _updateMVCParams: function() {
            var self = this;
            this._super.apply(this, arguments);
            // add 'viewType_view_ref' keys in context, to fetch the adequate view
            // viewType could be a pivot ỏr graph or viin_cohort
            _.each(this.fieldsView.subViews, function(viewID, viewType) {
                if (typeof viewID === 'string' || viewID instanceof String){
                    self.loadParams.context[viewID + '_view_ref'] = viewType;
                }
            });
            this.fieldsView.subViews = _.map(
                this.fieldsView.subViews, 
                function(viewID, viewType) {
                    // e.g. [false, 'pivot'] or [false, 'viin_cohort'] or [false, 'graph']);
                    if (Array.isArray(viewID)) {
                        return viewID;
                    } else if (viewType){ 
                        return [false, viewType];
                    }
                }
            ); 
        },
        
        /**
         * @override
         *
         * Traverses the arch and calls '_processNode' on each of its nodes.
         *
         * @private
         * @param {Object} arch a parsed arch
         * @param {Object} fv the fieldsView Object, in which _processNode can
         *   access and add information (like the fields' attributes in the arch)
         */
        _processArch: function(arch, fv) {
            fv.aggregates = [];
            fv.formulas = {};
            fv.subViews = {};
            fv.viewFields = $.extend(true, {}, fv.viewFields);
            this._super.apply(this, arguments);
        },
        
        /**
         * @override
         *
         * Processes a node of the arch (mainly nodes with tagname 'field'). Can
         * be overridden to handle other tagnames.
         *
         * @private
         * @param {Object} node
         * @param {Object} fv the fieldsView
         * @param {Object} fv.fieldsInfo
         * @param {Object} fv.fieldsInfo[viewType] fieldsInfo of the current viewType
         * @param {Object} fv.viewFields the result of a fields_get extend with the
         *   fields returned with the fields_view_get for the current viewType
         * @param {string} fv.viewType
         * @returns {boolean} false if subnodes must not be visited.
         */
        _processNode: function(node, fv) {
            var res = this._super.apply(this, arguments);
            switch (node.tag) {
                case 'aggregate':
                    return this._processAggregateNode(node, fv);
                case 'formula':
                    return this._processFormulaNode(node, fv);
                case 'view':
                    fv.subViews[node.attrs.type] = node.attrs.ref;
                    return false;
                default:
                    return res;
            }
        },
        
        _processAggregateNode: function(node, fv) {
            var field = fv.viewFields[node.attrs.field];
            
            var aggregate = _.defaults({}, node.attrs, {
                domain: '[]',
                group_operator: field.group_operator,
            });
            
            aggregate.Widget = this._getFieldWidgetClass('viin_dashboard', field, aggregate);
            
            if (field.type === 'many2one') {
                field.type = 'integer';
                field.realType = 'many2one';
                aggregate.realType = 'many2one';
                aggregate.group_operator = 'count_distinct';
            }
            
            aggregate.type = field.type;
            
            var aggregateID = node.attrs.name;
            fv.fieldsInfo.viin_dashboard[aggregateID] = aggregate;
            fv.viewFields[aggregateID] = _.extend({}, field, { name: aggregateID });
            fv.aggregates.push(aggregateID);
            
            return false;
        },
        
        _processFormulaNode: function(node, fv) {
            var formulaID = node.attrs.name || _.uniqueId('formula_');
            node.attrs.name = formulaID;
            
            var formula = _.extend({}, node.attrs, { type: 'float' });
            var field = { name: formulaID, type: 'float' };
            formula.Widget = this._getFieldWidgetClass('viin_dashboard', field, formula);
            
            fv.fieldsInfo.viin_dashboard[formulaID] = formula;
            fv.viewFields[formulaID] = field;
            fv.formulas[formulaID] = _.pick(node.attrs, ['string', 'value']);
            
            return false;
        },
    });
    
    view_registry.add('viin_dashboard', ViinDashboardView);
    
    return ViinDashboardView;

});
