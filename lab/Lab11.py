# Lab 11: Adventure Game

### authors ###################################################################
# J Asato
# M Robertson
# R Talmage
###############################################################################

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

    def __init__(self, name):
        self.name = name
        self.room_north = None
        self.room_south = None
        self.room_east = None
        self.room_west = None

    def add_north(self, other):
        """
        adds a room in the north position for this room
        adds this room to the south of the other room
        :param other: the other room to attach
        :return: void/Unit
        """
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


class GameEnvironment(object):
    # A   B
    # |   |
    # C - D - E
    #     |   |
    #     F - G
    #
    # A your neighbor's room
    # B your room (start)
    # C far hall
    # D your hall
    # E office
    # F rec room
    # G lobby

    def __init__(self):
        a = Room('your neighbor\'s room')
        b = Room('your room')
        c = Room('the far hall')
        d = Room('the hallway in front of your room')
        e = Room('the office')
        f = Room('the recreation room')
        g = Room('the lobby')

        a.add_south(c)
        b.add_south(d)
        c.add_east(d)
        d.add_east(e)
        d.add_south(f)
        e.add_south(g)
        f.add_east(g)

        self.current_room = b

    def go_north(self):
        if self.current_room.room_north is not None:
            self.current_room = self.current_room.room_north
            return True, Room.M_NOW_IN_ROOM % self.current_room.name
        return False, Room.M_NO_PASSAGE % 'north'

    def go_south(self):
        if self.current_room.room_south is not None:
            self.current_room = self.current_room.room_south
            return True, Room.M_NOW_IN_ROOM % self.current_room.name
        return False, Room.M_NO_PASSAGE % 'south'

    def go_east(self):
        if self.current_room.room_east is not None:
            self.current_room = self.current_room.room_east
            return True, Room.M_NOW_IN_ROOM % self.current_room.name
        return False, Room.M_NO_PASSAGE % 'east'

    def go_west(self):
        if self.current_room.room_west is not None:
            self.current_room = self.current_room.room_west
            return True, Room.M_NOW_IN_ROOM % self.current_room.name
        return False, Room.M_NO_PASSAGE % 'west'


class Commands(object):
    HELP, EXIT, NORTH, SOUTH, EAST, WEST = range(6)


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

    def play(self):

        self.ui.show(self.M_START)
        self.ui.show(Room.M_NOW_IN_ROOM % self.environment.current_room.name)

        while not self.game_over:
            self.next_command()

    def next_command(self, last_invalid=None, last_impossible=None):
        to_ask = self.M_COMMAND_ASK

        if last_invalid is not None:
            to_ask = self.M_COMMAND_INVALID % last_invalid
        elif last_impossible is not None:
            to_ask = last_impossible

        user_in = self.ui.ask(to_ask)

        parsed = self.parse_command(user_in)

        if parsed is None:
            self.next_command(last_invalid=user_in)
            return

        executed, message = self.execute_command(parsed)
        if not executed:
            self.next_command(last_impossible=message)
            return
        else:
            self.ui.show(message)

    @staticmethod
    def parse_command(input_string):
        return getattr(Commands, input_string.upper(), None)

    def execute_command(self, command):
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

        else:
            return False, self.M_COMMAND_ERROR % command

    def do_quit(self):
        self.game_over = True
        return True, self.M_EXIT

    def do_help(self):
        return True, self.M_START


def main():
    print("adventure game")
    game = Adventure(UserInterface.JES)
    game.play()
