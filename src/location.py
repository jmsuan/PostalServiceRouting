from __future__ import annotations
from hash_table import HashTable


class Location:
    # Stores all Location objects that are created
    _all_locations = []

    def __init__(self, name: str, street_address: str, city: str, state: str, zip_code: str):
        """Instantiates a location that can store driving distances from other locations."""
        self._name = name.strip().capitalize()
        self._address = street_address.strip().capitalize()
        self._city = city.strip().capitalize()
        self._state = state.strip().upper()
        self._zip = zip_code.strip()
        self._distance_table = HashTable(50)  # Size should (ideally) be at least 1.3x the max num of distances
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

            # Check address first, if it's not a match, check the next stored location
            if location.get_address() != street_address.strip().capitalize():
                continue  # Street address doesn't match. Check next stored Location.
            if location.get_city() != city.strip().capitalize():
                continue  # Address matches but not city.
            if location.get_state() != state.upper().strip():
                continue  # Address matches but not state.
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

        raise ValueError("Location with specified attributes not found! Please ensure that the Location's "
                         "full details are known and imported before attempting to find the Object.")
