from django.apps import apps
from django.db import models
from typing import Dict, Optional
import importlib.util
import os


TYPING_DEFINITIONS = [
    "export type EnumTextChoice = {label: string, value: string}",
    "export type EnumTextChoices = Record<string, EnumTextChoice>",
]


def load_django_enums():
    enums = {}

    for app_config in apps.get_app_configs():
        for model in app_config.get_models():
            for field in model._meta.fields:
                if (
                    isinstance(field, models.Field)
                    and field.choices
                    and isinstance(field.choices, models.TextChoices)
                ):
                    enums[field.name] = field.choices
    return enums


def enum_choice_to_interface(choice):
    label = getattr(choice, "label", choice.value.replace("_", " ").capitalize())
    return ",\n".join(
        "    " + line
        for line in [
            f'label: "{label}"',
            f'value: "{choice.value}"',
        ]
    )


def enum_to_interface(name, enum):
    return (
        "export const Enum"
        + name
        + ": EnumTextChoices = "
        + " {\n"
        + ",\n".join(
            "  "
            + "'"
            + item.value
            + "'"
            + ": {\n"
            + enum_choice_to_interface(item)
            + "\n  }"
            for item in enum
        )
        + "\n}"
    )


def generate_enum_typing_file(
    enums: Optional[Dict[str, type[models.TextChoices]]] = None,
    output_file: str = "hotbot/views/src/enums.ts",
):
    if output_file is None:
        return

    if enums is None:
        enums = load_django_enums()

    definitions = TYPING_DEFINITIONS + [
        enum_to_interface(name, enum) for name, enum in enums.items()
    ]

    with open(output_file, "w") as f:
        f.write("\n\n".join(definitions))
