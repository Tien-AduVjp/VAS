odoo.define('viin_web_map.ViinMapRenderer', function (require) {
    "use strict";

    const AbstractRenderer = require('web.AbstractRenderer');
    const field_utils = require('web.field_utils');

    const core = require('web.core');
    const qweb = core.qweb;

    const ViinMapRenderer = AbstractRenderer.extend({
        className: "o_viin_map_view row no-gutters",

        init: function (parent, state, params) {
            this._super(...arguments);

            this.markerPopupFieldDescriptors = params.markerPopupFieldDescriptors;
            this.numbering = params.numbering;
            this.hasFormView = params.hasFormView;
            this.defaultOrder = params.defaultOrder;

            this.mapIsInit = this.isInDom = false;
            this.polylines = this.markers = [];

            this.panelTitle = params.panelTitle;
            this.mapBoxToken = state.mapBoxToken;

            if (this.mapBoxToken) {
                this.tileDataUrl = 'https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}';
            } else {
                this.tileDataUrl = 'https://a.tile.openstreetmap.org/{z}/{x}/{y}.png';
            }
        },

        destroy: function () {
            _.each(this.markers, function (mrk) {
                mrk.off('click');
            });
            _.each(this.polylines, function (pol) {
                pol.off('click');
            });
            this.lMap.remove();
            return this._super(...arguments);
        },

        on_attach_callback: function () {
            this.isInDom = true;
            this._renderMap();

            const bounds = this._getMapBounds();
            if (bounds) {
                this.lMap.fitBounds(bounds);
            } else {
                this.lMap.fitWorld();
            }
            this._renderMarkers();
            this._renderRoutes();
            this._renderPinList();
        },

        /**
         * @override
         */
        on_detach_callback: function () {
            this.isInDom = false;
        },

        _render: function () {
            if (this.isInDom) {
                const bounds = this._getMapBounds();
                if (bounds) {
                    this.lMap.flyToBounds(bounds, {animate: false});
                } else {
                    this.lMap.fitWorld();
                }
                this._renderMarkers();
                this._renderRoutes();
                this._renderPinList();
            }
            return Promise.resolve();
        },

        _renderMap: function () {
            if (this.mapIsInit) {
                return;
            }

            const $mapContainer = $("<div/>", {'class': 'o_viin_map_container col-md-12 col-lg-10'});
            this.$el.append($mapContainer);
            this.lMap = L.map($mapContainer[0], {
                maxBounds: [L.latLng(180, -180), L.latLng(-180, 180)]
            });

            L.tileLayer(this.tileDataUrl, {
				tileSize: 512,
                minZoom: 4,
                maxZoom: 20,
				attribution: '© <a href="https://www.google.com/maps/about/" target="_blank">Google Map</a> © <a href="https://www.mapbox.com/about/maps/" target="_blank">Mapbox</a> © <a href="http://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> <strong><a href="https://www.mapbox.com/map-feedback/" target="_blank">Improve this map</a></strong>',

                zoomOffset: -1,
                accessToken: this.mapBoxToken,
                id: 'mapbox/streets-v11',
            }).addTo(this.lMap);

            this.mapIsInit = true;
        },

        _getMapBounds: function () {
            var latLng = [];
            var hasCoords = this.state.records.filter((r) => r.partner && r.partner.partner_latitude && r.partner.partner_longitude);
            _.each(hasCoords, (r) => latLng.push(L.latLng(r.partner.partner_latitude, r.partner.partner_longitude)));
            return latLng.length ? L.latLngBounds(latLng) : false;
        },

        _renderMarkerPopup: function (records) {
            var $popups;
            var self = this;
            var wrapper = $('<div>');
            _.each(records, record => {
                const data = self._getMarkerPopupData(record);
                const $popup = $(qweb.render('viin-map-popup', data));
                const $openButton = $popup.find('button.btn.btn-primary.o_viin_map_edit');
                if (self.hasFormView) {
                    $openButton.on('click', () => {
                        self.trigger_up('marker_edit_clicked', {id: record.id});
                    });
                } else {
                    $openButton[0].remove();
                }
                $popups = $popups ? $popups.add($popup) : $popup;
            });
            $popups.appendTo(wrapper);
            return wrapper[0];
        },

        _getMarkerPopupData: function (record) {
            const fields = [];
            _.each(this.markerPopupFieldDescriptors, field => {
                if (record[field['fieldName']]) {
                    let value = record[field['fieldName']];
                    if (value instanceof Array) {
                        value = value[1];
                    }
                    if (field.widget) {
                        value = field_utils.format[field.widget](field_utils.parse[field.widget](value, {}), {});
                    }
                    fields.push({label: field['string'], value: value});
                }
            });
            const direction_url = `https://www.google.com/maps/dir/?api=1&destination=${record.partner.partner_latitude},${record.partner.partner_longitude}`;
            return {
                fields: fields,
                direction_url: direction_url
            };
        },

        _renderMarkers: function () {
            // Remove old markers
            _.each(this.markers, marker => {
                this.lMap.removeLayer(marker);
            });
            this.markers = [];
            var self = this;
            var group_by_longlat = [];
            _.each(this.state.records, record => {
                if (!record.partner || !record.partner.partner_latitude || !record.partner.partner_longitude) {
                    return;
                }
                // find existing longlat in group_by_longlat
                var longlat_existed = false
                for (var i = 0; i < group_by_longlat.length; i++) {
                    if (group_by_longlat[i]['longlat']['long'] == record.partner.partner_longitude &&
                        group_by_longlat[i]['longlat']['lat'] == record.partner.partner_latitude) {
                            group_by_longlat[i]['records'].push(record)
                            longlat_existed = true
                        }
                }
                if(!longlat_existed) {
                    var record_longlat = {
                        'longlat': {'long': record.partner.partner_longitude, 'lat': record.partner.partner_latitude},
                        'records': [record]
                    }
                    group_by_longlat.push(record_longlat)
                }
            })

            _.each(group_by_longlat, longlat => {
                let marker, offset;
                if (this.numbering) {
                    const icon = L.divIcon({
                        className: 'o_viin_numbered_marker',
                        html: `<p class ="o_viin_number_icon">${this.state.records.indexOf(record) + 1}</p>`
                    });
                    marker = L.marker([longlat['longlat']['lat'], longlat['longlat']['long']], {icon: icon});
                    offset = new L.Point(0, -35);
                } else {
                    marker = L.marker([longlat['longlat']['lat'], longlat['longlat']['long']]);
                    offset = new L.Point(0, 0);
                }
                marker.addTo(this.lMap).bindPopup(function() {
                    return self._renderMarkerPopup(longlat['records'])
                },  {offset: offset});
                this.markers.push(marker);
            })
        },

        _renderRoutes: function () {
            const self = this;
            const route = this.state.route;
            if (route === undefined) {
                return;
            }

            // Remove old routes
            _.each(this.polylines, pol => {
                this.lMap.removeLayer(pol);
            });
            this.polylines = [];

            if (!this.mapBoxToken || !route.routes.length) {
                return;
            }

            // Add new routes
            _.each(route.routes[0].legs, leg => {
                const latLngs = [];
                _.each(leg.steps, step => {
                    _.each(step.geometry.coordinates, coord => {
                        latLngs.push(L.latLng(coord[1], coord[0]));
                    });
                });

                const polyline = L.polyline(latLngs, {
                    color: 'blue',
                    weight: 5,
                    opacity: 0.3,
                })
                    .addTo(self.lMap)
                    .on('click', function () {
                        _.each(self.polylines, pol => {
                            pol.setStyle({color: 'blue', opacity: 0.3});
                        });
                        this.setStyle({color: 'darkblue', opacity: 1.0});
                        this.bringToFront();
                    });
                self.polylines.push(polyline);
            });
        },

        _renderPinList: function () {
            this.$pinList = $(qweb.render('ViinMapView.pinlist', {widget: this}));
            const $div = this.$el.find('.o_viin_pin_list_container');
            if ($div.length) {
                $div.replaceWith(this.$pinList);
            } else {
                this.$el.append(this.$pinList);
            }
            this.$('.o_viin_pin_list_container li a').on('click', this._openPin.bind(this));
			// Add 'updating' tooltip
			$('.o_viin_pin_list_container li .text-muted').attr('data-toogle', 'tooltip');
			$('.o_viin_pin_list_container li .text-muted').attr('title', 'Updating');
        },

        _openPin: function (e) {
            e.preventDefault();
            // Centering map to the pin
            this.lMap.panTo(e.target.dataset, {animate: true});
            const marker = this.markers.find((m) => {
                return m._latlng.lat === e.target.dataset.lat && m._latlng.lng === e.target.dataset.lng;
            });
            if (marker) {
                marker.openPopup();
            }
        },
    });

    return ViinMapRenderer;
});
