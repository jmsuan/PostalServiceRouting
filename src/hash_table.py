from package import Package


class HashTable:
    def __init__(self, size: int):
        self._buckets = [[] for _ in range(size)]

    def insert(self, key, value=None):
        key_hash = key.__hash__()
        bucket_num = key_hash % len(self._buckets)
        bucket = self._buckets[bucket_num]
        # Enumerate to index sub item (collision) if we are modifying an existing value.
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))

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

    def all_values(self) -> list:
        """Returns a collision-separated list of all present values in the HashTable."""
        all_items = []
        for bucket in self._buckets:
            if len(bucket) >= 1:
                for item in bucket:
                    all_items.append(item[1])
        return all_items

    def values(self, keys: list) -> list:
        """Returns a list of values that were found from each key given."""
        values = []
        for key in keys:
            values.append(self.lookup(key))
        return values
