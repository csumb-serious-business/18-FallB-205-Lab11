# Lab 12: Adventure Game Enhanced

### authors ###################################################################
# J Asato
# M Robertson
# R Talmage
###############################################################################

# Game Guide
# map
# A   B
# |   |
# C - D - E - H
#     |   |
#     F - G
#
# legend
# A your neighbor's room
# B your room (start)
# C far hall - window [throw baseball -> lose game]
# D your hall
# E office - book [take reveals H], key
# F rec room - baseball
# G lobby - door [unlock door (need key) -> win game]
# H secret room

import sys, time

# use shim in non-JES environment, otherwise ignore
try:
    from JES_shim import showInformation, requestString
except ImportError:
    pass


class UserInterface(object):
    """
    models a user interface -- allowing this to be run in
    either JES or a python interpreter
    """

    JES, CONSOLE = range(2)  # the known interface environments

    def __init__(self, interface_type=JES):
        """
        create a interface
        :param interface_type: the target environment
        (default JES)
        """
        self.interface_type = interface_type

    def show(self, message):
        """
        tells the user interface to display a message
        :param message: the message to display
        :return: None
        """
        if self.interface_type == UserInterface.JES:
            showInformation(message)
        else:
            print(message)

    def ask(self, message):
        """
        tells the user interface to retrieve a string from the user
        :param message: the message to display when asking for input
        :return: the input string from the user
        """
        if self.interface_type == UserInterface.JES:
            return requestString(message)
        else:
            return raw_input(message)


class Log(object):
    """
    a rudimentary logger, without configuration (other than enable/disable)
      or logging levels other than info
    """
    enabled = True

    @staticmethod
    def info(message):
        """
        logs a system message with a timestamp (usually for debugging)
        :param message: the message to log
        :return: None
        """
        if Log.enabled:
            caller = sys._getframe(1).f_code.co_name
            if message != '...':
                print('info %s | %s -- %s' % (time.time(), caller, message))
            else:
                print('info %s | %s called' % (time.time(), caller))


class Room(object):
    """
    models a room in the game environment
    """

    # common room message strings
    M_CANNOT_ADD = "Error: can't add a room to an already used location"
    M_NO_PASSAGE = "You find no passage to the %s."
    M_NOW_IN_ROOM = "You are now in %s."
    M_INSIDE = "Inside you see: "
    M_NOT_INSIDE = "There was no %s in the room."

    def __init__(self, name, is_visible=True):
        """
        creates a new room
        :param name: the name of the room
        :param is_visible: whether the room is
         initially visible to the user
        """
        self.name = name
        self.is_visible = is_visible
        self.room_north = None
        self.room_south = None
        self.room_east = None
        self.room_west = None
        self.things = []
        Log.info("new room created -- %s" % self.name)

    def add_north(self, other):
        """
        links this room with another placing this room
        to the south and the other to the north
        :param other: the other room to link
        :return: None
        :raises ValueError: if either room is
        already linked in that location.
        """
        if self.room_north is not None or other.room_south is not None:
            raise ValueError(self.M_CANNOT_ADD)
        self.room_north = other
        other.room_south = self
        Log.info("south: %s, north: %s" % (self.name, other.name))

    def add_south(self, other):
        """
        links this room with another placing this room
        to the north and the other to the south
        :param other: the other room to link
        :return: None
        :raises ValueError: if either room is
        already linked in that location.
        """
        if self.room_south is not None or other.room_north is not None:
            raise ValueError(self.M_CANNOT_ADD)
        self.room_south = other
        other.room_north = self
        Log.info("north: %s, south: %s" % (self.name, other.name))

    def add_east(self, other):
        """
        links this room with another placing this room
        to the west and the other to the east
        :param other: the other room to link
        :return: None
        :raises ValueError: if either room is
        already linked in that location.
        """
        if self.room_east is not None or other.room_west is not None:
            raise ValueError(self.M_CANNOT_ADD)
        self.room_east = other
        other.room_west = self
        Log.info("west: %s, east: %s" % (self.name, other.name))

    def add_west(self, other):
        """
        links this room with another placing this room
        to the east and the other to the west
        :param other: the other room to link
        :return: None
        :raises ValueError: if either room is
        already linked in that location.
        """
        if self.room_west is not None or other.room_east is not None:
            raise ValueError(self.M_CANNOT_ADD)
        self.room_west = other
        other.room_east = self
        Log.info("east: %s, west: %s" % (self.name, other.name))

    def add_thing(self, thing):
        """
        adds a Thing (game object) to this room
        :param thing: the thing to add
        :return: None
        """
        self.things.append(thing)
        Log.info("room: %s, thing: %s" % (self.name, thing.name))

    def thing_there(self, thing):
        """
        queries this rooms list of things, to see if it is there
        :param thing: the thing to find
        :return: True if the thing is present
        """
        result = self.things.__contains__(thing)
        Log.info("room: %s, thing: %s, result: %s" % (self.name, thing.name, result))
        return result

    def thing_missing(self, thing):
        """
        queries this rooms list of things, to see if it is not there
        :param thing: the thing to find
        :return: True if the thing is NOT present
        """
        result = not self.things.__contains__(thing)
        Log.info("room: %s, thing: %s, result: %s" % (self.name, thing.name, result))
        return result

    def make_visible(self):
        """
        makes this room visible to the user
        :return: None
        """
        Log.info("room: %s" % self.name)
        self.is_visible = True

    def make_invisible(self):
        """
        makes this room invisible to the user
        :return: None
        """
        Log.info("room: %s" % self.name)
        self.is_visible = False

    def get_can_be_target_of(self, action):
        """
        gets the first item in this room's things that a given action can operate on
        :param action: the action to look for
        :return: the first thing that works with that action or None
        """
        for thing in self.things:
            if thing.can_be_target_of(action):
                Log.info("room: %s" % self.name)
                return thing
        return None

    def get_thing(self, name):
        """
        gets the first item in this room's things with a given name
        :param name: the name to look for
        :return: the first thing with that name or None
        """
        for thing in self.things:
            if thing.name == name:
                Log.info("found -- room: %s, thing: %s" % (self.name, thing.name))
                return thing
        Log.info("not found -- room: %s, thing: %s" % (self.name, name))
        return None

    # todo: show open directions of travel in the room when asking for input

    def describe(self):
        """
        generates a description for this room including
        its name and a list of the things inside it
        :return: the description
        """
        message = self.M_NOW_IN_ROOM % self.name
        list_str = ""
        if len(self.things) > 0:
            for thing in self.things:
                list_str += "\n    " + thing.desc
                if thing.hint != '':
                    list_str += " (" + thing.hint + ")"

            message += '\n' + self.M_INSIDE + list_str
        Log.info("...")
        return message


class Thing(object):
    """
    models a thing in the game environment
    """

    def __init__(self, name, desc, hint='', removable=True):
        """
        creates a new Thing (game object)
        :param name: the name of this thing
        :param desc: its description
        :param hint: a hint about its usage
            ex: a [ball] that looks easy to <throw>
            would allow: throw ball
        :param removable: if this thing can be removed from the room
         by the user (add added to thier inventory)
            ex: a door is a thing we don't want the user to remove
        """
        self.name = name
        self.desc = desc
        self.hint = hint
        self.can_take = removable
        self.source_of = []
        self.target_of = []
        Log.info("new thing created -- %s" % self.name)

    def add_source_of(self, action):
        """
        add an action's source -- used when evaluating if a particular action
        can be performed USING this item
        :param action: the action this can be the source of
        :return: None
        """
        Log.info("source: %s, action: %s" % (self.name, action))
        self.source_of.append(action)

    def add_target_of(self, action, message):
        """
        add an action's target -- used when evaluating if a particular action
        can be performed ON this item
        :param action: the action this can be the target of
        :param message: a message to show then the action occurs
        :return: None
        """
        Log.info("target: %s, action: %s" % (self.name, action))
        self.target_of.append((action, message))

    def remove_source_of(self, action):
        """
        remove an action's source from this item -- used when evaluating if a
        particular action can be performed USING this item
        :param action: the action to remove
        :return: None
        """
        Log.info("source: %s, action: %s" % (self.name, action))
        self.source_of.remove(action)

    def remove_target_of(self, action):
        """
        remove an action's target from this item -- used when evaluating if a
        particular action can be performed ON this item
        :param action: the action to remove
        :return: None
        """
        Log.info("target: %s, action: %s" % (self.name, action))
        to_remove = self._target_action_to_tuple(action)

        if to_remove is not None:
            self.target_of.remove(to_remove)

    def _target_action_to_tuple(self, action):
        Log.info("target: %s, action: %s" % (self.name, action))
        for target in self.target_of:
            act, mess = target
            if action == act:
                return target
        return None

    def can_be_target_of(self, action):
        """
        checks if this Thing can be the target of a particular action
        :param action: the action to check
        :return: True if the action can be performed on this Thing
        """
        result = self._target_action_to_tuple(action) is not None
        Log.info("target: %s, action: %s, result: %s" % (self.name, action, result))
        return result

    def cannot_be_target_of(self, action):
        """
        checks if this Thing can NOT be the target of a particular action
        :param action: the action to check
        :return: True if the action can NOT be performed on this Thing
        """
        result = not self.can_be_target_of(action)
        Log.info("target: %s, action: %s, result: %s" % (self.name, action, result))
        return result

    def get_target_message_for_action(self, action):
        """
        retrieves the corresponding target message
        for a given action on this Thing
        :param action: the action to get a message for
        :return: the corresponding message for the action on this Thing
        or '' if the action is not in this Thing's targets
        """
        target = self._target_action_to_tuple(action)
        Log.info("target: %s, action: %s" % (self.name, action))
        if target is not None:
            _, message = target
            return message
        else:
            return ''

    def can_be_source_of(self, action):
        """
        checks if this Thing can be the source of a particular action
        :param action: the action to check
        :return: True if the action can be performed using this Thing
        """
        result = False
        for source in self.source_of:
            if action == source:
                result = True
        Log.info("target: %s, action: %s, result: %s" % (self.name, action, result))
        return result


class Player(object):
    """
    models a player (user) in the game environment
    """

    # common player message strings
    M_TOOK = "You took the %s"
    M_CANT_TAKE = "You were unable to find a way to take the %s."

    def __init__(self):
        """
        creates a new player
        """
        self.inventory = []
        Log.info("new player created")

    def has(self, thing_name):
        """
        checks if this Player has an item with
         a given name in their inventory
        :param thing_name: the name to check
        :return: True if the item is present in the Player's inventory
        """
        result = self.get(thing_name) is not None
        Log.info("thing: %s, result: %s" % (thing_name, result))
        return result

    def get(self, thing_name):
        """
        gets a given item from a Player's inventory
        :param thing_name: the item's name
        :return: the item from the Player's inventory
        or None if it was not found
        """
        Log.info("thing: %s" % thing_name)
        for thing in self.inventory:
            if thing.name == thing_name:
                return thing
        return None

    def remove_from_inventory(self, thing_name):
        """
        removes the first item with a given name
        from the Player's inventory
        :param thing_name: the name of the item to remove
        :return: None
        """
        Log.info("thing: %s" % thing_name)
        for thing in self.inventory:
            if thing.name == thing_name:
                self.inventory.remove(thing)
                return

    def item_that_can(self, action):
        """
        finds the first item in a Player's inventory that
         can perform a given action
        :param action: the action to perform
        :return: the first item found that can perform the given action
        or None if not found
        """
        Log.info("action: %s" % action)
        for item in self.inventory:
            if item.can_be_source_of(action):
                return item
        return None


class GameEnvironment(object):
    """
    models a game environment -- where all the game objects interact
    """

    def __init__(self):
        """
        create a game environment
        """
        # initialize player
        self.player = Player()

        # game is not won or lost yet
        self.game_is_won = False
        self.game_is_lost = False

        # initialize game triggers
        self.triggers = []

        # create the game rooms
        r_a = Room('your neighbor\'s room')
        r_b = Room('your room')
        r_c = Room('the far hall')
        r_d = Room('the hallway in front of your room')
        r_e = Room('the office')
        r_f = Room('the recreation room')
        r_g = Room('the lobby')
        r_h = Room('a secret room attached to the office', False)

        # create the game map by linking the rooms
        r_a.add_south(r_c)
        r_b.add_south(r_d)
        r_c.add_east(r_d)
        r_d.add_east(r_e)
        r_d.add_south(r_f)
        r_e.add_south(r_g)
        r_e.add_east(r_h)
        r_f.add_east(r_g)

        # create the user-interactable things
        t_a = Thing('book', 'a suspicious looking [book] in a bookcase')
        t_b = Thing('key', 'a [key] sitting on the desk')
        t_c = Thing('window', 'a [window] at the end of the hall', 'maybe you can <throw> something at it', False)
        t_d = Thing('door', 'a [door] at the far side of the lobby', 'maybe you can <unlock> it', False)
        t_e = Thing('baseball', 'a [baseball] sitting on a chair')

        # place the things into their respective rooms
        r_c.add_thing(t_c)
        r_e.add_thing(t_a)
        r_e.add_thing(t_b)
        r_f.add_thing(t_e)
        r_g.add_thing(t_d)

        # setup the interactions
        t_b.add_source_of(Commands.UNLOCK)
        t_b.add_source_of(Commands.LOCK)
        t_d.add_target_of(Commands.UNLOCK,
                          'The door is unlocked. You have a feeling that freedom is not far away.')
        t_e.add_source_of(Commands.THROW)
        t_c.add_target_of(Commands.THROW, 'The window is now broken with a sizable hole in its center.')

        # setup the triggers
        self.add_trigger(t_d.can_be_target_of, self.win_game, "You win!", Commands.LOCK)
        self.add_trigger(t_c.cannot_be_target_of, self.lose_game, "You lose", Commands.THROW)
        self.add_trigger(r_e.thing_missing, r_h.make_visible, "A secret room has been revealed.", t_a)

        # set the initial room
        self.current_room = r_b
        Log.info("new game environment created")

    # todo go_dir, take, etc. methods should be on the player
    def go_north(self):
        """
        attempts to move the player into the next room to the north
        :return: a Tuple of Boolean, String
           the bool: True if the attempt was successful
           the string: the message to show the user
        """
        Log.info('...')
        if self.current_room.room_north is not None:
            if self.current_room.room_north.is_visible:
                self.current_room = self.current_room.room_north
                return True, self.current_room.describe()
        return False, Room.M_NO_PASSAGE % 'north'

    def go_south(self):
        """
        attempts to move the player into the next room to the south
        :return: a Tuple of Boolean, String
           the bool: True if the attempt was successful
           the string: the message to show the user
        """
        Log.info('...')
        if self.current_room.room_south is not None:
            if self.current_room.room_south.is_visible:
                self.current_room = self.current_room.room_south
                return True, self.current_room.describe()
        return False, Room.M_NO_PASSAGE % 'south'

    def go_east(self):
        """
        attempts to move the player into the next room to the east
        :return: a Tuple of Boolean, String
           the bool: True if the attempt was successful
           the string: the message to show the user
        """
        Log.info('...')
        if self.current_room.room_east is not None:
            if self.current_room.room_east.is_visible:
                self.current_room = self.current_room.room_east
                return True, self.current_room.describe()
        return False, Room.M_NO_PASSAGE % 'east'

    def go_west(self):
        """
        attempts to move the player into the next room to the west
        :return: a Tuple of Boolean, String
           the bool: True if the attempt was successful
           the string: the message to show the user
        """
        Log.info('...')
        if self.current_room.room_west is not None:
            if self.current_room.room_west.is_visible:
                self.current_room = self.current_room.room_west
                return True, self.current_room.describe()
        return False, Room.M_NO_PASSAGE % 'west'

    def player_take(self, thing_name):
        """
        attempts to move an item from the current Room into the Player's inventory
        :param thing_name: the name of the Thing in the current Room to move
        :return: a Tuple of Boolean, String
           the bool: True if the attempt was successful
           the string: the message to show the user
        """
        Log.info('...')
        found = None
        for thing in self.current_room.things:
            if thing.name == thing_name:
                found = thing
                break
        if found is not None:
            if found.can_take is False:
                return True, self.player.M_CANT_TAKE % thing_name
            self.player.inventory.append(found)
            self.current_room.things.remove(found)
            return True, self.player.M_TOOK % thing_name
        else:
            return False, Room.M_NOT_INSIDE % thing_name

    def player_throw(self, thing_name):
        """
        attempts to complete a THROW interaction between
           a given item in the Player's inventory and
           a THROW target in the current room
        if successful, it removes the item from the Player's inventory
        :param thing_name: the name of the Thing in the Player's inventory
        to THROW
        :return: a Tuple of Boolean, String
           the bool: True if the attempt was successful
           the string: the message to show the user
        """
        Log.info('...')
        target = self.current_room.get_can_be_target_of(Commands.THROW)
        if target is not None:
            source = self.player.get(thing_name)
            if source is None:
                return False, "You have no %s to even try to throw at the %s." % (thing_name, target.name)
            elif source.can_be_source_of(Commands.THROW):
                result_message = target.get_target_message_for_action(Commands.THROW)
                target.remove_target_of(Commands.THROW)
                self.player.remove_from_inventory(thing_name)
                return True, "You threw the %s at the %s. \n%s" % (thing_name, target.name, result_message)
            else:
                return False, \
                       "You could throw the %s at the %s, but you have a feeling that you'd regret it." \
                       % (thing_name, target.name)
        return False, "There was nothing to throw the %s at." % thing_name

    def player_lock(self, thing_name):
        """
        attempts to complete a LOCK interaction between
           a given item in the current room and
           an item in the player's inventory
        if successful, it changes the Thing's target of from LOCK to UNLOCK
        :param thing_name: the name of the thing in the current Room to LOCK
        :return: a Tuple of Boolean, String
           the bool: True if the attempt was successful
           the string: the message to show the user
        """
        Log.info('...')
        target = self.current_room.get_thing(thing_name)
        if target is None:
            return False, "You look around fruitlessly for a %s to lock." % thing_name
        elif target.can_be_target_of(Commands.LOCK):
            source = self.player.item_that_can(Commands.LOCK)
            if source is not None:
                result_message = target.get_target_message_for_action(Commands.LOCK)
                target.remove_target_of(Commands.LOCK)
                target.add_target_of(Commands.UNLOCK, "The %s is now unlocked" % target.name)
                return True, "You locked the %s with the %s. \n%s" % (target.name, source.name, result_message)
            else:
                return False, "There was nothing to lock the %s with." % thing_name
        elif target.can_be_target_of(Commands.UNLOCK):
            return False, "You find that the %s is already locked." % thing_name
        else:
            return False, "You ponder for a lengthy while, but fail to figure a way to lock the %s." % thing_name

    def player_unlock(self, thing_name):
        """
        attempts to complete a UNLOCK interaction between
           a given item in the current room and
           an item in the player's inventory
        if successful, it changes the Thing's target of from UNLOCK to LOCK
        :param thing_name: the name of the thing in the current Room to UNLOCK
        :return: a Tuple of Boolean, String
           the bool: True if the attempt was successful
           the string: the message to show the user
        """
        Log.info('...')
        target = self.current_room.get_thing(thing_name)
        if target is None:
            return False, "You look around fruitlessly for a %s to unlock." % thing_name
        elif target.can_be_target_of(Commands.UNLOCK):
            source = self.player.item_that_can(Commands.UNLOCK)
            if source is not None:
                result_message = target.get_target_message_for_action(Commands.UNLOCK)
                target.remove_target_of(Commands.UNLOCK)
                target.add_target_of(Commands.LOCK, "The %s is now locked" % target.name)
                return True, "You locked the %s with the %s. \n%s" % (target.name, source.name, result_message)
            else:
                return False, "You have nothing to unlock the %s with." % thing_name
        elif target.can_be_target_of(Commands.LOCK):
            return False, "You find that the %s is already unlocked." % thing_name
        else:
            return False, "You ponder for a lengthy while, but fail to figure a way to unlock the %s." % thing_name

    def win_game(self):
        """
        sets the won game condition to True
        :return: None
        """
        Log.info('...')
        self.game_is_won = True

    def lose_game(self):
        """
        sets the lost game condition to True
        :return: None
        """
        Log.info('...')
        self.game_is_lost = True

    def add_trigger(self, condition, result, message, args):
        """
        adds a game state trigger to this environment,
           when it becomes true, the result is executed and
           the message is given to the user
        :param condition: the condition (function) to evaluate
        :param result: the result (function) to execute
           when the trigger becomes true
        :param message: the message to display to the user
           when the condition becomes true
        :param args: the args to pass to the condition before evaluation
        :return: None
        """
        Log.info("condition: %s, result: %s, message: %s, args: %s" % (condition, result, message, args))
        self.triggers.append((condition, result, message, args))

    def execute_triggers(self):
        """
        runs each trigger in this environment's triggers,
           for each that has evaluated true, the result function is executed
           and the message is added to the return
        whenever a trigger is completed, it is removed from this environment's triggers
        :return: the aggregate messages from all completed triggers
        """
        Log.info('...')
        messages = None
        for trigger in self.triggers:
            condition, result, message, args = trigger
            if condition(args):
                result()
                self.triggers.remove(trigger)
                if messages is None:
                    messages = message
                else:
                    messages += "\n" + message
        return messages


class Commands(object):
    """
    a listing of the Commands (actions) the game knows about
    """
    HELP, EXIT, NORTH, SOUTH, EAST, WEST, TAKE, THROW, LOCK, UNLOCK = range(10)


class Adventure(object):
    """
    models a running game with ui
    """

    # common game message strings
    M_START = "Welcome to the adventure!"
    M_EXIT = "You have decided to abandon this adventure, farewell!"
    M_COMMAND_ASK = "What shall you do next?"
    M_COMMAND_INVALID = "To '%s' would be an impossible feat." \
                        " What would you like to do instead?"
    M_COMMAND_ERROR = "Something has gone awry when attempting" \
                      " to '%s', but what?"

    def __init__(self, interface_type=UserInterface.JES):
        """
        create a game to play in a given environment
        :param interface_type: the environment you are running in
           (default JES)
        """

        # use the specified UI environment
        self.ui = UserInterface(interface_type)

        # set initial game state
        self.game_over = False
        self.environment = GameEnvironment()
        Log.info("creating a new adventure -- interface_type: %s" % interface_type)

    def check_for_loss(self):
        """
        checks if the player has lost the game, game_over becomes True
        :return: None
        """
        Log.info('...')
        if self.environment.game_is_lost:
            self.game_over = True

    def check_for_win(self):
        """
        checks if the player has won the game, game_over becomes True
        :return: None
        """
        Log.info('...')
        if self.environment.game_is_won:
            self.game_over = True

    def play(self):
        """
        begins running the game
        :return: None
        """
        Log.info('...')
        # show the player the intro message
        self.ui.show(self.M_START)

        # show the player the initial room's info
        self.ui.show(self.environment.current_room.describe())

        # main game loop
        while not self.game_over:
            self.next_command()
            self.check_for_loss()
            self.check_for_win()

    def next_command(self, last_invalid=None, last_impossible=None):
        """
        prompts the user for the next command and evaluates their response
        modifies the prompt depending on whether their last response was
           invalid or impossible due to the game-state
        :param last_invalid: whether the last user-input was invalid
        :param last_impossible: whether the last user-input was
           impossible in the game-state
        :return: None
        """
        Log.info("last_invalid: %s, last_impossible: %s" % (last_invalid, last_impossible))
        # set the message based on last response (correct, invalid, impossible)
        to_ask = self.M_COMMAND_ASK

        if last_invalid is not None:
            to_ask = self.M_COMMAND_INVALID % last_invalid
        elif last_impossible is not None:
            to_ask = last_impossible

        # ask the user for input
        user_in = self.ui.ask(to_ask)

        # parse the user input as a Command (and possibly a parameter -- Thing)
        parsed, param = self.parse_command(user_in)

        # if parsing failed on the Command part, re-run next_command with last_invalid=True
        if parsed is None:
            self.next_command(last_invalid=user_in)
            return

        # try execting the Command (with the parameter)
        executed, message = self.execute_command(parsed, param)

        # if it was not executed (due to game-state) re-run next_command with last=impossible=message
        if not executed:
            self.next_command(last_impossible=message)
            return
        else:
            # it was executed, show the user the message and evaluate any game-state changes
            self.ui.show(message)
            self.notify_state_changes(self.environment.execute_triggers())

    @staticmethod
    def parse_command(input_string):
        """
        parses a user input into a Tuple(String, String) containing
            Command & parameter
        :param input_string: the string to parse
        :return: the Tuple(Command, parameter)
            if the parameter is missing, it will be returned as None
        """
        Log.info("input_string: %s" % input_string)
        split = input_string.split(' ')
        command = split[0]

        param = None if len(split) <= 1 else split[1]

        return getattr(Commands, command.upper(), None), param

    def execute_command(self, command, param):
        """
        attempts to execute a given Command with a given parameter (if applicable)
        :param command: the command to execute
        :param param: the parameter to use
        :return: a Tuple(Boolean, String)
            the bool: whether the execution attempt was successful
            the string: a message to display to the user
        """
        Log.info("command: %s, param: %s" % (command, param))
        if command == Commands.EXIT:
            return self.do_exit()
        if command == Commands.HELP:
            return self.do_help()
        if command == Commands.NORTH:
            return self.environment.go_north()
        if command == Commands.SOUTH:
            return self.environment.go_south()
        if command == Commands.EAST:
            return self.environment.go_east()
        if command == Commands.WEST:
            return self.environment.go_west()
        if command == Commands.TAKE:
            return self.environment.player_take(param)
        if command == Commands.THROW:
            return self.environment.player_throw(param)
        if command == Commands.LOCK:
            return self.environment.player_lock(param)
        if command == Commands.UNLOCK:
            return self.environment.player_unlock(param)
        else:
            return False, self.M_COMMAND_ERROR % command

    def do_exit(self):
        """
        a game-level command to exit the game
        :return: a Tuple(Boolean, String)
           the bool: True -- always will be successful
           the string: the game exit message
        """
        Log.info('...')
        self.game_over = True
        return True, self.M_EXIT

    def do_help(self):
        """
        a game-level command to display game help
        :return: a Tuple(Boolean, String)
           the bool: True -- always will be successful
           the string: the game help message
        """
        Log.info('...')
        return True, self.M_START

    def notify_state_changes(self, message):
        Log.info("message: %s" % message)
        if message is not None:
            self.ui.show(message)


def main():
    """
    convenience function for starting the game
    :return: None
    """
    Log.enabled = True
    game = Adventure(UserInterface.CONSOLE)
    game.play()


# === unit tests =============================================================#
def run_test_suite():
    test_suite = [
        t_room_add_north,
        t_room_add_south,
        t_room_add_thing,
        t_room_get_can_be_target_of,

    ]

    for test in test_suite:
        test()


# --- Room tests -------------------------------------------------------------#
def t_room_add_north():
    subject = Room('subject')
    other = Room('other')
    subject.add_north(other)

    check_true(subject.room_north == other)
    check_true(other.room_south == subject)


def t_room_add_south():
    subject = Room('subject')
    other = Room('other')
    subject.add_south(other)

    check_true(subject.room_south == other)
    check_true(other.room_north == subject)


# todo: add all room directions

def t_room_add_thing():
    subject = Room('subject')
    thing = Thing('thing', 'a test thing')

    check_false(subject.thing_there(thing))
    check_true(subject.thing_missing(thing))
    subject.add_thing(thing)

    check_true(subject.thing_there(thing))
    check_false(subject.thing_missing(thing))


# todo: make_visible, make_invisible

def t_room_get_can_be_target_of():
    subject = Room('subject')
    thing = Thing('thing', 'a test thing')
    thing.add_target_of(Commands.TAKE, 'testing')

    expect = None
    actual = subject.get_can_be_target_of(Commands.TAKE)

    check(expect, actual)
    subject.add_thing(thing)

    expect = thing
    actual = subject.get_can_be_target_of(Commands.TAKE)
    check(expect, actual)


# todo: get_thing *
# todo: describe *

# --- thing tests ------------------------------------------------------------#
# todo add_source_of
# todo add_target_of
# todo remove_source_of
# todo remove_target_of
# todo can_be_target_of *
# todo cannot_be_target_of *
# todo get_target_message_for_action *
# todo can_be_source_of *

# --- player tests -----------------------------------------------------------#
# todo has
# todo get
# todo remove_from_inventory *
# todo item_that_can *

# --- game environment tests -------------------------------------------------#
# todo go_north, go_south, go_east, go_west
# todo player_take *
# todo player_throw *
# todo player_lock *
# todo player_unlock *
# todo win_game
# todo lose_game
# todo add_trigger
# todo execute_triggers *

# --- adventure tests --------------------------------------------------------#
# todo check_for_loss
# todo check_for_win
# todo next_command
# todo parse_command *
# todo execute_command *
# todo do_exit
# todo do_help
# todo notify_state_change *

# === a rudimentary unit testing framework ===================================#
def check(expect, actual):
    caller = sys._getframe(1).f_code.co_name
    result = 'PASS' if expect == actual else 'FAIL'
    print("%s -- %s -- expected: %s, actual: %s" % (caller, result, expect, actual))


def check_true(actual):
    caller = sys._getframe(1).f_code.co_name
    result = 'PASS' if actual else 'FAIL'
    print("%s -- %s -- expected: True, actual: %s" % (caller, result, actual))


def check_false(actual):
    caller = sys._getframe(1).f_code.co_name
    result = 'PASS' if not actual else 'FAIL'
    print("%s -- %s -- expected: False, actual: %s" % (caller, result, actual))
