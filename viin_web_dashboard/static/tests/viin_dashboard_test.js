odoo.define('viin_web_dashboard.viin_dashboard_test', function(require) {
	var ViinDashboardView = require('viin_web_dashboard.ViinDashboardView');
	var testUtils = require('viin_web_dashboard.test_utils');
	var session = require('web.session');
	var sample_cohort_data = require('viin_web_dashboard.sample_cohort_data');

	var createViinDashboardView = testUtils.createViinDashboardView;

	function _preventScroll(ev) {
		ev.stopImmediatePropagation();
	}

	function timeout(ms) {
		return new Promise(resolve => setTimeout(resolve, ms));
	}

	function offsetByDay(d, days = 0) {
		d.setDate(d.getDate() + days);
		var year = d.getFullYear();
		var month = ('0' + (d.getMonth() + 1)).substr(-2);
		var day = ('0' + d.getDate()).substr(-2);

		var hours = ('0' + d.getHours()).substr(-2);
		var minute = ('0' + d.getMinutes()).substr(-2);
		var second = ('0' + d.getSeconds()).substr(-2);

		return year + '-' + month + '-' + day + ' ' + hours + ':' + minute + ':' + second;
	}

	QUnit.module('Views', {
		beforeEach: function() {
			window.addEventListener('scroll', _preventScroll, true);
			session.uid = -1; // TO CHECK
			this.data = {
				lead: {
					fields: {
						id: { string: "ID", type: "integer" },
						date_deadline: { string: "Date Deadline", type: "datetime", store: true },
						create_date: { string: "Create Date", type: "datetime" },
						name: { string: "name", type: "char" },
						email_from: { string: "Email From", type: "char", store: true },
						city: { string: 'City', type: 'char', store: true },
						phone: { string: 'Phone', type: 'char', store: true },
						activity_date_deadline: { string: 'Planned End Date', type: 'datetime' },
						activity_summary: { string: 'Summary', type: 'char' },
						medium_id: { 'type': 'many2one', 'string': 'Medium', relation: 'utm_medium', store: true },
						campaign_id: { 'type': 'many2one', 'string': 'Campaign', relation: 'utm_campaign', store: true },
						source_id: { 'type': 'many2one', 'string': 'Source', relation: 'utm_source', store: true },
						stage_id: { 'type': 'many2one', 'string': 'Stage', relation: 'stage', store: true },
						planned_revenue: { string: 'Planned Revenue', type: 'float', group_operator: "sum" },
						probability: { string: 'Probability', type: 'float' },
						user_id: { string: "User", type: "many2one", relation: 'user', default: session.uid, store: true },
						referred: { string: 'Referred By', type: 'char', store: true },
						write_date: { string: 'Write Date', type: "datetime", store: true },
						company_id: { string: "Company", type: "many2one", relation: "company", store: true },
						priority: {
							string: "Priority", type: "selection", selection: [
								['0', 'Low'],
								['1', 'Medium'],
								['2', 'High'],
								['3', 'Very High'],
							], store: true
						},
						date_closed: { string: 'Closed Date', type: 'datetime', store: true },
						activity_exception_decoration: {
							string: "Priority", type: "selection", selection: [
								['warning', 'Alert'],
								['danger', 'Error'],
							]
						},
						expected_revenue: { string: "Prorated Revenue", type: 'monetary', group_operator: 'sum' },
						day_open: { string: "Days to Assign", type: "float", store: true },
						day_close: { string: "Days to Close", type: "float", store: true },
						days_exceeding_closing: { string: "Exceeded Closing Days", type: "float" },
						won_status: {
							string: "Is Won", selection: [
								['won', 'Won'],
								['lost', 'Lost'],
								['pending', 'Pending'],
							]
						},
						active: { string: 'Active', type: 'boolean', default: true },
					},
					records: [
						{
							"id": 25,
							"date_deadline": false,
							"create_date": offsetByDay(new Date(), -20),
							"name": "Modern Open Space",
							"email_from": "henry@elight.com",
							"city": "Buenos Aires",
							"activity_date_deadline": offsetByDay(new Date(), -10).split(' ')[0],
							"medium_id": false,
							"campaign_id": 3,
							"source_id": 1,
							"stage_id": 3,
							"planned_revenue": 4500,
							"probability": 60,
							"user_id": 2,
							"write_date": offsetByDay(new Date(), -18),
							"company_id": 1,
							"priority": "2",
							"date_closed": false,
							"activity_exception_decoration": false,
							"activity_exception_icon": false,
							"expected_revenue": 2700.0,
							"day_open": 1.0,
							"day_close": 0.0,
							"days_exceeding_closing": 0.0,
							"won_status": 'pending',
							"active": true
						},
						{
							"id": 21,
							"date_deadline": false,
							"create_date": offsetByDay(new Date(), -20),
							"name": "Office Design and Architecture",
							"email_from": "ready.mat28@example.com",
							"city": "Birmingham",
							"activity_date_deadline": offsetByDay(new Date(), -10).split(' ')[0],
							"medium_id": 2,
							"campaign_id": 3,
							"source_id": 1,
							"stage_id": 3,
							"planned_revenue": 9000,
							"probability": 91.67,
							"user_id": 2,
							"write_date": offsetByDay(new Date(), -15),
							"company_id": 1,
							"priority": "2",
							'date_closed': false,
							"activity_exception_decoration": false,
							"activity_exception_icon": false,
							"expected_revenue": 0.0,
							"day_open": 1.0,
							"day_close": 0.0,
							"days_exceeding_closing": 0.0, "won_status": 'pending',
							"active": true
						},
						{
							"id": 20,
							"date_deadline": false,
							"create_date": offsetByDay(new Date(), -30),
							"name": "Distributor Contract",
							"email_from": "john.b@tech.info",
							"phone": "+1 312 349 2324",
							"city": "Chicago",
							"activity_date_deadline": offsetByDay(new Date(), -20).split(' ')[0],
							"medium_id": false,
							"campaign_id": 4,
							"source_id": 2,
							"stage_id": 4,
							"planned_revenue": 19800,
							"probability": 100,
							"user_id": 2,
							"write_date": offsetByDay(new Date(), -25),
							"company_id": 1,
							"priority": "2",
							"date_closed": offsetByDay(new Date(), -20),
							"activity_exception_decoration": false,
							"activity_exception_icon": false,
							"expected_revenue": 19800.0,
							"day_open": 7.0,
							"day_close": 7.0,
							"days_exceeding_closing": 0.0,
							"won_status": "won",
							"active": true
						},
						{
							"id": 16,
							"date_deadline": offsetByDay(new Date(), -20).split(' ')[0],
							"create_date": offsetByDay(new Date(), -22),
							"name": "Global Solutions: Furnitures",
							"email_from": "ready.mat28@example.com",
							"phone": "(803)-873-6126",
							"city": "Liverpool",
							"activity_date_deadline": offsetByDay(new Date(), -17).split(' ')[0],
							"medium_id": false,
							"campaign_id": 4,
							"source_id": 2,
							"stage_id": 2,
							"planned_revenue": 3800,
							"probability": 90,
							"user_id": 2,
							"write_date": offsetByDay(new Date(), -21),
							"company_id": 1,
							"priority": "2",
							"date_closed": false,
							"activity_exception_decoration": false,
							"activity_exception_icon": false,
							"expected_revenue": 3420.0, "day_open": 2.0,
							"day_close": 0.0, "days_exceeding_closing": 0.0,
							"won_status": 'pending',
							"active": true
						},
						{
							"id": 32,
							"date_deadline": offsetByDay(new Date(), -21).split(' ')[0],
							"create_date": offsetByDay(new Date(), -22),
							"name": "Quote for 600 Chairs",
							"email_from": "ErikNFrench@armyspy.com",
							"phone": false,
							"city": "Chevy Chase",
							"activity_date_deadline": false,
							"medium_id": 4,
							"campaign_id": 4,
							"source_id": 1,
							"stage_id": 2,
							"planned_revenue": 22500,
							"probability": 20,
							"user_id": 2,
							"write_date": offsetByDay(new Date(), -19),
							"company_id": 1,
							"priority": "1",
							"date_closed": false,
							"activity_exception_decoration": false,
							"activity_exception_icon": false,
							"expected_revenue": 4500.0,
							"day_open": 61.0,
							"day_close": 0.0,
							"days_exceeding_closing": 0.0,
							"won_status": "pending",
							"active": true
						},
						{
							"id": 31,
							"date_deadline": offsetByDay(new Date(), -15).split(' ')[0],
							"create_date": offsetByDay(new Date(), -21),
							"name": "Quote for 150 carpets",
							"email_from": "ErikNFrench@armyspy.com",
							"phone": false,
							"city": "Chevy Chase",
							"activity_date_deadline": false,
							"medium_id": 4,
							"campaign_id": 4,
							"source_id": 1,
							"stage_id": 1,
							"planned_revenue": 40000,
							"probability": 10,
							"user_id": 2,
							"write_date": offsetByDay(new Date(), -19),
							"company_id": 1,
							"priority": "1",
							"date_closed": false,
							"activity_exception_decoration": false,
							"activity_exception_icon": false,
							"expected_revenue": 4000.0,
							"day_open": 31.0,
							"day_close": 0.0,
							"days_exceeding_closing": 0.0,
							"won_status": 'pending',
							"active": true
						},
						{
							"id": 22,
							"date_deadline": false,
							"create_date": offsetByDay(new Date(), -25),
							"name": "5 VP Chairs",
							"email_from": "azure.Interior24@example.com",
							"phone": "(870)-931-0505",
							"city": "Fremont",
							"activity_date_deadline": offsetByDay(new Date(), -15).split(' ')[0],
							"medium_id": 4,
							"campaign_id": 3,
							"source_id": 1,
							"stage_id": 3,
							"planned_revenue": 5600,
							"probability": 30,
							"user_id": 2,
							"write_date": offsetByDay(new Date(), -18),
							"company_id": 1,
							"priority": "1",
							"date_closed": false,
							"activity_exception_decoration": false,
							"activity_exception_icon": false,
							"expected_revenue": 1680.0,
							"day_open": 8.0,
							"day_close": 0.0,
							"days_exceeding_closing": 0.0,
							"won_status": 'pending',
							"active": true
						},
						{
							"id": 15,
							"date_deadline": offsetByDay(new Date(), -15).split(' ')[0],
							"create_date": offsetByDay(new Date(), -20),
							"name": "Info about services",
							"email_from": "virginie@agrolait.com",
							"phone": "+32 10 588 558",
							"city": "Wavre",
							"activity_date_deadline": offsetByDay(new Date(), -14).split(' ')[0],
							"medium_id": false,
							"campaign_id": 4,
							"source_id": 3,
							"stage_id": 2,
							"planned_revenue": 25000,
							"probability": 30,
							"user_id": 2,
							"write_date": offsetByDay(new Date(), -20),
							"company_id": 1,
							"priority": "1",
							"date_closed": false,
							"activity_exception_decoration": false,
							"activity_exception_icon": false,
							"expected_revenue": 7500.0,
							"day_open": 1.0,
							"day_close": 0.0,
							"days_exceeding_closing": 0.0,
							"won_status": 'pending',
							"active": true
						},
						{
							"id": 13,
							"date_deadline": offsetByDay(new Date(), -14).split(' ')[0],
							"create_date": offsetByDay(new Date(), -20),
							"name": "Quote for 12 Tables",
							"email_from": "willmac@rediffmail.example.com",
							"phone": false,
							"city": "Melbourne",
							"activity_date_deadline": offsetByDay(new Date(), -15).split(' ')[0],
							"activity_summary": "Meeting to go over pricing information.",
							"medium_id": 4,
							"campaign_id": 4,
							"source_id": 1,
							"stage_id": 1,
							"planned_revenue": 40000,
							"probability": 10,
							"user_id": 2,
							"write_date": offsetByDay(new Date(), -19),
							"company_id": 1,
							"priority": "1",
							"date_closed": false,
							"activity_exception_decoration": false,
							"activity_exception_icon": false,
							"expected_revenue": 4000.0,
							"day_open": 1.0,
							"day_close": 0.0,
							"days_exceeding_closing": 0.0,
							"won_status": 'pending',
							"active": true
						},
						{
							"id": 24,
							"date_deadline": false,
							"create_date": offsetByDay(new Date(), -20),
							"name": "Need 20 Desks",
							"email_from": "info@mycompany.net",
							"phone": false,
							"city": "Lima",
							"activity_date_deadline": offsetByDay(new Date(), -15).split(' ')[0],
							"medium_id": 1,
							"campaign_id": 3,
							"source_id": 1,
							"stage_id": 3,
							"planned_revenue": 60000,
							"probability": 90,
							"user_id": 2,
							"write_date": offsetByDay(new Date(), -15),
							"company_id": 1,
							"priority": "0",
							"date_closed": false,
							"activity_exception_decoration": false,
							"activity_exception_icon": false,
							"expected_revenue": 54000.0,
							"day_open": 7.0,
							"day_close": 0.0,
							"days_exceeding_closing": 0.0,
							"won_status": 'pending',
							"active": true
						}
					],
					check_access_rights: function() {
						return Promise.resolve(true);
					},
				},
				company: {
					fields: {
						id: { string: "ID", type: "integer" },
						name: { string: "name", type: "char" },
						display_name: { string: "Display Name", type: "char" },
					},
					records: [
						{ id: 1, name: "Chicago Company", display_name: "Chicago Company" },
						{ id: 2, name: "San Fransisco Company", display_name: "San Fransisco Company" },
					]
				},
				user: {
					fields: {
						id: { string: "ID", type: "integer" },
						name: { string: "Name", type: "char" },
						display_name: { string: "Displayed name", type: "char" },
					},
					records: [
						{ id: session.uid, display_name: "user 1" },
						{ id: 4, display_name: "user 4" },
						{ id: 2, display_name: "Michell" },
					]
				},
				stage: {
					fields: {
						id: { string: "ID", type: "integer" },
						name: { string: "name", type: "char" },
						display_name: { string: "Display Name", type: "char" },
						color: { string: "Color", type: "integer" },
						sequence: { string: "Sequence", type: "integer" },
					},
					records: [
						{ id: 1, name: "New", display_name: "New", color: 1, sequence: 1 },
						{ id: 2, name: "Qualified", display_name: "Qualified", color: 2, sequence: 2 },
						{ id: 3, name: "Proposition", display_name: "Proposition", color: 2, sequence: 2 },
						{ id: 4, name: "Won", display_name: "Won", color: 2, sequence: 2 },
					]
				},
				utm_medium: {
					fields: {
						id: { string: "ID", type: "integer" },
						name: { string: "Medium Name", type: "char" },
					},
					records: [
						{ id: 1, name: "Website" },
						{ id: 2, name: "Phone" },
						{ id: 3, name: "Direct" },
						{ id: 4, name: "Email" },
						{ id: 5, name: "Banner" },
						{ id: 6, name: "Twitter" },
						{ id: 7, name: "Facebook" },
						{ id: 8, name: "LinkedIn" },
						{ id: 9, name: "Television" },
						{ id: 10, name: "Google Adwords" },
					]
				},
				utm_campaign: {
					fields: {
						id: { string: "ID", type: "integer" },
						name: { string: "Campaign Name", type: "char" },
					},
					records: [
						{ id: 1, name: "Sale" },
						{ id: 2, name: "Christmas Special" },
						{ id: 3, name: "Email Campaign - Services" },
						{ id: 4, name: "Email Campaign - Products" },
					]
				},
				utm_source: {
					fields: {
						id: { string: "ID", type: "integer" },
						name: { string: "Source Name", type: "char" },
					},
					records: [
						{ id: 1, name: "Search engine" },
						{ id: 2, name: "Lead Recall" },
						{ id: 3, name: "Newsletter" },
						{ id: 4, name: "Facebook" },
						{ id: 5, name: "Twitter" },
					]
				}

			};
		},
		afterEach: function() {
			window.removeEventListener('scroll', _preventScroll, true);
		},
	}, function() {
		QUnit.module('ViinDashboardView');

		var archs = {
			"lead,false,form":
				'<form>' +
				'<field name="name"/>' +
				'</form>',
			"lead,1,form":
				'<form>' +
				'</form>',
			"lead,viin_crm.crm_opportunity_view_graph,graph":
				'<graph>' +
				'<field name="stage_id" type="row" />' +
				'<field name="date_deadline" interval="month" type="row" />' +
				'</graph>',
			"lead,crm.crm_lead_view_pivot,pivot":
				'<pivot string="Pipeline Analysis">' +
				'<field name="create_date" interval="month" type="row"/>' +
				'<field name="stage_id" type="col"/>' +
				'<field name="planned_revenue" type="measure"/>' +
				'</pivot>',
			"lead,viin_crm.crm_lead_view_viin_cohort,viin_cohort":
				'<viin_cohort string="Opportunities" ' +
				'start_date="create_date" stop_date="date_closed" interval="week" ' +
				'mode="churn" />',
		};

		odoo.session_info = {};
		odoo.session_info.user_context = {};

		QUnit.test('simple rendering web dashboard', async function(assert) {
			assert.expect(3);
			var viin_dashboard = await createViinDashboardView({
				View: ViinDashboardView,
				model: 'lead',
				data: this.data,
				arch: `
					<viin_dashboard>
					<view type="graph" ref="viin_crm.crm_opportunity_view_graph" />
					<group>
						<group>
							<widget name="pie_chart" title="Win/Loss Ratio"
								attrs="{'groupby': 'won_status', 'domain': '[\\'|\\', (\\'active\\', \\'=\\', False), (\\'active\\', \\'=\\', True), (\\'won_status\\', \\'!=\\', \\'pending\\')]'}" />
							<widget name="pie_chart" title="Medium"
								attrs="{'groupby': 'medium_id'}" />
						</group>
						<group>
							<widget name="pie_chart" title="Source"
								attrs="{'groupby': 'source_id'}" />
							<widget name="pie_chart" title="Campaign"
								attrs="{'groupby': 'campaign_id'}" />
						</group>
						<group>
							<aggregate name="opportunities" string="Opportunities"
								group_operator="count" field="id" measure="__count__" />
							<aggregate name="expected_revenue_aggregate"
								field="planned_revenue" string="Expected Revenue" />
							<aggregate name="prorated_revenue_aggregate"
								field="expected_revenue" invisible="1" />
							<formula name="prorated_revenue"
								string="Prorated Revenue"
								value="record.prorated_revenue_aggregate" widget="monetary" />
							<formula name="deal_size" string="Average Deal Size"
								value="record.expected_revenue_aggregate / record.opportunities"
								widget="monetary" />
						</group>
						<group>
							<aggregate name="days_to_assign"
								string="Days to Assign" field="day_open" group_operator="avg"
								value_label="days" />
							<aggregate name="days_to_close" string="Days to Close"
								field="day_close" group_operator="avg" value_label="days" />
							<aggregate name="days_exceeding_closing"
								string="Exceeding Close Days" field="days_exceeding_closing"
								group_operator="avg" />
						</group>
					</group>
					<view type="pivot" ref="crm.crm_lead_view_pivot" />
					<view type="viin_cohort" ref="viin_crm.crm_lead_view_viin_cohort" />
				</viin_dashboard>
				`,

				archs: archs,
				mockRPC: function(route, args) {
					var aggregate_fields = [
						"opportunities:count(id)",
						"expected_revenue_aggregate:sum(planned_revenue)",
						"prorated_revenue_aggregate:sum(expected_revenue)",
						"days_to_assign:avg(day_open)",
						"days_to_close:avg(day_close)",
						"days_exceeding_closing:avg(days_exceeding_closing)"
					]
					if (route == '/web/viin_cohort/get_data') {
						return Promise.resolve(sample_cohort_data.get_cohort_data_week());
					}
					if (route == '/web/dataset/call_kw/lead/read_group' && _.isEqual(args.kwargs.fields, aggregate_fields)) {
						var aggregate_sample_data = {
							"id": 13,
							"__count": 10,
							"opportunities": 10,
							"expected_revenue_aggregate": 320200,
							"prorated_revenue_aggregate": 131875,
							"days_to_assign": 8.9,
							"days_to_close": 5.8,
							"days_exceeding_closing": 6.13
						}
						return Promise.resolve([aggregate_sample_data]);
					}
					return this._super.apply(this, arguments);
				},
				viewOptions: {},
			}, { positionalClicks: true });
			await timeout(1000);
			assert.equal($('.o_viin_dashboard_subview[type=graph]').length, 1, 'should have 1 sub view graph');
			assert.equal($('.o_viin_dashboard_subview[type=pivot]').length, 1, 'should have 1 sub view pivot');
			assert.equal($('.o_viin_dashboard_subview[type=viin_cohort]').length, 1, 'should have 1 sub view viin_cohort');
			viin_dashboard.destroy();
		});

		QUnit.test('check sub view functionality in viin dashboard', async function(assert) {
			assert.expect(3);
			var viin_dashboard = await createViinDashboardView({
				View: ViinDashboardView,
				model: 'lead',
				data: this.data,
				arch: `
					<viin_dashboard>
					<view type="graph" ref="viin_crm.crm_opportunity_view_graph" />
					<group>
						<group>
							<widget name="pie_chart" title="Win/Loss Ratio"
								attrs="{'groupby': 'won_status', 'domain': '[\\'|\\', (\\'active\\', \\'=\\', False), (\\'active\\', \\'=\\', True), (\\'won_status\\', \\'!=\\', \\'pending\\')]'}" />
							<widget name="pie_chart" title="Medium"
								attrs="{'groupby': 'medium_id'}" />
						</group>
						<group>
							<widget name="pie_chart" title="Source"
								attrs="{'groupby': 'source_id'}" />
							<widget name="pie_chart" title="Campaign"
								attrs="{'groupby': 'campaign_id'}" />
						</group>
						<group>
							<aggregate name="opportunities" string="Opportunities"
								group_operator="count" field="id" measure="__count__" />
							<aggregate name="expected_revenue_aggregate"
								field="planned_revenue" string="Expected Revenue" />
							<aggregate name="prorated_revenue_aggregate"
								field="expected_revenue" invisible="1" />
							<formula name="prorated_revenue"
								string="Prorated Revenue"
								value="record.prorated_revenue_aggregate" widget="monetary" />
							<formula name="deal_size" string="Average Deal Size"
								value="record.expected_revenue_aggregate / record.opportunities"
								widget="monetary" />
						</group>
						<group>
							<aggregate name="days_to_assign"
								string="Days to Assign" field="day_open" group_operator="avg"
								value_label="days" />
							<aggregate name="days_to_close" string="Days to Close"
								field="day_close" group_operator="avg" value_label="days" />
							<aggregate name="days_exceeding_closing"
								string="Exceeding Close Days" field="days_exceeding_closing"
								group_operator="avg" />
						</group>
					</group>
					<view type="pivot" ref="crm.crm_lead_view_pivot" />
					<view type="viin_cohort" ref="viin_crm.crm_lead_view_viin_cohort" />
				</viin_dashboard>
				`,
				archs: archs,
				mockRPC: function(route, args) {
					var aggregate_fields = [
						"opportunities:count(id)",
						"expected_revenue_aggregate:sum(planned_revenue)",
						"prorated_revenue_aggregate:sum(expected_revenue)",
						"days_to_assign:avg(day_open)",
						"days_to_close:avg(day_close)",
						"days_exceeding_closing:avg(days_exceeding_closing)"
					]
					if (route == '/web/viin_cohort/get_data') {
						return Promise.resolve(sample_cohort_data.get_cohort_data_week());
					}
					if (route == '/web/dataset/call_kw/lead/read_group' && _.isEqual(args.kwargs.fields, aggregate_fields)) {
						var aggregate_sample_data = {
							"id": 13,
							"__count": 10,
							"opportunities": 10,
							"expected_revenue_aggregate": 320200,
							"prorated_revenue_aggregate": 131875,
							"days_to_assign": 8.9,
							"days_to_close": 5.8,
							"days_exceeding_closing": 6.13
						}
						return Promise.resolve([aggregate_sample_data]);
					}
					return this._super.apply(this, arguments);
				},
				viewOptions: {},
			}, { positionalClicks: true });
			await timeout(1000);
			/*
			* Counting number of cell contain value of priority field before select priority field
			*/
			var priority_cell_count_1 = $('.o_pivot .o_pivot_header_cell_closed[data-original-title=Priority]').length;
			var close_pivot_header_cell = $('.o_viin_dashboard_subview[type=pivot] .o_pivot table thead .o_pivot_header_cell_closed');
			await testUtils.dom.click(close_pivot_header_cell.first());
			assert.equal($('.o_pivot_field_menu.show').length, 1, 'should show menu of field to select');
			assert.equal($('.o_pivot_field_menu.show .dropdown-item.disabled').length, 1, 'should have only 1 selected field');
			// select priority field
			await testUtils.dom.click($('.o_pivot_field_menu.show .dropdown-item[data-field=priority]'));
			await timeout(1000);
			/*
			* Counting number of cell contain value of priority field after select priority field
			*/
			var priority_cell_count_2 = $('.o_pivot .o_pivot_header_cell_closed[data-original-title=Priority]').length;
			assert.equal(priority_cell_count_1 < priority_cell_count_2, true, 'Priority field value should displayed in cell.');
			viin_dashboard.destroy();
		});

		QUnit.test('when switch to screen of sub view button with graph', async function(assert) {
			assert.expect(1);
			var viin_dashboard = await createViinDashboardView({
				View: ViinDashboardView,
				model: 'lead',
				data: this.data,
				arch: `
					<viin_dashboard>
					<view type="graph" ref="viin_crm.crm_opportunity_view_graph" />
					<group>
						<group>
							<aggregate name="opportunities" string="Opportunities"
								group_operator="count" field="id" measure="__count__" />
							<aggregate name="expected_revenue_aggregate"
								field="planned_revenue" string="Expected Revenue" />
							<aggregate name="prorated_revenue_aggregate"
								field="expected_revenue" invisible="1" />
							<formula name="prorated_revenue"
								string="Prorated Revenue"
								value="record.prorated_revenue_aggregate" widget="monetary" />
							<formula name="deal_size" string="Average Deal Size"
								value="record.expected_revenue_aggregate / record.opportunities"
								widget="monetary" />
						</group>
						<group>
							<aggregate name="days_to_assign"
								string="Days to Assign" field="day_open" group_operator="avg"
								value_label="days" />
							<aggregate name="days_to_close" string="Days to Close"
								field="day_close" group_operator="avg" value_label="days" />
							<aggregate name="days_exceeding_closing"
								string="Exceeding Close Days" field="days_exceeding_closing"
								group_operator="avg" />
						</group>
					</group>
					<view type="pivot" ref="crm.crm_lead_view_pivot" />
					<view type="viin_cohort" ref="viin_crm.crm_lead_view_viin_cohort" />
				</viin_dashboard>
				`,
				archs: archs,
				mockRPC: function(route, args) {
					if (route == '/web/viin_cohort/get_data') {
						return Promise.resolve(sample_cohort_data.get_cohort_data_week());
					}
					return this._super.apply(this, arguments);
				},
				intercepts: {
					do_action: function(event) {
						// When click switch view button, action open_fullscreen in viin dashboard will trigger 
						// window action, this method will receive the action data in testing js
						assert.deepEqual(event.data.action.views, [[false, 'graph']], 'show open full screen graph view');
					},
				},
				viewOptions: {},
			}, { positionalClicks: true });
			await timeout(1000);
			await testUtils.dom.click($('.o_viin_dashboard_subview[type=graph] .o_button_switch'));
			viin_dashboard.destroy();
		});

		QUnit.test('when switch to screen of sub view button with pivot', async function(assert) {
			assert.expect(1);
			var viin_dashboard = await createViinDashboardView({
				View: ViinDashboardView,
				model: 'lead',
				data: this.data,
				arch: `
					<viin_dashboard>
					<view type="graph" ref="viin_crm.crm_opportunity_view_graph" />
					<group>
						<group>
							<aggregate name="opportunities" string="Opportunities"
								group_operator="count" field="id" measure="__count__" />
							<aggregate name="expected_revenue_aggregate"
								field="planned_revenue" string="Expected Revenue" />
							<aggregate name="prorated_revenue_aggregate"
								field="expected_revenue" invisible="1" />
							<formula name="prorated_revenue"
								string="Prorated Revenue"
								value="record.prorated_revenue_aggregate" widget="monetary" />
							<formula name="deal_size" string="Average Deal Size"
								value="record.expected_revenue_aggregate / record.opportunities"
								widget="monetary" />
						</group>
						<group>
							<aggregate name="days_to_assign"
								string="Days to Assign" field="day_open" group_operator="avg"
								value_label="days" />
							<aggregate name="days_to_close" string="Days to Close"
								field="day_close" group_operator="avg" value_label="days" />
							<aggregate name="days_exceeding_closing"
								string="Exceeding Close Days" field="days_exceeding_closing"
								group_operator="avg" />
						</group>
					</group>
					<view type="pivot" ref="crm.crm_lead_view_pivot" />
					<view type="viin_cohort" ref="viin_crm.crm_lead_view_viin_cohort" />
				</viin_dashboard>
				`,
				archs: archs,
				mockRPC: function(route, args) {
					if (route == '/web/viin_cohort/get_data') {
						return Promise.resolve(sample_cohort_data.get_cohort_data_week());
					}
					return this._super.apply(this, arguments);
				},
				intercepts: {
					do_action: function(event) {
						// When click switch view button, action open_fullscreen in viin dashboard will trigger 
						// window action, this method will receive the action data in testing js
						assert.deepEqual(event.data.action.views, [[false, 'pivot']], 'show open full screen pivot view');
					},
				},
				viewOptions: {},
			}, { positionalClicks: true });
			await timeout(1000);
			await testUtils.dom.click($('.o_viin_dashboard_subview[type=pivot] .o_button_switch'));
			viin_dashboard.destroy();
		});

		QUnit.test('when switch to screen of sub view button with viin cohort', async function(assert) {
			assert.expect(1);
			var viin_dashboard = await createViinDashboardView({
				View: ViinDashboardView,
				model: 'lead',
				data: this.data,
				arch: `
					<viin_dashboard>
					<view type="graph" ref="viin_crm.crm_opportunity_view_graph" />
					<group>
						<group>
							<aggregate name="opportunities" string="Opportunities"
								group_operator="count" field="id" measure="__count__" />
							<aggregate name="expected_revenue_aggregate"
								field="planned_revenue" string="Expected Revenue" />
							<aggregate name="prorated_revenue_aggregate"
								field="expected_revenue" invisible="1" />
							<formula name="prorated_revenue"
								string="Prorated Revenue"
								value="record.prorated_revenue_aggregate" widget="monetary" />
							<formula name="deal_size" string="Average Deal Size"
								value="record.expected_revenue_aggregate / record.opportunities"
								widget="monetary" />
						</group>
						<group>
							<aggregate name="days_to_assign"
								string="Days to Assign" field="day_open" group_operator="avg"
								value_label="days" />
							<aggregate name="days_to_close" string="Days to Close"
								field="day_close" group_operator="avg" value_label="days" />
							<aggregate name="days_exceeding_closing"
								string="Exceeding Close Days" field="days_exceeding_closing"
								group_operator="avg" />
						</group>
					</group>
					<view type="pivot" ref="crm.crm_lead_view_pivot" />
					<view type="viin_cohort" ref="viin_crm.crm_lead_view_viin_cohort" />
				</viin_dashboard>
				`,
				archs: archs,
				mockRPC: function(route, args) {
					if (route == '/web/viin_cohort/get_data') {
						return Promise.resolve(sample_cohort_data.get_cohort_data_week());
					}
					return this._super.apply(this, arguments);
				},
				intercepts: {
					do_action: function(event) {
						// When click switch view button, action open_fullscreen in viin dashboard will trigger 
						// window action, this method will receive the action data in testing js
						assert.deepEqual(event.data.action.views, [[false, 'viin_cohort']], 'show open full screen viin cohort view');
					},
				},
				viewOptions: {},
			}, { positionalClicks: true });
			await timeout(1000);
			await testUtils.dom.click($('.o_viin_dashboard_subview[type=viin_cohort] .o_button_switch'));
			viin_dashboard.destroy();
		});

		QUnit.test('checking data display in viin cohort sub view', async function(assert) {
			assert.expect(5);
			var viin_dashboard = await createViinDashboardView({
				View: ViinDashboardView,
				model: 'lead',
				data: this.data,
				arch: `
					<viin_dashboard>
					<view type="graph" ref="viin_crm.crm_opportunity_view_graph" />
					<group>
						<group>
							<aggregate name="opportunities" string="Opportunities"
								group_operator="count" field="id" measure="__count__" />
							<aggregate name="expected_revenue_aggregate"
								field="planned_revenue" string="Expected Revenue" />
							<aggregate name="prorated_revenue_aggregate"
								field="expected_revenue" invisible="1" />
							<formula name="prorated_revenue"
								string="Prorated Revenue"
								value="record.prorated_revenue_aggregate" widget="monetary" />
							<formula name="deal_size" string="Average Deal Size"
								value="record.expected_revenue_aggregate / record.opportunities"
								widget="monetary" />
						</group>
						<group>
							<aggregate name="days_to_assign"
								string="Days to Assign" field="day_open" group_operator="avg"
								value_label="days" />
							<aggregate name="days_to_close" string="Days to Close"
								field="day_close" group_operator="avg" value_label="days" />
							<aggregate name="days_exceeding_closing"
								string="Exceeding Close Days" field="days_exceeding_closing"
								group_operator="avg" />
						</group>
					</group>
					<view type="pivot" ref="crm.crm_lead_view_pivot" />
					<view type="viin_cohort" ref="viin_crm.crm_lead_view_viin_cohort" />
				</viin_dashboard>
				`,
				archs: archs,
				mockRPC: function(route, args) {
					if (route == '/web/viin_cohort/get_data') {
						return Promise.resolve(sample_cohort_data.get_cohort_data_week());
					}
					return this._super.apply(this, arguments);
				},
				viewOptions: {},
			}, { positionalClicks: true });
			await timeout(1000);
			var row1Col2Val = $('.viin_cohort_row').eq(0).find('.viin_cohort_cell_value').eq(1).text();
			row1Col2Val = row1Col2Val.trim();
			assert.equal(row1Col2Val, '1.0', 'The 2nd column of 1st row should have value of 1.0');
			var row2Col2Val = $('.viin_cohort_row').eq(1).find('.viin_cohort_cell_value').eq(1).text();
			row2Col2Val = row2Col2Val.trim();
			assert.equal(row2Col2Val, '1.0', 'The 2nd column of 2nd row should have value of 1.0');

			var row3Col2Val = $('.viin_cohort_row').eq(2).find('.viin_cohort_cell_value').eq(1).text();
			row3Col2Val = row3Col2Val.trim();
			assert.equal(row3Col2Val, '4.0', 'The 2nd column of 3rd row should have value of 4.0');

			var row4Col2Val = $('.viin_cohort_row').eq(3).find('.viin_cohort_cell_value').eq(1).text();
			row4Col2Val = row4Col2Val.trim();
			assert.equal(row4Col2Val, '4.0', 'The 2nd column of 4th row should have value of 4.0');

			var row3Col4Val = $('.viin_cohort_row').eq(2).find('.viin_cohort_cell_value').eq(3).text();
			row3Col4Val = row3Col4Val.trim();
			assert.equal(row3Col4Val, '25%', 'The 4th column of 3rd row should have value of 25%');
			viin_dashboard.destroy();
		});
	});
});
