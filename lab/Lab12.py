# Lab 12: Adventure Game Enhanced

### authors ###################################################################
# J Asato
# M Robertson
# R Talmage
###############################################################################

# todo: add pydocs to each function

try:
    from JES_shim import showInformation, requestString
except ImportError:
    pass


class UserInterface(object):
    JES, CONSOLE = range(2)

    def __init__(self, interface_type=JES):
        self.interface_type = interface_type

    def show(self, message):
        if self.interface_type == UserInterface.JES:
            showInformation(message)
        else:
            print(message)

    def ask(self, message):
        if self.interface_type == UserInterface.JES:
            return requestString(message)
        else:
            return raw_input(message)


class Room(object):
    M_CANNOT_ADD = "Error: can't add a room to an already used location"
    M_NO_PASSAGE = "You find no passage to the %s."
    M_NOW_IN_ROOM = "You are now in %s."
    M_INSIDE = "Inside you see: "
    M_NOT_INSIDE = "There was no %s in the room."

    def __init__(self, name, is_visible=True):
        self.name = name
        self.is_visible = is_visible
        self.room_north = None
        self.room_south = None
        self.room_east = None
        self.room_west = None
        self.things = []

    def add_north(self, other):
        if self.room_north is not None or other.room_south is not None:
            raise ValueError(self.M_CANNOT_ADD)
        self.room_north = other
        other.room_south = self

    def add_south(self, other):
        if self.room_south is not None or other.room_north is not None:
            raise ValueError(self.M_CANNOT_ADD)
        self.room_south = other
        other.room_north = self

    def add_east(self, other):
        if self.room_east is not None or other.room_west is not None:
            raise ValueError(self.M_CANNOT_ADD)
        self.room_east = other
        other.room_west = self

    def add_west(self, other):
        if self.room_west is not None or other.room_east is not None:
            raise ValueError(self.M_CANNOT_ADD)
        self.room_west = other
        other.room_east = self

    def add_thing(self, thing):
        self.things.append(thing)

    def thing_there(self, thing):
        return self.things.__contains__(thing)

    def thing_missing(self, thing):
        return not self.things.__contains__(thing)

    def make_visible(self):
        self.is_visible = True

    def make_invisible(self):
        self.is_visible = False

    def get_actionable(self, action):
        for thing in self.things:
            if thing.can_be_target_of(action):
                return thing
        return None

    def get_thing(self, name):
        for thing in self.things:
            if thing.name == name:
                return thing
        return None

    # todo: show open directions of travel in the room when asking for input

    def describe(self):
        message = self.M_NOW_IN_ROOM % self.name
        list_str = ""
        if len(self.things) > 0:
            for thing in self.things:
                list_str += "\n    " + thing.desc
                if thing.hint != '':
                    list_str += " (" + thing.hint + ")"

            message += '\n' + self.M_INSIDE + list_str
        return message


class Thing(object):
    def __init__(self, name, desc, hint='', removable=True):
        self.name = name
        self.desc = desc
        self.hint = hint
        self.can_take = removable
        self.source_of = []
        self.target_of = []

    def add_source_of(self, action):
        self.source_of.append(action)

    def add_target_of(self, action, message):
        self.target_of.append((action, message))

    def remove_source_of(self, action):
        self.source_of.remove(action)

    def remove_target_of(self, action):
        to_remove = self._target_action_to_tuple(action)

        if to_remove is not None:
            self.target_of.remove(to_remove)

    def _target_action_to_tuple(self, action):
        for target in self.target_of:
            act, mess = target
            if action == act:
                return target
        return None

    def can_be_target_of(self, action):
        return self._target_action_to_tuple(action) is not None

    def cannot_be_target_of(self, action):
        return not self.can_be_target_of(action)

    def get_target_message_for_action(self, action):
        target = self._target_action_to_tuple(action)
        if target is not None:
            _, message = target
            return message
        else:
            return ''

    def can_be_source_of(self, action):
        for source in self.source_of:
            if action == source:
                return True
        return False


class Player(object):
    M_TOOK = "You took the %s"
    M_CANT_TAKE = "You were unable to find a way to take the %s."

    def __init__(self):
        self.inventory = []

    def has(self, thing_name):
        return self.get(thing_name) is not None

    def get(self, thing_name):
        for thing in self.inventory:
            if thing.name == thing_name:
                return thing
        return None

    def remove_from_inventory(self, thing_name):
        for thing in self.inventory:
            if thing.name == thing_name:
                self.inventory.remove(thing)
                return

    def item_that_can(self, action):
        for item in self.inventory:
            if item.can_be_source_of(action):
                return item
        return None


class GameEnvironment(object):
    # A   B
    # |   |
    # C - D - E - H
    #     |   |
    #     F - G
    #
    # A your neighbor's room
    # B your room (start)
    # C far hall - window
    # D your hall
    # E office - book, key
    # F rec room - baseball
    # G lobby - door (locked)
    # H secret room

    def __init__(self):
        self.player = Player()
        self.game_is_won = False
        self.game_is_lost = False
        self.triggers = []

        r_a = Room('your neighbor\'s room')
        r_b = Room('your room')
        r_c = Room('the far hall')
        r_d = Room('the hallway in front of your room')
        r_e = Room('the office')
        r_f = Room('the recreation room')
        r_g = Room('the lobby')
        r_h = Room('a secret room attached to the office', False)

        t_a = Thing('book', 'a suspicious looking [book] in a bookcase')
        t_b = Thing('key', 'a [key] sitting on the desk')
        t_c = Thing('window', 'a [window] at the end of the hall', 'maybe you can <throw> something at it', False)
        t_d = Thing('door', 'a [door] at the far side of the lobby', 'maybe you can <unlock> it', False)
        t_e = Thing('baseball', 'a [baseball] sitting on a chair')

        t_b.add_source_of(Commands.UNLOCK)
        t_b.add_source_of(Commands.LOCK)
        t_d.add_target_of(Commands.UNLOCK,
                          'The door is unlocked. You have a feeling that freedom is not far away.')
        self.add_trigger(t_d.can_be_target_of, self.win_game, "You win!", Commands.LOCK)

        t_e.add_source_of(Commands.THROW)
        t_c.add_target_of(Commands.THROW, 'The window is now broken with a sizable hole in its center.')
        self.add_trigger(t_c.cannot_be_target_of, self.lose_game, "You lose", Commands.THROW)

        r_a.add_south(r_c)
        r_b.add_south(r_d)
        r_c.add_east(r_d)
        r_d.add_east(r_e)
        r_d.add_south(r_f)
        r_e.add_south(r_g)
        r_e.add_east(r_h)
        r_f.add_east(r_g)

        r_c.add_thing(t_c)

        r_e.add_thing(t_a)
        self.add_trigger(r_e.thing_missing, r_h.make_visible, "A secret room has been revealed.", t_a)

        r_e.add_thing(t_b)
        r_f.add_thing(t_e)

        r_g.add_thing(t_d)

        self.current_room = r_b

    # todo go_dir, take, etc. methods should be on the player
    def go_north(self):
        if self.current_room.room_north is not None:
            if self.current_room.room_north.is_visible:
                self.current_room = self.current_room.room_north
                return True, self.current_room.describe()
        return False, Room.M_NO_PASSAGE % 'north'

    def go_south(self):
        if self.current_room.room_south is not None:
            if self.current_room.room_south.is_visible:
                self.current_room = self.current_room.room_south
                return True, self.current_room.describe()
        return False, Room.M_NO_PASSAGE % 'south'

    def go_east(self):
        if self.current_room.room_east is not None:
            if self.current_room.room_east.is_visible:
                self.current_room = self.current_room.room_east
                return True, self.current_room.describe()
        return False, Room.M_NO_PASSAGE % 'east'

    def go_west(self):
        if self.current_room.room_west is not None:
            if self.current_room.room_west.is_visible:
                self.current_room = self.current_room.room_west
                return True, self.current_room.describe()
        return False, Room.M_NO_PASSAGE % 'west'

    def player_take(self, thing_name):
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
        actionable = self.current_room.get_actionable(Commands.THROW)
        if actionable is not None:
            thing = self.player.get(thing_name)
            if thing is None:
                return True, "You have no %s to even try to throw at the %s." % (thing_name, actionable.name)
            elif thing.can_be_source_of(Commands.THROW):
                result_message = actionable.get_target_message_for_action(Commands.THROW)
                actionable.remove_target_of(Commands.THROW)
                self.player.remove_from_inventory(thing_name)
                return True, "You threw the %s at the %s. \n%s" % (thing_name, actionable.name, result_message)
            else:
                return True, \
                       "You could throw the %s at the %s, but you have a feeling that you'd regret it." \
                       % (thing_name, actionable.name)
        return False, "There was nothing to throw the %s at." % thing_name

    def player_lock(self, thing_name):
        target = self.current_room.get_thing(thing_name)
        if target is None:
            return True, "You look around fruitlessly for a %s to lock." % thing_name
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
            return True, "You find that the %s is already locked." % thing_name
        else:
            return True, "You ponder for a lengthy while, but fail to figure a way to lock the %s." % thing_name

    def player_unlock(self, thing_name):
        target = self.current_room.get_thing(thing_name)
        if target is None:
            return True, "You look around fruitlessly for a %s to unlock." % thing_name
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
            return True, "You find that the %s is already unlocked." % thing_name
        else:
            return True, "You ponder for a lengthy while, but fail to figure a way to unlock the %s." % thing_name

    def win_game(self):
        self.game_is_won = True

    def lose_game(self):
        self.game_is_lost = True

    def add_trigger(self, condition, result, message, args):
        self.triggers.append((condition, result, message, args))

    def execute_triggers(self):
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
    HELP, EXIT, NORTH, SOUTH, EAST, WEST, TAKE, THROW, LOCK, UNLOCK = range(10)


class Adventure(object):
    M_START = "Welcome to the adventure!"
    M_EXIT = "You have decided to abandon this adventure, farewell!"
    M_COMMAND_ASK = "What shall you do next?"
    M_COMMAND_INVALID = "To '%s' would be an impossible feat." \
                        " What would you like to do instead?"
    M_COMMAND_ERROR = "Something has gone awry when attempting" \
                      " to '%s', but what?"

    def __init__(self, interface_type=UserInterface.JES):
        self.game_over = False
        self.ui = UserInterface(interface_type)
        self.environment = GameEnvironment()

    def check_for_loss(self):
        if self.environment.game_is_lost:
            self.game_over = True

    def check_for_win(self):
        if self.environment.game_is_won:
            self.game_over = True

    def play(self):

        self.ui.show(self.M_START)
        self.ui.show(self.environment.current_room.describe())

        while not self.game_over:
            self.next_command()
            self.check_for_loss()
            self.check_for_win()

    def next_command(self, last_invalid=None, last_impossible=None):
        to_ask = self.M_COMMAND_ASK

        if last_invalid is not None:
            to_ask = self.M_COMMAND_INVALID % last_invalid
        elif last_impossible is not None:
            to_ask = last_impossible

        user_in = self.ui.ask(to_ask)

        parsed, param = self.parse_command(user_in)

        if parsed is None:
            self.next_command(last_invalid=user_in)
            return

        executed, message = self.execute_command(parsed, param)
        if not executed:
            self.next_command(last_impossible=message)
            return
        else:
            self.ui.show(message)
            self.notify_state_changes(self.environment.execute_triggers())

    @staticmethod
    def parse_command(input_string):

        split = input_string.split(' ')
        command = split[0]

        param = None if len(split) <= 1 else split[1]

        return getattr(Commands, command.upper(), None), param

    def execute_command(self, command, param):
        if command == Commands.EXIT:
            return self.do_quit()
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

    def do_quit(self):
        self.game_over = True
        return True, self.M_EXIT

    def do_help(self):
        return True, self.M_START

    def notify_state_changes(self, message):
        if message is not None:
            self.ui.show(message)


def main():
    game = Adventure(UserInterface.CONSOLE)
    game.play()

# todo: add unit tests
