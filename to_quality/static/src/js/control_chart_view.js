odoo.define('web.ControlChartView', function (require) {
    var GraphView = require('web.GraphView');
    var GraphController = require('web.GraphController');
    var ControlChartModel = require('web.ControlChartModel');
    var ControlChartRenderer = require('web.ControlChartRenderer');

    var ControlChartView = GraphView.extend({
        config: _.extend({}, GraphView.prototype.config, {
            Model: ControlChartModel,
            Controller: GraphController,
            Renderer: ControlChartRenderer
        }),
        init: function (viewInfo, params) {
            this._super.apply(this, arguments);

            var rangeFields = [];
            this.arch.children.forEach(function (field) {
                var fieldName = field.attrs.name;
                if (field.attrs.type === 'range') {
                    rangeFields.push(fieldName);
                }
            });
            this.loadParams.rangeFields = rangeFields;
            this.rendererParams.rangeFields = rangeFields;
        }
    });

    var view_registry = require('web.view_registry');
    view_registry.add('control_chart', ControlChartView);
})
