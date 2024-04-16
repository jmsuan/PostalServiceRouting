from driver import Driver
from package import Package
from location import Location
from interface import Interface
from datetime import datetime
from datetime import timedelta
from route_list import RouteList


class Truck:
    def __init__(self, truck_id: int, capacity: int = 16, avg_speed: float = 18.0, driver: Driver = None):
        """
        Creates a truck that can hold Packages and be driven by a Driver.

        :param truck_id: The unique identifier of the Truck.
        :param capacity: The maximum number of Packages that the Truck can contain. (Default: 16)
        :param avg_speed: The average speed of the Truck throughout the day. (Default: 18.0 miles per hour)
        :param driver: The Driver that is assigned to deliver Packages using this Truck. (Default: None)
        """
        self._id = truck_id
        self._capacity = capacity
        self._avg_speed = avg_speed  # Miles per hour
        self._driver = driver
        self._packages: list[Package] = []
        self._mileage = 0.0
        self._last_location = Interface.get_hub()
        self._route = []
        self._distance_to_next = 0.0

    def load(self, package: Package):
        if len(self._packages) >= self._capacity:
            return  # Truck is full
        self._packages.append(package)
        package.update_status(f"EN ROUTE - TRUCK {self.get_id()}")

    def drive(self) -> bool:
        """
        Drives the Truck for one minute to the next Location in the route, updating the mileage and distance to the next
        Location. Returns True if the Truck has reached a destination, False otherwise.
        """
        if not self._route:
            # Truck has no route to follow
            return False

        travel_distance = self._avg_speed / 60.0  # miles per minute
        if self.distance_to_next() < travel_distance:
            travel_distance = self.distance_to_next()
            extra_distance = travel_distance - self.distance_to_next()  # delivery/stops assumed to be instantaneous
            self._last_location = self._route[0]
            self._route.pop(0)
            if not self._route:
                self.set_distance_to_next(0.0)
            else:
                self.set_distance_to_next(self._last_location.distance_from(self._route[0]) - extra_distance)
            return True  # Truck has reached a destination

        # Truck has not reached a destination
        self.add_miles(travel_distance)
        self.set_distance_to_next(self.distance_to_next() - travel_distance)
        return False

    def attempt_delivery(self, location: Location, time_str: str) -> bool:
        """
        Attempts to deliver a Package to a Location. If the Truck is at the Location, the Package is delivered and the
        status is updated and True is returned. If the Truck is not at the Location, returns False.
        """
        package_delivered = False
        for package in self._packages:
            if package.get_destination() == location:
                self._packages.remove(package)
                package.update_status(f"DELIVERED at {time_str}")
                print(f"Package {package.get_package_id()} delivered from Truck {self.get_id()}.")
                package_delivered = True
        if package_delivered:
            return True
        return False

    def set_distance_to_next(self, distance: float):
        self._distance_to_next = distance

    def distance_to_next(self) -> float:
        return self._distance_to_next

    def add_miles(self, miles: float):
        self._mileage += miles

    def reset_odometer(self):
        self._mileage = 0.0

    def set_driver(self, new_driver: Driver):
        self._driver = new_driver

    def reset_driver(self):
        self._driver = None

    def add_to_route(self, destination: Location):
        # If the Truck is at the hub, set the distance to the next location
        if not self._route and self.is_at_hub():
            self.set_distance_to_next(self._last_location.distance_from(destination))
        self._route.append(destination)

    def reset_route(self):
        self._route = []
        self._last_location = Interface.get_hub()

    def reset_packages(self):
        for package in self._packages:
            package.update_status("IN HUB")
        self._packages = []

    def is_at_hub(self) -> bool:
        if self._last_location == Interface.get_hub() and not self._route:
            return True
        return False

    def get_eta(self, now: datetime) -> datetime | None:
        """
        :return: The estimated time that the Truck will finish its route, or None if the Truck has no route.
        """
        if not self._route:
            return None
        route = [self._last_location] + self._route
        route_distance = RouteList.get_route_distance(route)
        hours = route_distance / self._avg_speed
        minutes = (hours - int(hours)) * 60
        eta = now + timedelta(hours=int(hours), minutes=int(minutes))
        return eta

    def get_id(self) -> int:
        return self._id

    def get_driver(self) -> Driver:
        return self._driver

    def get_capacity(self) -> int:
        return self._capacity

    def get_avg_speed(self) -> float:
        return self._avg_speed

    def get_packages(self) -> list[Package]:
        return self._packages

    def get_mileage(self) -> float:
        return self._mileage

    def get_last_location(self) -> Location:
        return self._last_location

    def get_route(self) -> list[Location]:
        return self._route

    def is_en_route(self) -> bool:
        if self._route:
            return True
        return False

    def set_last_location(self, location: Location):
        self._last_location = location

