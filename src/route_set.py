from __future__ import annotations

import random

from location import Location


class RouteSet:
    def __init__(self, routes: set[list[Location]]):
        """
        A set of Routes (in this case, an ordered list of Locations). Defines methods to help mutate a set of routes,
        and also to help calculate the overall fitness.

        :param routes: A set of routes (i.e. a set of Location lists).
        """
        self._route_set = routes

    def mutate(self) -> RouteSet:
        """
        Change this RouteSet slightly such that some neighboring Location(s) could be "swapped" between their respective
        routes, or given from one route to another.

        :return: A new RouteSet that can be considered a child of this single parent RouteSet.
        """
        # Save routes into an iterable list
        new_list = list(self._route_set)
        num_routes = len(new_list)

        # For each route
        for i in range(num_routes):
            current_route = new_list[i]

            # Choose whether to mutate this particular route or not at all
            if random.randint(1, 2) % 2 == 0:
                # Skip mutating this route
                continue

            # Choose to reorder self or exchange with neighbor
            if random.randint(1, 2) % 2 == 0:
                # Chose to exchange with neighbor.
                # Choose a random neighbor
                if random.randint(1, 2) % 2 == 0:
                    # Next Neighbor
                    neighbor_route = new_list[(i + 1) % num_routes]
                else:
                    # Previous Neighbor
                    neighbor_route = new_list[(i - 1) % num_routes]

                # Choose whether to "swap" or "give".
                if random.randint(1, 2) % 2 == 0:
                    # Swap
                    ix_swap_from = random.randint(1, len(current_route) - 2)
                    ix_swap_to = random.randint(1, len(neighbor_route) - 2)
                    swap_location = current_route[ix_swap_from]
                    current_route[ix_swap_from] = neighbor_route[ix_swap_to]
                    neighbor_route[ix_swap_to] = swap_location
                else:
                    # Give
                    if len(current_route) <= 2 and len(neighbor_route) <= 2:
                        # Both routes only have the HUB location. Skip giving.
                        continue
                    if len(current_route) <= 2:
                        # Current route too short. Take from neighbor instead of giving.
                        ix_give = random.randint(1, len(neighbor_route) - 2)
                        ix_insert = random.randint(1, len(current_route) - 2)
                        current_route.insert(ix_insert, neighbor_route[ix_give])
                    else:
                        # Give to neighbor
                        ix_give = random.randint(1, len(current_route) - 2)
                        ix_insert = random.randint(1, len(neighbor_route) - 2)
                        neighbor_route.insert(ix_insert, current_route[ix_give])
            else:
                # Chose to reorder self.
                ix_swap_from = random.randint(1, len(current_route) - 2)
                ix_swap_to = random.randint(1, len(current_route) - 2)
                swap_location = current_route[ix_swap_from]
                current_route[ix_swap_from] = current_route[ix_swap_to]
                current_route[ix_swap_to] = swap_location
        return RouteSet(set(new_list))

    def offspring(self, other_parent: RouteSet) -> RouteSet:
        """

        :param other_parent:
        :return:
        """
        # Here, we aim to do the following:
        # 1. Combine the "best" routes from each set into a new RouteSet.
        #   a. We will need to detect if ANY subset of routes has the same Locations as the other RouteSet
        #   b. Check for partial fitness of the route subsets to determine which to keep.
        # 2. If no subsets with equal Locations exist, then:
        #   a. Test partial fitness of all routes.
        #   b. Keep the "best" route.
        #   c. (Iteratively) go through the rest of the routes, and if any of the Locations are in the routes chosen
        #      before it, remove the Location from the route, then choose it to add to the child.

        # Make new lists for each parent
        list_one = list(self._route_set)
        list_two = list(other_parent._route_set)
        len_one = len(list_one)
        len_two = len(list_two)

        # Validate num_routes
        if len_one != len_two:
            raise ValueError("Two RouteSets with a different number of routes detected! This method doesn't support "
                             "RouteSets of varying length.")
        else:
            num_routes = len_one

        # Test largest sets of route Locations first, progressively reducing size until it can't find any more matches.
        location_set_one = set()
        for route in list_one:
            for location in route:
                location_set_one.add(location)
        location_set_two = set()
        for route in list_two:
            for location in route:
                location_set_two.add(location)

        # Validate locations
        if location_set_one != location_set_two:
            raise ValueError("Two RouteSets don't have the same locations! Two parent RouteSets must have the same "
                             "locations.")
        else:
            all_locations = location_set_one

        # We will cycle through each route, subtracting locations in the chosen route from the set of all locations
        # If one of these subtracted location sets is in a subtracted location set of the RouteSet we're comparing to,
        # then we can continue trying to reduce the set size until we find the smallest equivalent location subsets.
        subset_one = all_locations
        subset_two = all_locations
        subset_list_one = list_one.__new__(list)
        subset_list_two = list_two.__new__(list)
        for i in range(num_routes):
            # Update search params for each level
            num_routes_at_this_level = len(subset_one)
            common_grouping_at_this_level = False

            for j in range(num_routes_at_this_level):
                # Subtract one route from test set
                set_compare_one = subset_one.difference(set(subset_list_one[j][1:-1]))  # Don't include HUB

                # Test each subtracted set in subset_two
                for k in range(num_routes_at_this_level):
                    set_compare_two = subset_two.difference(set(subset_list_two[k][1:-1]))  # Don't include HUB

                    # Check if there is a grouping of route(s) that share common locations among the subsets.
                    if set_compare_one.issubset(set_compare_two):
                        # Use the first one found.
                        subset_one = set_compare_one.__new__(set)
                        subset_two = set_compare_two.__new__(set)
                        subset_list_one = subset_list_one - subset_list_one[j]
                        subset_list_two = subset_list_two - subset_list_two[k]
                        common_grouping_at_this_level = True
                        break

                if common_grouping_at_this_level:
                    break  # Continue to next "level" of route subtraction

            if common_grouping_at_this_level is False:
                break  # There are no more location grouping matches

        # Test to see if there was a grouping that was found
        if subset_list_one != list_one and subset_list_two != list_two:
            # A subgroup of Location matches were found among the RouteSets.
            # Compare them here.
            pass  # TODO: compare the two RouteSet subsets for partial fitness to choose which one to keep and return.

    def get_routes(self) -> set[list[Location]]:
        return self._route_set

    def get_route_from_location(self, location: Location) -> list[Location]:
        """
        :param location: The Location you're searching this RouteSet for. Cannot be the HUB location.
        :return: A route (list of Locations) that contains the Location specified.
        """
        num_routes_found = 0
        route_found = None
        for route in self._route_set:
            if location in route:
                num_routes_found += 1
                route_found = route
        if num_routes_found > 1:
            raise ValueError(f"Invalid RouteSet detected! {self} has more than one {location} location.\n"
                             f"If this is the intended HUB location, ensure that ")
        if num_routes_found == 0:
            raise ValueError(f"Invalid RouteSet detected! {self} doesn't have the {location} location.")
        return route_found

    def get_total_distance(self) -> float:
        """
        :return: The total distance in miles of all routes in the set, assuming each route is only traversed once by one
                 Truck.
        """
        distance = 0.0
        for route in self._route_set:
            distance += RouteSet.__get_route_distance(route)
        return distance

    def get_all_locations(self) -> set[Location]:
        """
        :return: A set of every location the RouteSet traverses. Ideally, this is all the Locations that need
            traversing.
        """
        found_locations = set()
        for route in self._route_set:
            for location in route:
                found_locations.add(location)
        return found_locations

    def get_max_route_length(self) -> int:
        """
        :return: The number of Locations in the longest route that's part of the set.
        """
        max_length = -1
        for route in self._route_set:
            if len(route) > max_length:
                max_length = len(route)
        return max_length

    def get_med_route_length(self) -> float:
        """
        :return: The median number of Locations across all routes.
        """
        # Gather the location count of each route
        lengths = []
        for route in self._route_set:
            lengths.append(len(route))

        return RouteSet.__calculate_median(lengths)

    def get_max_deviance(self, hub_location: Location) -> float:
        """
        Calculates the maximum route distance deviance from a theoretically ideal route (a straight line going out and
        back with all locations). Essentially, the "width" of the widest route petal.

        :param hub_location: The starting and ending point of all the routes.
        :return: The largest route-petal width of all the given routes in the set.
        """
        max_deviance = -1.0
        for route in self._route_set:
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
        for route in self._route_set:
            deviance = RouteSet.__get_route_deviance(route, hub_location)
            deviance_list.append(deviance)
        return sum(deviance_list) / len(deviance_list)

    def get_max_locations_per_mile(self) -> float:
        """
        Calculates the distance-efficiency of the most distance-efficient route in the RouteSet.
        :return: The Location density of the route (num_locations / route_distance).
        """
        max_density = 0.0
        for route in self._route_set:
            location_density = len(route) / RouteSet.__get_route_distance(route)
            if location_density > max_density:
                max_density = location_density
        return max_density

    def get_med_locations_per_mile(self) -> float:
        """
        Calculates the median distance-efficiency of the all routes in the RouteSet.
        :return: The median Location density of the routes (num_locations / route_distance).
        """
        density_list = []
        for route in self._route_set:
            location_density = len(route) / RouteSet.__get_route_distance(route)
            density_list.append(location_density)

        return RouteSet.__calculate_median(density_list)

    def get_avg_locations_per_mile(self) -> float:
        """
        Calculates the average distance-efficiency of the all routes in the RouteSet.
        :return: The average Location density of the routes (num_locations / route_distance).
        """
        density_list = []
        for route in self._route_set:
            location_density = len(route) / RouteSet.__get_route_distance(route)
            density_list.append(location_density)

        return sum(density_list) / len(density_list)

    @staticmethod
    def __get_route_deviance(route: list[Location], hub_location: Location) -> float:
        """Calculates the deviance from the theoretically ideal route in miles."""
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
        """Calculates the total distance of the route in miles."""
        distance = 0.0
        prev_location = None
        for location in route:
            if prev_location is None:
                prev_location = location
            else:
                distance += location.distance_from(prev_location)
        return distance

    @staticmethod
    def __calculate_median(float_list: list[float]) -> float:
        """Calculates the median of the given list of floats."""
        # Ensure there's at least two routes in the set, otherwise return the only value
        list_len = len(float_list)
        if list_len < 2:
            return float_list[0]

        # Calculate the median
        float_list.sort()
        middle_ix = (list_len - 1) // 2  # Subtract one from length to get the maximum index (ix)
        if list_len % 2 == 0:
            # Number of routes is even
            median_length = float_list[middle_ix]
        else:
            # Number of routes is odd
            median_length = float_list[middle_ix] + float_list[middle_ix + 1] / 2.0

        return median_length
