import sys

if __name__ == "__main__":
    input_fname = sys.argv[1]
    output_fname = sys.argv[2]

    input_file = open(input_fname, "r", encoding="utf-8")
    output_file = open(output_fname, "w", encoding="utf-8")

    seen = set()

    for line in input_file:
        named_node = line.split("->")[0]
        if named_node not in seen:
            seen.add(named_node)
            output_file.write(f"{named_node} feat:[1,1,1]\n")

    input_file.close()
    output_file.close()
