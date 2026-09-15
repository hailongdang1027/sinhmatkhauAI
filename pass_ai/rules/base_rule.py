from abc import ABC, abstractmethod

class BaseRule(ABC):
    """
    Lớp cơ sở cho mọi Rule.
    """

    rule_id = ""
    display_name = ""

    @abstractmethod
    def execute(self, passwords, profile):
        """
        passwords : set[str]
        profile   : dict

        return set[str]
        """
        pass