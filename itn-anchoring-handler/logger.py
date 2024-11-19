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


def info(message: str):
    print(message)


def warning(message: str):
    print(f"{bcolors.WARNING}{message}{bcolors.ENDC}")


def error(message: str):
    print(f"{bcolors.ERROR}{message}{bcolors.ENDC}")


def success(message: str):
    print(f"{bcolors.OKGREEN}{message}{bcolors.ENDC}")