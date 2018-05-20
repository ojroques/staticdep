import argparse
import json
from objectfile import ObjectFile    # A class to represent an object file

def main():
    """The main function."""
    # Parse the argument line
    parser = argparse.ArgumentParser(description="Parse the JSON output file to print leaves or verify if a list of object files is complete.")
    parser.add_argument("outfile", metavar="json_outfile",
                        help="the JSON file to parse")
    outfile = parser.parse_args().outfile   # The name of the json output file


main()
