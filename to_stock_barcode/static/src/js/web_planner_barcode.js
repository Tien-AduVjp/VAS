odoo.define('to_stock_barcode.stock_barcode_planner', function (require) {
    "use strict";

    var planner = require('web.planner.common');

    planner.PlannerDialog.include({

        prepare_planner_event: function () {
            this._super.apply(this, arguments);

            if (this.planner.planner_application === 'planner_barcode') {
                var $cr = this.$el.find('.carriage-return');
                var $cr_label = this.$el.find('.carriage-return span');

                function toggle_cr_label (cr) {
                    $cr.show();
                    if (cr) {
                        $cr_label.addClass('label-success').removeClass('label-danger').text('ON');
                    } else {
                        $cr_label.addClass('label-danger').removeClass('label-success').text('OFF');
                    }
                }

                $cr.hide();

                var cr_timeout = null;
                this.$el.find('.barcode-scanner').keypress(function (e) {
                    clearTimeout(cr_timeout);
                    var code = e.charCode || e.keyCode;
                    if (code === 13) {
                        toggle_cr_label(true);
                    } else {
                        cr_timeout = setTimeout(_.bind(toggle_cr_label, false), 50);
                    }
                });

            }
        }
    });

});
