import sys


def main():
    # begin repl with unprivileged user tag
    sys.stdout.write("$ ")
    # read user input
    cmd = input()
    print(f"{cmd}: command not found")
    

if __name__ == "__main__":
    main()
