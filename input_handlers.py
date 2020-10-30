from __future__ import annotations

import os

from typing import Optional, TYPE_CHECKING, Callable, Tuple, Union
import tcod.event
from components import ai
import actions
from actions import(
    Action,
    BumpAction,
    PickupAction,
    WaitAction,
)
import game_map
import color
import exceptions
if TYPE_CHECKING:
    from engine import Engine
    from entity import Item

MOVE_KEYS = {
    tcod.event.K_UP: (0, -1),
    tcod.event.K_DOWN: (0, 1),
    tcod.event.K_LEFT: (-1, 0),
    tcod.event.K_RIGHT: (1, 0),
    tcod.event.K_HOME: (-1, -1),
    tcod.event.K_END: (-1, 1),
    tcod.event.K_PAGEUP: (1, -1),
    tcod.event.K_PAGEDOWN: (1,1),
    # Numpad keys.
    tcod.event.K_KP_1: (-1, 1),
    tcod.event.K_KP_2: (0, 1),
    tcod.event.K_KP_3: (1, 1),
    tcod.event.K_KP_4: (-1, 0),
    tcod.event.K_KP_6: (1, 0),
    tcod.event.K_KP_7: (-1, -1),
    tcod.event.K_KP_8: (0, -1),
    tcod.event.K_KP_9: (1, -1),
    # Vi keys.
    tcod.event.K_h: (-1, 0),
    tcod.event.K_j: (0, 1),
    tcod.event.K_k: (0, -1),
    tcod.event.K_l: (1, 0),
    tcod.event.K_y: (-1, -1),
    tcod.event.K_u: (1, -1),
    tcod.event.K_b: (-1, 1),
    tcod.event.K_n: (1, 1),
}

WAIT_KEYS = {
    tcod.event.K_PERIOD,
    tcod.event.K_KP_5,
    tcod.event.K_CLEAR,
}

CONFIRM_KEYS = {
    tcod.event.K_RETURN,
    tcod.event.K_KP_ENTER,
}

CURSOR_Y_KEYS = {
    tcod.event.K_UP: -1,
    tcod.event.K_DOWN: 1,
    tcod.event.K_PAGEUP: -10,
    tcod.event.K_PAGEDOWN: 10,
}

ActionOrHandler = Union[Action, "BaseEventHandler"]
"""an event handler return value which can trigger action or switch handler
if an action is returned the handler is the active handler,
else switch handler"""

class BaseEventHandler(tcod.event.EventDispatch[ActionOrHandler]):
    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        """handle an event and return the next active event handler"""
        state = self.dispatch(event)
        if isinstance(state, BaseEventHandler):
            return state
        assert not isinstance(state, Action), f"{self!r} can not handle actions."
        return self
    def on_render(self, console: tcod.Console)->None:
        raise NotImplementedError()
    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        raise SystemExit()

class PopupMessage(BaseEventHandler):
    """popup text menu"""

    def __init__(self, parent_handler: BaseEventHandler, text:str):
        self.parent = parent_handler
        self.text = text

    def on_render(self, console: tcod.Console) ->None:
        """render the parent and dim the result, print message on top"""
        self.parent.on_render(console)
        console.tiles_rgb["fg"] //= 8
        console.tiles_rgb["bg"] //= 8

        console.print(
            console.width //2,
            console.height //2,
            self.text,
            fg=color.white,
            bg=color.black,
            alignment=tcod.CENTER,
        )

    def ev_keydown(self, event: "tcod.event.KeyDown") -> Optional[BaseEventHandler]:
        return self.parent

class EventHandler(BaseEventHandler):
    def __init__(self, engine: Engine):
        self.engine = engine

    def handle_events(self, event: tcod.context.Event) -> BaseEventHandler:
        """handle events for input handlers with an engine"""
        action_or_state = self.dispatch(event)
        if isinstance(action_or_state, BaseEventHandler):
            return action_or_state
        if self.handle_action(action_or_state):
            # a valid action
            if not self.engine.player.is_alive:
                #the player was killed sometime during/after aciton
                return GameOverEventHandler(self.engine)
            elif self.engine.player.level.requires_level_up:
                return LevelUpEventHandler(self.engine)
            return MainEventHandler(self.engine) #return to main handler
        return self

    def handle_action(self, action: Optional[Action]) -> bool:
        """handle actions returned from event methods"""
        if action is None:
            return False

        try:
            action.perform()
        except exceptions.Impossible as exc:
            self.engine.message_log.add_message(exc.args[0], color.impossible)
            return False #skip enemy turn
        self.engine.handle_enemy_turns()
        self.engine.update_fov()
        return True


    def ev_mousemotion(self, event: tcod.event.MouseMotion) -> None:
        if self.engine.game_map.in_bounds(event.tile.x, event.tile.y):
            self.engine.mouse_location = event.tile.x, event.tile.y

    def on_render(self, console: tcod.Console) -> None:
        self.engine.render(console)

class AskUserEventHandler(EventHandler):
    """handles user input for actions which require special input"""

    def ev_keydown(self, event: "tcod.event.KeyDown") -> Optional[ActionOrHandler]:
        """by default any key exits"""
        if event.sym in {
            tcod.event.K_LSHIFT,
            tcod.event.K_RSHIFT,
            tcod.event.K_LCTRL,
            tcod.event.K_RCTRL,
            tcod.event.K_LALT,
            tcod.event.K_RALT,
        }:
            return None
        return self.on_exit()

    def ev_mousebuttondown(
        self, event: "tcod.event.MouseButtonDown"
    ) -> Optional[ActionOrHandler]:
        return self.on_exit()

    def on_exit(self) -> Optional[ActionOrHandler]:
        """called when user is trying to exit or cancel an action
        by default this returns main event handler"""
        return MainEventHandler(self.engine)

class CharacterScreenEventHandler(AskUserEventHandler):
   TITLE = "Character Information"

   def on_render(self, console: tcod.Console) -> None:
       super().on_render(console)

       if self.engine.player.x <= 30:
           x = 40
       else:
           x = 0

       y = 0

       width = len(self.TITLE) + 4

       console.draw_frame(
           x=x,
           y=y,
           width=width,
           height=7,
           title=self.TITLE,
           clear=True,
           fg=(255, 255, 255),
           bg=(0, 0, 0),
       )

       console.print(
           x=x + 1, y=y + 1, string=f"Level: {self.engine.player.level.current_level}"
       )
       console.print(
           x=x + 1, y=y + 2, string=f"XP: {self.engine.player.level.current_xp}"
       )
       console.print(
           x=x + 1,
           y=y + 3,
           string=f"XP for next Level: {self.engine.player.level.experience_to_next_level}",
       )

       console.print(
           x=x + 1, y=y + 4, string=f"Attack: {self.engine.player.fighter.power}"
       )
       console.print(
           x=x + 1, y=y + 5, string=f"Defense: {self.engine.player.fighter.defense}"
       )

class LevelUpEventHandler(AskUserEventHandler):
   TITLE = "Level Up"

   def on_render(self, console: tcod.Console) -> None:
       super().on_render(console)

       if self.engine.player.x <= 30:
           x = 40
       else:
           x = 0

       console.draw_frame(
           x=x,
           y=0,
           width=35,
           height=8,
           title=self.TITLE,
           clear=True,
           fg=(255, 255, 255),
           bg=(0, 0, 0),
       )

       console.print(x=x + 1, y=1, string="Congratulations! You level up!")
       console.print(x=x + 1, y=2, string="Select an attribute to increase.")

       console.print(
           x=x + 1,
           y=4,
           string=f"a) Constitution (+20 HP, from {self.engine.player.fighter.max_hp})",
       )
       console.print(
           x=x + 1,
           y=5,
           string=f"b) Strength (+1 attack, from {self.engine.player.fighter.power})",
       )
       console.print(
           x=x + 1,
           y=6,
           string=f"c) Agility (+1 defense, from {self.engine.player.fighter.defense})",
       )

   def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
       player = self.engine.player
       key = event.sym
       index = key - tcod.event.K_a

       if 0 <= index <= 2:
           if index == 0:
               player.level.increase_max_hp()
           elif index == 1:
               player.level.increase_power()
           else:
               player.level.increase_defense()
       else:
           self.engine.message_log.add_message("Invalid entry.", color.invalid)
           return None

       return super().ev_keydown(event)

   def ev_mousebuttondown(
       self, event: tcod.event.MouseButtonDown
   ) -> Optional[ActionOrHandler]:
       """
       Don't allow the player to click to exit the menu, like normal.
       """
       return None

class InventoryEventHandler(AskUserEventHandler):
    """asks user when they select item. parent class"""

    TITLE = "<missing title>"

    def on_render(self, console: tcod.Console) -> None:
        """render an inventory menu. window location based on user location"""
        super().on_render(console)
        number_of_items_in_inventory = len(self.engine.player.inventory.items)

        height = number_of_items_in_inventory + 2

        if height <= 3:
            height = 3

        if self.engine.player.x <= 30:
            x=40
        else:
            x=0

        y = 0

        width = len(self.TITLE) + 12

        console.draw_frame(
            x=x,
            y=y,
            width=width,
            height=height,
            title=self.TITLE,
            clear=True,
            fg=(255,255,255),
            bg=(0,0,0),
        )

        if number_of_items_in_inventory > 0:
            for i, item in enumerate(self.engine.player.inventory.items):
                item_key = chr(ord("a") + i)
                is_equipped = self.engine.player.equipment.item_is_equipped(item)
                item_string = f"({item_key}) {item.name}"
                if is_equipped:
                    item_string = f"{item_string} (E)"
                console.print(x + 1, y + i + 1, item_string)

        else:
            console.print(x+1, y+1, "(Empty)")

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        player = self.engine.player
        key = event.sym
        index = key - tcod.event.K_a

        if 0 <= index <= 26:
            try:
                selected_item = player.inventory.items[index]
            except IndexError:
                self.engine.message_log.add_message("Invalid entry", color.invalid)
                return None
            return self.on_item_selected(selected_item)
        return super().ev_keydown(event)

    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        """called when a user selects a vlaid item"""
        raise NotImplementedError()

class InventoryActivateHandler(InventoryEventHandler):
    """handle using an inventory item"""
    TITLE = "Select an item to use"

    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        if item.consumable:
        # Return the action for the selected item.
            return item.consumable.get_action(self.engine.player)
        elif item.equippable:
            return actions.EquipAction(self.engine.player, item)
        else:
            return None

class InventoryDropHandler(InventoryEventHandler):
    """handle dropping an inventory item"""

    TITLE = "Select and item to drop"

    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        """drop this item"""
        return actions.DropItem(self.engine.player, item)

class SelectIndexHandler(AskUserEventHandler):
    """handles user for asking an index on the map"""

    def __init__(self, engine: Engine):
        """sets the cursor to the player when this handler is constructed"""
        super().__init__(engine)
        player = self.engine.player
        engine.mouse_location = player.x, player.y

    def on_render(self, console: tcod.Console) -> None:
        """highlight tile under the cursor"""
        super().on_render(console)
        x, y = self.engine.mouse_location
        console.tiles_rgb["bg"][x, y] = color.white
        console.tiles_rgb["fg"][x, y] = color.black

    def ev_keydown(self, event: "tcod.event.KeyDown") -> Optional[ActionOrHandler]:
        """check for key movement"""
        key = event.sym
        if key in MOVE_KEYS:
            modifier = 1 #holding modifier keys wll sped up key movement
            if event.mod & (tcod.event.KMOD_LSHIFT | tcod.event.KMOD_RSHIFT):
                modifier *= 5
            if event.mod & (tcod.event.KMOD_LCTRL | tcod.event.KMOD_RCTRL):
                modifier *= 10
            if event.mod & (tcod.event.KMOD_LALT | tcod.event.KMOD_RALT):
                modifier *= 20

            x,y = self.engine.mouse_location
            dx, dy = MOVE_KEYS[key]
            x += dx * modifier
            y += dy * modifier
            #clamp cursor index to the map size
            x = max(0, min(x, self.engine.game_map.width - 1))
            y = max(0, min(y, self.engine.game_map.height -1))
            self.engine.mouse_location = x, y
            return None
        elif key in CONFIRM_KEYS:
            return self.on_index_selected(*self.engine.mouse_location)
        return super().ev_keydown(event)

    def ev_mousebuttondown(
        self, event: "tcod.event.MouseButtonDown"
    ) -> Optional[ActionOrHandler]:
        """Left click confirms selection"""
        if self.engine.game_map.in_bounds(*event.tile):
            if event.button ==1:
                return self.on_index_selected(*event.tile)
        return super().ev_mousebuttondown(event)

    def on_index_selected(self, x: int, y: int) -> Optional[ActionOrHandler]:
        """called when an index is selected"""
        raise NotImplementedError()

class LookHandler(SelectIndexHandler):
    """lets the player look arond using the keyboard"""
    def on_index_selected(self, x: int, y: int) -> MainEventHandler:
        """return to main handler"""
        return MainEventHandler(self.engine)

class SingleRangedAttackHandler(SelectIndexHandler):
    """handles targeting a single enemy. only the enemy effected"""
    def __init__(
            self,
            engine: Engine,
            callback: Callable[[Tuple[int, int]], Optional[Action]]
    ):
        super().__init__(engine)
        self.callback= callback

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        return self.callback((x,y))

class AreaRangedAttackHandler(SelectIndexHandler):
    """Handles targeting an area within a given radius. Any entity within the area takes damage"""

    def __init__(
            self,
            engine: Engine,
            radius: int,
            callback: Callable[[Tuple[int, int]], Optional[Action]],
    ):
        super().__init__(engine)

        self.radius = radius
        self.callback = callback

    def on_render(self, console: tcod.Console)->None:
        """Highligt the tile under the cursor"""
        super().on_render(console)
        x, y = self.engine.mouse_location

        #draw a rectangle around the targeted area so the player can see AOE
        console.draw_frame(
            x=x - self.radius-1,
            y=y - self.radius -1,
            width=self.radius **2,
            height= self.radius **2,
            fg=color.red,
            clear=False
        )

    def on_index_selected(self, x: int, y:int) -> Optional[Action]:
        return self.callback((x,y))

class HistoryViewer(EventHandler):
    """Print the message history on a larger window which can be navigated"""
    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.log_length = len(engine.message_log.messages)
        self.cursor = self.log_length-1

    def on_render(self, console: tcod.Console)->None:
        super().on_render(console) #draw main state as bbkgrnd

        log_console = tcod.Console(console.width-6, console.height-6)

        #draw a frame with a custom banner title
        log_console.draw_frame(0,0,log_console.width, log_console.height)
        log_console.print_box(
            0,0,log_console.width, 1, "-|Message history|-", alignment=tcod.CENTER
        )

        # render message log using cursor param
        self.engine.message_log.render_messages(
            log_console,
            1,
            1,
            log_console.width-2,
            log_console.height-2,
            self.engine.message_log.messages[: self.cursor +1]
        )
        log_console.blit(console, 3,3)

    def ev_keydown(self, event: tcod.event.KeyDown)->Optional[MainEventHandler]:
        #conditional movement
        if event.sym in CURSOR_Y_KEYS:
            adjust = CURSOR_Y_KEYS[event.sym]
            if adjust < 0 and self.cursor ==0:
                #only move from top to bottom when you are on the edge of the list
                self.cursor = self.log_length -1
            elif adjust > 0 and self.cursor == self.log_length -1:
                #same with bottom to top movement
                self.cursor = 0
            else:
                #other wise move in bounds of history log
                self.cursor=max(0,min(self.cursor + adjust, self.log_length -1))
        elif event.sym == tcod.event.K_HOME:
            self.cursor = 0 # move directly to top message
        elif event.sym == tcod.event.K_END:
            self.cursor = self.log_length -1 # move directly to last message
        else: #any other key move switches back to game state
            return MainEventHandler(self.engine)
        return None

class MainEventHandler(EventHandler):
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        action: Optional[Action] = None

        key = event.sym
        modifier = event.mod

        player = self.engine.player
        if isinstance(player.ai, ai.DefenseModifier):
            player.ai.perform()

        if key == tcod.event.K_PERIOD and modifier & (
            tcod.event.KMOD_LSHIFT | tcod.event.KMOD_RSHIFT
        ):
            return actions.TakeStairsAction(player)

        if key == tcod.event.K_6 and modifier & (
            tcod.event.KMOD_LSHIFT | tcod.event.KMOD_RSHIFT
        ) and self.engine.player_at_artifact:
            return GameWinEventHandler(self.engine, f"As you lay your hands on the glowing artifact, the world around"
                                                    f"\nyou begins to disappear... in a moment you realize you are "
                                                    f"\nstanding at the entrance of the forsaken cave. You have done it."
                                                    f"\nYou bested the ultimate suicide mission, reclaiming your innocence"
                                                    f"\nfor crimes you never committed. You begin the long walk back home,"
                                                    f"\nready for a new life. CONGRATULATIONS!")

        if key in MOVE_KEYS:
            dx, dy = MOVE_KEYS[key]
            action = BumpAction(player, dx, dy)
        elif key in WAIT_KEYS:
            action = WaitAction(player)
        elif key == tcod.event.K_ESCAPE:
            raise SystemExit()
        elif key == tcod.event.K_v:
            return HistoryViewer(self.engine)
        elif key == tcod.event.K_g:
            action = PickupAction(player)
        elif key == tcod.event.K_i:
            return InventoryActivateHandler(self.engine)
        elif key == tcod.event.K_d:
            return InventoryDropHandler(self.engine)
        elif key == tcod.event.K_c:
            return CharacterScreenEventHandler(self.engine)
        elif key == tcod.event.K_SLASH:
            return LookHandler(self.engine)

        return action

class GameOverEventHandler(EventHandler):
    def on_quit(self) -> None:
        """Handle exiting out of a finished game"""
        if os.path.exists("savegame.sav"):
            os.remove("savegame.sav")
        raise exceptions.QuitWithoutSaving() # avoid saving a finished game

    def ev_quit(self, event: tcod.event.Quit) -> None:
        self.on_quit()

    def ev_keydown(self, event: "tcod.event.KeyDown") -> Optional[Action]:
        if event.sym == tcod.event.K_ESCAPE:
            self.on_quit()

class GameWinEventHandler(EventHandler):
    def __init__(self, engine: Engine, text:str):
        super().__init__(engine)
        self.engine = engine
        self.text = text

    def on_render(self, console: tcod.Console) ->None:
        """render the parent and dim the result, print message on top"""
        super().on_render(console)
        console.tiles_rgb["fg"] //= 8
        console.tiles_rgb["bg"] //= 8

        console.print(
            console.width //2,
            console.height //2,
            self.text,
            fg=color.white,
            bg=color.black,
            alignment=tcod.CENTER,
        )
    def on_quit(self) -> None:
        """Handle exiting out of a finished game"""
        if os.path.exists("savegame.sav"):
            os.remove("savegame.sav")
        raise exceptions.QuitWithoutSaving() # avoid saving a finished game
    def ev_quit(self, event: tcod.event.Quit) -> None:
        self.on_quit()

    def ev_keydown(self, event: "tcod.event.KeyDown") -> Optional[Action]:
        if event.sym == tcod.event.K_ESCAPE:
            self.on_quit()