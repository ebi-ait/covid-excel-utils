from datetime import date
from typing import List


def clean_entity_name(name: str) -> str:
    # Entities may include a postfix which can be discarded
    return clean_name(name.partition('-')[0])


def clean_name(name: str) -> str:
    # Object and Attribute name are lower case with underscores
    # Parentheses are removed
    return name.strip().lower()\
        .replace(' ', '_')\
        .replace('/', '_')\
        .replace('(', '')\
        .replace(')', '')


def clean_key(key: str) -> str:
    # Keys are CamelCase and singleton
    return key.replace(' ', '').rstrip('s')


def clean_formula_list(formula: str) -> List[str]:
    # Embedded formula lists contain redundant outer quotes
    return clean_validation_list(formula.strip('"').split(','))


def clean_validation_list(validation_list: List[str]) -> List[str]:
    new_list = []
    for value in validation_list:
        new_list.append(clean_validation(value))
    return new_list


def clean_validation(value: str) -> str:
    # Validation is case-insensitive
    return value.lower()


def entity_has_attribute(object_data: dict, attribute: str) -> bool:
    return attribute in object_data and is_value_populated(object_data[attribute].strip())


def is_value_populated(value: str) -> bool:
    stripped_value = value.lower().replace(' ', '')
    return stripped_value


def is_valid_date(value: str) -> bool:
    try:
        date.fromisoformat(value)
        return True
    except (TypeError, ValueError):
        return False
