#!/usr/bin/python3
#!/usr/bin/python3

from sys import argv
import asyncio

def main():
    try:
        from musikla.cli_application import CliApplication

        asyncio.run( CliApplication( argv[ 1: ] ).run() )
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()