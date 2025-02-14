import click

from .core import create_model, run_agent
from .default_tools import get_tool
from .prompts import SOLVE_PROBLEM
import faster_than_light as ftl
import gradio as gr
import time
from contextlib import redirect_stdout
import io


@click.command()
@click.option("--tools", "-t", multiple=True)
@click.option("--problem", "-p")
@click.option("--system-design", "-s")
@click.option("--model", "-m", default="ollama_chat/deepseek-r1:14b")
@click.option("--inventory", "-i", default="inventory.yml")
@click.option("--extra-vars", "-e", multiple=True)
def main(tools, problem, system_design, model, inventory, extra_vars):
    """A agent that solves a problem given a system design and a set of tools"""
    model = create_model(model)
    state = {
        "LOCKED": True,
        "inventory": ftl.load_inventory(inventory),
        "modules": ["modules"],
    }
    for extra_var in extra_vars:
        name, _, value = extra_var.partition("=")
        state[name] = value

    def echo(problem, history, system_design, tools):
        response = f"System desgin: {system_design}\n Problem: {problem}."
        for i in range(len(response)):
            time.sleep(0.05)
            yield response[:i]

        f = io.StringIO()
        with redirect_stdout(f):
            output = run_agent(
                tools=[get_tool(state, t) for t in tools],
                model=model,
                problem_statement=SOLVE_PROBLEM.format(
                    problem=problem, system_design=system_design
                ),
            )
        stdout = f.getvalue()
        for i in range(len(stdout)):
            time.sleep(0.00)
            yield response + stdout[:i]
        for i in range(len(output)):
            time.sleep(0.00)
            yield response + stdout + output[:i]

    demo = gr.ChatInterface(
        echo,
        type="messages",
        additional_inputs=[
            gr.Textbox(system_design, label="System Design"),
            gr.CheckboxGroup(choices=tools, label="Tools"),
        ],
        additional_inputs_accordion=gr.Accordion(visible=True),
    )

    demo.launch()


if __name__ == "__main__":
    main()
