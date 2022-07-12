Installation
============

1. Navigate to Apps
2. Find with keyword 'to_fleet_operation_planning'
3. Install it as usual then you are done

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
7. Vehicle Trip: is an Odoo document to help plan and track trips of your vehicles.

Usages
------
1. Prepare Master Data
	* Create / Update your vehicles (navigating to the menu Fleet > Vehicles)
		* On the vehicle form view, you may want to input the Warning Volume, Max. Volume, Warning Weight Load, Max. Weight Load
	* Create / Update your drivers (navigating to the menu Fleet > Drivers > Drivers).
		* You may also want to update the drivers licenses (Fleet > Drivers > Licenses).
	* Create / Update your Geo-Routes data (Fleet Operations > Routes & Waypoints)
2. Plan your first trip
	* Navigate to Fleet Operations to see a calendar view of your trips
	* Click on a cell of your desired trip time to open vehicle trip form view
	* Assign a vehicle, a driver, a route, one or more assistants, etc
	* Hit Confirm button to confirm the trip schedule
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
