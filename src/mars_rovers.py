from enum import Enum
from functools import reduce
from typing import Dict, Callable, Iterator, List, Tuple

class AbstractAction(Enum):
    pass

class RotateAction(AbstractAction):
    Left  = "L"
    Right = "R"

class MoveAction(AbstractAction):
    Move  = "M"

class InvalidActionException(Exception):
    pass

class Cardinal(Enum):
    North = "N"
    East  = "E"
    South = "S"
    West  = "W"

class Compass:
    cardinals: List[Cardinal] = list(Cardinal)
    
    @staticmethod
    def rotate(current:Cardinal, turn_to:RotateAction) -> Cardinal:
        direction: int = 1 if turn_to == RotateAction.Right else - 1
        _ , idx = divmod( Compass.cardinals.index(current) + direction , len(Compass.cardinals) )
        return Compass.cardinals[idx]

class WheelSystem:
    MoveCommand = Callable[[int,int],Tuple[int,int]]
    move_north: MoveCommand = lambda x,y: (x,y+1)
    move_east:  MoveCommand = lambda x,y: (x+1,y)
    move_south: MoveCommand = lambda x,y: (x,y-1)
    move_west:  MoveCommand = lambda x,y: (x-1,y)
    move_commands: Dict[Cardinal, MoveCommand] = {
        Cardinal.North: move_north,
        Cardinal.East: move_east,
        Cardinal.South: move_south,
        Cardinal.West: move_west
    }

    @staticmethod
    def move(x: int, y:int, orientation: Cardinal) -> Tuple[int,int]:
        move_command: WheelSystem.MoveCommand = WheelSystem.move_commands[orientation]
        return move_command(x,y)

class Rover:
    def __init__(self, start_x: int = 0, start_y:int = 0, orientation: Cardinal = Cardinal.North):
        self.x: int = start_x
        self.y: int = start_y
        self.orientation: Cardinal = orientation

    def execute(self, action: AbstractAction):
        if isinstance(action, MoveAction):
            self.x, self.y = WheelSystem.move(self.x, self.y, self.orientation)
        elif isinstance(action, RotateAction):
            self.orientation = Compass.rotate(self.orientation, action)
        else:
            raise InvalidActionException(str(action))

    def __str__(self) -> str:
        return f"{self.x} {self.y} {self.orientation.value}"


class MarsPateau:

    class CardinalSymbol(Enum):
        North = "^"
        East  = ">"
        South = "v"
        West  = "<"

    def __init__(self, rows:int, columns:int):
        self.rows = rows
        self.columns = columns
        self.rovers: List[Rover] = list()
        self.cardinal_symbols: Dict[Cardinal, MarsPateau.CardinalSymbol] = {
            Cardinal.North: MarsPateau.CardinalSymbol.North,
            Cardinal.East:  MarsPateau.CardinalSymbol.East,
            Cardinal.South: MarsPateau.CardinalSymbol.South,
            Cardinal.West:  MarsPateau.CardinalSymbol.West,
        }

    def rover_landing(self, rover: Rover):
        self.rovers.append(rover)

    def get_rovers_positions(self) -> str:
        return " ".join(map(str,self.rovers))

    def get_snapshot(self) -> str:
        matrix: List[List[str]] = [["•" for _ in range(self.columns)] for _ in range(self.rows)]
        for rover in self.rovers:
            matrix[rover.y][rover.x] = self.cardinal_symbols[rover.orientation].value
        matrix_str: str = reduce(lambda row_k, row_k1: row_k1 +"\n"+row_k, map(lambda row: " ".join(row), matrix))
        return matrix_str


class MissionControl:

    class RoverCommands:
        def __init__(self, land_command: str, move_commands: str):
            coordinates: List[str] = land_command.split()
            assert len(coordinates) == 3
            
            self.x: int = int(coordinates[0])
            self.y: int = int(coordinates[1])
            self.o: Cardinal = Cardinal(coordinates[2])

            self.move_commands: str = move_commands
        
        def get_landing_params(self) -> Tuple[int,int,Cardinal]:
            return self.x, self.y, self.o

        def get_actions(self) -> Iterator[AbstractAction]:
            for action in self.move_commands:
                if action == MoveAction.Move.value:
                    yield MoveAction.Move
                else:
                    yield RotateAction(action)

    def _parse_input(self, input:str) -> Tuple[int,int,List[RoverCommands]]:
        lines: List[str] = input.split(sep="\n")

        plateau_top_coordinates: List[str] = lines[0].split()
        assert len(plateau_top_coordinates) == 2
        n, m = map(lambda k: int(k), plateau_top_coordinates)
        lines = lines[1:]

        reover_commands_list: List[MissionControl.RoverCommands] = list()
        for coordinates_str, actions_str in zip(lines[0::2], lines[1::2]):
            rover_commands: MissionControl.RoverCommands = MissionControl.RoverCommands(coordinates_str, actions_str)
            reover_commands_list.append(rover_commands)

        return n,m,reover_commands_list

    def __init__(self, input: str):
        n,m,rover_commands_list = self._parse_input(input)
        self.mars_plateau = MarsPateau(n+1,m+1)
        self.rover_commands_list: List[MissionControl.RoverCommands] = rover_commands_list

    def get_mars_plateau(self) -> MarsPateau:
        return self.mars_plateau

    def send_comms_to_rovers(self):
        for rover_commands in self.rover_commands_list:
            landing_x, landing_y, landing_orientation = rover_commands.get_landing_params()
            rover: Rover = Rover(landing_x, landing_y, landing_orientation)
            
            self.mars_plateau.rover_landing(rover)
            for action in rover_commands.get_actions():
                rover.execute(action)


sample_input: str = "5 5\n1 2 N\nLMLMLMLMM\n3 3 E\nMMRMMRMRRM"

mc: MissionControl = MissionControl(sample_input)
mc.send_comms_to_rovers()
print(mc.get_mars_plateau().get_rovers_positions())
print(mc.get_mars_plateau().get_snapshot())