import click

from .core import create_model, run_agent
from .default_tools import TOOLS
from .tools import get_tool, load_tools
from .prompts import SOLVE_PROBLEM
from .codegen import generate_header, reformat, generate_tool_call
import faster_than_light as ftl
from smolagents.memory import ActionStep
from smolagents.agent_types import AgentText


@click.command()
@click.option("--tools", "-t", multiple=True)
@click.option("--tools-files", "-f", multiple=True)
@click.option("--problem", "-p", prompt="What is the problem?")
@click.option("--system-design", "-s", prompt="What is the system design?")
@click.option("--model", "-m", default="ollama_chat/deepseek-r1:14b")
@click.option("--inventory", "-i", default="inventory.yml")
@click.option("--extra-vars", "-e", multiple=True)
@click.option("--output", "-o", default="output.py")
def main(
    tools, tools_files, problem, system_design, model, inventory, extra_vars, output
):
    """A agent that solves a problem given a system design and a set of tools"""
    modules = ["modules"]
    tool_classes = {}
    tool_classes.update(TOOLS)
    for tf in tools_files:
        tool_classes.update(load_tools(tf))
    model = create_model(model)
    state = {
        "LOCKED": True,
        "inventory": ftl.load_inventory(inventory),
        "modules": ["modules"],
    }
    for extra_var in extra_vars:
        name, _, value = extra_var.partition("=")
        state[name] = value

    generate_header(output, tools_files, tools, inventory, modules, extra_vars)

    for o in run_agent(
        tools=[get_tool(tool_classes, t, state) for t in tools],
        model=model,
        problem_statement=SOLVE_PROBLEM.format(
            problem=problem, system_design=system_design
        ),
    ):
        if isinstance(o, ActionStep):
            if o.tool_calls:
                for call in o.tool_calls:
                    generate_tool_call(output, call)
        elif isinstance(o, AgentText):
            print(o.to_string())

    reformat(output)
