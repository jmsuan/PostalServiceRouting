import csv
from datetime import datetime

from package import Package


class PgmInterface:
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
            special_code = PgmInterface.__special_notes_to_code(package_info[7])

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
            converted_package = PgmInterface.__list_to_package(raw_package)
            package_list.append(converted_package)

        return package_list

    @staticmethod
    def read_csv(filepath: str) -> list[list]:
        file_rows = []
        with open(filepath, newline='') as csvfile:
            file_reader = csv.reader(csvfile)
            for row in file_reader:
                file_rows.append(row)
            return file_rows

    @staticmethod
    def __table_index_max_length(table: list[list], index: int) -> int:
        """Loops through all items in a column and returns the character length of the longest item."""
        max_length = -1
        for row in table:
            ix_item_length = len(str(row[index]))  # Character length
            if ix_item_length > max_length:
                max_length = ix_item_length
        return max_length

    @staticmethod
    def print_all_packages(table: list[list]) -> None:
        """

        :param table: A list with lists inside of it. This method expects 8 columns.
        :return: This function does not return a value.
        """
        # Ensure that the expected column number is as expected
        num_columns = 9
        for row in table:
            if len(row) != num_columns:
                raise ValueError(f"Error in row length! Expecting {num_columns} columns and got {len(row)}")

        # Prepend table header strings so that the length is accounted for in formatting (not just data)
        headers = [(
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
        table = headers + table

        # Store maximum character length of each column (index) in a list
        len_columns = []
        for i in range(len(table[0])):
            len_columns.append(PgmInterface.__table_index_max_length(table, i))

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
                print(f" {row[i]} ", end="")
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
