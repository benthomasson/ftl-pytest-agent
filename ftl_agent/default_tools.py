from smolagents.tools import Tool
from ftl_agent.tools import get_json_schema
from ftl_agent.local_python_executor import FinalAnswerException

class Complete(Tool):
    name = "complete"

    def __init__(self, state, *args, **kwargs):
        self.state = state
        super().__init__(*args, **kwargs)

    def forward(self, message: str):
        """
        Mark the solution as complete.

        Args:
            message: A completion message
        """

        raise FinalAnswerException(message)

    description, inputs, output_type = get_json_schema(forward)

TOOLS = {
    "complete": Complete,
}
