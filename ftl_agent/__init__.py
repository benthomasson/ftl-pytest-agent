from contextlib import contextmanager

from smolagents.tools import Tool
from .tools import load_tools, get_tool
from .default_tools import TOOLS
from dataclasses import dataclass
from faster_than_light import load_inventory
from ftl_agent.local_python_executor import FinalAnswerException
from faster_than_light import localhost


class Tools(object):

    def __init__(self, tools: dict[str, Tool]):
        self.__dict__.update(tools)


@dataclass
class FTL:
    tools: Tools


@contextmanager
def automation(tools_files, tools, inventory, modules, **kwargs):
    tool_classes = {}
    tool_classes.update(TOOLS)
    state = {
        "inventory": load_inventory(inventory),
        "modules": modules,
        "localhost": localhost,
    }
    state.update(kwargs)
    for tf in tools_files:
        tool_classes.update(load_tools(tf))
    ftl = FTL(
        tools=Tools({name: get_tool(tool_classes, name, state) for name in tools})
    )
    try:
        yield ftl
    except FinalAnswerException as e:
        print(e)
