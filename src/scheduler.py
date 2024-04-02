from datetime import datetime
from datetime import timedelta

from driver import Driver
from hash_table import HashTable
from location import Location
from package import Package
from truck import Truck
from route_list import RouteList


class Scheduler:
    """
    TODO: Apply Dijkstra's algorithm when we have to skip locations in a route.
    """
    initialized_time: datetime = None
    current_time: datetime = None
    delivery_start_time: datetime = None
    package_table: HashTable = None
    prioritized_pkgs: list[tuple[Package, int]] = None
    route_list: list[list[Location]] = None
    trucks: list[Truck] = None
    drivers: list[Driver] = None
    hub: Location = None

    @classmethod
    def initialize(
            cls,
            init_time: str,
            begin_delivery_time: str,
            routes_to_follow: list[list[Location]],
            package_table: HashTable,
            package_priorities: list[int],
            truck_list: list[Truck],
            driver_list: list[Driver],
            hub_location: Location
    ):
        """
        Initializes the Scheduler with the necessary information to begin scheduling. Sets the packages to their initial
        statuses.

        :param init_time: The time at which the Scheduler should begin with. The time should be in the format
            "HH:MM AM/PM".
        :param begin_delivery_time: The time at which the Scheduler should begin delivering packages. The time should be
            in the format "HH:MM AM/PM".
        :param routes_to_follow: The list of routes that the Scheduler should follow.
        :param package_table: The list of packages that the Scheduler should schedule.
        :param package_priorities: The list of priorities for each package in the package_list.
        :param truck_list: The list of trucks available for the Scheduler to use.
        :param driver_list: The list of drivers that are available to drive the trucks.
        :param hub_location: The location that serves as the hub that the Trucks return to.
        """
        # Sort packages based on priority and store
        package_list = package_table.all_values()
        cls.prioritized_pkgs = sorted(zip(package_list, package_priorities), key=lambda x: x[1], reverse=True)

        # Initialize the Scheduler's attributes
        cls.current_time = datetime.strptime(init_time, "%I:%M %p")
        cls.initialized_time = cls.current_time
        cls.delivery_start_time = datetime.strptime(begin_delivery_time, "%I:%M %p")
        cls.route_list = routes_to_follow.copy()
        cls.package_table = package_table
        cls.trucks = truck_list
        cls.drivers = driver_list
        cls.hub = hub_location

        # Set the initial status of each package
        for package in cls.package_table.all_values():
            # Check if the special codes has "DELAY"
            if any("DELAY[" in code for code in package.get_special_code()):
                for code in package.get_special_code():
                    if "DELAY[" in code:
                        time_str = code.replace("DELAY[", "").replace("]", "")
                        time = datetime.strptime(time_str, "%H:%M:%S")
                        package.update_status(f"DELAYED UNTIL {time.strftime('%I:%M %p')}")
                        break
            else:
                package.update_status("IN HUB")

    @classmethod
    def reset_day(cls):
        """
        Resets the packages to its initial state.
        """
        # Set the initial status of each package
        for package in cls.package_table.all_values():
            # Check if the special code has "DELAY"
            if any("DELAY[" in code for code in package.get_special_code()):
                for code in package.get_special_code():
                    if "DELAY[" in code:
                        time_str = code.replace("DELAY[", "").replace("]", "")
                        time = datetime.strptime(time_str, "%H:%M:%S")
                        package.update_status(f"DELAYED UNTIL {time.strftime('%I:%M %p')}")
                        break
            else:
                package.update_status("IN HUB")

        # Reset the trucks
        for truck in cls.trucks:
            truck.reset_packages()
            truck.reset_driver()
            truck.reset_route()
            truck.set_distance_to_next(0.0)
            truck.reset_odometer()
            truck.set_last_location(cls.hub)

        # Reset the current time to the initialized time
        cls.current_time = cls.initialized_time

    @classmethod
    def tick(cls) -> bool:
        """
        Advances the Scheduler's current time by one minute after doing everything that needs to be done in the current
        minute. The Scheduler will check the current status of all packages and trucks to determine if any actions need
        to be taken. If a package is ready to be delivered, the Scheduler will assign a Truck and Driver to deliver the
        package. If a Truck has returned to the hub, the Scheduler will load the Truck and assign the Truck and Driver
        to a new route.

        Here, we need to check and do the following (updating package statuses throughout):
            1. Check if it's before the delivery_start_time. If it is, skip all scheduling and advance the time to the
                next minute.
            2. Check if all the packages are delivered and all the trucks are back at the hub. If they are, return
                False.
            3. Determine how many packages are in the hub that need to be delivered on particular a truck.
                - Assign a score to each truck based on the number of packages that must be on that truck
            4. Check if there is a driver and truck at the hub to load and deploy en route.
                - If there is, assign the driver to the highest-score truck, and start loading packages to the truck:
                    a. Look through available routes, and add-up a score based on the priorities of each package to be
                        delivered on the route, if the package is in the hub.
                    b. From a list of packages that are available to be delivered to the highest-score route, load the
                        packages to the truck in the order of priority.
                    c. Optimize the route that the truck will take to deliver the packages in the most efficient manner
                        using Dijkstra's algorithm.
                    d. Assign the truck to the route and the driver to the truck.
            5. Progress trucks towards their destination based on their speed if they are en route.
            6. If a truck has reached its destination:
                - Deliver the package(s) if it has a package for the Location, update their statuses.
                - Set the next destination for the truck from the route. Remove the previous location from the route.
                - If the destination it reached was the hub, unload the truck and remove the driver.
            7. Progress the current time by one minute.

        :return: True if the Scheduler has more work to do, False if all packages are delivered and all trucks are back
            at the hub.
        """
        # Check if it's before the delivery_start_time
        if cls.current_time < cls.delivery_start_time:
            cls.current_time += timedelta(minutes=1)
            return True  # It's before the delivery start time, loop again

        # Check if all the packages are delivered and all the trucks are back at the hub
        acceptable_statuses = ["DELIVERED", "ATTEMPTED"]
        all_packages_delivered = (
            all(Package.get_status(package).split(" ")[0].strip() in acceptable_statuses
                for package in cls.package_table.all_values()))
        # Check if all trucks are at the hub (not necessary to check due to the requirements of the project)
        # all_trucks_at_hub = all(truck.is_at_hub() for truck in cls.trucks)
        if all_packages_delivered:  # Could check if all_trucks_at_hub here
            return False  # The day is over

        # Progress trucks towards their destination based on their speed if they are en route
        for truck in cls.trucks:
            if truck.is_en_route():
                if truck.drive():
                    # Truck has reached its destination, last location is the location it arrived at.
                    truck.attempt_delivery(truck.get_last_location(), cls.get_current_time())
                    if truck.get_last_location() == cls.hub and not truck.get_route():
                        # Truck has returned to the hub with no more locations to visit
                        truck.reset_route()
                        truck.reset_driver()
                        truck.reset_packages()

        # Determine how many packages are in the hub that need to be delivered on particular a truck. Give a score to
        # each truck based on the number of packages that must be on that truck
        truck_scores = {truck.get_id(): 0 for truck in cls.trucks}
        for package in cls.package_table.all_values():
            if any("TRUCK[" in code for code in package.get_special_code()):
                for code in package.get_special_code():
                    if "TRUCK[" in code:
                        truck_list_str = code.replace("TRUCK[", "").replace("]", "")
                        truck_ids = [int(id_num.strip()) for id_num in truck_list_str.split(",")]
                        for truck_id in truck_ids:
                            if package.get_status() == "IN HUB":
                                truck_scores[truck_id] += 1

        # Check if there is a driver and truck at the hub to load and deploy en route
        trucks_at_hub = [truck for truck in cls.trucks if truck.is_at_hub()]
        # A driver that isn't driving a truck should always be at the hub
        drivers_at_hub = \
            [driver for driver in cls.drivers if driver not in [truck.get_driver() for truck in cls.trucks]]

        # Load and deploy trucks en route
        while trucks_at_hub and drivers_at_hub:
            # Find the highest-score truck that is at the hub
            trucks_at_hub_scores = {truck_id: score for truck_id, score in truck_scores.items() if truck_id in
                                    [truck.get_id() for truck in trucks_at_hub]}
            highest_score_truck_id = max(trucks_at_hub_scores, key=trucks_at_hub_scores.get)
            highest_score_truck = next(truck for truck in cls.trucks if truck.get_id() == highest_score_truck_id)

            # Assign the first available driver to the highest score truck
            first_available_driver = next(driver for driver in drivers_at_hub if driver not in
                                          [truck.get_driver() for truck in cls.trucks])
            highest_score_truck.set_driver(first_available_driver)

            # Assign a score for each route the truck could take (using package priority)
            route_scores = []
            for route in cls.route_list:
                score = 0
                for package, priority in cls.prioritized_pkgs:
                    if package.get_status() == "IN HUB" and package.get_destination() in route:
                        score += priority
                route_scores.append(score)
            highest_score_route, _ = sorted(
                zip(cls.route_list.copy(), route_scores), key=lambda x: x[1], reverse=True)[0]

            # Load packages onto the truck if the package can be loaded onto this particular truck.
            for package, _ in cls.prioritized_pkgs:
                # Check is truck is at capacity
                if len(highest_score_truck.get_packages()) >= highest_score_truck.get_capacity():
                    break

                # Load batched packages first (batched packages have a high priority)
                if any("BATCH[" in code for code in package.get_special_code()):
                    # Include the package itself
                    if cls.__check_package_for_loading(package, highest_score_truck,
                                                       [location for route in cls.route_list for location in route]):
                        highest_score_truck.load(package)
                    # Load the rest of the batched packages
                    for code in package.get_special_code():
                        if "BATCH[" in code:
                            pkg_list_str = code.replace("BATCH[", "").replace("]", "")
                            pkg_ids = [int(id_num.strip()) for id_num in pkg_list_str.split(",")]
                            for pkg_id in pkg_ids:
                                pkg = cls.package_table.lookup_package(pkg_id)
                                # Check if the package can be loaded onto the truck, regardless of the route
                                if cls.__check_package_for_loading(pkg, highest_score_truck,
                                                                   [location for route in cls.route_list
                                                                    for location in route]):
                                    highest_score_truck.load(pkg)

                # Load package if priority is very high regardless of the route
                for pkg, priority in cls.prioritized_pkgs:
                    if (priority > 1000000
                            and cls.__check_package_for_loading(pkg, highest_score_truck,
                                                                [location for route in cls.route_list
                                                                 for location in route])):
                        highest_score_truck.load(pkg)

                # Check if the package can be loaded onto the truck
                if cls.__check_package_for_loading(package, highest_score_truck, highest_score_route):
                    highest_score_truck.load(package)

            # If truck still has space, load the rest of the packages
            for package, _ in cls.prioritized_pkgs:
                if len(highest_score_truck.get_packages()) >= highest_score_truck.get_capacity():
                    break
                if package not in highest_score_truck.get_packages() and package.get_status() == "IN HUB":
                    if any("INVALID" in code for code in package.get_special_code()):
                        continue
                    highest_score_truck.load(package)

            # Optimize the route that the truck will take to deliver the packages in the most efficient manner
            optimized_route = cls.__optimize_route(highest_score_truck.get_packages(), highest_score_route)
            for location in optimized_route:
                if not highest_score_truck.get_route() and location == cls.hub:
                    continue  # Skip the hub if it's the first location
                highest_score_truck.add_to_route(location)

            # Remove the chosen truck and driver from hub
            trucks_at_hub.remove(highest_score_truck)
            drivers_at_hub.remove(first_available_driver)

        # Check for delayed packages and update their statuses if necessary
        for package, _ in cls.prioritized_pkgs:
            if any("DELAY[" in code for code in package.get_special_code()) and "DELAY" in package.get_status():
                for code in package.get_special_code():
                    if "DELAY[" in code:
                        time_str = code.replace("DELAY[", "").replace("]", "")
                        time = datetime.strptime(time_str, "%H:%M:%S")
                        if cls.current_time >= time:
                            package.update_status("IN HUB")

        # Progress the current time by one minute
        cls.current_time += timedelta(minutes=1)
        return True

    @classmethod
    def get_current_time(cls) -> str:
        """
        :return: The current time of the Scheduler.
        """
        return cls.current_time.strftime("%I:%M %p")

    @classmethod
    def __check_package_for_loading(cls, package: Package, truck: Truck, route: list[Location]) -> bool:
        """
        Checks if a package can be loaded onto a truck based on if the package is on another truck, the package's
        special codes, the package's destination, and the route that the truck will take.

        :param package: The package to check.
        :param truck: The truck to check.
        :param route: The route that the truck will take.
        :return: True if the package can be loaded onto the truck, False otherwise.
        """
        # Check if package has to be on another truck
        truck_ids_special_code = []
        if any("TRUCK[" in code for code in package.get_special_code()):
            for code in package.get_special_code():
                if "TRUCK[" in code:
                    truck_list_str = code.replace("TRUCK[", "").replace("]", "")
                    truck_ids_special_code = [int(id_num.strip()) for id_num in truck_list_str.split(",")]
        pkg_allowed_on_truck = (
                truck.get_id() in truck_ids_special_code or not truck_ids_special_code)
        if not pkg_allowed_on_truck:
            return False

        # Check if the package is not on the highest-score route
        if package.get_destination() not in route:
            return False

        # Check if the package is on any other trucks
        if any(package in truck.get_packages() for truck in cls.trucks):
            return False

        # Check if the package is not in the hub
        if package.get_status() != "IN HUB":
            return False

        # Check if the package is invalid
        if any("INVALID" in code for code in package.get_special_code()):
            return False

        return True

    @classmethod
    def __optimize_route(
            cls,
            packages_to_deliver: list[Package],
            route_to_optimize: list[Location]
    ) -> list[Location]:
        """
        Optimizes the route that the truck will take to deliver the packages in the most efficient manner. The route
        will be optimized to minimize the distance traveled by the truck. The route will be optimized using Dijkstra's
        algorithm, which will only be used if the truck has to skip a location. The optimization will also account for
        any locations that aren't in the route that the truck will take. (This is to allow for batch deliveries.)

        :param packages_to_deliver: The list of packages that the truck will deliver.
        :param route_to_optimize: The route that the truck will take to deliver the packages.
        :return: The optimized route that the truck can take to deliver the packages.
        """
        route_copy = route_to_optimize.copy()
        package_locations = [package.get_destination() for package in packages_to_deliver]
        package_priorities = {package: priority for package, priority in cls.prioritized_pkgs
                              if package in packages_to_deliver}
        location_priorities = {package.get_destination(): package_priorities.get(package)
                               for package in packages_to_deliver}

        # Add all locations that aren't in the route to the route
        for location in package_locations:
            if location not in route_copy:
                # Find best place in the route to insert the location
                best_index = 0
                best_distance = float("inf")
                for i in range(1, len(route_copy)):  # Skip the first and last location (hub)
                    temp_route = route_copy.copy()
                    temp_route.insert(i, location)
                    distance = RouteList.get_route_distance(temp_route)
                    if distance < best_distance:
                        best_index = i
                        best_distance = distance
                route_copy.insert(best_index, location)

        # Remove locations that don't need to be visited
        for location in route_copy.copy():
            if location not in package_locations and location != cls.hub:
                route_copy.remove(location)

        # Check if the route should be reversed based on package priorities
        if len(route_copy) > 2:
            dont_reverse_score = 0
            reverse_score = 0
            for i in range(1, len(route_copy) - 1):
                # We are going through the route in regular order, weight priority by index (earlier is better)
                dont_reverse_score += location_priorities.get(route_copy[i], 0) * (len(route_copy) - i)
            for i in range(len(route_copy) - 1, 1, -1):
                # We are going through the route in reverse order, weight priority by index (earlier is better)
                reverse_score += location_priorities.get(route_copy[i], 0) * (len(route_copy) - i)
            if reverse_score > dont_reverse_score:
                route_copy = route_copy[::-1]

        # Implement Dijkstra's algorithm to optimize the route ONLY if the truck has to skip a location on the route.
        # TODO: Remove any unvisited locations from the route (only if we implement Dijkstra's algorithm)

        # TODO: Implement Dijkstra's algorithm here

        return route_copy

    @staticmethod
    def validate_time(time_str):
        """
        Validates the time string to ensure that it is in the correct format. Returns the time if it is in the correct
        format, otherwise returns False.
        """
        try:
            time_entered = datetime.strptime(time_str, "%I:%M %p")
            return time_entered
        except ValueError:
            return False
