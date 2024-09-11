from hotbot.utils.enums import generate_enum_typing_file


def run():
    generate_enum_typing_file(output_file="hotbot/views/src/enums.ts")
