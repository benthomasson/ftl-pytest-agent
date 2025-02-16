import os


def generate_header(output, system_design, problem, tools_files, tools, inventory, modules, extra_vars):

    with open(output, "w") as f:
        f.write("#!/usr/bin/env python3\n")
        f.write(f'"""\nSystem Design: {system_design}\nProblem:{problem}\n"""\n')
        f.write("import ftl_agent\n")
        f.write("import os\n\n\n")
        f.write("with ftl_agent.automation(\n")
        f.write(f"tools_files={tools_files},\n")
        f.write(f"tools={tools},\n")
        f.write(f"inventory='{inventory}',\n")
        f.write(f"modules={modules},\n")
        for e in extra_vars:
            e, _, _ = e.partition("=")
            f.write(f"{e.lower()} = os.environ['{e.upper()}'],\n")
        f.write(") as ftl:\n\n")

        for t in tools:
            f.write(f"    {t} = ftl.tools.{t}\n")

        f.write("\n")


def generate_tool_call(output, call):
    with open(output, "a") as f:
        f.write("\n    ")
        f.write("\n    ".join(call.arguments.strip().split("\n")))
        f.write("\n")


def reformat(output):
    os.system("black " + output)
