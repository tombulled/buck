import collections


class BaseType(collections.UserString):
    def __init__(self, value: str):
        error_message = self.validate(value)

        if error_message is not None:
            class_name = self.__class__.__name__
            sep = " - " if error_message else ""

            raise ValueError(f"Invalid {class_name}{sep}{error_message}")

        super().__init__(value)

    @staticmethod
    def validate(value: str):
        return
