from package import Package
from location import Location
from route_set import RouteSet


class Scheduler:
    """
    The scheduler is divided into two parts to simplify mileage optimization.

    First, the Scheduler generates routes from the hub, using the list of Locations.
    - The routes aim to achieve optimal milage by creating static routes that hit the most Locations with the smallest
      total distance travelled. This means that a single route ideally follow a straight line out from the hub to the
      furthest destination, then comes back (stopping to deliver packages to locations along the line).
    - However, in practice, the Locations that need to be delivered to are never all located in a straight line. So this
      routing algorithm aims to generate routes that look like "petals" or "ellipses." These petals should have as many
      routes on them as possible, while aiming to minimize the "deviance" it has from a theoretical straight line from
      the hub to the furthest Location on the route. We can measure this deviance by taking the total distance of the
      route and comparing it to a round trip from the hub to the furthest location.
    - This solution takes into consideration that the trucks have a limited capacity, so they will need to return to the
      hub anyway. This gives the truck the opportunity to follow another "semi-ideal" route that starts from the hub.
      The main benefit to this approach is the fact that it's easy to calculate the routes from a list of Locations,
      when only the distances between the Locations are given.
    - In the case that a Truck needs to reuse a route because it could not carry all the packages for locations on the
      route the first time, it will only travel to the Locations that need to be delivered to (in the order that is
      specified by the route).

    Next, the Scheduler generates "priorities" for each package. This takes into account the following characteristics:
    -
    - TODO: Add other characteristics
    -
    - How far it is from the HUB. (This is to prioritize delivering the furthest packages first within a route, which is
      beneficial to the total mileage if the Truck cannot deliver to all the locations on a route at once.)
    """
    @staticmethod
    def generate_routes(hub: Location, location_list: list[Location]):
        # Change as desired to optimize mileage based on num of Trucks and Locations
        number_of_routes = 5

        # For simplicity, we will make a list that doesn't have the HUB.
        if hub in location_list:
            destinations = location_list.remove(hub)
        else:
            destinations = location_list

        #
        pass

    @staticmethod
    def prioritize_packages(package_list: list[Package]) -> list[int]:
        """
        Assign package priorities based on multiple scoring factors:
            - distance to hub(?)
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
        pass  # TODO: Implement

    @staticmethod
    def __validate_routes(route_set: RouteSet, location_list: list[Location]) -> bool:
        pass
