import os
import types

import importlib


def get_functions(code_file):

    # Load module from file path
    if not code_file.endswith(".py"):
        raise Exception('Expects a python file')
    module_name = os.path.basename(code_file[:-3])
    spec = importlib.util.spec_from_file_location(module_name, code_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    fns = []

    # Find and instantiate the Tool class
    for item_name in dir(module):
        item = getattr(module, item_name)
        if isinstance(item, types.FunctionType):
            fns.append(item.__name__)

    return module.__name__, fns


def generate_python_header(
    output,
    problem,
    tools_files,
    code_files,
    tools,
):

    with open(output, "w") as f:
        f.write("#!/usr/bin/env python3\n")
        if problem:
            f.write('"""\n')
            f.write(f"Problem:{problem}\n")
            f.write('"""\n')

        for code_file in code_files:
            module_name, fns = get_functions(code_file)
            fns = ", ".join(fns)
            f.write(f"from {module_name} import {fns}")

            f.write(
                """
def complete(message: str=None):
  print(message)\n"""
            )

        f.write("\n\ndef test():\n")


def generate_python_tool_call(output, call):
    with open(output, "a") as f:
        f.write("\n    ")
        f.write("\n    ".join(call.arguments.strip().split("\n")))
        f.write("\n")


def reformat_python(output):
    os.system("black " + output)


def generate_explain_header(explain, problem):
    with open(explain, "w") as f:
        if problem:
            f.write("Problem: {problem}\n\n")


def generate_explain_action_step(explain, o):
    if o.model_output:
        with open(explain, "a") as f:
            f.write(f"Step {o.step_number:2d} ")
            f.write("-" * 100)
            f.write("\n\n")
            f.write(o.model_output)
            f.write("\n\n")
