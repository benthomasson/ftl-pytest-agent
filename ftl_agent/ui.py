import click

from .core import create_model, run_agent
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


@click.command()
@click.option("--tools-files", "-f", multiple=True)
@click.option("--system-design", "-s")
@click.option("--model", "-m", default="ollama_chat/deepseek-r1:14b")
@click.option("--inventory", "-i", default="inventory.yml")
@click.option("--extra-vars", "-e", multiple=True)
@click.option("--python", "-o", default="output.py")
@click.option("--explain", "-o", default="output.txt")
@click.option("--playbook", default="playbook.yml")
def main(
    tools_files, system_design, model, inventory, extra_vars, python, explain, playbook
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

    def bot(problem, history, system_design, tools):

        generate_python_header(
            python,
            system_design,
            problem,
            tools_files,
            tools,
            inventory,
            modules,
            extra_vars,
        )
        generate_explain_header(explain, system_design, problem)
        generate_playbook_header(playbook, system_design, problem)
        python_output = ""
        playbook_output = ""

        def update_code():
            nonlocal python_output, playbook_output
            with open(python) as f:
                python_output = f.read()
            with open(playbook) as f:
                playbook_output = f.read()

        update_code()

        response = f"System design: {system_design}\n Problem: {problem}.\n"
        for i in range(len(response)):
            time.sleep(0.00)
            yield response[:i], python_output, playbook_output

        tools.append("complete")

        f = io.StringIO()
        with redirect_stdout(f):
            gen = run_agent(
                tools=[get_tool(tool_classes, t, state) for t in tools],
                model=model,
                problem_statement=SOLVE_PROBLEM.format(
                    problem=problem, system_design=system_design
                ),
            )
        output = f.getvalue()
        yield response + output, python_output, playbook_output

        response = response + output
        try:
            while True:
                f = io.StringIO()
                with redirect_stdout(f):
                    o = next(gen)
                    if isinstance(o, ActionStep):
                        generate_explain_action_step(explain, o)
                        if o.tool_calls:
                            for call in o.tool_calls:
                                generate_python_tool_call(python, call)
                        generate_playbook_task(playbook, o)
                    elif isinstance(o, AgentText):
                        print(o.to_string())

                output = f.getvalue()
                for i in range(len(output)):
                    time.sleep(0.00)
                    yield response + output[:i], python_output, playbook_output
                response = response + output
        except StopIteration:
            pass

        reformat_python(python)
        add_lookup_plugins(playbook)
        update_code()
        yield response + output[:i], python_output, playbook_output

    with gr.Blocks() as demo:
        python_code = gr.Code(render=False)
        playbook_code = gr.Code(render=False)
        with gr.Row():
            with gr.Column():
                gr.Markdown("<center><h1></h1></center>")
                gr.ChatInterface(
                    bot,
                    type="messages",
                    additional_inputs=[
                        gr.Textbox(system_design, label="System Design"),
                        gr.CheckboxGroup(choices=sorted(tool_classes), label="Tools"),
                    ],
                    # additional_inputs_accordion=gr.Accordion(visible=True),
                    additional_outputs=[python_code, playbook_code],
                )
            with gr.Column():
                python_code.render()
                playbook_code.render()

    demo.launch()


if __name__ == "__main__":
    main()
