import datetime


class HashTable:
    def __init__(self, size: int):
        self._buckets = [[]] * size

    def insert(self, key, value=None):
        key_hash = key.__hash__()
        bucket_num = key_hash % len(self._buckets)
        bucket = self._buckets[bucket_num]
        # Enumerate to index sub item (collision) if we are modifying an existing value.
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        self._buckets[bucket_num].append((key, value))

    # TODO: Convert to class logic; include package formatting info in class definition.
    def insert_package(
            self,
            package_id: int,
            address: str,
            deadline: datetime,
            city: str,
            zip_code: str,
            weight: float,
            special_code: tuple[str, ...] = None,
            status: str = "IN HUB"
    ) -> None:
        """
        Inserts a package with its associated details into the hash table.

        Args:
            package_id (int): The unique identifier of the package.
            address (str): The delivery address of the package.
            deadline (datetime): The delivery deadline for the package.
            city (str): The city associated with the delivery address.
            zip_code (str): The zip code associated with the delivery address.
            weight (float): The weight of the package in kilograms.
            special_code (tuple[str, ...], optional): A tuple of special delivery
                requirements or conditions, potentially containing multiple codes.
                Available codes:
                    - TRUCK[{list of truck IDs}]: specifies required truck numbers.
                    - INVALID: Indicates invalid package information (must remain "IN HUB" until package is updated).
                    - BUNDLE[{list of package IDs}]: Specifies joint delivery with other packages.
                    - DELAY[{datetime}]: Specifies a delayed arrival time for the package.
            status (str, optional): The current status of the package. Defaults to "IN HUB".
        """
        self.insert(package_id, (package_id, address, deadline, city, zip_code, weight, special_code, status))

    def lookup(self, key):
        key_hash = key.__hash__()
        bucket_num = key_hash % len(self._buckets)
        bucket = self._buckets[bucket_num]
        for item, value in bucket:
            if item == key:
                return value
        return None

    def lookup_package(self, package_id):
        """
        Returns the tuple with all the parcel's info.
        """
        return self.lookup(package_id)
