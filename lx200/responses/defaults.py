import lx200.commands as c


COMMAND_DEFAULT_MAP = {}


def add_default(command, response_data):
    if command in COMMAND_DEFAULT_MAP:
        raise ValueError('Command {} already mapped to a default response data'.format(command))
    COMMAND_DEFAULT_MAP[command] = response_data


def for_command(command):
    return COMMAND_DEFAULT_MAP.get(command, {})


add_default(c.GetBrowseBrighterMagnitudeLimit, {
    'value': 10
})

add_default(c.GetBrowseFaintMagnitudeLimit, {
    'value': 0
})

add_default(c.GetUTCOffsetTime, {
    'value': 0
})

add_default(c.GetLowerLimit, {
    'value': 0
})

add_default(c.GetHighLimit, {
    'value': 110
})
