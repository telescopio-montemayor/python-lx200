# python-lx200

Utilities to generate and parse LX200 protocol messages


## Installation

Under a virtualenv do:

```
    pip install -e .
```

in order to fetch all the dependencies and install it.


## Usage examples

While we produce a better documentation the files under */lx200/examples* are a good guide.


### Simple parsing:

Run

```
    cat file_with_lx200_commands.txt | python -m lx200.examples.parse
```

to test the command parser.


### TCP Scope server:

Run

```
    python -m lx200.examples.tcpserver
```

to start a tcp server that speaks LX200 on port 7634. The internal scope state can be accessed on port 8081


The full set of options is:

```
$ python -m lx200.examples.tcpserver --help
usage: lx200.examples.tcpserver [-h] [--verbose] [--port PORT]
                                [--web-port WEB_PORT] [--host HOST]

Simulates an LX200 compatible telescope with tcp connection

optional arguments:
  -h, --help           show this help message and exit
  --verbose
  --port PORT          TCP port for the LX200 server (7634)
  --web-port WEB_PORT  TCP port for the status server (8081)
  --host HOST          Host for all the servers (127.0.0.1)
```
