odoo.define('to_org_chart.OrgChartViewTest', function(require) {
	var OrgChartView = require('to_org_chart.OrgChartView');
	var testUtils = require('to_org_chart.test_utils');
	var session = require('web.session');
	var createOrgChartView = testUtils.createOrgChartView;
	var sample_data = require('to_org_chart.sample_data');
	
	function _preventScroll(ev) {
	    ev.stopImmediatePropagation();
	}
    /*
    * recursively loop each tables from top to bottom in org chart and get direct children table
    * to count the level of org chart
    */
    function getDeepestLevelOrgChart(tables, initLevel) {
        var directCollection = [];
        for ( var i = 0; i < tables.length; i++) {
            var directChild = $(tables[i]).find('> .nodes > td > table');
            if(directChild.length > 0) {
                directCollection.push(directChild);
            }
        }
        if(directCollection.length == 0) {
            return initLevel;
        }
        return getDeepestLevelOrgChart(directCollection, initLevel + 1);
    }
    
    function getProgressColorNode(record) {
        progressColor = 'bg-danger'
        if ((record.type == 'aspirational' && record.progress >= 70) ||
            (record.type == 'committed' && record.progress >= 100)) {
            progressColor = 'bg-success';
        }
        return progressColor
    }
    
    function timeout(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
	
	QUnit.module('to_org_chart', {
		beforeEach: function() {
			window.addEventListener('scroll', _preventScroll, true);
			session.uid = -1;
			this.data = {
				okr: {
					fields: {
						id: {string: "ID", type: "integer"},
						name: {string: "name", type: "char"},
                        display_name: {string: "display name", type: "char"},
						year: {string: "year", type: "char"},
						quarter: {string: "quarter", type: "selection", selection: [
                            ['0', 'Q1'],
                            ['1', 'Q2'],
                            ['2', 'Q3'],
                            ['3', 'Q4'],
                        ]},
						time_frame: {string: "time frame", type: "char"},
						quarter_full_name: {string: "quarter full name", type: "char"},
						description: {string: "description", type: "text"},
						mode: {string: "mode", type: "selection", selection: [
							['company', 'Company'],
							['department', 'Department'],
							['employee', 'Employee'],
						]},
						type: {string: "type", type: "selection", selection: [
							['committed', 'Committed'],
							['aspirational', 'Aspirational'],
						]},
						state: {string: "state", type: "selection", selection: [
							['draft', 'Draft'],
							['confirmed', 'Confirmed'],
							['cancelled', 'Cancelled'],
						]},
						result: {string: "result", type: "selection", selection: [
							['successful', 'Successful'],
							['failed', 'Failed'],
						]},
						company_id: {string: "company id", type: "many2one", relation: 'company'},
						department_id: {string: "department id", type: "many2one", relation: 'department'},
						employee_id: {string: "employee id", type: "many2one", relation: 'employee'},
						owner: {string: "owner", type: "char"},
						user_id: {string: "user id", type: "many2one", relation: 'user'},
						parent_id: {string: "parent id", type: "many2one", relation: 'okr'},
						child_ids: {string: "child ids", type: "one2many", relation: 'okr'},
						key_results_count: {string: "key results count", type: "integer"},
						recursive_child_ids: {string: "key results count", type: "many2many", relation: 'okr'},
						points: {string: "points", type: "float"},
						progress: {string: "progress", type: "float"},
						weight: {string: "weight", type: "float"},
					},
					records: sample_data.data_q3(),
				},
				company: {
					fields: {
						id: {string: "ID", type: "integer"},
						name: {string: "name", type: "char"},
					},
					records: [
						{id: 4, name: 'Example Company for OKR'}
					]
				},
				department: {
					fields: {
						id: {string: "ID", type: "integer"},
						name: {string: "name", type: "char"},
					},
					records: []
				},
				employee: {
					fields: {
						id: {string: "ID", type: "integer"},
						name: {string: "name", type: "char"},
					},
					records: [
						{id: 3572, name: 'Owner Example Company'},
					]
				},
				user: {
					fields: {
						id: {string: "ID", type: "integer"},
						name: {string: "name", type: "char"},
					},
					records: [
						{id: 2, name: 'Mitchell Admin'},
					]
				}
			}
		},
		afterEach: function () {
	        window.removeEventListener('scroll', _preventScroll, true);
	    },
	}, function () {
	    QUnit.module('OrgChartView');
	
		odoo.session_info = {};
		odoo.session_info.user_context = {};
        
        QUnit.test('TC01: Q3 rendering test',  async function (assert) {
            assert.expect(2);
            var org_chart = await createOrgChartView({
                View: OrgChartView,
                model: 'okr',
                data: this.data,
                arch: '<tree><field name="name"/></tree>',
                viewOptions: {}
            });
            assert.equal(org_chart.$('.node').length, 16, 'Number of okr node should be 16');
            var superParentTable = $('.to_org_chart > table');
            var depestLevel = getDeepestLevelOrgChart(superParentTable, 1);
            assert.equal(depestLevel, 7, 'The whole level should be 7');
            org_chart.destroy();
        });
        
        QUnit.test('TC02:Q3, Q4 rendering test',  async function (assert) {
            assert.expect(2);
            this.data.okr.records = sample_data.data_q3q4();
            var org_chart = await createOrgChartView({
                View: OrgChartView,
                model: 'okr',
                data: this.data,
                arch: '<tree><field name="name"/></tree>',
                viewOptions: {}
            });
            assert.equal(org_chart.$('.node').length, 20, 'Number of okr node should be 20');
            var superParentTable = $('.to_org_chart > table');
            var depestLevel = getDeepestLevelOrgChart(superParentTable, 1);
            assert.equal(depestLevel, 7, 'The whole level should be 7');
            org_chart.destroy();
        });
        
        QUnit.test('TC03: Q3, Q4 filter for Q4',  async function (assert) {
            assert.expect(2);
            this.data.okr.records = sample_data.data_q3q4();
            var archs = {
                "okr,false,search":
                '<search>'+
                    '<filter name="q4_okr" string="Q4"  domain="[(\'quarter\', \'=\', '+ '\'3\'' +')]"/>'
                +'</search>' 
                
            };
            var org_chart = await createOrgChartView({
                View: OrgChartView,
                model: 'okr',
                data: this.data,
                arch: '<tree><field name="name"/></tree>',
                archs: archs,
                viewOptions: {}
            }, {positionalClicks: true});
            await testUtils.dom.triggerMouseEvent($('.o_filters_menu_button'), 'click');
            await testUtils.dom.triggerMouseEvent($('.o_filters_menu.show .o_menu_item'), 'click');
            await timeout(1000);
            
            assert.equal(org_chart.$('.node').length, 6, 'Number of okr node should be 6');
            var superParentTable = $('.to_org_chart > table');
            var depestLevel = getDeepestLevelOrgChart(superParentTable, 1);
            assert.equal(depestLevel, 5, 'The whole level should be 5');
            org_chart.destroy();
        });
        
        QUnit.test('TC04: Q3, Q4 filter for successfull result',  async function (assert) {
            assert.expect(2);
            this.data.okr.records = sample_data.data_q3q4();
            var archs = {
                "okr,false,search":
                '<search>'+
                    '<filter name="result_okr" string="Successfull"  domain="[(\'result\', \'=\', '+ '\'successful\'' +')]"/>'+
                    '<filter name="q4_okr" string="Q4"  domain="[(\'quarter\', \'=\', '+ '\'3\'' +')]"/>'
                +'</search>' 
                
            };
            var org_chart = await createOrgChartView({
                View: OrgChartView,
                model: 'okr',
                data: this.data,
                arch: '<tree><field name="name"/></tree>',
                archs: archs,
                viewOptions: {}
            }, {positionalClicks: true});
            await testUtils.dom.triggerMouseEvent($('.o_filters_menu_button'), 'click');
            await testUtils.dom.triggerMouseEvent($('.o_filters_menu.show .o_menu_item').first(), 'click');
            await timeout(1000);
            assert.equal(org_chart.$('.node').length, 2, 'Number of okr node should be 2');
            var superParentTable = $('.to_org_chart > table');
            var depestLevel = getDeepestLevelOrgChart(superParentTable, 1);
            assert.equal(depestLevel, 2, 'The whole level should be 2');
            org_chart.destroy();
        });
        
        QUnit.test('TC05: Q3 rendering and click the node',  async function (assert) {
            assert.expect(3);
            this.data.okr.records = sample_data.data_q3();
            var org_chart = await createOrgChartView({
                View: OrgChartView,
                model: 'okr',
                data: this.data,
                arch: '<tree><field name="name"/></tree>',
                viewOptions: {},
            }, {positionalClicks: true});
            testUtils.mock.intercept(org_chart, "open_record", function (event) {
                assert.ok("org chart view should trigger 'open_record' with id:"+ event.data.id +" event");
            });
            await testUtils.dom.triggerMouseEvent($('.objective_name').eq(3), 'click');
            await testUtils.dom.triggerMouseEvent($('.department').eq(3), 'click');
            await testUtils.dom.triggerMouseEvent($('.bottom_block').eq(3), 'click');
            org_chart.destroy();
        });
        
        QUnit.test('TC06: Q3 rendering and test the node action click',  async function (assert) {
            assert.expect(1);
            this.data.okr.records = sample_data.data_q3();
            var org_chart = await createOrgChartView({
                View: OrgChartView,
                model: 'okr',
                data: this.data,
                arch: '<tree><field name="name"/></tree>',
                viewOptions: {},
            }, {positionalClicks: true});
            testUtils.mock.intercept(org_chart, "open_record", function (event) {
                assert.ok("org chart view should trigger 'open_record' with id:"+ event.data.id +" action node event");
            });
            await testUtils.dom.triggerMouseEvent($('#node_menu_4'), 'click');
            await testUtils.dom.triggerMouseEvent(jQuery('.dropdown-menu.show > a').first(), 'click');
            org_chart.destroy();
        });
        
        QUnit.test('TC07: Q3 rendering and test wheel event to scale chart',  async function (assert) {
            assert.expect(1);
            this.data.okr.records = sample_data.data_q3();
            var org_chart = await createOrgChartView({
                View: OrgChartView,
                model: 'okr',
                data: this.data,
                arch: '<tree><field name="name"/></tree>',
                viewOptions: {},
            }, {positionalClicks: true});
            var transform_befor_wheel = document.querySelector('.to_org_chart').style.transform;
            document.querySelector('.to_org_chart').dispatchEvent(new Event('wheel', {"bubbles":true, "cancelable":false}));
            var transform_after_wheel = document.querySelector('.to_org_chart').style.transform;
            assert.notEqual(transform_befor_wheel, transform_after_wheel, 
            'The transform of before should be different from transform of after when trigger wheel event');
            org_chart.destroy();
        });
        
        QUnit.test('TC08: Q3 Q4 test with button arrow in the node of org chart',  async function (assert) {
            assert.expect(5);
            this.data.okr.records = sample_data.data_q3q4();
            var org_chart = await createOrgChartView({
                View: OrgChartView,
                model: 'okr',
                data: this.data,
                arch: '<tree><field name="name"/></tree>',
                viewOptions: {},
            }, {positionalClicks: true});
            assert.ok("Testing with node have record id = 7 in sample data");
            // test with the node have record id = 7
            var node = $('#node_menu_7').parents('.node');
            testUtils.dom.triggerMouseEvent(node, 'mouseenter');
            // b1
            await testUtils.dom.click($('.rightEdge.oci-chevron-left'));
            await timeout(500);
            assert.equal($('.node:not(.slide-left)').length, 17, 'Total should be 17 slide in left node');
            // b2
            testUtils.dom.triggerMouseEvent(node, 'mouseenter');
            await testUtils.dom.click($('.rightEdge.oci.oci-chevron-right'));
            await timeout(500);
            assert.equal($('.node:not(.slide-left)').length, 20, 'Total should be 20 slide out left node');
            //b3
            testUtils.dom.triggerMouseEvent(node, 'mouseenter');
            await testUtils.dom.click($('.topEdge.oci.oci-chevron-down'));
            await timeout(500);
            assert.equal($('.node.slide-up, .node.slide-left, .node.slide-down, .node.slide-right').length, 16, 
            'Total should be 16 slide in all around node except children');
            // b4
            testUtils.dom.triggerMouseEvent(node, 'mouseenter');
            await testUtils.dom.click($('.topEdge.oci-chevron-up'));
            await timeout(500);
            assert.equal($('.node.slide-up, .node.slide-left, .node.slide-down, .node.slide-right').length, 15, 
            'Total should be 15 slide in all around node except children');
            org_chart.destroy();
        });
        
        QUnit.test('TC09: Q3, Q4 rendering and test progress',  async function (assert) {
            assert.expect(1);
            this.data.okr.records = sample_data.data_q3q4();
            var org_chart = await createOrgChartView({
                View: OrgChartView,
                model: 'okr',
                data: this.data,
                arch: '<tree><field name="name"/></tree>',
                viewOptions: {},
            }, {positionalClicks: true});
            // test with the node have record id = 4
            var node = $('#node_menu_4').parents('.node');
            var progress = node.find('.progress .progress-bar');
            assert.equal(progress.hasClass('bg-danger'), true, 
            'Progress bar should have bg-danger class');
            org_chart.destroy();
        });
        
        QUnit.test('TC010: Q3, Q4 rendering and test point with aspirational and committed',  async function (assert) {
            assert.expect(3);
            this.data.okr.records = sample_data.data_q3q4();
            var org_chart = await createOrgChartView({
                View: OrgChartView,
                model: 'okr',
                data: this.data,
                arch: '<tree><field name="name"/></tree>',
                viewOptions: {},
            }, {positionalClicks: true});
            // test with the node have record id = 3
            var node = $('#node_menu_3').parents('.node');
            var progress3 = node.find('.progress .progress-bar');
            // get record id = 3 in data
            var recordId3;
            for(var i =0; i< this.data.okr.records.length; i++) {
                var r = this.data.okr.records[i];
                if(r.id == 3) {
                    recordId3 = r;
                    break;
                }
            }
            
            var progressColor3 = getProgressColorNode(recordId3);
            
            assert.equal(progress3.hasClass(progressColor3), true, 
            'Progress bar of record id of 3 and type is '+ 
            recordId3.type +' and progress is '+ recordId3.progress +' should have '+ progressColor3 +' class');
            
            // test with the node have record id = 4
            var node4 = $('#node_menu_4').parents('.node');
            var progress4 = node4.find('.progress .progress-bar');
            
            // get record id = 4 in data
            var recordId4;
            for(var i =0; i< this.data.okr.records.length; i++) {
                var r = this.data.okr.records[i];
                if(r.id == 4) {
                    recordId4 = r;
                    break;
                }
            }
            var progressColor4 = getProgressColorNode(recordId4);
            assert.equal(progress4.hasClass(progressColor4), true, 
            'Progress bar of record id of 4 and type is '+ 
            recordId4.type +' and progress is '+ recordId4.progress +' should have '+ progressColor4 +' class');
            
            // test with the node have record id = 15
            var node15 = $('#node_menu_15').parents('.node');
            var progress15 = node15.find('.progress .progress-bar');
            
            // get record id = 15 in data
            var recordId15;
            for(var i =0; i< this.data.okr.records.length; i++) {
                var r = this.data.okr.records[i];
                if(r.id == 15) {
                    recordId15 = r;
                    break;
                }
            }
            var progressColor15 = getProgressColorNode(recordId15);
            assert.equal(progress15.hasClass(progressColor15), true, 
            'Progress bar of record id of 15 and type is '+ 
            recordId15.type +' and progress is '+ recordId15.progress +' should have '+ progressColor15 +' class');
            org_chart.destroy();
        });
        
        QUnit.test('TC12: Q3, Q4 rendering and change node with id 1 to Q4',  async function (assert) {
            assert.expect(4);
            this.data.okr.records = sample_data.data_q3q4();
            for(var i =0; i< this.data.okr.records.length; i++) {
                var r = this.data.okr.records[i];
                if(r.id == 1) {
                    assert.equal(r.quarter, "2", "The node 'Hoàn thiện hệ thống SaaS Website Sales' should be 2 at first");
                    assert.notOk($(".quarter_node:contains('4')").closest('table').find('[data-record-id=1]').length,
                "The node 'Hoàn thiện hệ thống SaaS Website Sales' should not exist in Quarter 4 ");
                    this.data.okr.records[i].quarter = "3";
                    assert.ok(this.data.okr.records[i].quarter == "3", "Change 'Hoàn thiện hệ thống SaaS Website Sales' to Q4");
                    break;
                }
            }
            var org_chart = await createOrgChartView({
                View: OrgChartView,
                model: 'okr',
                data: this.data,
                arch: '<tree><field name="name"/></tree>',
                viewOptions: {},
            }, {positionalClicks: true});
            $('')
            assert.ok($(".quarter_node:contains('4')").closest('table').find('[data-record-id=1]').length,
                "The node 'Hoàn thiện hệ thống SaaS Website Sales' should exist in Quarter 4");
            org_chart.destroy();
        });
		
	});
});
