import sys

def in_venv():
    return sys.prefix != sys.base_prefix

def main():
    print(in_venv())

if __name__ == "__main__":
    main()