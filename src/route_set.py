from __future__ import annotations
from location import Location


class RouteSet:
    def __init__(self, routes: set[list[Location]]):
        """
        A set of Routes (in this case, an ordered list of Locations). Defines methods to help mutate a set of routes,
        and also to help calculate the overall fitness.

        :param routes: A set of routes (i.e. a set of Location lists).
        """
        self.route_set = routes

    def mutate(self) -> RouteSet:
        """
        Change this RouteSet slightly such that some neighboring Location(s) could be "swapped" between their respective
        routes, or given from one route to another.

        :return: A new RouteSet that can be considered a child of this single parent RouteSet.
        """
        pass

    def offspring(self, other_parent: RouteSet) -> RouteSet:
        """

        :param other_parent:
        :return:
        """
        pass

    def get_total_distance(self) -> float:
        """
        :return: The total distance in miles of all routes in the set, assuming each route is only traversed once by one
                 Truck.
        """
        distance = 0.0
        for route in self.route_set:
            distance += RouteSet.__get_route_distance(route)
        return distance

    def get_all_locations(self) -> set[Location]:
        """
        :return: A set of every location the RouteSet traverses. Ideally, this is all the Locations that need
            traversing.
        """
        found_locations = set()
        for route in self.route_set:
            for location in route:
                found_locations.add(location)
        return found_locations

    def get_max_route_length(self) -> int:
        """
        :return: The number of Locations in the longest route that's part of the set.
        """
        max_length = -1
        for route in self.route_set:
            if len(route) > max_length:
                max_length = len(route)
        return max_length

    def get_med_route_length(self) -> float:
        """
        :return: The median number of Locations across all routes.
        """
        # Gather the location count of each route
        lengths = []
        for route in self.route_set:
            lengths.append(len(route))

        # Ensure there's at least two routes in the set, otherwise return the only length
        num_lengths = len(lengths)
        if num_lengths < 2:
            return lengths[0]

        # Find the median length of all routes
        lengths.sort()
        middle_ix = (num_lengths - 1) // 2  # Subtract one from length to get the maximum index (ix)
        if num_lengths % 2 == 0:
            # Number of routes is even
            median_length = lengths[middle_ix]
        else:
            # Number of routes is odd
            median_length = lengths[middle_ix] + lengths[middle_ix + 1] / 2.0

        return median_length

    def get_max_deviance(self, hub_location: Location) -> float:
        """
        Calculates the maximum route distance deviance from a theoretically ideal route (a straight line going out and
        back with all locations). Essentially, the "width" of the widest route petal.

        :param hub_location: The starting and ending point of all the routes.
        :return: The largest route-petal width of all the given routes in the set.
        """
        max_deviance = -1.0
        for route in self.route_set:
            deviance = RouteSet.__get_route_deviance(route, hub_location)
            if deviance > max_deviance:
                max_deviance = deviance
        return max_deviance

    def get_avg_deviance(self, hub_location: Location) -> float:
        """
        Calculates the average route distance deviance from a theoretically ideal route (a straight line going out and
        back with all locations). Essentially, the average "width" of all route petals.

        :param hub_location: The starting and ending point of all the routes.
        :return: The average route-petal width of all the given routes in the set.
        """
        deviance_list = []
        for route in self.route_set:
            deviance = RouteSet.__get_route_deviance(route, hub_location)
            deviance_list.append(deviance)
        return sum(deviance_list) / len(deviance_list)

    def get_max_locations_per_mile(self) -> float:
        pass

    def get_med_locations_per_mile(self) -> float:
        pass

    @staticmethod
    def __get_route_deviance(route: list[Location], hub_location: Location) -> float:
        # Ensure that each route starts and ends with the hub Location.
        if route[0] != hub_location or route[-1] != hub_location:
            raise ValueError(f"One or more routes do not start/end with the HUB location!\n"
                             f"The route: {route}.")

        # Calculate distance to furthest Location
        longest_distance = 0.0
        for location in route:
            distance_from_hub = location.distance_from(hub_location)
            if distance_from_hub > longest_distance:
                longest_distance = distance_from_hub

        # Calculate theoretically ideal total distance
        ideal_distance = longest_distance * 2  # Round-trip to the furthest Location

        # Calculate deviance of the route
        deviance = RouteSet.__get_route_distance(route) - ideal_distance

        return deviance

    @staticmethod
    def __get_route_distance(route: list[Location]) -> float:
        distance = 0.0
        prev_location = None
        for location in route:
            if prev_location is None:
                prev_location = location
            else:
                distance += location.distance_from(prev_location)
        return distance
