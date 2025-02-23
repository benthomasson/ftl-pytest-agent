import click
import cmd

from .core import create_model, run_agent
from .default_tools import TOOLS
from .tools import get_tool, load_tools
from .prompts import SOLVE_PROBLEM
from .codegen import (
    generate_python_header,
    reformat_python,
    generate_python_tool_call,
    generate_explain_header,
    generate_explain_action_step,
    generate_playbook_header,
    generate_playbook_task,
)
import faster_than_light as ftl
from ftl_agent.memory import ActionStep
from smolagents.agent_types import AgentText


class FTLAgentShell(cmd.Cmd):

    intro = "Welcome to ftl agent shell"
    prompt = "(ftl-agent)> "

    def __init__(
        self,
        tools_files,
        tools,
        tool_classes,
        model,
        modules,
        inventory,
        extra_vars,
        state,
        problem,
        system_design,
        output,
        explain,
        playbook,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.tools_files = tools_files
        self.tools = tools
        self.tool_classes = tool_classes
        self.model = model
        self.modules = modules
        self.inventory = inventory
        self.extra_vars = extra_vars
        self.state = state
        self.problem = problem
        self.system_design = system_design
        self.output = output
        self.explain = explain
        self.playbook = playbook

    def do_run(self, line):
        generate_python_header(
            self.output,
            self.system_design,
            self.problem,
            self.tools_files,
            self.tools,
            self.inventory,
            self.modules,
            self.extra_vars,
        )
        generate_explain_header(self.explain, self.system_design, self.problem)
        generate_playbook_header(self.playbook, self.system_design, self.problem)

        for o in run_agent(
            tools=[get_tool(self.tool_classes, t, self.state) for t in self.tools],
            model=self.model,
            problem_statement=SOLVE_PROBLEM.format(
                problem=self.problem, system_design=self.system_design
            ),
        ):
            if isinstance(o, ActionStep):
                generate_explain_action_step(self.explain, o)
                if o.trace and o.tool_calls:
                    for call in o.tool_calls:
                        generate_python_tool_call(self.output, call)
                    generate_playbook_task(self.playbook, o)
            elif isinstance(o, AgentText):
                print(o.to_string())

        reformat_python(self.output)

    def do_systemdesign(self, line):
        if line:
            self.system_design = line
        print(self.system_design)

    def do_problem(self, line):
        if line:
            self.problem = line
        print(self.problem)

    def default(self, line):
        if line:
            self.problem = line
        print(self.problem)

    def do_tools(self, line):
        print(self.tools)

@click.command()
@click.option("--tools", "-t", multiple=True)
@click.option("--tools-files", "-f", multiple=True)
@click.option("--problem", "-p")
@click.option("--system-design", "-s", prompt="What is the system design?")
@click.option("--model", "-m", default="ollama_chat/deepseek-r1:14b")
@click.option("--modules", "-M", default=["modules"], multiple=True)
@click.option("--inventory", "-i", default="inventory.yml")
@click.option("--extra-vars", "-e", multiple=True)
@click.option("--output", "-o", default="output.py")
@click.option("--explain", "-o", default="output.txt")
@click.option("--playbook", default="playbook.yml")
def main(
    tools,
    tools_files,
    problem,
    system_design,
    model,
    modules,
    inventory,
    extra_vars,
    output,
    explain,
    playbook,
):
    """A agent that solves a problem given a system design and a set of tools"""
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

    FTLAgentShell(
        tools_files,
        tools,
        tool_classes,
        model,
        modules,
        inventory,
        extra_vars,
        state,
        problem,
        system_design,
        output,
        explain,
        playbook,
    ).cmdloop()
