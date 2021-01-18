from abc import ABC, abstractmethod
from enum import Enum
from functools import reduce
from typing import Dict, Callable, Iterator, List, Optional, Tuple, cast

class AbstractAction(Enum):
    pass

class RotateAction(AbstractAction):
    Left  = "L"
    Right = "R"

class MoveAction(AbstractAction):
    Move  = "M"

class Observer(ABC):

    @abstractmethod
    def update(self, subject, action: AbstractAction):
        pass

class Observable:
    def __init__(self):
        self.observers: List[Observer] = list()

    def register(self, object: Observer):
        self.observers.append(object)

    def nofity(self, action: AbstractAction):
        for o in self.observers:
            o.update(self, action)

class RoverNotLandedError(Exception):
    pass

class LocationOutOfPlateauError(Exception):
    def __init__(self, x:int, y:int):
        super().__init__(f"{x},{y} out of bounds")

class Cardinal(Enum):
    North = "N"
    East  = "E"
    South = "S"
    West  = "W"

class MarsPlateauLocation:
    def __init__(self, x: int = 0, y:int = 0):
        self.x: int = x
        self.y: int = y

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

class Rover(Observable):
    def __init__(self, orientation: Cardinal):
        super().__init__()
        self.orientation = orientation

    def execute(self, action: AbstractAction):
        if isinstance(action, RotateAction):
            self.orientation = Compass.rotate(self.orientation, action)
        else:
            # Doesn't care about any other action
            pass
        # Notify observers about the action
        self.nofity(action)

class MarsPateau(Observer):

    class CardinalSymbol(Enum):
        North = "^"
        East  = ">"
        South = "v"
        West  = "<"

    def __init__(self, rows:int, columns:int):
        self.rows = rows
        self.columns = columns
        self.plateau: Dict[int, Dict[int, Rover]] = dict()
        self.cardinal_symbols: Dict[Cardinal, MarsPateau.CardinalSymbol] = {
            Cardinal.North: MarsPateau.CardinalSymbol.North,
            Cardinal.East:  MarsPateau.CardinalSymbol.East,
            Cardinal.South: MarsPateau.CardinalSymbol.South,
            Cardinal.West:  MarsPateau.CardinalSymbol.West,
        }

    def _place_rover(self, rover: Rover, x:int, y:int):
        if x<0 or x>=self.columns or y<0 or y>=self.rows:
            raise LocationOutOfPlateauError(x,y)
        if not y in self.plateau:
            self.plateau[y] = dict()
        self.plateau[y][x] = rover

    def _find_rover(self, rover) -> Optional[MarsPlateauLocation]:
        for x in range(self.columns):
            for y in range(self.rows):
                if self.plateau.get(y,{}).get(x) == rover:
                    return MarsPlateauLocation(x,y)
        return None

    def rover_landing(self, rover: Rover, loc: MarsPlateauLocation):
        self._place_rover(rover, loc.x, loc.y)
        rover.register(self)

    def update(self, subject, action: AbstractAction):
        rover: Rover = cast(Rover, subject)
        if isinstance(action, MoveAction):
            current_loc: Optional[MarsPlateauLocation] = self._find_rover(rover)
            if current_loc:
                del self.plateau[current_loc.y][current_loc.x]
                new_x, new_y = WheelSystem.move(current_loc.x, current_loc.y, rover.orientation)
                self._place_rover(rover, new_x, new_y)
            else:
                raise RoverNotLandedError()
        else:
            # Doesn't care about any other action
            pass

    def get_snapshot(self) -> str:
        matrix: List[List[str]] = [
            [self.cardinal_symbols[self.plateau[y][x].orientation].value 
            if self.plateau.get(y,{}).get(x) else "•" 
            for x in range(self.columns)] 
                for y in range(self.rows)]
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
            loc: MarsPlateauLocation = MarsPlateauLocation(landing_x, landing_y)
            rover: Rover = Rover(landing_orientation)
            
            self.mars_plateau.rover_landing(rover, loc)
            for action in rover_commands.get_actions():
                rover.execute(action)


# Test input
sample_input: str = "5 5\n1 2 N\nLMLMLMLMM\n3 3 E\nMMRMMRMRRM"

mc: MissionControl = MissionControl(sample_input)
mc.send_comms_to_rovers()
print(mc.get_mars_plateau().get_snapshot())