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
        self._avg_speed = avg_speed  # Miles per hour
        self._driver = driver
        self._packages = []
        self._mileage = 0.0
        self._last_location = Interface.get_hub()
        self._route = []

    def load(self, package: Package):
        self._packages.append(package)

    def add_miles(self, miles: float):
        self._mileage += miles

    def reset_odometer(self):
        self._mileage = 0.0

    def set_driver(self, new_driver: Driver):
        self._driver = new_driver

    def add_to_route(self, destination: Location):
        self._route.append(destination)

    def reset_route(self):
        self._route = []

    def is_at_hub(self) -> bool:
        if self._last_location == Interface.get_hub() and not self._route:
            return True
        return False

    def get_id(self) -> int:
        return self._id
