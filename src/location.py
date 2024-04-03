from __future__ import annotations


class Location:
    # Stores all Location objects that are created
    _all_locations = []

    def __init__(self, name: str, street_address: str, zip_code: str):
        """Instantiates a location that can store driving distances from other locations."""
        # Contain all adjustments that need to be made to address strings in a function.

        # Initialize the attributes and add self to the class list
        self._name = name.strip().title()
        self._address = Location.format_address(street_address)
        self._zip = zip_code.strip()
        self._distance_table = {}
        Location._all_locations.append(self)

    @staticmethod
    def format_address(address: str) -> str:
        """Make all necessary adjustments to an address string as needed for consistency."""
        address_to_adjust = address
        address_to_adjust = address_to_adjust.replace(" Sta ", " Station ")
        address_to_adjust = address_to_adjust.replace(" N ", " North ")
        address_to_adjust = address_to_adjust.replace(" E ", " East ")
        address_to_adjust = address_to_adjust.replace(" W ", " West ")
        address_to_adjust = address_to_adjust.replace(" S ", " South ")

        # Handle when the address ends with the cardinal direction
        match address_to_adjust[-2:].lower():
            case " n":
                address_to_adjust = address_to_adjust[:-2] + " North"
            case " e":
                address_to_adjust = address_to_adjust[:-2] + " East"
            case " w":
                address_to_adjust = address_to_adjust[:-2] + " West"
            case " s":
                address_to_adjust = address_to_adjust[:-2] + " South"

        # We could add support for converting NW/NE/SW etc., but that's beyond the scope of this project.

        return address_to_adjust.strip().title()

    def add_distance(self, location: Location, miles_to_drive: float):
        self._distance_table[location] = miles_to_drive
        location._distance_table[self] = miles_to_drive  # Distance assumed to be same both ways

    def distance_from(self, location: Location) -> float:
        """
        :param location: Another location that's distant from the current one.
        :return: The distance in miles between the two Locations.
        """
        return self._distance_table.get(location)

    def neighbors(self) -> dict[Location, float]:
        """
        :return: A dictionary of all neighboring Locations and their distances from the current Location.
        """
        return self._distance_table

    def get_address(self) -> str:
        return self._address

    def get_zip(self) -> str:
        return self._zip

    def get_name(self) -> str:
        return self._name

    def __str__(self):
        return (f"[{self.get_name()}, "
                f"{self.get_address()}, "
                f"({self.get_zip()})]")

    def __repr__(self):
        return self.__str__()

    def __lt__(self, other):
        return self._name < other.get_name()

    @staticmethod
    def get_location_by_address(street_address: str, zip_code: str) -> Location:
        # Initialize search variables
        street_address = Location.format_address(street_address)
        locations_found = 0
        found_location = None

        # Search all stored locations (every location that's instantiated should be stored)
        for location in Location._all_locations:

            # Check address first, if it's not a match, check the next stored location
            if location.get_address() != street_address.strip().title():
                continue  # Street address doesn't match. Check next stored Location.
            if location.get_zip() != zip_code.strip():
                continue  # Address matches but not zip.

            # This Location fully matches a stored one
            if locations_found < 1:
                locations_found += 1
                found_location = location
            else:
                raise ValueError(f"Multiple conflicting locations with same info. Make sure the "
                                 f"Location is only added once.\n"
                                 f"Location 1: {found_location}\n"
                                 f"Location 2: {location}")

        if found_location is not None:
            return found_location
        else:
            raise ValueError("Location with specified attributes not found! Please ensure that the Location's "
                             "full details are known and imported before attempting to find the Object.")

    @staticmethod
    def get_location_by_name(location_name: str) -> Location:
        # Initialize search variables
        locations_found = 0
        found_location = None

        # Search all stored locations (every location that's instantiated should be stored)
        for location in Location._all_locations:

            # Check name first, if it's not a match, check the next location.
            if location.get_name() != location_name.strip().title():
                continue

            # This Location matches a stored one
            if locations_found < 1:
                locations_found += 1
                found_location = location
            else:
                raise ValueError(f"Multiple conflicting locations with same info. Make sure the "
                                 f"Location is only added once.\n"
                                 f"Location 1: {found_location}\n"
                                 f"Location 2: {location}")

        if found_location is not None:
            return found_location
        else:
            raise ValueError("Location with specified name not found! Please ensure that the Location's "
                             "full details are known and imported before attempting to find the Object.")
