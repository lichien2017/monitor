# coding=utf-8

import BaseModel
import argparse
import sys
sys.path.append("..")
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Optional arguments: input file.
    parser.add_argument(
        "-f","--input_file",
        help="Path to the configure file"
    )

    # Optional arguments: input threadnum.
    parser.add_argument(
        "-n", "--number",
        help="Threading Numbers",
        type=int
    )

    # Optional arguments: input threadnum.
    parser.add_argument(
        "-t", "--sleeptime",
        help="sleep time",
        type=int
    )

    args = parser.parse_args()

    if args.input_file == None:
        args.input_file = "scrapyServer/config.json"

    if args.number == None:
        args.number = 10

    if args.sleeptime == None:
        args.sleeptime = 10

    print(args)

    control = BaseModel.MainControl(args.input_file, args.sleeptime, args.number)
    control.startthread()