import datetime
from package import Package


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

    def insert_package(self, pkg: Package) -> None:
        """Inserts a package with its associated details into the hash table."""
        self.insert(pkg.get_package_id(), pkg)

    def lookup(self, key):
        key_hash = key.__hash__()
        bucket_num = key_hash % len(self._buckets)
        bucket = self._buckets[bucket_num]
        for item, value in bucket:
            if item == key:
                return value
        return None

    def lookup_package(self, package_id):
        """Returns the tuple with all the parcel's info."""
        return self.lookup(package_id)
