from __future__ import annotations
import random
from location import Location


class RouteList:
    def __init__(self, routes: list[list[Location]]):
        """
        A set of Routes (in this case, an ordered list of Locations). Defines methods to help mutate a set of routes,
        and also to help calculate the overall fitness.

        :param routes: A set of routes (i.e. a set of Location lists).
        """
        self._route_set = routes

    def mutate(self) -> RouteList:
        """
        Change this RouteList slightly such that some neighboring Location(s) could be "swapped" between their
        respective routes, or given from one route to another.

        :return: A new RouteList that can be considered a child of this single parent RouteList.
        """
        # Save routes into an iterable list
        new_list = self._route_set.copy()
        num_routes = len(new_list)

        # For each route
        for i in range(num_routes):
            current_route = new_list[i]

            # Choose whether to mutate this route at all
            if random.randint(1, num_routes) != 1:  # 1 in num_routes chance to mutate this route.
                continue

            # Choose to reorder self or exchange with neighbor
            if random.random() < 0.1 or len(current_route) <= 10:
                # Chose to exchange with neighbor.
                # Choose a random neighbor
                if random.randint(0, 1) == 0:
                    # Next Neighbor
                    neighbor_route = new_list[(i + 1) % num_routes]
                else:
                    # Previous Neighbor
                    neighbor_route = new_list[(i - 1) % num_routes]

                # Choose whether to "swap" or "give".
                if random.random() < 0.1:
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

                # Determine if the swap will be with the next or previous location
                if random.randint(0, 1) == 0:
                    # Swap with next location
                    ix_swap_to = ix_swap_from + 1 if ix_swap_from < len(current_route) - 3 else ix_swap_from - 1
                else:
                    # Swap with previous location
                    ix_swap_to = ix_swap_from - 1 if ix_swap_from > 2 else ix_swap_from + 1

                swap_location = current_route[ix_swap_from]
                current_route[ix_swap_from] = current_route[ix_swap_to]
                current_route[ix_swap_to] = swap_location
        return RouteList(new_list)

    def offspring(self, other_parent: RouteList, hub_location: Location) -> RouteList:
        """
        Create a new RouteList that is a child of this RouteList and another parent RouteList. The offspring will
        contain at least one of the routes from both parents, and will contain all the Locations from both parents.

        :param other_parent: The other parent RouteList to create an offspring with.
        :param hub_location: The Location that is the starting and ending point of all routes.
        :return:
        """
        # Check if both RouteList instances have the same set of Locations
        if self.get_all_locations() != other_parent.get_all_locations():
            raise ValueError("Both RouteList instances must have the same set of Locations.")

        # Check if both RouteList instances have the same number of routes
        if len(self._route_set) != len(other_parent._route_set):
            raise ValueError("Both RouteList instances must have the same number of routes.")

        # Define a function to calculate the location density of a route
        def location_density(route: list[Location]) -> float:
            route_distance = RouteList.get_route_distance(route)
            if route_distance == 0.0:
                return 0.0
            else:
                # Subtract 2 to account for the HUB location at the start and end of the route
                return (len(route) - 2) / route_distance

        # Define a function to calculate the fitness of a route
        def route_fitness(route: list[Location]) -> float:
            # Get all factors
            total_distance = RouteList.get_route_distance(route)
            num_locations = len(route) - 2  # Subtract 2 to account for the HUB location
            deviance = RouteList.__get_route_deviance(route, hub_location)
            density = location_density(route)

            # Apply weights to each factor
            # A negative weight means that we want to minimize the value.
            distance_weight = -0.3
            num_locations_weight = -6.0
            deviance_weight = -0.5
            density_weight = 5.0

            # Calculate fitness
            fitness = (total_distance * distance_weight) + (num_locations * num_locations_weight) + (
                    deviance * deviance_weight) + (density * density_weight)

            return fitness

        # Create a list of all routes from both parents and calculate their location densities
        all_routes = (self._route_set + other_parent._route_set).copy()
        route_densities = [(route, route_fitness(route)) for route in all_routes]

        # Sort the list of routes in descending order of location density
        route_densities.sort(key=lambda x: x[1], reverse=True)

        # Initialize an empty set to store the locations that have already been added to the offspring's routes
        added_locations = set()

        # Initialize an empty list to store the offspring's routes
        offspring_routes = []

        # Iterate over the sorted list of routes
        for route, _ in route_densities:
            # Stop adding routes if offspring has same number of routes as parents
            if len(offspring_routes) >= len(self._route_set):
                break
            # Create a new route that contains only the locations that are not already in the set of added locations
            new_route = [location for location in route if location not in added_locations and location != hub_location]
            # Add the HUB location to the start and end of the new route
            new_route.insert(0, hub_location)
            new_route.append(hub_location)
            # Add this new route to the offspring's list of routes and add its locations to the set of added locations
            offspring_routes.append(new_route)
            added_locations.update(new_route)

        # If the number of offspring routes is less than the number of parent routes, add empty routes until they are
        # equal
        while len(offspring_routes) < len(self._route_set):
            offspring_routes.append([hub_location, hub_location])

        # Iterate over all Locations from both parents
        all_locations = self.get_all_locations().union(other_parent.get_all_locations())
        for location in all_locations:
            # If the Location is not in the set of added locations, add it to the least dense route in the offspring
            if location not in added_locations and location != hub_location:
                least_dense_route = min(offspring_routes, key=location_density)
                least_dense_route.insert(-1, location)  # Insert before the last HUB location
                added_locations.add(location)

        # Create a new RouteList instance using the offspring's list of routes
        offspring = RouteList(offspring_routes)

        return offspring

    def get_routes(self) -> list[list[Location]]:
        return self._route_set

    def get_route_from_location(self, location: Location) -> list[Location]:
        """
        :param location: The Location you're searching this RouteList for. Cannot be the HUB location.
        :return: A route (list of Locations) that contains the Location specified.
        """
        num_routes_found = 0
        route_found = None
        for route in self._route_set:
            if location in route:
                num_routes_found += 1
                route_found = route
        if num_routes_found > 1:
            raise ValueError(f"Invalid RouteList detected! {self} has more than one {location} location.\n"
                             f"If this is the intended HUB location, ensure that ")
        if num_routes_found == 0:
            raise ValueError(f"Invalid RouteList detected! {self} doesn't have the {location} location.")
        return route_found

    def get_all_locations(self) -> set[Location]:
        """
        :return: A set of every location the RouteList traverses. Ideally, this is all the Locations that need
            traversing.
        """
        found_locations = set()
        for route in self._route_set:
            for location in route:
                found_locations.add(location)
        return found_locations

    def get_total_distance(self) -> float:
        """
        :return: The total distance in miles of all routes in the set, assuming each route is only traversed once by one
                 Truck.
        """
        distance = 0.0
        for route in self._route_set:
            distance += RouteList.get_route_distance(route)
        return distance

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

        return RouteList.__calculate_median(lengths)

    def get_max_deviance(self, hub_location: Location) -> float:
        """
        Calculates the maximum route distance deviance from a theoretically ideal route (a straight line going out and
        back with all locations). Essentially, the "width" of the widest route petal.

        :param hub_location: The starting and ending point of all the routes.
        :return: The largest route-petal width of all the given routes in the set.
        """
        max_deviance = -1.0
        for route in self._route_set:
            deviance = RouteList.__get_route_deviance(route, hub_location)
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
            deviance = RouteList.__get_route_deviance(route, hub_location)
            deviance_list.append(deviance)
        return sum(deviance_list) / len(deviance_list)

    def get_max_locations_per_mile(self) -> float:
        """
        Calculates the distance-efficiency of the most distance-efficient route in the RouteList.
        :return: The Location density of the route (num_locations / route_distance).
        """
        max_density = 0.0
        for route in self._route_set:
            location_density = len(route) / RouteList.get_route_distance(route)
            if location_density > max_density:
                max_density = location_density
        return max_density

    def get_med_locations_per_mile(self) -> float:
        """
        Calculates the median distance-efficiency of the all routes in the RouteList.
        :return: The median Location density of the routes (num_locations / route_distance).
        """
        density_list = []
        for route in self._route_set:
            location_density = len(route) / RouteList.get_route_distance(route)
            density_list.append(location_density)

        return RouteList.__calculate_median(density_list)

    def get_avg_locations_per_mile(self) -> float:
        """
        Calculates the average distance-efficiency of the all routes in the RouteList.
        :return: The average Location density of the routes (num_locations / route_distance).
        """
        density_list = []
        for route in self._route_set:
            location_density = len(route) / RouteList.get_route_distance(route)
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
        deviance = RouteList.get_route_distance(route) - ideal_distance

        return deviance

    @staticmethod
    def get_route_distance(route: list[Location]) -> float:
        """Calculates the total distance of the route in miles."""
        distance = 0.0
        prev_location = None
        for location in route:
            if prev_location is None:
                prev_location = location
            else:
                distance += location.distance_from(prev_location)
                prev_location = location
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
