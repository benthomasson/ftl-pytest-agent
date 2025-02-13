import click

from .core import create_model, run_agent
from .default_tools import get_tool
from .prompts import SOLVE_PROBLEM
import faster_than_light as ftl


@click.command()
@click.option("--tools", "-t", multiple=True)
@click.option("--problem", "-p", prompt="What is the problem?")
@click.option("--system-design", "-s", prompt="What is the system design?")
@click.option("--model", "-m", default="ollama_chat/deepseek-r1:14b")
@click.option("--inventory", "-i", default="inventory.yml")
def main(tools, problem, system_design, model, inventory):
    """A agent that solves a problem given a system design and a set of tools"""
    model = create_model(model)
    state = {'LOCKED': True, 'inventory': ftl.load_inventory(inventory), 'modules': ['modules']}
    run_agent(
        tools=[get_tool(state, t) for t in tools],
        model=model,
        problem_statement=SOLVE_PROBLEM.format(
            problem=problem, system_design=system_design
        ),
    )


if __name__ == "__main__":
    main()
