

class BaseFactory:
    """
    Base class for factory
    """

    def __init__(self, repository, schema):
        self.repository = repository
        self.schema = schema

    def exclude_schema(self, exclude: list):
        """
        Exclude fields from schema
        """
        new_schema = self.schema(exclude=exclude)

        return new_schema
