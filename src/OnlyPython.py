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


SIZE = 12

# %%


def difference(start, end):
    return end - start if end > start else start + SIZE - end


def distance(start, end):
    return min((end - start) % SIZE, (start - end) % SIZE)


@dataclass
class Player:
    position: int = 1
    absolute_position: int = 1
    last_submission: int = 0
    papers: list[Object] = field(default_factory=lambda: [None] * SIZE)
    paper_state: list[int] = field(default_factory=lambda: [None] * SIZE)

    def skip_papers(self):
        self.last_submission += 3
        for i, _ in enumerate(self.paper_state):
            if self.paper_state[i] is None:
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

    def survey(self, planet_type: Object, start, end, result):
        if difference(end, self.position) >= SIZE // 2:
            raise ValueError("survey must be within visible sky")
        n_search_segments = difference(start, end)
        if 1 <= n_search_segments <= 3:
            self.move_forward(4)
        elif 4 <= n_search_segments <= 6:
            self.move_forward(3)
        elif 7 <= n_search_segments <= 9:
            self.move_forward(2)
        else:
            raise ValueError("survey must be in the visible sky segments")

    def target(self, sector_id: int, result: Object):
        self.move_forward(4)

    def research(self):
        self.move_forward(1)

    def locate_x(self):
        self.move_forward(5)

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
    print()
    print(f"SKY: {p.position} -> {(p.position + 4) % SIZE + 1}")
    print()
    print(tabulate(SOLUTION,
        headers=["Object"] + [i+1 for i in range(SIZE)],
        stralign="center"))
    print("===")


def mark_not_present(planet_type, sector):
    match planet_type:
        case Object.COMET:
            SOLUTION[planet_type.value][sector] = "-c-"
        case Object.ASTEROID:
            SOLUTION[planet_type.value][sector] = "-a-"
        case Object.DWARF:
            SOLUTION[planet_type.value][sector] = "-d-"
        case Object.GAS_CLOUD:
            SOLUTION[planet_type.value][sector] = "-g-"
        case Object.TRULY_EMPTY:
            SOLUTION[planet_type.value][sector] = "-e-"
        case Object.PLANET_X:
            SOLUTION[planet_type.value][sector] = "-x-"


# %%

mark_not_present(Object.ASTEROID, 3)
mark_not_present(Object.DWARF, 5)
mark_not_present(Object.GAS_CLOUD, 7)
mark_not_present(Object.GAS_CLOUD, 11)


print_all()


# %%
print("bla-bla")

