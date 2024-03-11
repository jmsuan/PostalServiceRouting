# Student ID: 001264312

from hash_table import HashTable
from pgm_interface import PgmInterface

# Create custom HashTable
package_table = HashTable(50)

# Read CSV package data
package_data = PgmInterface.read_csv("data/package_info.csv")

# Convert CSV data to a list of Package objects
raw_package_list = PgmInterface.list_to_package_list(package_data)

# Add all Packages to custom HashTable
for package in raw_package_list:
    package_table.insert_package(package)

# Print all packages in HashTable in a table format
package_list = package_table.all_values()
PgmInterface.print_all_packages(package_list)
