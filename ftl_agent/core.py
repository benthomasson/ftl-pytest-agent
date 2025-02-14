from ftl_agent.agents import CodeAgent
from smolagents import LiteLLMModel
from ftl_agent.prompts import CODE_SYSTEM_PROMPT


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
        system_prompt=CODE_SYSTEM_PROMPT,
    )
    return agent.run(problem_statement, stream=True)


