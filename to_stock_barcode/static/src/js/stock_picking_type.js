odoo.define('to_stock_barcode.picking_type_kanban', function (require) {
    'use strict';

    var KanbanRecord = require('web.KanbanRecord');

    KanbanRecord.include({
        _openRecord: function () {
            if (this.modelName === 'stock.picking.type') {
                this.$('button').first().click();
                return;
            }
            this._super.apply(this, arguments);
        }
    });

});
