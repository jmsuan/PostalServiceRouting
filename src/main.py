# Student ID: 001264312

from hash_table import HashTable
from interface import Interface
from location import Location

# Print WIP Notes TODO: Remove WIP notes
print("WIP NOTES:\n"
      "Ideally, the program flows as follows:\n"
      "- Import locations and their distances from each other\n"
      "- Import packages and associate with locations\n"
      "- (Calculate priority of packages?)\n"
      "        Assign package priorities based on multiple scoring factors:\n"
      "        distance to hub\n"
      "        avg distance from other destinations(?)\n"
      "        special priority\n"
      "        deadline\n"
      "        HOW MANY other high priority packages are nearby that facilitate ideal “elevator” routes. "
      "(Second-pass priority?)\n"
      "        Could calc potential facilitators based off if the dist to hub is greater than itself, and if the "
      "distance is under some value\n"
      "\n"
      "- Add packages to trucks based on (package priority? use time variable to track current time?)\n"
      "- Packages should be updated by truck action methods (load, drive, deliver(maybe a Driver method?))\n")

# Import location info (creates Location objects and sets distances)
raw_locations = Interface.read_csv("data/distance_info.csv")
Interface.list_to_location_list(raw_locations)

# Set the HUB for this instance
wgu = Location.get_location_by_name("Western Governors University")
Interface.set_hub(wgu)

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
print("Package Table:")
Interface.print_package_table(pkg_table.values(pkg_ids))
