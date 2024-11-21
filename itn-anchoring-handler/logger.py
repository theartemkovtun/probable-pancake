from datetime import datetime

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def _build_output_message(message: str):
    return f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {message}\n"


def info(message: str, output: list[str]):
    print(message)
    output.append(_build_output_message(message))


def warning(message: str, output: list[str]):
    print(f"{bcolors.WARNING}{message}{bcolors.ENDC}")
    output.append(_build_output_message(message))


def error(message: str, output: list[str]):
    print(f"{bcolors.ERROR}{message}{bcolors.ENDC}")
    output.append(_build_output_message(message))


def success(message: str, output: list[str]):
    print(f"{bcolors.OKGREEN}{message}{bcolors.ENDC}")
    output.append(_build_output_message(message))