import sys
import pyulog as ulog

assert len(sys.argv) > 1, f"No input file specified"

print(f"input: {sys.argv[1]}")

log = ulog.ULog(sys.argv[1])
data = log.data_list

# Print Message Names
for thing in data:
    print(thing.name)

# Print all timestamps for all data
for x in data:
    print(x.data["timestamp"])
