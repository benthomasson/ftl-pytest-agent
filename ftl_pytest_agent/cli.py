import click

from .core import create_model, run_agent
from .default_tools import TOOLS
from .tools import get_tool, load_tools, load_code
from .codegen import (
    generate_python_header,
    reformat_python,
    generate_python_tool_call,
    generate_explain_header,
    generate_explain_action_step,
)
from ftl_pytest_agent.memory import ActionStep
from smolagents.agent_types import AgentText


@click.command()
@click.option("--code-files", "-c", multiple=True)
@click.option("--tools-files", "-f", multiple=True)
@click.option("--tools", "-t", multiple=True)
@click.option("--problem", "-p", prompt="What is the problem?")
@click.option("--model", "-m", default="ollama_chat/deepseek-r1:14b")
@click.option("--output", "-o", default="output.py")
@click.option("--explain", "-o", default="output.txt")
def main(
    code_files,
    tools_files,
    tools,
    problem,
    model,
    output,
    explain,
):
    """A agent that solves a problem given a system design and a set of tools"""
    tool_classes = {}
    tool_classes.update(TOOLS)
    for tf in tools_files:
        tool_classes.update(load_tools(tf))
    for cf in code_files:
        tool_classes.update(load_code(cf))
    model = create_model(model)
    state = {
    }

    generate_python_header(
        output,
        problem,
        tools_files,
        code_files,
        tools,
    )
    generate_explain_header(explain, problem)

    for o in run_agent(
        tools=[get_tool(tool_classes, t, state) for t in tools],
        model=model,
        problem_statement=problem,
    ):
        if isinstance(o, ActionStep):
            generate_explain_action_step(explain, o)
            if o.trace and o.tool_calls:
                for call in o.tool_calls:
                    generate_python_tool_call(output, call)
        elif isinstance(o, AgentText):
            print(o.to_string())

    reformat_python(output)
