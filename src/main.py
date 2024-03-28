# Student ID: 001264312

from hash_table import HashTable
from interface import Interface
from location import Location
from scheduler import Scheduler
from optimizer import Optimizer
from truck import Truck
from driver import Driver

# Print a new line for readability
print()

# Import location info (creates Location objects and sets distances)
raw_locations = Interface.read_csv("data/distance_info.csv")
location_list = Interface.list_to_location_list(raw_locations)

# Set the HUB for this instance
wgu = Location.get_location_by_name("Western Governors University")
Interface.set_hub(wgu)

# Check if there is a saved set of routes
try:
    Interface.read_csv("data/saved_routes.csv")
    saved_routes_exist = True
except FileNotFoundError:
    saved_routes_exist = False

# Create the list of routes (list of lists of Location objects)
if saved_routes_exist:
    # Ask user if they want to use saved routes or create new ones
    print("There is a saved set of routes that have already been created. Do you want to use these routes?")
    use_saved_routes = input("\nEnter 'y' or 'n' [y]: ").strip().lower()
    if use_saved_routes == "n":
        print("\nAre you sure you want to create new routes? This will overwrite the saved routes.\n"
              "(Creating routes might take a large amount of memory or compute power depending on the what parameters "
              "you enter for the genetic algorithm!)")
        confirm = input("\nEnter 'y' or 'n' [n]: ").strip().lower()
        if confirm == "y":
            # Ask user for parameters to create routes
            route_list = list(Interface.create_routes(location_list, wgu).get_routes())
        else:
            print("\nUsing saved routes...\n")
            route_list = Interface.list_to_route_list(Interface.read_csv("data/saved_routes.csv"))
    else:
        print("\nUsing saved routes...\n")
        route_list = Interface.list_to_route_list(Interface.read_csv("data/saved_routes.csv"))
else:
    # Ask user if they want to create new routes
    print("There are no saved routes for the trucks to use. Do you want to create new routes?")
    create_new_routes = input("Enter 'y' or 'n' [n]: ").strip().lower()
    if create_new_routes == "y":
        # Ask user for parameters to create routes
        route_list = list(Interface.create_routes(location_list, wgu).get_routes())
    else:
        print("Unable to route trucks. Exiting program...")
        exit()

# Display a menu for the user
print("==========================================\n"
      "1. Print All Packages With Total Mileage\n"
      "2. Get a Single Package Status with a Time\n"
      "3. Get All Package Status with a Time\n"
      "4. Exit application\n"
      "==========================================")


# Print all route statistics
Interface.print_route_statistics(list(route_list))

# Create custom HashTable object to hold packages
pkg_table = HashTable(50)

# Read CSV package data
raw_pkgs = Interface.read_csv("data/package_info.csv")

# Convert CSV data to a list of Package objects
pkg_list = Interface.list_to_package_list(raw_pkgs)

# Add all Packages to custom HashTable; save Package IDs for later retrieval
pkg_ids = []
for pkg in pkg_list:
    pkg_ids.append(pkg.get_package_id())
    pkg_table.insert_package(pkg)

# Print all packages in HashTable in a table format
print("\nPackage Table:")
Interface.print_package_table(pkg_table.values(pkg_ids))

# Create the Trucks and Drivers
truck_list = []
driver_list = []
for i in range(1, 4):
    truck_list.append(Truck(i))
    driver_list.append(Driver(i))

# Initialize the Scheduler with the necessary information
Scheduler.initialize(
    "12:00 AM",
    "8:00 AM",
    route_list,
    pkg_table,
    Optimizer.prioritize_packages(pkg_table.values(pkg_ids), Interface.get_hub()),
    truck_list,
    driver_list,
    Interface.get_hub()
)

# Print all packages in HashTable in a table format
print("\nNew Package Table:")
Interface.print_package_table(pkg_table.values(pkg_ids))

while Scheduler.tick():
    pass
