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
            model_file = model.__module__.replace(".", "/") + ".py"
            if os.path.exists(model_file):
                spec = importlib.util.spec_from_file_location(
                    model.__module__, model_file
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                for name, obj in vars(module).items():
                    if isinstance(obj, type) and issubclass(obj, models.TextChoices):
                        enums[name] = obj
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
