from collections import deque
from enum import Enum


from .commands import ALL_COMMANDS, is_command, ACK, EOT, UnknownCommand


COMMAND_START = ':'
COMMAND_END = '#'


class State(Enum):
    IDLE = 1
    PARSING = 2


class Parser:

    def __init__(self, maxlen=32):
        self.state = State.IDLE
        self.buffer = []
        self.output = deque()
        self.maxlen = maxlen

    def __reset_input_state(self):
        self.buffer.clear()
        self.state = State.IDLE

    def feed_one(self, data):
        """ Takes a single character and processes it """
        if self.state is State.IDLE:
            # These two are special
            if is_command(data, ACK):
                self.output.appendleft(ACK.from_data(data))
                return

            if is_command(data, EOT):
                self.output.appendleft(EOT.from_data(data))
                return

            if data == COMMAND_START:
                self.state = State.PARSING
                return

        elif self.state is State.PARSING:
            if data == COMMAND_END:
                self.output.appendleft(self.parse(''.join(self.buffer)))
                self.__reset_input_state()
            else:
                if len(self.buffer) < self.maxlen:
                    self.buffer.append(data)
                else:
                    self.__reset_input_state()

    def feed(self, data):
        """ Takes one or more characters and processes them """
        for c in data:
            self.feed_one(c)

    def parse(self, data):
        for command in ALL_COMMANDS:
            if is_command(data, command):
                return command.from_data(data)
        return UnknownCommand.from_data(data)
