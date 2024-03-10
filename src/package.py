import datetime


class Package:

    def __init__(
            self,
            package_id: int,
            address: str,
            deadline: datetime,
            city: str,
            zip_code: str,
            weight: float,
            special_code: tuple[str, ...] = None,
            status: str = "IN HUB"
    ):
        """
        Creates a new package.

        Args:
            package_id (int): The unique identifier of the package.
            address (str): The delivery address of the package.
            deadline (datetime): The delivery deadline for the package.
            city (str): The city associated with the delivery address.
            zip_code (str): The zip code associated with the delivery address.
            weight (float): The weight of the package in kilograms.
            special_code (tuple[str, ...], optional): A tuple of special delivery
                requirements or conditions, potentially containing multiple codes.
                Available codes:
                    - TRUCK[{list of truck IDs}]: specifies required truck numbers.
                    - INVALID: Indicates invalid package information (must remain "IN HUB" until package is updated).
                    - BUNDLE[{list of package IDs}]: Specifies joint delivery with other packages.
                    - DELAY[{datetime}]: Specifies a delayed arrival time for the package.
            status (str, optional): The current status of the package. Defaults to "IN HUB".
        """
        self._package_id = package_id
        self._address = address
        self._deadline = deadline
        self._city = city
        self._zip_code = zip_code
        self._weight = weight
        self._special_code = special_code
        self._status = status

    def get_package_id(self) -> int:
        return self._package_id

    def get_address(self) -> str:
        return self._address

    def get_deadline(self) -> datetime:
        return self._deadline

    def get_city(self) -> str:
        return self._city

    def get_zip_code(self) -> str:
        return self._zip_code

    def get_weight(self) -> float:
        return self._weight

    def get_special_code(self) -> tuple[str, ...]:
        return self._special_code

    def get_status(self) -> str:
        return self._status

    def __str__(self):
        """Returns a string representation of the package."""
        return (
            f"[{self._package_id}, "
            f"{self._address}, "
            f"{self._deadline.strftime('%H:%M')}, "  # Format deadline for readability
            f"{self._city}, "
            f"{self._zip_code}, "
            f"{self._weight} kg, "
            f"{self._special_code}, "
            f"{self._status}]"
        )

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        """Returns the number of attributes the package object has."""
        return len([attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")])

    def __getitem__(self, key: int):
        match key:
            case 0:
                return self._package_id
            case 1:
                return self._address
            case 2:
                return self._deadline.strftime('%H:%M')
            case 3:
                return self._city
            case 4:
                return self._zip_code
            case 5:
                return self._weight
            case 6:
                return self._special_code
            case 7:
                return self._status
            case _:
                return
