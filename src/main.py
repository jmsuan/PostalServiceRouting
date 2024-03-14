# Student ID: 001264312
"""
WIP NOTES:
Ideally, the program flows as follows:
- Import locations and their distances from each other
- Import packages and associate with locations
- (Calculate priority of packages?)
- Add packages to trucks based on (package priority? use time variable to track current time?)
- Packages should be updated by truck action methods (load, drive, deliver(maybe a Driver method?))
"""

from hash_table import HashTable
from interface import Interface

# Import location info
raw_locations = Interface.read_csv("../data/distance_info.csv")
location_list = Interface.list_to_location_list(raw_locations)

''' (rest of program)
# Create custom HashTable object
pkg_table = HashTable(50)

# Read CSV package data
raw_pkgs = Interface.read_csv("../data/package_info.csv")

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
'''
