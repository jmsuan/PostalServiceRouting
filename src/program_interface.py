class ProgramInterface:
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
        num_columns = 8
        for row in table:
            if len(row) != num_columns:
                raise ValueError(f"Error in row length! Expecting {num_columns} columns and got {len(row)}")

        # Prepend table header strings so that the length is accounted for in formatting (not just data)
        headers = [("Pkg ID:", "Address:", "Deadline:", "City:", "Zip Code:", "Weight:", "Special Code:", "Status:")]
        table = headers + table

        # Store maximum character length of each column (index) in a list
        len_columns = []
        for i in range(len(table[0])):
            len_columns.append(ProgramInterface.__table_index_max_length(table, i))

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
