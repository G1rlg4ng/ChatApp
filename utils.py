from string import ascii_letters
import random

def generate_room_code(length: int, existing_codes: list[str]) -> str:
    while True:
        code_chars = [random.choice(ascii_letters) for _ in range(length)] # Create a list of code characters
        code = ''.join(code_chars) # convert the list of random characters (code_chars) into a single string by joining them together
        if code not in existing_codes:
            return code