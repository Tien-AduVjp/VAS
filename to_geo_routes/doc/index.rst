Installation
============

1. Navigate to Apps
2. Find with keyword 'to_geo_routes'
3. Install it as usual then you are done

Concepts
========

1. Route Section: is a section defined by two addresses where each **Address** (aka From and To) is an Odoo partner record. This design model to ensure short learning curve and easy to extend and fully integrated with existing features in Odoo
2. Waypoint: also known as "Route Waypoint", is a model that presents an instance of an Address which creates a data link between a Route and an Address in Odoo
3. Section Line: also known as "Route Section", is a model that presents an instance of a Section which creates a data link between a Route and an Route Section in Odoo
4. Route: is a model to present a route that defined by Waypoints and Sections. Then Odoo will automatically find and link the related Sections and Addresses for the Route


Instructions
============

1. Without other modules that extending this module, you are required to be an administrator in Odoo to access the module's menu: Settings > Geo-Routes. If you have other modules that developed on top of this, there should be other ways to access the features. For example, if you have the module "Fleet Operation & Planning" installed, you may access the features through "Fleet Operation > Routes & Waypoints" which does not required administrator access rights. In this document, it is assumed that you have administration access rights.
2. Define a new Route:
	* Navigate to "Settings > Geo-Routes > Routes" to see the routes list view
	* Hit Create button to open the route form view, on which you can input:
		* The name of the route. For example: `Hanoi to Ha Long Bay via Hai Phong City`
		* In the Waypoint table, you can start adding waypoints for your route
