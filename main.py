import rarfile
import itertools
import string

MIN_PASSWORD_LENGTH = 1
MAX_PASSWORD_LENGTH = 16


def intro_message():
    print("===============================")
    print("===============================")
    print("           RAR-FORCE           ")
    print("RAR Password Brute-force Script")
    print("===============================")
    print("===============================")
    print("This script attempts to brute-force the password of a locked RAR file.")
    print(
        f"It supports options for lowercase, uppercase, numbers, symbols and a range of {MIN_PASSWORD_LENGTH}-{MAX_PASSWORD_LENGTH} characters."
    )
    print(
        "With longer passwords and more characters to check, this will take more time."
    )
    print()


def setup():
    file_path = input("> Enter the absolute path of the RAR file: ").strip()
    min_length = int(MIN_PASSWORD_LENGTH)
    max_length = int(MAX_PASSWORD_LENGTH)
    lowercase = uppercase = numbers = symbols = "y"

    try:
        with rarfile.RarFile(file_path, "r") as rf:
            if not rf.needs_password():
                print("The provided RAR file is not password-protected.")
                return None

    except rarfile.BadRarFile:
        print("Invalid RAR file. Please check the file path.")
        return None
    except FileNotFoundError:
        print("File not found. Please check the file path.")
        return None
    except Exception as e:
        print(f"An error occurred while opening the RAR file: {e}")
        return None

    while True:
        lowercase = get_yes_no_input("> Include lowercase letters? (y/n): ")
        uppercase = get_yes_no_input("> Include uppercase letters? (y/n): ")
        numbers = get_yes_no_input("> Include numbers? (y/n): ")
        symbols = get_yes_no_input("> Include symbols? (y/n): ")

        if any([lowercase, uppercase, numbers, symbols]):
            break
        else:
            print("At least one character set must be included. Please try again.")

    while True:
        min_length = get_digit_input(
            f"> Enter minimum password length ({MIN_PASSWORD_LENGTH}-{MAX_PASSWORD_LENGTH}): "
        )

        if min_length >= MAX_PASSWORD_LENGTH:
            print(f"Maximum length is set to {MAX_PASSWORD_LENGTH}")
        else:
            max_length = get_digit_input(
                f"> Enter maximum password length ({min_length}-{MAX_PASSWORD_LENGTH}): "
            )

        if MIN_PASSWORD_LENGTH <= min_length <= max_length <= MAX_PASSWORD_LENGTH:
            break
        else:
            print("Invalid password length. Please try again.")

    return {
        "file_path": file_path,
        "character_sets": {
            "lowercase": lowercase,
            "uppercase": uppercase,
            "numbers": numbers,
            "symbols": symbols,
        },
        "min_length": min_length,
        "max_length": max_length,
    }


def generate_passwords(character_sets, min_length, max_length):
    chars = {
        "lowercase": string.ascii_lowercase if character_sets["lowercase"] else "",
        "uppercase": string.ascii_uppercase if character_sets["uppercase"] else "",
        "numbers": string.digits if character_sets["numbers"] else "",
        "symbols": string.punctuation if character_sets["symbols"] else "",
    }

    all_characters = "".join(chars.values())
    for length in range(min_length, max_length + 1):
        for password in itertools.product(all_characters, repeat=length):
            yield "".join(password)


def brute_force(file_path, character_sets, min_length, max_length):
    print("===============================")
    print("Starting brute-force...")
    print("===============================")
    with rarfile.RarFile(file_path, "r") as rf:
        for character_set in character_sets:
            if character_sets[character_set]:
                print(f"Checking {character_set} characters...")
                passwords = generate_passwords(character_sets, min_length, max_length)
                for password in passwords:
                    try:
                        rf.extractall(
                            pwd=password.encode("utf-8"),
                        )
                        print(f"SUCCESS! The password was found to be: {password}")
                        rf.close()
                        return
                    except rarfile.RarWrongPassword:
                        pass
                    except Exception as e:
                        print(f"An error occurred while trying to open the file: {e}")
                        rf.close()
                        return
                print(f"Completed check for {character_set} characters.")
    print("Brute-force unsuccessful. Password not found.")


def get_yes_no_input(prompt):
    while True:
        user_input = input(prompt).strip().lower()
        if user_input == "y" or user_input == "n":
            return user_input == "y"
        else:
            print("Invalid input. Please enter 'y' or 'n'.")


def get_digit_input(prompt):
    while True:
        user_input = input(prompt).strip()
        if user_input.isdigit() and (
            MIN_PASSWORD_LENGTH <= int(user_input) <= MAX_PASSWORD_LENGTH
        ):
            return int(user_input)
        else:
            print("Invalid input. Please enter a number in range.")


def main():
    intro_message()
    setup_params = setup()
    if setup_params:
        brute_force(
            setup_params["file_path"],
            setup_params["character_sets"],
            setup_params["min_length"],
            setup_params["max_length"],
        )
    print("===============================")


if __name__ == "__main__":
    main()
