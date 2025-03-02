import click

from .core import create_model, make_agent
from .default_tools import TOOLS
from .tools import get_tool, load_tools
from .prompts import SOLVE_PROBLEM
import faster_than_light as ftl
import gradio as gr
import time
from contextlib import redirect_stdout
import io
from .codegen import (
    generate_python_header,
    reformat_python,
    add_lookup_plugins,
    generate_python_tool_call,
    generate_explain_header,
    generate_explain_action_step,
    generate_playbook_header,
    generate_playbook_task,
)
from ftl_agent.memory import ActionStep
from smolagents.agent_types import AgentText

from .Gradio_UI import GradioUI


@click.command()
@click.option("--tools-files", "-f", multiple=True)
@click.option("--tools", "-t", multiple=True)
@click.option("--system-design", "-s")
@click.option("--model", "-m", default="ollama_chat/deepseek-r1:14b")
@click.option("--inventory", "-i", default="inventory.yml")
@click.option("--extra-vars", "-e", multiple=True)
@click.option("--python", "-o", default="output.py")
@click.option("--explain", "-o", default="output.txt")
@click.option("--playbook", default="playbook.yml")
def main(
    tools_files, tools, system_design, model, inventory, extra_vars, python, explain, playbook
):
    """A agent that solves a problem given a system design and a set of tools"""
    modules = ["modules"]
    tool_classes = {}
    tool_classes.update(TOOLS)
    for tf in tools_files:
        tool_classes.update(load_tools(tf))
    model = create_model(model)
    state = {
        "inventory": ftl.load_inventory(inventory),
        "modules": modules,
        "localhost": ftl.localhost,
    }
    for extra_var in extra_vars:
        name, _, value = extra_var.partition("=")
        state[name] = value

    agent = make_agent(
        tools=[get_tool(tool_classes, t, state) for t in tools],
        model=model,
    )
    GradioUI(agent).launch(tool_classes, system_design)


if __name__ == "__main__":
    main()
