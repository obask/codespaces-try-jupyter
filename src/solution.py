# pylint: disable=missing-docstring
# %%
from dataclasses import dataclass, field
from enum import Enum, auto

from tabulate import tabulate


class Object(Enum):
    COMET = auto()
    ASTEROID = auto()
    DWARF = auto()
    GAS_CLOUD = auto()
    TRULY_EMPTY = auto()
    PLANET_X = auto()

LOG = []
SIZE = 12

def planet_to_char(space_object):
    match space_object:
        case Object.COMET:
            return "C"
        case Object.ASTEROID:
            return "A"
        case Object.DWARF:
            return "D"
        case Object.GAS_CLOUD:
            return "G"
        case Object.TRULY_EMPTY:
            return "E"
        case Object.PLANET_X:
            return "X"


# %%


def difference(start, end):
    return (end - start) % SIZE


def distance(start, end):
    return min((end - start) % SIZE, (start - end) % SIZE)


@dataclass
class Player:
    position: int = 1
    absolute_position: int = 1
    last_submission: int = 0
    papers: list[Object] = field(default_factory=lambda: [None] * SIZE)
    paper_state: list[int] = field(default_factory=lambda: [None] * SIZE)
    completed_x_conference: bool = False

    def skip_papers(self):
        self.last_submission += 3
        for i, _ in enumerate(self.paper_state):
            if self.paper_state[i] is not None:
                self.paper_state[i] += 1

    def submit_papers(self, *items):
        for i, x in items:
            self.papers[i-1] = x
            self.paper_state[i-1] = 0
        self.skip_papers()

    def confirm_hypotesys(self, i):
        self.papers[i-1] = None
        self.paper_state[i-1] = None

    def move_forward(self, steps: int):
        self.position = (self.position - 1 + steps) % SIZE + 1
        self.absolute_position += steps

    def survey(self, planet_type: Object, begin, end, result):
        LOG.append(f"{planet_to_char(planet_type)} {begin}-{end}\t=> {result}")
        if difference(begin, self.position) >= SIZE // 2:
            raise ValueError(f"survey must start within visible sky: {begin=}")
        if difference(self.position, end) >= SIZE // 2:
            raise ValueError(f"survey must end within visible sky: {end=}")
        n_search_segments = difference(begin, end) + 1
        print(f"{n_search_segments = }")
        if 1 <= n_search_segments <= 3:
            self.move_forward(4)
        elif 4 <= n_search_segments <= 6:
            self.move_forward(3)
        elif 7 <= n_search_segments <= 9:
            self.move_forward(2)
        else:
            raise ValueError(
                f"survey must be in the visible sky segment; {n_search_segments = }")

    def target(self, sector_id: int, result: Object):
        self.move_forward(4)

    def research(self, text=""):
        self.move_forward(1)
        LOG.append(f"Res {text}")

    def locate_x(self):
        self.move_forward(5)

    def planet_x_conference(self):
        self.completed_x_conference = True
        LOG.append("X&G Conf")



p = Player()

# %%

SOLUTION = [["?"] * (SIZE+1) for _ in range(6)]

SOLUTION[0][0] = "comet"
SOLUTION[1][0] = "asteroid"
SOLUTION[2][0] = "dwarf"
SOLUTION[3][0] = "gas cloud"
SOLUTION[4][0] = "empty"
SOLUTION[5][0] = "planet x"


def print_all():
    print("=== GAME STATE ===")
    print(f"POS: {p.absolute_position}")
    print(f"SKY: {p.position} -> {(p.position + 4) % SIZE + 1}")
    print()
    print("LOG:")
    print("---")
    for line in LOG:
        print(line)
    print("---")
    print()
    print(tabulate(SOLUTION,
                   headers=["BOARD"] + [i+1 for i in range(SIZE)],
                   stralign="center"))
    print("===")


def mark_not_present(planet_type, sector):
    SOLUTION[planet_type.value][sector] = f"-{planet_to_char(planet_type).lower()}-"


# %%
if __name__ == "__main__":
    mark_not_present(Object.GAS_CLOUD, 2)
    mark_not_present(Object.GAS_CLOUD, 5)
    mark_not_present(Object.DWARF, 7)
    mark_not_present(Object.ASTEROID, 11)

    p.survey(Object.ASTEROID, 1, 6, result=3)
    p.research("A&C")
    p.skip_papers()
    p.survey(Object.COMET, 5, 7, result=1)
    p.skip_papers()
    p.survey(Object.ASTEROID, 9, 12, result=0)
    p.target(3, result=Object.DWARF)
    p.planet_x_conference()
    p.research("G&A")
    p.locate_x()

    print_all()

