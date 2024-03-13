from driver import Driver
from package import Package


class Truck:
    def __init__(self, truck_id: int, avg_speed: float = 18.0, driver: Driver = None):
        """
        Creates a truck that can hold Packages and be driven by a Driver.

        :param truck_id: The unique identifier of the Truck.
        :param avg_speed: The average speed of the Truck throughout the day. (Default: 18.0 miles per hour)
        :param driver: The Driver that is assigned to deliver Packages using this Truck. (Default: None)
        """
        self._id = truck_id
        self._avg_speed = avg_speed  # Miles per hour
        self._driver = driver
        self._packages = []
        self._mileage = 0.0

    def load(self, package: Package):
        self._packages.append(package)

    def add_miles(self, miles: float):
        self._mileage += miles

    def reset_odometer(self):
        self._mileage = 0.0

    def set_driver(self, new_driver: Driver):
        self._driver = new_driver
