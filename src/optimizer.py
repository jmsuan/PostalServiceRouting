import random
import datetime
from datetime import datetime

from package import Package
from location import Location
from route_list import RouteList


class Optimizer:
    """
    The Optimizer is divided into two parts to help simplify mileage optimization.

    First, the Optimizer generates routes from the hub, using the list of Locations.
    - The routes aim to achieve optimal mileage by creating static routes that hit the most Locations with the smallest
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
    - Any special delivery requirements (e.g. a package that needs to be delivered by a truck with a certain id).
    - How distant it is  from the HUB. (This is to prioritize delivering the furthest packages first within a route,
      which is beneficial to the total mileage if the Truck cannot deliver to all the locations on a route at once.)
    - How many other high priority packages are nearby. (This is a second-pass priority, as it requires the other
      characteristics to be calculated first.)

    The Optimizer can then assign the packages to the Trucks in the order of their priority. The Trucks will then follow
    the routes that were generated earlier, and deliver the packages in the order that they appear on the route, but
    only if the package is on the route that the Truck is following.
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
        if num_routes < 1 or num_routes > 50:
            raise ValueError("num_routes must be 1 to 50")
        if total_generations < 100 or total_generations > 100000:
            raise ValueError("total_generations must be at least 50 and at most 100000 to allow ample time to find a "
                             "good solution.")
        if population_size < 50 or population_size > 1000:
            raise ValueError("population_size must be at least 50 and less than 1000 to allow for a diverse "
                             "population.")

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
            # Select the best RouteLists
            best_route_lists_sorted: list[RouteList] = Optimizer.__select(current_generation, fitness_scores)

            # Implement elitism to keep a certain number of the best solutions
            elitism_size = 5
            elite_pool: list[RouteList] = best_route_lists_sorted[0:elitism_size]

            # Create new RouteLists using randomness, crossover and mutation
            new_generation = []
            for i in range(population_size):
                # Keep the elite RouteLists
                if i < elitism_size:
                    new_generation.append(elite_pool[i])
                    continue

                # Choose parents for crossover
                if random.random() < 0.5:  # 50% chance of choosing a good solution to evolve
                    parent_1 = random.choice(elite_pool)
                else:
                    parent_1 = random.choice(best_route_lists_sorted)
                parent_2 = random.choice(
                    [routes for routes in best_route_lists_sorted if routes != parent_1])

                # Make new RouteList to add to generation
                offspring = parent_1
                if random.random() < 0.5:  # 50% chance of crossover
                    offspring = Optimizer.__crossover(parent_1.copy(), parent_2.copy(), hub)
                    if random.random() < 0.5:  # 50% chance of mutation with crossover
                        mutated_offspring = Optimizer.__mutate(offspring.copy())
                        new_generation.append(mutated_offspring)
                        continue
                else:
                    mutated_offspring = Optimizer.__mutate(offspring.copy())
                    new_generation.append(mutated_offspring)
                    continue

                # Add offspring to new generation
                new_generation.append(offspring.copy())

            # Update the current generation
            current_generation = new_generation

            # Calculate fitness for each RouteList in the new generation
            fitness_scores = []
            for route_list in current_generation:
                route_fitness = Optimizer.__fitness(route_list, hub)
                fitness_scores.append(route_fitness)

            # Print the fitness scores of the current generation
            print(f"Generation {total_generations - generations_left + 1} "
                  f"fitness scores: {sorted(fitness_scores, reverse=True)}")

            generations_left -= 1

        # Select the best RouteList from the final generation
        best_route_set = Optimizer.__select(current_generation, fitness_scores)[0]

        return best_route_set

    @staticmethod
    def prioritize_packages(package_list: list[Package], hub_location: Location) -> list[int]:
        """
        Assign package priorities based on multiple characteristics:

        - The deadline of the package.
        - Any special delivery requirements (e.g. a package that needs to be delivered by a truck with a certain id).
        - How distant it is  from the HUB. (This is to prioritize delivering the furthest packages first within a route,
          which is beneficial to the total mileage if the Truck cannot deliver to all the locations on a route at once.)
        - How many other high priority packages are nearby. (This is a second-pass priority, as it requires the other
          characteristics to be calculated first.)

        :param package_list: A list of Package objects to prioritize.
        :param hub_location: The central location that the routes will be generated from and return to.
        :return: A list of scores for each package in the package_list. The scores are in the same order as the
                    package_list.
        """
        # Initialize the list of priorities
        priorities = []

        # Calculate the priority for each package
        for package in package_list:
            priority = 0

            # Add to priority based on the deadline
            eod_time = datetime.strptime("11:59:59 PM", "%I:%M:%S %p")
            deadline = package.get_deadline()
            time_left = eod_time - deadline
            seconds_left = int(time_left.total_seconds())
            minutes_left = seconds_left // 60  # "Minutes before EOD"
            priority += round(minutes_left ** 1.4)

            # Add to priority based on special requirements
            special_code = package.get_special_code()
            if special_code is not None and special_code != "":
                # If special_code is not None, it should be a list of strings.
                assert isinstance(special_code, list) and all(isinstance(item, str) for item in special_code)
                num_codes = len(special_code)
                priority += num_codes * 50  # Add to priority proportional to how many special requirements there are
                # Check for batch codes
                for code in special_code:
                    if "BATCH" in code:
                        # Add a large number to the priority to ensure that batched packages are delivered together
                        priority += 1000
                        break

                # Add very high priority if package has a special code and a deadline
                if deadline != eod_time:
                    priority += 1000

            # Add to priority based on the distance to the HUB
            priority += round(package.get_destination().distance_from(hub_location) * 10000)

            priorities.append(priority)

        # Second-pass priorities
        priorities_to_add = []
        for package in package_list:
            priority = 0

            # Add to priority based on how many other high priority packages are nearby.
            for i, other_package in enumerate(package_list):
                if package == other_package:
                    priorities_to_add.append(0)
                    continue
                if priorities[i] > 0:
                    distance = package.get_destination().distance_from(other_package.get_destination())
                    if distance < 10:
                        priority += 10
                    elif distance < 20:
                        priority += 5
                    elif distance < 30:
                        priority += 2

                priorities_to_add.append(priority)

        # Add the second-pass priorities to the first-pass priorities
        for i in range(len(priorities)):
            priorities[i] += priorities_to_add[i]

        return priorities

    @staticmethod
    def __fitness(route_set: RouteList, hub_location: Location) -> int:
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

        :param route_set: The RouteList to calculate the fitness of.
        :param hub_location: The central location that the routes will be generated from and return to.
        :return: The fitness score of the RouteList.
        """
        # Get all factors
        total_distance = route_set.get_total_distance()
        max_route_length = route_set.get_max_route_length()
        med_route_length = route_set.get_med_route_length()
        max_deviation = route_set.get_max_deviance(hub_location)
        avg_deviation = route_set.get_avg_deviance(hub_location)
        max_density = route_set.get_max_locations_per_mile()
        med_density = route_set.get_med_locations_per_mile()
        avg_density = route_set.get_avg_locations_per_mile()

        # Apply weights to each factor
        distance_weight = -20  # Negative because we want to minimize distance
        max_route_length_weight = -1
        med_route_length_weight = -50
        max_deviation_weight = -50
        avg_deviation_weight = -20
        max_density_weight = 1
        med_density_weight = 50
        avg_density_weight = 10

        # Calculate fitness
        fitness = int(total_distance * distance_weight +
                      max_route_length * max_route_length_weight +
                      med_route_length * med_route_length_weight +
                      max_deviation * max_deviation_weight +
                      avg_deviation * avg_deviation_weight +
                      max_density * max_density_weight +
                      med_density * med_density_weight +
                      avg_density * avg_density_weight)

        return fitness + 10000  # Add 10000 to ensure that the fitness is always positive

    @staticmethod
    def __select(routes: list[RouteList], fitness_scores: list[float]) -> list[RouteList]:
        """
        Select the best RouteLists from a generation based on their fitness scores. Half of the RouteLists will be
        selected to be used as parents for the next generation.

        :param routes: The RouteLists to select from.
        :param fitness_scores: The fitness scores of the RouteLists.
        :return: The best RouteLists from the generation.
        """
        # Sort the routes by their fitness scores
        sorted_routes = sorted(zip(routes, fitness_scores), key=lambda x: x[1], reverse=True)

        # Select the best half of the routes
        best_routes = [route.copy() for route, _ in sorted_routes[:int(len(sorted_routes) * 0.7)]]

        return best_routes

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

        # If the fitness scores are all the same, the algorithm has converged
        if len(set(fitness_scores)) == 1:  # Convert to set to remove duplicates
            print(f"Converged with {generations} generations left.")
            return True

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
