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


    # todo: add trigger to reveal hidden doors & alert user of the change
    # todo: show open directions of travel in the room when asking for input

    def describe(self):
        message = self.M_NOW_IN_ROOM % self.name
        list_str = None
        if len(self.things) > 0:
            for thing in self.things:
                if list_str is None:
                    list_str = thing.name
                else:
                    list_str += ', ' + thing.name
            message += '\n' + self.M_INSIDE + list_str
        return message


class Thing(object):
    def __init__(self, name, secret_message=None, direction=None):
        self.name = name
        self.secret_message = secret_message
        self.direction = direction

    def add_secret_message(self, other):
        self.secret_message = other
    #secret message to display upon finding the object

    def add_direction(self, other):
        self.direction = other
        #added direction to indicate what path opens when you fins an item


class Player(object):
    M_TOOK = "You took the %s"

    def __init__(self):
        self.inventory = []


class GameEnvironment(object):
    # A   B
    # |   |
    # C - D - E - H
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
    # H secret room

    def __init__(self):
        self.player = Player()

        r_a = Room('your neighbor\'s room')
        r_b = Room('your room')
        r_c = Room('the far hall')
        r_d = Room('the hallway in front of your room')
        r_e = Room('the office')
        r_f = Room('the recreation room')
        r_g = Room('the lobby')
        r_h = Room('a secret room attached to the office', False)

        t_a = Thing("a suspicious looking [book] in a bookcase")
        t_a.add_secret_message('You hear a rumble as a bookcase to the East moves to reveal a passage')
        t_a.add_direction('EAST')

        r_a.add_south(r_c)
        r_b.add_south(r_d)
        r_c.add_east(r_d)
        r_d.add_east(r_e)
        r_d.add_south(r_f)
        r_e.add_south(r_g)
        r_e.add_east(r_h)
        r_f.add_east(r_g)

        r_e.add_thing(t_a)


        self.current_room = r_b

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
            import re
            if re.compile(r'(' + thing_name + ')').search(thing.name):
                found = thing
                break
        if found is not None:
            self.player.inventory.append(found)
            self.current_room.things.remove(found)
            if found.direction == 'NORTH':
                self.current_room.room_north.is_visible = True # these check which direction to make visible based on the item
            if found.direction == 'EAST':
                self.current_room.room_east.is_visible = True
            if found.direction == 'SOUTH':
                self.current_room.room_south.is_visible = True
            if found.direction == 'WEST':
                self.current_room.room_west.is_visible = True
            return True, self.player.M_TOOK % thing_name + '\n' + found.secret_message # displays the took message along with and endline and the secret message
        else:
            return False, Room.M_NOT_INSIDE % thing_name


class Commands(object):
    HELP, EXIT, NORTH, SOUTH, EAST, WEST, TAKE = range(7)


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

        else:
            return False, self.M_COMMAND_ERROR % command

    def do_quit(self):
        self.game_over = True
        return True, self.M_EXIT

    def do_help(self):
        return True, self.M_START


def main():
    print("adventure game")
    game = Adventure(UserInterface.CONSOLE)
    game.play()
