# Student ID: 001264312

from hash_table import HashTable
from interface import Interface

# Create custom HashTable
package_table = HashTable(50)

# Read CSV package data
raw_pkgs = Interface.read_csv("../data/package_info.csv")

# Convert CSV data to a list of Package objects
pkg_list = Interface.list_to_package_list(raw_pkgs)

# Add all Packages to custom HashTable
for pkg in pkg_list:
    package_table.insert_package(pkg)

# Print all packages in HashTable in a table format
Interface.print_package_table(package_table.all_values())

raw_distances = Interface.read_csv("../data/distance_info.csv")

Interface.fancy_table(raw_distances)
