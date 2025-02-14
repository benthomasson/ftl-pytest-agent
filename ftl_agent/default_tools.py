from smolagents.tools import Tool
from ftl_agent.tools import get_json_schema
from ftl_agent.local_python_executor import FinalAnswerException

import faster_than_light as ftl
import asyncio


class Package(Tool):
    name = "package"

    def __init__(self, state, *args, **kwargs):
        self.state = state
        super().__init__(*args, **kwargs)

    def forward(self, name: str, state: str) -> bool:
        """Installs a package. Returns True if successful.

        Args:
            name: The name of the package
            state: One of present or absent

        Returns:
            boolean
        """
        output = asyncio.run(
            ftl.run_module(
                self.state["inventory"],
                self.state["modules"],
                "argtest",
                module_args=dict(somekey="somevalue"),
            )
        )

        return True

    description, inputs, output_type = get_json_schema(forward)


class Copy(Tool):
    name = "copy"

    def __init__(self, state, *args, **kwargs):
        self.state = state
        super().__init__(*args, **kwargs)

    def forward(self, src: str, dest: str) -> bool:
        """
        Copies a file to the server. Returns True if successful.

        Args:
            src: The source of the file
            dest: The destination of the file

        Returns:
            boolean
        """

        return True

    description, inputs, output_type = get_json_schema(forward)


class Service(Tool):
    name = "service"

    def __init__(self, state, *args, **kwargs):
        self.state = state
        super().__init__(*args, **kwargs)

    def forward(self, name: str, state: str) -> bool:
        """
        Starts or stops a service. Returns True if successful.

        Args:
            name: The name of the package
            state: One of started or stopped

        Returns:
            boolean
        """

        return True

    description, inputs, output_type = get_json_schema(forward)


class Check(Tool):
    name = "check"

    def __init__(self, state, *args, **kwargs):
        self.state = state
        super().__init__(*args, **kwargs)

    def forward(self, name: str) -> bool:
        """
        Checks the state of a service.  Returns True if running.

        Args:
            name: The name of the package

        Returns:
            boolean
        """

        return True

    description, inputs, output_type = get_json_schema(forward)


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


class Slack(Tool):
    name = "slack"

    def __init__(self, state, *args, **kwargs):
        self.state = state
        super().__init__(*args, **kwargs)

    def forward(self, message: str) -> bool:
        """Sends a message to slack.

        Args:
            message: the message to send

        Returns:
            boolean
        """
        output = asyncio.run(
            ftl.run_module(
                self.state["inventory"],
                self.state["modules"],
                "slack",
                module_args=dict(msg=message, token=self.state["slack_token"]),
            )
        )

        return True

    description, inputs, output_type = get_json_schema(forward)


class Discord(Tool):
    name = "discord"

    def __init__(self, state, *args, **kwargs):
        self.state = state
        super().__init__(*args, **kwargs)

    def forward(self, message: str) -> bool:
        """Sends a message to discord.

        Args:
            message: the message to send

        Returns:
            boolean
        """
        output = asyncio.run(
            ftl.run_module(
                self.state["inventory"],
                self.state["modules"],
                "discord",
                module_args=dict(
                    content=message,
                    webhook_token=self.state["discord_token"],
                    webhook_id=self.state["discord_channel"],
                ),
            )
        )

        return True

    description, inputs, output_type = get_json_schema(forward)


TOOLS = {
    "package": Package,
    "copy": Copy,
    "service": Service,
    "check": Check,
    "complete": Complete,
    "slack": Slack,
    "discord": Discord,
}


def get_tool(state, name):
    return TOOLS[name](state)
