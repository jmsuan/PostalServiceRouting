from datetime import datetime
from datetime import timedelta

from driver import Driver
from hash_table import HashTable
from location import Location
from package import Package
from truck import Truck


class Scheduler:
    """
    TODO: Apply Dijkstra's algorithm when we have to skip locations in a route.
    """
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
        all_packages_delivered = all(package.get_status() == "DELIVERED" for package in cls.package_table.all_values())
        all_trucks_at_hub = all(truck.is_at_hub() for truck in cls.trucks)
        if all_packages_delivered and all_trucks_at_hub:
            return False  # All packages are delivered and all trucks are back at the hub

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

                # Check if the package can be loaded onto the truck
                if cls.__check_package_for_loading(package, highest_score_truck, highest_score_route):
                    # All checks passed. We can now load the truck.
                    # TODO: Account for BATCH requirements
                    highest_score_truck.load(package)
                    package.update_status(f"EN ROUTE - TRUCK {highest_score_truck.get_id()}")
                    print(f"Package {package.get_package_id()} loaded onto Truck {highest_score_truck.get_id()}.")

            # Remove the chosen truck and driver from hub
            trucks_at_hub.remove(highest_score_truck)
            drivers_at_hub.remove(first_available_driver)

        print(f"The current time is {cls.get_current_time()}")

        return False

        # Progress the current time by one minute
        # cls.current_time += timedelta(minutes=1)

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
    def __optimize_route(cls, packages_to_deliver: list[Package], route_to_optimize: list[Location]) -> list[Location]:
        """
        Optimizes the route that the truck will take to deliver the packages in the most efficient manner. The route
        will be optimized to minimize the distance traveled by the truck. The route will be optimized using Dijkstra's
        algorithm, which will only be used if the truck has to skip a location.

        :param packages_to_deliver: The list of packages that the truck will deliver.
        :param route_to_optimize: The route that the truck will take to deliver the packages.
        :return: The optimized route that the truck can take to deliver the packages.
        """
        pass
