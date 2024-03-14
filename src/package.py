import datetime
from location import Location


class Package:

    def __init__(
            self,
            package_id: int,
            address: str,
            city: str,
            state: str,
            zip_code: str,
            deadline: datetime,
            weight: float,
            special_code: list[str] = None,
            status: str = "IN HUB"
    ):
        """
        Creates a new package.

        :param package_id: (int) The unique identifier of the package.
        :param address: (str) The delivery address of the package.
        :param city: (str) The city associated with the delivery address.
        :param state: (str) The state associated with the delivery address.
        :param zip_code: (str) The zip code associated with the delivery address.
        :param deadline: (datetime) The delivery deadline for the package.
        :param weight: (float) The weight of the package in kilograms.
        :param special_code: (list[str], optional) A tuple of special delivery requirements or conditions,
            potentially containing multiple codes.
            Available codes:
                - TRUCK[{list of truck IDs}]: specifies required truck numbers.
                - INVALID: Indicates invalid package information (must remain in location until package is updated).
                - BUNDLE[{list of package IDs}]: Specifies joint delivery with other packages.
                - DELAY[{datetime}]: Specifies a delayed arrival time for the package.
        :param status: (str, optional) The current status of the package. Defaults to "IN HUB".
        """
        self._package_id = package_id
        self._destination = Location.get_location(address, zip_code)
        self.__null = None  # This is a quick fix to the object __len__ method. _destination accounts for two values.
        self._city = city
        self._state = state
        self._deadline = deadline
        self._weight = weight
        self._special_code = special_code
        self._status = status

    def get_package_id(self) -> int:
        return self._package_id

    def get_destination(self) -> Location:
        return self._destination

    def get_address(self) -> str:
        return self._destination.get_address()

    def get_deadline(self) -> datetime:
        return self._deadline

    def get_city(self) -> str:
        return self._city

    def get_state(self) -> str:
        return self._state

    def get_zip(self) -> str:
        return self._destination.get_zip()

    def get_weight(self) -> float:
        return self._weight

    def get_special_code(self) -> list[str]:
        return self._special_code

    def get_status(self) -> str:
        return self._status

    def __str__(self):
        """Returns a string representation of the Package."""
        return (
            f"[{self._package_id}, "
            f"{self._destination.get_address()}, "
            f"{self.get_city()}, "
            f"{self.get_state()}, "
            f"{self._destination.get_zip()}, "
            f"{self._deadline.strftime("%I:%M %p")}, "  # Format deadline for readability
            f"{self._weight} kg, "
            f"{self._special_code}, "
            f"{self._status}]"
        )

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        """Returns the number of attributes the Package object has."""
        return len([attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")])

    def __getitem__(self, key: int):
        match key:
            case 0:
                return self.get_package_id()
            case 1:
                return self.get_address()
            case 2:
                return self.get_city()
            case 3:
                return self.get_state()
            case 4:
                return self.get_zip()
            case 5:
                if self._deadline.strftime("%I:%M:%S %p") == "11:59:59 PM":
                    return "EOD"
                else:
                    return self._deadline.strftime("%I:%M %p")
            case 6:
                return f"{self._weight} kg"
            case 7:
                return self.get_special_code()
            case 8:
                return self.get_status()
            case _:
                return
