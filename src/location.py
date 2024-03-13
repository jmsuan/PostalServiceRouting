from __future__ import annotations
from hash_table import HashTable


class Location:
    _all_locations = []

    def __init__(self, name: str, street_address: str, city: str, state: str, zip_code: str):
        """Instantiates a location that can store driving distances from other locations."""
        self._name = name
        self._address = street_address.strip()
        self._city = city
        self._state = state
        self._zip = zip_code
        self._distance_table = HashTable(50)
        Location._all_locations.append(self)

    def add_distance(self, location: Location, miles_to_drive: float):
        self._distance_table.insert(location, miles_to_drive)

    def distance_from(self, location: Location) -> float:
        return self._distance_table.lookup(location)

    def get_address(self) -> str:
        return self._address

    def get_city(self) -> str:
        return self._city

    def get_state(self) -> str:
        return self._state

    def get_zip(self) -> str:
        return self._zip

    def get_name(self) -> str:
        return self._name

    @staticmethod
    def get_location(street_address: str, city: str, state: str, zip_code: str) -> Location:
        # Initialize search variables
        locations_found = 0
        found_location = None

        # Search all stored locations (every location that's instantiated should be stored)
        for location in Location._all_locations:
            if locations_found > 1:
                raise AttributeError("Multiple conflicting locations with same info!")

            # Check address first, if it's not a match, check the next stored location
            if location.get_address() == street_address.strip():
                locations_found += 1
                found_location = location
            else:
                continue  # TODO: finish location search logic

            if location.get_city() == city.strip():
                pass  # TODO: finish location search logic

        if found_location is not None:
            return found_location

        raise ValueError("Location with specified attributes not found! Please ensure that the Location's "
                         "full details are known and imported before attempting to find the Object.")
