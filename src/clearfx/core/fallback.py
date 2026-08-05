import sys
import os

def fallback_clear() -> None:
    """
    Fallback clear method that clears the terminal directly without any dependencies.
    Used when animations fail or are disabled.
    """
    if os.name == 'nt':
        os.system('cls')
    else:
        sys.stdout.write('\033[H\033[2J\033[3J')
        sys.stdout.flush()
