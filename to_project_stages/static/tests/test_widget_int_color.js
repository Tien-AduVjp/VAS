odoo.define('to_project_stages.test_widget_int_color', function(require) {
    "use strict";

    var FormView = require('web.FormView');
    var testUtils = require('web.test_utils');
    var KanbanView = require('web.KanbanView');

    var createView = testUtils.createView;
    
    var session = require('web.session');
    
    function timeout(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    QUnit.module('to_project_stages', {
        beforeEach: function() {
            this.data = this.data = {
                project_task_type: {
                    fields: {
                        id: { string: "ID", type: "integer" },
                        name: { string: "Stage Test", type: "char" },
                        color: { string: "Color", type: "integer", default: 0 }
                    },
                    records: [{
                        id: 1,
                        name: 'New',
                        color: 4
                    }]
                }
            }
        }
    }, function() {
        QUnit.module('WidgetIntColor');
        QUnit.test('Check color selection in form view when create record', async function(assert) {
            assert.expect(3);
            var form = await createView({
                View: FormView,
                model: 'project_task_type',
                data: this.data,
                arch: '<form string="Stages">' +
                    '<group>' +
                    '<field name="name" />' +
                    '<field name="color" widget="int_color"/>' +
                    '</group>' +
                    '</form>',
                viewOptions: {
                    mode: 'edit',
                },
                mockRPC: function(route, args) {
                    if (args.method == 'create') {
                        assert.equal(args.args[0].color, 3, 'The color index should be 3')
                    }
                    return this._super.apply(this, arguments);
                }
            }, { positionalClicks: true });
            await testUtils.fields.editInput(form.$('input[name=name]'), 'stage empty create');
            await testUtils.dom.click($('.o_color_pill.o_color_3'));
            await testUtils.dom.click($('.o_control_panel .o_form_button_save'));
            assert.equal($('.o_color_pill').length, 1, 'There is only 1 color pill after save')
            assert.equal($('.o_color_pill').hasClass('o_color_3'), true, "Color index should be 3")
            form.destroy();
        });
        
        QUnit.test('Check color display in form view when open record', async function(assert) {
            assert.expect(2);
            var form = await createView({
                View: FormView,
                model: 'project_task_type',
                data: this.data,
                arch: '<form string="Stages">' +
                    '<group>' +
                    '<field name="name" />' +
                    '<field name="color" widget="int_color"/>' +
                    '</group>' +
                    '</form>',
                viewOptions: {
                    currentId: 1,
                },
            }, { positionalClicks: true });
            assert.equal($('.o_color_pill').length, 1, 'There is only 1 color pill')
            assert.equal($('.o_color_pill').hasClass('o_color_4'), true, "Color index should be 4")
            form.destroy();
        })
        
        QUnit.test('Check color display in form view when edit record', async function(assert) {
            assert.expect(2);
            var form = await createView({
                View: FormView,
                model: 'project_task_type',
                data: this.data,
                arch: '<form string="Stages">' +
                    '<group>' +
                    '<field name="name" />' +
                    '<field name="color" widget="int_color"/>' +
                    '</group>' +
                    '</form>',
                viewOptions: {
                    mode: 'edit',
                },
                res_id: 1,
            }, { positionalClicks: true });
            assert.equal($('.o_color_pill').length, 12, 'There are 12 color pill');
            assert.equal($('.o_color_pill.active').hasClass('o_color_4'), true, "Color index should be 4")
            form.destroy();
        });
        
        QUnit.test('Check color display in form view when edit record with other color', async function(assert) {
            assert.expect(4);
            var form = await createView({
                View: FormView,
                model: 'project_task_type',
                data: this.data,
                arch: '<form string="Stages">' +
                    '<group>' +
                    '<field name="name" />' +
                    '<field name="color" widget="int_color"/>' +
                    '</group>' +
                    '</form>',
                viewOptions: {
                    mode: 'edit',
                },
                res_id: 1,
                mockRPC: function(route, args) {
                    if (args.method == 'write') {
                        assert.equal(args.args[1].color, 5, 'The sent color index should be 5')
                    }
                    return this._super.apply(this, arguments);
                }
            }, { positionalClicks: true });
            assert.equal($('.o_color_pill').length, 12, 'There are 12 color pill');
            await testUtils.dom.click($('.o_color_pill.o_color_5'));
            await testUtils.dom.click($('.o_control_panel .o_form_button_save'));
            assert.equal($('.o_color_pill').length, 1, 'There is only 1 color pill after save')
            assert.equal($('.o_color_pill.active').hasClass('o_color_5'), true, "Color index should be 5")
            form.destroy();
        });
        
        QUnit.test('Check default color when create record', async function(assert) {
            assert.expect(1);
            var form = await createView({
                View: FormView,
                model: 'project_task_type',
                data: this.data,
                arch: '<form string="Stages">' +
                    '<group>' +
                    '<field name="name" />' +
                    '<field name="color" widget="int_color"/>' +
                    '</group>' +
                    '</form>',
                viewOptions: {
                    mode: 'edit',
                },
            }, { positionalClicks: true });
            assert.equal($('.o_color_pill.active').hasClass('o_color_0'), true, "Default olor index should be 0")
            form.destroy();
        });
    })
})
