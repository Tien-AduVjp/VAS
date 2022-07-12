odoo.define('viin_web_map.ViinMapController', function (require) {
    'use strict';

    const AbstractController = require('web.AbstractController');
    const Pager = require('web.Pager');

    const core = require('web.core');
    const qweb = core.qweb;

    const MAP_API_URL = 'https://www.google.com/maps/dir/?api=1';

    const ViinMapController = AbstractController.extend({
        custom_events: _.extend({}, AbstractController.prototype.custom_events, {
            'marker_edit_clicked': '_onMarkerEditClicked',
        }),

        update: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                self._fetchCoordinateFromAddress();
                return self._updatePager();
            });
        },
        
        on_attach_callback: function() {
            this._fetchCoordinateFromAddress();
            return this._super.apply(this, arguments)
        },

        renderButtons: function ($node) {
            let url = MAP_API_URL;
            const records = this.model.data.records;
            
            if (records.length) {
                url += '&waypoints=';
                const hasCoordinates = records.filter((r) => r.partner && r.partner.partner_latitude && r.partner.partner_longitude);
                var uniqRecordHasCoordinates = _.uniq(hasCoordinates, (r) => r.partner.partner_latitude + '|' + r.partner.partner_longitude);
                _.each(uniqRecordHasCoordinates, function(r) {
                    url += r.partner.partner_latitude + ',' + r.partner.partner_longitude + '|';
                })
                url = url.slice(0, -1);
            }
            const $buttons = $(qweb.render("ViinMapView.buttons"), {widget: this});
            $buttons.find('a').attr('href', url);
            $buttons.appendTo($node);
        },

        renderPager: function ($node) {
            var self = this;
            const pager_params = this._getPagerParams();
            this.pager = new Pager(this, pager_params.size, pager_params.current_min, pager_params.limit);
            this.pager.on('pager_changed', self, function (newState) {
                self.pager.disable();
                return self.reload({
                    limit: newState.limit,
                    offset: newState.current_min - 1
                }).then(self.pager.enable.bind(self.pager));
            });
            return this.pager.appendTo($node);
        },

        _getPagerParams: function () {
            const currentState = this.model.get();
            return {
                size: currentState.count,
                current_min: currentState.offset + 1,
                limit: currentState.limit,
            };
        },

        _updatePager: function () {
            if (this.pager) {
                const params = this._getPagerParams();
                this.pager.updateState(params);
            }
        },

        _onMarkerEditClicked: function (e) {
            if (e && e.data) {
                this.trigger_up('switch_view', {
                view_type: 'form',
                res_id: e.data.id,
                mode: 'readonly',
                model: this.modelName
            });
        }
        },
        
        _fetchCoordinateFromAddress: function(){
            var self = this;
            var promises = this.model.fetchCoordinateFromAddress();
            this.model.partnerWithoutLatLong = [];
            Promise.all(promises).then(function(partners) {
                var detail_list_scroll = $('.o_viin_pin_list_container').scrollTop();
                self.renderer._renderMarkers();
                self.renderer._renderRoutes();
                // Update pin list detail
                self.renderer._renderPinList();
                $('.o_viin_pin_list_container').scrollTop(detail_list_scroll);
                // Remove 'updating' tooltip
                $('.o_viin_pin_list_container li .text-muted').removeAttr('data-toogle');
                $('.o_viin_pin_list_container li .text-muted').removeAttr('title');
            });
        },
    });

    return ViinMapController;
});
