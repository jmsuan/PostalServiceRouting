import csv
from datetime import datetime
from package import Package
from location import Location


class Interface:
    _hub_location = None

    @staticmethod
    def set_hub(hub_location: Location):
        Interface._hub_location = hub_location

    @staticmethod
    def get_hub() -> Location:
        return Interface._hub_location

    @staticmethod
    def read_csv(filepath: str) -> list[list]:
        file_rows = []
        with open(filepath, newline='') as csvfile:
            file_reader = csv.reader(csvfile)
            for row in file_reader:
                file_rows.append(row)
            return file_rows

    @staticmethod
    def list_to_location_list(location_data: list[list[str]]) -> list[Location]:
        """
        Converts a collection of raw location data into a list of Location objects. Also adds all location distances
        from each other.

        :param location_data: Raw location data with multiple lists containing
            all required attributes of the Location class.
        :return: A list of Packages that were created from the raw data.
        """
        location_names = []
        location_addresses = []
        location_zips = []

        # Parse location info
        for row in location_data[1:]:
            # Get name and address from first column
            try:
                name, address, _ = str.split(row[0], "\n", 2)
            except ValueError:  # The csv table is inconsistent. Sometimes listing city/state, and sometimes not.
                name, address = str.split(row[0], "\n", 1)
            location_names.append(name.strip())
            location_addresses.append(
                address.strip().replace(",", ""))  # Account for commas that might be added as part of the address

            # Get zip code from second column (except for on the HUB row)
            if row[1].strip() == "HUB":
                location_zips.append(row[0].strip()[-5:])
            else:
                location_zips.append(row[1].strip()[-6:-1])

        # Ensure everything is here
        if len(location_names) != len(location_addresses) or len(location_addresses) != len(location_zips):
            raise ValueError(f"Couldn't find names, addresses, or zips for all locations! There are:\n"
                             f"- {len(location_names)} Location names imported.\n"
                             f"- {len(location_addresses)} Location addresses imported.\n"
                             f"- {len(location_zips)} Location zip codes imported.")

        # Create Location objects and add to list
        location_objects = []
        num_columns = len(location_names)
        for i in range(num_columns):
            location_objects.append(Location(
                location_names[i],
                location_addresses[i],
                location_zips[i]
            ))

        # Add distances from each other

        return location_objects

    @staticmethod
    def list_to_package_list(package_data: list[list[str]]) -> list[Package]:
        """
        Converts a collection of raw package data into a list of Package objects.

        :param package_data: Raw package data with multiple lists containing
            all required attributes of the Package class.
        :return: A list of Packages that were created from the raw data.
        """
        # Remove header row if present
        if package_data[0] == ["PackageID", "Address", "City", "State", "Zip",
                               "DeliveryDeadline", "WeightKILO", "SpecialNotes"]:
            package_data = package_data[1:]

        # Individually convert each row to a package and add to new list
        package_list = []
        for raw_package in package_data:
            converted_package = Interface.__list_to_package(raw_package)
            package_list.append(converted_package)

        return package_list

    @staticmethod
    def print_package_table(table: list[list]) -> None:
        """
        Print the given package table in a human-readable format.

        :param table: A list with lists inside of it. Expects values in the order of
            "Pkg ID:",
            "Address:",
            "City:",
            "State:",
            "Zip Code:",
            "Deadline:",
            "Weight:",
            "Special Code:",
            "Status:"
        :return: This function does not return a value.
        """
        header = [(
            "Pkg ID:",
            "Address:",
            "City:",
            "State:",
            "Zip Code:",
            "Deadline:",
            "Weight:",
            "Special Code:",
            "Status:"
        )]

        Interface.fancy_table(table, header)

    @staticmethod
    def fancy_table(table: list[list], header: list[tuple[any, ...]] = None) -> None:
        """
        Print a human-readable table from the given values.

        :param table: A list with lists inside of it.
        :param header: The title of each column in order.
        :return: This function does not return a value.
        """
        if header is None:
            header = [table[0]]
        else:
            # Prepend table header strings so that the length is accounted for in formatting (not just data)
            table = header + table

        # Ensure that the column number is as expected
        num_columns = len(header[0])
        row_count = -1
        for row in table:
            row_count += 1
            if len(row) != num_columns:
                raise ValueError(f"Error in row length! Expecting {num_columns} "
                                 f"columns and got {len(row)} on row {row_count}.")

        # Store maximum character length of each column (index) in a list
        len_columns = []
        for i in range(num_columns):
            len_columns.append(Interface.__table_index_max_length(table, i))

        # Format top border with proper lengths
        print("┌─", end="")
        for i in range(num_columns):
            for _ in range(len_columns[i]):  # Range is character length of each column
                print("─", end="")
            if i == num_columns - 1:
                print("─┐")
                continue
            print("─┬─", end="")

        # Print data rows (including header)
        for row in table:
            print("│", end="")
            for i in range(num_columns):
                print(f" {str(row[i]).replace("\n", " ")} ", end="")
                spaces_to_add = len_columns[i] - len(str(row[i]))
                for _ in range(spaces_to_add):
                    print(" ", end="")
                print("│", end="")
            print("")

        # Print bottom border
        print("└─", end="")
        for i in range(num_columns):
            for _ in range(len_columns[i]):  # Range is character length of each column
                print("─", end="")
            if i == num_columns - 1:
                print("─┘")
                continue
            print("─┴─", end="")

    @staticmethod
    def __special_notes_to_code(special_notes: str) -> list[str]:
        """
        Converts a "Special Notes" string from the package_info data imported into a format this program expects and
        can work with. Used to create the "special code" when instantiating a Package object.

        :param special_notes: A string-based description of a special delivery requirement for a Package.
        :return: A tuple with strings that describe the delivery requirements for a Package.
        """
        codes = []

        truck_note = "Can only be on truck "
        if truck_note in special_notes:
            # Get the index of the number that comes after truck_note
            num_ix = special_notes.find(truck_note) + len(truck_note)
            str_with_trucks = special_notes[num_ix:]

            # Split the string by spaces or commas
            potential_truck_nums = str_with_trucks.replace(",", " ").split()

            # Filter out any non-digit sequences
            valid_truck_nums = []
            for seq in potential_truck_nums:
                if seq.isdigit():
                    valid_truck_nums.append(int(seq))
                else:
                    break  # Maybe the beginning of a separate requirement in "Special Notes"

            if valid_truck_nums:
                # Add the numbers of the specified trucks (separated by commas and no spaces).
                truck_nums = str.join(",", map(str, valid_truck_nums))
                codes.append(f"TRUCK[{truck_nums}]")
            else:
                raise ValueError("No valid truck numbers found after \"Can only be on truck \".")

        delay_note = "Delayed on flight---will not arrive to depot until "
        if delay_note in special_notes:
            # Get the index of the end of delay_note, slice string to region that follows delay_note
            time_ix = special_notes.find(delay_note) + len(delay_note)
            str_with_time = special_notes[time_ix:]  # Expected value from file is "#:## am" or "##:## pm"

            # Parse time values
            ix_delimiter = str_with_time.index(":")
            hour_str = str_with_time[:ix_delimiter]
            minute_str = str_with_time[(ix_delimiter + 1):(ix_delimiter + 3)]  # Minute str should always be length 2
            period_str = str_with_time[(ix_delimiter + 3):(ix_delimiter + 6)].strip()  # Remove extra space if present

            # Insert delay requirement
            try:
                time = datetime.strptime(f"{hour_str}:{minute_str}:00 {period_str.upper()}", "%I:%M:%S %p")
                codes.append(f"DELAY[{time.time()}]")
            except ValueError as e:
                print(f"Error parsing time in special_notes_to_code: {e}")

        invalid_note = "Wrong address listed"
        if invalid_note in special_notes:
            codes.append("INVALID")

        batch_note = "Must be delivered with "
        if batch_note in special_notes:
            # Get the index of the number that comes after batch_note
            num_ix = special_notes.find(batch_note) + len(batch_note)
            str_with_package_nums = special_notes[num_ix:]

            # Split the string by spaces or commas
            potential_package_nums = str_with_package_nums.replace(",", " ").split()

            # Filter out any non-digit sequences
            valid_package_nums = []
            for seq in potential_package_nums:
                if seq.isdigit():
                    valid_package_nums.append(int(seq))
                else:
                    break  # Maybe the beginning of a separate requirement in "Special Notes"

            if valid_package_nums:
                # Add the numbers of the specified packages (separated by commas and no spaces).
                package_nums = str.join(",", map(str, valid_package_nums))
                codes.append(f"BATCH[{package_nums}]")
            else:
                raise ValueError("No numeric package numbers found after \"Must be delivered with \".")

        if codes == [] and len(special_notes) > 0:
            raise ValueError(f"Unexpected item in \"SpecialNotes\" column. Please update "
                             f"PgmInterface.__special_notes_to_code() to accommodate: {special_notes}")

        return codes

    @staticmethod
    def __list_to_package(package_info: list[str]) -> Package:
        """
        Converts a list of strings that contain information about a single package into a Package object.

        :param package_info: A list of strings that contain all the ordered information needed to instantiate a Package.
        :return: A Package object derived from the information in the list.
        """

        package_id = int(package_info[0])
        address = package_info[1]
        city = package_info[2]
        state = package_info[3]
        zip_code = package_info[4]

        if package_info[5] == "EOD":
            deadline = datetime.strptime("11:59:59 PM", "%I:%M:%S %p")
        else:
            deadline = datetime.strptime(package_info[5], "%I:%M:%S %p")

        weight = float(package_info[6])

        if package_info[7] == "":
            special_code = ""
        else:
            special_code = Interface.__special_notes_to_code(package_info[7])

        status = "NEW"

        created_package = Package(
            package_id,
            address,
            city,
            state,
            zip_code,
            deadline,
            weight,
            special_code,
            status
        )

        return created_package

    @staticmethod
    def __table_index_max_length(table: list[list], index: int) -> int:
        """Loops through all items in a column and returns the character length of the longest item."""
        max_length = -1
        for row in table:
            ix_item_length = len(str(row[index]))  # Character length
            if ix_item_length > max_length:
                max_length = ix_item_length
        return max_length
