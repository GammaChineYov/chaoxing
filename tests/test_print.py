import time
from colorama import init, Fore, Style

# 初始化 colorama
init()

def log_and_print():
    while True:
        log_message = "Logging at: " + time.strftime("%Y-%m-%d %H:%M:%S")
        print(Fore.GREEN + log_message + Style.RESET_ALL)
        time.sleep(1)

if __name__ == "__main__":
    log_and_print()
