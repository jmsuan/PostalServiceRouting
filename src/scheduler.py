from package import Package


class Scheduler:
    @staticmethod
    def prioritize_packages(package_list: list[Package]) -> list[int]:
        """
        Assign package priorities based on multiple scoring factors:
            - distance to hub(?)
            - avg distance from other destinations(?)
            - special priority!
            - deadline!
            - HOW MANY other high priority packages are nearby that facilitate ideal “elevator” routes.
                (Second-pass priority?)
            - Could calc potential facilitators based off if the dist to hub is greater than itself, and if the
                distance is under some value

        :param package_list:
        :return:
        """
        pass  # TODO: Implement
