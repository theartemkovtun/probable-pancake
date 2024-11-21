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
    return f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {message}"


def _build_log(media_id: str, message: str):
    return f"{media_id}: {message}"


def info(media_id: str, message: str, output: list[str]):
    log = _build_log(media_id, message)
    print(log)
    output.append(_build_output_message(log))


def warning(media_id: str, message: str, output: list[str]):
    log = _build_log(media_id, message)
    print(f"{bcolors.WARNING}{log}{bcolors.ENDC}")
    output.append(_build_output_message(log))


def error(media_id: str, message: str, output: list[str]):
    log = _build_log(media_id, message)
    print(f"{bcolors.ERROR}{log}{bcolors.ENDC}")
    output.append(_build_output_message(log))


def success(media_id: str, message: str, output: list[str]):
    log = _build_log(media_id, message)
    print(f"{bcolors.OKGREEN}{log}{bcolors.ENDC}")
    output.append(_build_output_message(log))