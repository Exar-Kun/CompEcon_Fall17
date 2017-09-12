class Backpack(object):
    """A Backpack object class. Has a name and a list of contents.
    Attributes:
    name (str): the name of the backpack's owner.
    contents (list): the contents of the backpack.
    """
def __init__(self, name, color, max_size): # This function is the constructor.
    """Set the name and initialize an empty contents list.
    Inputs:
    name (str): the name of the backpack's owner.
    Returns:
    A Backpack object wth no contents.
    """
    self.name = name # Initialize some attributes.
    self.color = color
    self.max_size = 5
    self.contents = []

def put(self, item):
    """Add 'item' to the backpack's list of contents."""
    if len(self.contents) < self.max_size:
        self.contents.append(item)
    else:
        print("No More Room!")
