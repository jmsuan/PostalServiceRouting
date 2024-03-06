class PostalHashTable:
    def __init__(self, size):
        self._buckets = [[] for i in range(size)]

    # TODO: Support key-value pairs
    def insert(self, key):
        key_hash = key.__hash__()
        bucket_num = key_hash % len(self._buckets)
        self._buckets[bucket_num].append(key)

    def lookup(self, key):
        key_hash = key.__hash__()
        bucket_num = key_hash % len(self._buckets)
        bucket = self._buckets[bucket_num]
        if len(bucket) > 1:
            for item in bucket:
                if item is key:
                    return item
        elif len(bucket) == 0:
            return None
        else:
            return bucket[0]

    def get_buckets(self):
        return self._buckets
