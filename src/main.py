# Student ID: 001264312
import datetime

from hash_table import HashTable
from package import Package
from program_interface import ProgramInterface

package_table = HashTable(50)

# Sample packages
package = Package(123, "100 Main St", datetime.time(15, 3), "Anytown", "12345", 5.2)
package2 = Package(234, "100 Main St", datetime.time(15, 3), "Anytown", "12345", 5.2)
package_table.insert_package(package)
package_table.insert_package(package2)
ProgramInterface.print_all_packages(package_table.all_values())
