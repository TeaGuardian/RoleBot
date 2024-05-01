import os


def count_lines(ptf: str) -> int:
    with open(ptf, 'rb') as fi:
        return len(fi.readlines())


def find_py(direc=os.getcwd(), rf=".py", dcl=["venv", "ipynb_checkpoints"]):
    total = 0
    for root, dirs, files in os.walk(direc):
        for file in files:
            if file.endswith(rf) and all(map(lambda g: g not in root, dcl)):
                fi = os.path.join(root, file)
                lines = count_lines(fi)
                print(f"file {fi}: {lines} lines")
                total += lines
    return total


if __name__ == "__main__":
    print("total:", find_py())
