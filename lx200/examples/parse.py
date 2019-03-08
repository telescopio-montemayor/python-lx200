#!/usr/bin/env python3

import fileinput

from lx200.parser import Parser


if __name__ == '__main__':

    parser = Parser()
    for line in fileinput.input():
        parser.feed(line)
        while(parser.output):
            command = parser.output.pop()
            print(command)
