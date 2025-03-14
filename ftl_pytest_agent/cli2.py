#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
from ftl_pytest_agent.util import get_functions

from .testgen import generate_test


@click.command()
@click.argument("code-file")
@click.option("--model", "-m", default="ollama_chat/deepseek-r1:14b")
@click.option("--function", "-f", default=None)
@click.option("--additional-info", "-a", default=None)
def main(model, code_file, function, additional_info):
    print(code_file)
    module, fns = get_functions(code_file)
    print(module.__name__, [fn.__name__ for fn in fns])

    for fn in fns:
        fn_name = fn.__name__
        if (function and fn_name == function) or function is None:
            fn_doc = fn.__doc__
            tools = ['complete', fn_name]
            prompt = f"Call {fn_name} with suitable arguments, use assert statement on the result to make sure it is correct, and then complete.  Consider the docstring for {fn_name} in your work:\n{fn_doc}\n"
            if additional_info:
                with open(additional_info) as f:
                    prompt += "\nConsider this additional info as well:\n"
                    prompt += f.read()
            output = f"test_{fn_name}.py"
            explain = f"test_{fn_name}.txt"
            generate_test(model, code_file, tools, prompt, output, explain)


if __name__ == "__main__":
    main()
