from .name_rule import NameRule
from .date_rule import DateRule
from .leet_rule import LeetRule
from .separator_rule import SeparatorRule
from .special_rule import SpecialRule


RULES = {

    "NAME": NameRule,

    "DATE": DateRule,

    "LEET": LeetRule,

    "SPECIAL": SpecialRule,

    "SEPARATOR": SeparatorRule

}