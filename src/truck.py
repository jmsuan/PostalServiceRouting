from driver import Driver
from package import Package
from location import Location
from interface import Interface


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
        self._packages = []
        self._mileage = 0.0
        self._last_location = Interface.get_hub()
        self._route = []
        self._distance_to_next = 0.0

    def load(self, package: Package):
        self._packages.append(package)
        package.update_status(f"EN ROUTE - TRUCK {self.get_id()}")

    def deliver(self, package: Package):
        self._packages.remove(package)
        package.update_status("DELIVERED")
        print(f"Package {package.get_package_id()} delivered from Truck {self.get_id()}.")

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
        self._route.append(destination)

    def reset_route(self):
        self._route = []
        self._last_location = Interface.get_hub()

    def reset_packages(self):
        self._packages = []

    def is_at_hub(self) -> bool:
        if self._last_location == Interface.get_hub() and not self._route:
            return True
        return False

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
