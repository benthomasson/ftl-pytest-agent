from smolagents import tool
from smolagents.local_python_executor import FinalAnswerException

@tool
def open_door(name: str) -> bool:
    """Opens the door with the given name. Returns True if successful, False otherwise.

    Args:
        name: The name of the door to open.
    """
    global LOCKED

    if name == "exit":
        if LOCKED:
            raise Exception("Locked. Look for a key.")
        raise FinalAnswerException("Success!")
    else:
        raise Exception(f"there is no door named {name}")


@tool
def unlock_door(name: str, using: str) -> bool:
    """Unlocks the door with the given name and given item. Returns True if successful, False otherwise.

    Args:
        name: The name of the door to unlock.
        using: The name of the item to unlock the door with.
    """
    global LOCKED

    if name == "exit" and using == "pick":
        LOCKED = False
        return True
    elif name != "exit":
        raise Exception(f"there is no door named {name}")
    elif using != "pick":
        raise Exception(f"{name} is the wrong key")
    raise Exception("wat")


@tool
def open_chest(name: str) -> list[str]:
    """Opens the chest with the given name. Returns the contents of the chest as a list

    Args:
        name: The name of the door to open.
    """

    return ["pick"]


@tool
def look_around() -> list[str]:
    """Shows you what is in the room with you.
    """

    return ['exit', 'chest']

TOOLS = {'open_door': open_door,
         'open_chest': open_chest,
         'unlock_door': unlock_door,
         'look_around': look_around}

def get_tool(name):
    return TOOLS[name]



