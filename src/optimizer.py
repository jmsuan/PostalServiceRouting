import copy
import math
import random

from package import Package
from location import Location
from route_list import RouteList


class Optimizer:
    """
    The Optimizer is divided into two parts to help simplify mileage optimization.

    First, the Optimizer generates routes from the hub, using the list of Locations.

    - The routes aim to achieve optimal milage by creating static routes that hit the most Locations with the smallest
      total distance travelled. This means that a single route ideally follows a straight line out from the hub to the
      furthest destination, then comes back (stopping to deliver packages to locations along the line).
    - However, in practice, the Locations that need to be delivered to are never all located in a straight line. So this
      routing algorithm aims to generate routes that look like "petals" or "ellipses." These petals should have as many
      Locations on them as possible, while aiming to minimize the "deviance" it has from the theoretical straight line
      from the hub to the furthest Location on the route. We can measure this deviance by taking the total distance of
      the route and comparing it to a round trip from the hub to the furthest location.
    - This solution takes into consideration that the trucks have a limited capacity, so they will need to return to the
      hub anyway. This gives the truck the opportunity to follow another "semi-ideal" route that starts from the hub.
      The main benefit to this approach is the fact that it's easy to calculate the routes from a list of Locations,
      when only the distances between the Locations are given.
    - In the case that a Truck needs to reuse a route because it could not carry all the packages for locations on the
      route the first time, it will only travel to the Locations that need to be delivered to (in the order that is
      specified by the route).

    Next, the Optimizer generates "priorities" for each package. This takes into account the following characteristics:

    - The deadline of the package.
    - Any special truck requirements (e.g. a package that needs to be delivered by a truck with a certain id).
    - How distant it is  from the HUB. (This is to prioritize delivering the furthest packages first within a route,
      which is beneficial to the total mileage if the Truck cannot deliver to all the locations on a route at once.)
    - How many other high priority packages are nearby. (This is a second-pass priority, as it requires the other
      characteristics to be calculated first.)

    The Optimizer can then assign the packages to the Trucks in the order of their priority. The Trucks will then follow
    the routes that were generated earlier, and deliver the packages in the order that they were assigned, but only if
    the package is on the route that the Truck is following.
    """
    @staticmethod
    def generate_routes(
            all_location_list: list[Location],
            hub: Location,
            num_routes: int,
            total_generations: int,
            population_size: int
    ) -> RouteList:
        """
        Generates a set of routes that aim to minimize the total mileage of the Trucks. The routes are generated using a
        genetic algorithm that aims to minimize the total distance travelled by the Trucks. The algorithm will generate
        a set of routes that will be used to deliver the packages to the Locations.

        :param hub: The central location that the routes will be generated from and return to.
        :param all_location_list: The list of all Locations that need to be visited by the Trucks.
        :param total_generations: The number of generations that the genetic algorithm will run for.
        :param num_routes: The number of routes to be in the RouteList.
        :param population_size: The number of RouteLists to be in each generation.
        :return: A RouteList object that contains the routes (lists of Locations) that the Trucks will follow.
        """
        if num_routes < 1:
            raise ValueError("num_routes must be at least 1")
        if population_size < 5:
            raise ValueError("population_size must at least 5")
        if total_generations < 50:
            raise ValueError("total_generations must be at least 50 to ensure the algorithm has enough time to "
                             "converge on a solution.")

        # Collect all Locations that aren't the hub
        locations_to_visit = all_location_list.copy()
        locations_to_visit.remove(hub)

        # Generate initial population
        current_generation = []
        for _ in range(population_size):  # Create a RouteList for each member of the population
            route_list = []
            random.shuffle(locations_to_visit)  # Shuffle the locations
            for i in range(num_routes):
                route = locations_to_visit[i::num_routes]  # Slice the list of locations into num_routes parts
                route.insert(0, hub)
                route.append(hub)
                route_list.append(route)
            # Convert the set of routes to a RouteList and add it to the first generation
            current_generation.append(RouteList(route_list))

        # Calculate fitness for each RouteList the first generation
        fitness_scores = []
        for route_list in current_generation:
            route_fitness = Optimizer.__fitness(route_list, hub)
            fitness_scores.append(route_fitness)

        # Run genetic algorithm
        generations_left = total_generations
        while not Optimizer.__terminate(generations_left, fitness_scores):
            # Calculate fitness for each RouteList in the new generation
            fitness_scores = []
            for route_list in current_generation:
                route_fitness = Optimizer.__fitness(route_list, hub)
                fitness_scores.append(route_fitness)

            # Print the fitness scores of the current generation
            print(f"Generation {total_generations - generations_left + 1} "
                  f"top fitness scores: {sorted(fitness_scores, reverse=True)[:5]}")

            # Elitism: Keep the best RouteLists from the previous generation
            elitism_size = 2

            # Select the best RouteLists
            sorted_best_routes = sorted(zip(current_generation, fitness_scores), key=lambda x: x[1], reverse=True)
            best_routes_ordered = [route for route, _ in sorted_best_routes]

            # Preserve elites by directly copying the best RouteLists to the next generation
            elite_routes = best_routes_ordered[:elitism_size].copy()

            # Create new RouteLists using crossover and mutation
            new_generation = elite_routes.copy()
            for i in range(population_size):
                if i < elitism_size:  # Don't alter the elites
                    continue  # Skip to the next iteration
                parent_1 = random.choice(
                    [route for route in best_routes_ordered if route not in elite_routes]
                )
                parent_2 = random.choice(
                    [route for route in best_routes_ordered if route not in elite_routes and route != parent_1]
                )
                # Choose to crossover or mutate
                if random.random() < 0.5:  # 50% chance of crossover
                    offspring = Optimizer.__crossover(parent_1, parent_2, hub)
                    if random.random() < 0.8:  # 80% chance of mutation assuming crossover
                        offspring = Optimizer.__mutate(offspring)
                else:  # 50% chance of mutation
                    offspring = Optimizer.__mutate(random.choice(best_routes_ordered))
                new_generation.append(offspring)

            # Update the current generation
            current_generation = new_generation
            generations_left -= 1

        # Select the best RouteList from the final generation
        best_route_set = Optimizer.__select(current_generation, fitness_scores)[0]

        return best_route_set

    @staticmethod
    def prioritize_packages(package_list: list[Package]) -> list[int]:
        """
        Assign package priorities based on multiple scoring factors:
            - distance to hub (furthest first, to minimize total mileage)
            - avg distance from other destinations(?)
            - special priority!
            - deadline!
            - HOW MANY other high priority packages are nearby that facilitate ideal “elevator” routes.
                (Second-pass priority?)
            - Could calc potential facilitators based off if the dist to hub is greater than itself, and if the
                distance is under some value

        :param package_list:
        :return:
        """
        # TODO: Implement
        pass

    @staticmethod
    def __fitness(route_list: RouteList, hub_location: Location) -> float:
        """
        Calculate the fitness of a route. The fitness of a route is scored based on numerous factors:

        - The total distance travelled by all routes in the RouteList.
        - The maximum number of locations in a route.
        - The median number of locations in a route.
        - The maximum deviation from a straight line from the hub to the furthest location on a route.
        - The average deviation from a straight line from the hub to the furthest location on a route for all routes.
        - The maximum location density of all routes.
        - The median location density of all routes.
        - The average location density of all routes.

        :param route_list: The RouteList to calculate the fitness of.
        :param hub_location: The central location that the routes will be generated from and return to.
        :return: The fitness score of the RouteList.
        """
        return route_list.get_fitness(hub_location)

    @staticmethod
    def __select(routes_list: list[RouteList], fitness_scores: list[float]) -> list[RouteList]:
        """
        Select the best RouteLists from a generation based on their fitness scores. Half of the RouteLists will be
        selected to be used as parents for the next generation.

        :param routes_list: The RouteLists to select from.
        :param fitness_scores: The fitness scores of the RouteLists.
        :return: The best 50% of RouteLists from the generation.
        """
        # Sort the routes by their fitness scores
        sorted_routes = sorted(zip(routes_list, fitness_scores), key=lambda x: x[1], reverse=True)

        # Select the best half of the routes
        num_to_keep = math.ceil(len(sorted_routes) / 2)

        # Return the best RouteLists
        best_route_lists = []
        for i in range(num_to_keep):
            route_to_keep, _ = sorted_routes[i]
            best_route_lists.append(route_to_keep)

        return best_route_lists

    @staticmethod
    def __terminate(generations: int, fitness_scores: list[float]) -> bool:
        """
        Determine if the genetic algorithm should terminate based on the number of generations and the fitness scores.

        :param generations: The number of generations that the genetic algorithm will run for.
        :param fitness_scores: The fitness scores of the current generation.
        :return: True if the genetic algorithm should terminate, False otherwise.
        """
        if generations <= 0:
            print("All generations completed.")
            return True

        """# If the fitness scores are all the same, the algorithm has converged
        if len(set(fitness_scores)) == 1:  # Convert to set to remove duplicates
            print(f"Converged with {generations} generations left.")
            return True"""

        return False

    @staticmethod
    def __mutate(route_set: RouteList) -> RouteList:
        """
        Mutate a RouteList to create a new RouteList with a slightly different set of routes.

        :param route_set: The RouteList to mutate.
        :return: A new RouteList that is a mutation of the original RouteList.
        """
        mutation = route_set.mutate()
        return mutation

    @staticmethod
    def __crossover(route_set_1: RouteList, route_set_2: RouteList, hub_location: Location) -> RouteList:
        """
        Create offspring from two RouteLists using crossover.

        :param route_set_1: The first parent RouteList
        :param route_set_2: The second parent RouteList
        :param hub_location: The central location that the routes will be generated from and return to.
        :return: A new RouteList that is the offspring of the two parent RouteLists.
        """
        offspring = RouteList.offspring(route_set_1, route_set_2, hub_location)
        return offspring
