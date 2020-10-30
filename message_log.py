from typing import List, Reversible, Tuple, Iterable
import textwrap

import tcod

import color

class Message:
    def __init__(self, text: str, fg: Tuple[int,int,int]):
        self.plain_text = text
        self.fg = fg
        self.count = 1

    @property
    def full_text(self) -> str:
        """The full text of this message, including count if necessary"""
        if self.count >1:
            return f"{self.plain_text} (x{self.count})"
        return self.plain_text

class MessageLog:
    def __init__(self) -> None:
        self.messages: List[Message] = []

    def add_message(
            self,
            text: str,
            fg: Tuple[int,int,int] = color.white,
            *,
            stack: bool = True,
    )->None:
        """add message to this log.
        'text' is the message text. fg is text color
        if stack is true than message can stack with previous message"""
        if stack and self.messages and text == self.messages[-1].plain_text:
            self.messages[-1].count +=1
        else:
            self.messages.append(Message(text, fg))

    def render(
            self,
            console: tcod.Console,
            x: int,
            y: int,
            width: int,
            height: int,
    ) -> None:
        """render this log over the given area.
        'x', 'y', 'width', 'height' is the rectangular region to render
        onto the 'console'"""
        self.render_messages(console, x,y,width,height,self.messages)

    @staticmethod
    def wrap(string: str, width: int) -> Iterable[str]:
        """return a wrapped tet message"""
        if string is not None:
            for line in string.splitlines(): #handle newlines in messages
                yield from textwrap.wrap(
                    line, width, expand_tabs=True,
                )

    @classmethod
    def render_messages(
            cls,
            console: tcod.Console,
            x: int,
            y: int,
            width: int,
            height: int,
            messages: Reversible[Message],
    ) -> None:
        """Render the messages in list. start at last message work backwards"""
        y_offset = height -1

        for message in reversed(messages):
            for line in reversed(list(cls.wrap(message.full_text, width))):
                console.print(x=x, y=y+y_offset, string=line, fg=message.fg)
                y_offset -=1
                if y_offset <0:
                    return # no more space to print messages