import sys

if __name__ == "__main__":
    append_fname = sys.argv[1]
    source_fname = sys.argv[2]

    append_file = open(append_fname, "a", encoding="utf-8")
    source_file = open(source_fname, "r", encoding="utf-8")

    for line in source_file:
        append_file.write(line)

    append_file.close()
    source_file.close()
