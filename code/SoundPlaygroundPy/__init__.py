#!/usr/bin/python3
from sys import argv
from gui_application import GuiApplication
from cli_application import CliApplication

if __name__ == "__main__":
    try:
        if '--gui' in argv or '-g' in argv:
            GuiApplication().run()
        else:
            CliApplication( argv[ 1: ] ).run()
    except KeyboardInterrupt:
        pass
