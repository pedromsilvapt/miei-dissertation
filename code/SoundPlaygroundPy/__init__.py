#!/usr/bin/python3

# Modules used:
# pip3 install imgui[glfw] py_linq

from core import Context, Instrument
from parser.abstract_syntax_tree import MusicSequenceNode
from parser.abstract_syntax_tree.context_modifiers import ContextModifierNode
from graphics import BaseApplication

class Application( BaseApplication ):
    pass

if __name__ == "__main__":
    Application().run()
