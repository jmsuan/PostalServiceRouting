class PostalHashTable:
    def __init__(self, size):
        self._buckets = [[] for i in range(size)]

    def insert(self, key, value=None):
        key_hash = key.__hash__()
        bucket_num = key_hash % len(self._buckets)
        bucket = self._buckets[bucket_num]
        # Enumerate to index sub item (collisions) if we are modifying an existing value.
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        self._buckets[bucket_num].append((key, value))

    def lookup(self, key):
        key_hash = key.__hash__()
        bucket_num = key_hash % len(self._buckets)
        bucket = self._buckets[bucket_num]
        for item, value in bucket:
            if item == key:
                return value
        return None

    def get_buckets(self):
        return self._buckets
