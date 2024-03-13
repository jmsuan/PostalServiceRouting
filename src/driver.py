class Driver:
    def __init__(self, driver_id: int, driver_name: str):
        self._id = driver_id
        self._name = driver_name

    def get_id(self):
        return self._id

    def get_name(self):
        return self._name
