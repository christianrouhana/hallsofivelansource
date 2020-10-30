class Impossible(Exception):
    """exception raised when action is impossible to be performed
    reason is given as exception method
    called as raise Impossible("an exception method")"""

class QuitWithoutSaving(SystemExit):
    """can be raised to exit the game without saving"""