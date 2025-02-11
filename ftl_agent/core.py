from smolagents import CodeAgent, LiteLLMModel


def create_model(model_id, context=8192):

    return LiteLLMModel(
        model_id=model_id,
        num_ctx=context,
    )


def run_agent(tools, model, problem_statement):
    agent = CodeAgent(
        tools=tools,
        model=model,
        verbosity_level=4,
    )
    agent.run(problem_statement)
