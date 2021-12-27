from typing import Union, Optional

PROTOCOL_REQUIREMENT = "\r\n"

def encode_number(number: Union[str, int]):
    return ":{number}{PROTOCOL_REQUIREMENT}"

def encode_string(string: Optional[str]):
    if string is None:
        return "$-1{PROTOCOL_REQUIREMENT}"
    return f"${len(string)}{PROTOCOL_REQUIREMENT}{string}{PROTOCOL_REQUIREMENT}"

def encode_list(initial_list: list):
    encoded = f"*{str(len(initial_list))}{PROTOCOL_REQUIREMENT}{''.join(initial_list)}{PROTOCOL_REQUIREMENT}"
    return encoded

def format_command_string(command: str, noarg: bool = True):
    if noarg:
        return (f"{command}{PROTOCOL_REQUIREMENT}")
    return f"${len(command)}{PROTOCOL_REQUIREMENT}{command}{PROTOCOL_REQUIREMENT}"