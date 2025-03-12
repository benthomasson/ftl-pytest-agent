
from ftl_pytest_agent.core import create_model, run_agent
from ftl_pytest_agent.default_tools import TOOLS
from ftl_pytest_agent.tools import get_tool, load_code
from ftl_pytest_agent.codegen import (
    generate_python_header,
    reformat_python,
    generate_python_tool_call,
    generate_explain_header,
    generate_explain_action_step,
)
from ftl_pytest_agent.memory import ActionStep
from smolagents.agent_types import AgentText


def generate_test(model, code_file, tools, prompt, output, explain):

    code_files = [code_file]

    tool_classes = {}
    tool_classes.update(TOOLS)
    for cf in code_files:
        tool_classes.update(load_code(cf))
    model = create_model(model)
    state = {
    }

    generate_python_header(
        output,
        prompt,
        [],
        code_files,
        tools,
    )
    generate_explain_header(explain, prompt)

    for o in run_agent(
        tools=[get_tool(tool_classes, t, state) for t in tools],
        model=model,
        problem_statement=prompt,
    ):
        if isinstance(o, ActionStep):
            generate_explain_action_step(explain, o)
            if o.trace and o.tool_calls:
                for call in o.tool_calls:
                    generate_python_tool_call(output, call)
        elif isinstance(o, AgentText):
            print(o.to_string())

    reformat_python(output)
