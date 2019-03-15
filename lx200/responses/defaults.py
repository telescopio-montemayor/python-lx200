import lx200.commands as c


COMMAND_DEFAULT_MAP = {}


def add_default(command, response_data):
    if command in COMMAND_DEFAULT_MAP:
        raise ValueError('Command {} already mapped to a default response data'.format(command))
    COMMAND_DEFAULT_MAP[command] = response_data


def for_command(command):
    try:
        return COMMAND_DEFAULT_MAP.get(command, {})
    except TypeError:
        return COMMAND_DEFAULT_MAP.get(command.__class__, {})


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

add_default(c.GetAlignmentMenuEntry0, {
    'value': 'Menu0'
})

add_default(c.GetAlignmentMenuEntry1, {
    'value': 'Menu1'
})

add_default(c.GetAlignmentMenuEntry2, {
    'value': 'Menu2'
})

add_default(c.GetTrackingRate, {
    'value': 60.0
})

add_default(c.SelectSiderealTrackingRate, {
    'value': 'SIDEREAL'
})

add_default(c.QueryFocuserBusyStatus, {
    'value': False
})


# XXX WARNING: LX200 specifies only three letters
add_default(c.GetSite1Name, {
    'value': 'SI1'
})
add_default(c.GetSite2Name, {
    'value': 'SI2'
})
add_default(c.GetSite3Name, {
    'value': 'SI3'
})
add_default(c.GetSite4Name, {
    'value': 'SI4'
})
add_default(c.SelectSite, {
    'value': 1
})

# True: 24H
add_default(c.GetClockFormat, {
    'value': True
})

add_default(c.SetDSTEnabled, {
    'value': False
})
