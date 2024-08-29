import sys

if (len(sys.argv) > 1):
    inp_file = sys.argv[1]

stripped_inp = inp_file.split("/")[-1]

# TODO currently only converts xnetwork to snap; generalise it maybe ?

# output file comments
predata_comments = f"""# Directed edge list for {stripped_inp} in SNAP format
# Taken from {inp_file}
# Save as tab-separated list of edges
# FromNodeId\tToNodeId"""

DELIM = " "

with open(f"./formattedData/{stripped_inp}", "w+") as out:
    print(predata_comments, file=out)

    with open(inp_file, "r") as inp:
        line = inp.readline()
        while line and not str.isspace(line):
            line_info = line.split(DELIM)
            print(f"{line_info[0]}\t{line_info[1]}", file=out)
            line = inp.readline()
            