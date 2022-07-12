Installation
============

1. Navigate to Apps
2. Find with keyword 'to_fleet_stock_picking'
3. Install it as usual then you are ready to enjoy the application.

Instructions
============

Concepts
--------

1. Route Section: is a section defined by two addresses where each **Address** (aka From and To) is an Odoo partner record. This design model to ensure short learning curve and easy to extend and fully integrated with existing features in Odoo
2. Waypoint: also known as "Route Waypoint", is a model that presents an instance of an Address which creates a data link between a Route and an Address in Odoo
3. Section Line: also known as "Route Section", is a model that presents an instance of a Section which creates a data link between a Route and an Route Section in Odoo
4. Route: is a model to present a route that defined by Waypoints and Sections. Then Odoo will automatically find and link the related Sections and Addresses for the Route
5. Vehicle Cost: this is a native model offered by the Fleet application to record costs related to your vehicles with Fleet application. It is also used in Fleet Vehicle Trips
6. Driver: an Odoo document (offered by the module `to_fleet_driver`) to help you manage your drivers. Drivers can be assigned to vehicle trips
7. Vehicle Trip: is an Odoo document to help plan and track trips of your vehicles. Each trip can be assigned with a vehicle, a driver, several stock pickings (also known as Delivery Orders, Goods Receipts, etc)

Usages
------
1. Prepare Master Data
	* Create / Update your vehicles (navigating to the menu Fleet > Vehicles)
		* On the vehicle form view, you may want to input the Warning Volume, Max. Volume, Warning Weight Load, Max. Weight Load
	* Create / Update your drivers (navigating to the menu Fleet > Drivers > Drivers).
		* You may also want to update the drivers licenses (Fleet > Drivers > Licenses)
	* Create / Update your Geo-Routes data (Fleet Operations > Routes & Waypoints)
	* Update dimensions (Length, Width, Height) and other parameters (Volume, Weight, etc) for your products on product form views
2. Plan your first trip
	* Navigate to Fleet Operations to see a calendar view of your trips
	* Click on a cell of your desired trip time to open vehicle trip form view
	* Assign a vehicle, a driver, a route, one or more assistants, etc
	* Pick one or more transfers (also known as Stock Picking in Odoo terms)
	* Hit Confirm button to schedule the trip
3. Starting a trip
	* Navigate to the menu Fleet Operations > Operations > Trips Confirmed
	* Find the trip you want to start and open it in form view
	* Hit the Start button to open Trip Starting Wizard on which you can update the following information:
		* Driver (if you want to change the driver)
		* Assistants (if you want to add/change the assistants)
		* Odometer
		* Start time
		* Vehicle (if you want to change the vehicle)
4. Adding on-trip information
	* Register a vehicle cost
		* Navigate to the menu Fleet Operations > Operations > Trips in Operation to find the trip that you want to register a vehicle cost
		* Open the trip in form view
		* Hit the button Register Cost to open Trip Cost Registration Wizard, on which you can entry the following:
			* Date: the date on which the cost was raised
			* Amount: the cost/expense amount
			* Cost Type: the type of the cost
			* Trip Waypoint: the waypoint of the route at which the cost was raised
			* Trip Section: the route section of the trip in which the cost was raised
5. Ending an In-Operation Trip
	* Navigate to the menu Fleet Operations > Operations > Trips in Operation to find the trip that you want to end
	* Open the trip in form view
	* Hit the button Done to open Trip Ending Wizard, on which you can entry the following:
		* End Time: the time at which the trip was actually end.
		* Odometer: the value of the odometer at the end of the trip
		* Fuel Consumption: the actual fuel consumption of the trip.
6. Adding costs to trip can be done for trips that are neither in Draft nor Cancelled state
7. Accessing the drivers and trip assistants data from Salary Rules:
	* The following fields are availble in the model 'hr.employee'
		* driver_done_trip_ids: This stores all the trips that have been completed by the employee as the roll of driver
		* assitant_done_trip_ids: This stores all the trips that have been completed by the employee as the roll of trip assistant
	* Sample salary rules:
		* compute salary for a driver based on number of trips he completed during the payslip period (assumed that wage/trip is 100.0): `result = len(employee.driver_done_trip_ids.filtered(lambda t: t.end_date >= payslip.date_from and t.end_date <= payslip.date_to)) * 100.0`
		* compute salary for a driver based on number of transfers he delivered/picked during the payslip period (assumed that wage/transfer is 10.0): `result = len(employee.driver_done_trip_ids.filtered(lambda t: t.end_date >= payslip.date_from and t.end_date <= payslip.date_to).mapped('stock_picking_ids')) * 100.0`
		* compute salary for a trip assistant based total weight of the transfers he complated during the payslip period (assume that wage per picked/delivered kilogram is 1.2): `result = sum(employee.assitant_done_trip_ids.filtered(lambda t: t.end_date >= payslip.date_from and t.end_date <= payslip.date_to).mapped('stock_picking_ids.total_weight')) * 1.2`
8. Reports and Analysis
	* Fleet Trips Analysis: navigate to the menu: Fleet Operations > Reports > Fleet Trips Analysis.
	* Cost Analysis: navigate to the menu: Fleet Operations > Reports > Cost Analysis.
	* Stock Moves:
		* filtered by Vehicle, Trip, Vehicle Services, Drivers
		* group by vehicle, trip, driver
	* Trip Reports: You can print Trip Reports from trip's list view and form view. A Trip Report includes consolidated information about the trip: start, stop, waypoints, pickings, delivery orders, etc
