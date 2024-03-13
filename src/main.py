# Student ID: 001264312

from hash_table import HashTable
from pgm_interface import PgmInterface

# Create custom HashTable
package_table = HashTable(40)

# Read CSV package data
raw_pkgs = PgmInterface.read_csv("../data/package_info.csv")

# Convert CSV data to a list of Package objects
pkg_list = PgmInterface.list_to_package_list(raw_pkgs)

# Add all Packages to custom HashTable
for pkg in pkg_list:
    package_table.insert_package(pkg)

# Print all packages in HashTable in a table format
PgmInterface.print_package_table(package_table.all_values())
