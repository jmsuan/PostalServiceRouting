# Student ID: 001264312

from hash_table import HashTable
from interface import Interface
from location import Location
from scheduler import Scheduler
from optimizer import Optimizer
from truck import Truck
from driver import Driver

# Import location info (creates Location objects and sets distances)
raw_locations = Interface.read_csv("data/distance_info.csv")
location_list = Interface.list_to_location_list(raw_locations)

# Set the HUB for this instance
wgu = Location.get_location_by_name("Western Governors University")
Interface.set_hub(wgu)

# Check if there are saved routes
try:
    Interface.read_csv("data/saved_routes.csv")
    saved_routes_exist = True
except FileNotFoundError:
    saved_routes_exist = False

# Create the list of routes (list of lists of Location objects)
if saved_routes_exist:
    # Ask user if they want to use saved routes or create new ones
    print("There is a saved set of routes that have already been created. Using saved routes...")
    raw_routes = Interface.read_csv("data/saved_routes.csv")
    route_list = Interface.list_to_route_list(raw_routes)
else:
    # Ask user if they want to create new routes
    print("There are no saved routes for the trucks to use. Do you want to create new routes?")
    create_new_routes = input("Enter 'y' or 'n': ").strip().lower()
    if create_new_routes == "y":
        # Ask user for parameters to create routes
        raw_route_list = Interface.create_routes(location_list, wgu)
        route_list = raw_route_list.get_routes()
    else:
        print("Unable to route trucks. Exiting program...")
        exit()

# Import package info (creates Package objects and saves to list)
raw_pkgs = Interface.read_csv("data/package_info.csv")
pkg_list = Interface.list_to_package_list(raw_pkgs)

# Create custom HashTable object to hold packages
pkg_table = HashTable(50)

# Add all Packages to custom HashTable; save Package IDs for later retrieval
pkg_ids = []
for pkg in pkg_list:
    pkg_ids.append(pkg.get_package_id())
    pkg_table.insert_package(pkg)

# Create the Trucks and Drivers
truck_list = []
driver_list = []
# 3 Trucks
for i in range(1, 4):
    truck_list.append(Truck(i))
# 2 Drivers
for i in range(1, 3):
    driver_list.append(Driver(i))

# Set the initial time for the Scheduler
initial_time = "12:00 AM"

# Initialize the Scheduler with the necessary information
Scheduler.initialize(
    initial_time,
    "8:00 AM",
    route_list,
    pkg_table,
    Optimizer.prioritize_packages(pkg_table.values(pkg_ids), Interface.get_hub()),
    truck_list,
    driver_list,
    Interface.get_hub()
)

# Main menu for the application
menu = ("\n=========================================================\n"
        "1. Print All Packages With Total Mileage\n"
        "2. Get a Single Package Status With a Time\n"
        "3. Get All Package Statuses With a Time\n"
        "4. Generate New Routes for the Trucks (Genetic Algorithm)\n"
        "5. Print the current route list statistics\n"
        "6. Exit Application\n"
        "=========================================================")


# Define updates to make to the packages during the day
def update_packages(time: str):
    # Update Package statuses based on the current time
    if time == "10:20 AM":
        correct_location = Location.get_location_by_address("410 S State St", "84111")
        pkg_table.lookup_package(9).set_destination(correct_location)
        pkg_table.lookup_package(9).update_status("IN HUB")
        pkg_table.lookup_package(9).make_valid()


# Main loop for the application
u_input = input(menu + "\nEnter a number from the menu: ").strip()
while u_input != "6":

    # 1. Print All Packages With Total Mileage
    if u_input == "1":
        # Run the Scheduler until the end of the day
        while Scheduler.get_current_time() != "11:59 PM" and Scheduler.tick():
            update_packages(Scheduler.get_current_time())

        # Get time for end of day
        time_end = Scheduler.get_current_time()

        # Get total mileage for all trucks
        total_mileage = 0
        for truck in truck_list:
            total_mileage += truck.get_mileage()

        # Print all packages with total mileage
        print()
        Interface.print_package_table(
            pkg_table.values(pkg_ids),
            f"Routing Finished - Day ended at {time_end}",
            f"Total Mileage: {total_mileage:.2f} miles"
        )
        
    # 2. Get a Single Package Status With a Time
    elif u_input == "2":
        # Reset the day to have accurate info for the time entered
        Scheduler.reset_day()

        # Ask user for the desired time
        time_str = input("Enter a time in the format 'HH:MM AM/PM': ").strip()
        desired_time = Scheduler.validate_time(time_str)
        # Validate the time entered
        if not desired_time:
            print("Invalid time entered. Try again.")
            continue
        time_str = desired_time.strftime("%I:%M %p")  # Format the time for comparison

        # Run the Scheduler until the desired time is reached OR the end of the day
        while Scheduler.get_current_time() != time_str and Scheduler.tick():
            update_packages(Scheduler.get_current_time())

        # Get time after ticking to the desired time (redundant, but good to check)
        time_end = Scheduler.get_current_time()

        # Ask user for a package ID to get the status of
        pkg_id = int(input("Enter a package ID to get the status of: ").strip())
        # Validate the package ID entered
        if pkg_id not in pkg_ids:
            print("Invalid package ID entered. Try again.\n")
            continue

        # Print all packages with total mileage
        print()
        Interface.print_package_table(
            pkg_table.values([pkg_id]),
            f"Routing Status - Current Time: {time_end}",
        )
    
    # 3. Get All Package Statuses With a Time
    elif u_input == "3":
        # Reset the day to have accurate info for the time entered
        Scheduler.reset_day()

        # Ask user for the desired time
        time_str = input("Enter a time in the format 'HH:MM AM/PM': ").strip()
        desired_time = Scheduler.validate_time(time_str)
        # Validate the time entered
        if not desired_time:
            print("Invalid time entered. Try again.")
            continue
        time_str = desired_time.strftime("%I:%M %p")  # Format the time for comparison

        # Run the Scheduler until the desired time is reached OR the end of the day
        while Scheduler.get_current_time() != time_str and Scheduler.tick():
            update_packages(Scheduler.get_current_time())

        # Get time after ticking to the desired time (redundant, but good to check)
        time_end = Scheduler.get_current_time()

        # Get total mileage for all trucks
        total_mileage = 0
        for truck in truck_list:
            total_mileage += truck.get_mileage()

        # Print all packages with total mileage
        print()
        Interface.print_package_table(
            pkg_table.values(pkg_ids),
            f"Routing Status - Current Time: {time_end}",
            f"Total Mileage: {total_mileage:.2f} miles"
        )
        
    # 4. Generate New Routes for the Trucks (Genetic Algorithm)
    elif u_input == "4":
        # Generate new routes for the trucks
        print("\nAre you sure you want to create new routes? This will overwrite the saved routes.\n"
              "(Creating routes might take a large amount of memory or compute power depending on the what parameters "
              "you enter for the genetic algorithm!)")
        confirm = input("\nEnter 'y' or 'n': ").strip().lower()
        if confirm == "y":
            # Ask user for parameters to create routes
            route_list = list(Interface.create_routes(location_list, wgu).get_routes())
        else:
            print("\nUsing saved routes...\n")
            route_list = Interface.list_to_route_list(Interface.read_csv("data/saved_routes.csv"))
            
    # 5. Print the current route list statistics
    elif u_input == "5":
        # Print all route statistics
        Interface.print_route_statistics(route_list)
        
    # Invalid input
    else:
        print("Invalid input. Please enter a number from the menu.")
        
    # Ask user for another input
    u_input = input(menu + "\nEnter a number from the menu: ").strip()

print("\nExiting application...")
