# pylint: disable=missing-docstring
from dataclasses import dataclass, field
from enum import Enum, auto
from telnetlib import GA

from tabulate import tabulate

from z3 import *

# [gharrma] This is a test.


def get_sector(pos: int):
    return BOARD[(pos-1) % SIZE]


SOLVER = Solver()
SIZE = 12

SpaceBodySort, (comet, asteroid, dwarf, gas_cloud, truly_empty, planet_x) = EnumSort('ObjectSort', ['COMET', 'ASTEROID', 'DWARF',
                                                                                                    'GAS_CLOUD', 'TRULY_EMPTY', 'PLANET_X'])


BOARD = [Const(f'X{i+1}', SpaceBodySort) for i in range(SIZE)]

# s = Solver()

# [s.add(x != comet) for x in BOARD]

# s.add(get_sector(11) != asteroid)

# s.check()

ALL_OBJECTS = [comet, asteroid, dwarf, gas_cloud, truly_empty, planet_x]

LOG = []


def planet_to_char(space_object: DatatypeRef):
    return {
        comet: "c",
        asteroid: "a",
        dwarf: "d",
        gas_cloud: "g",
        truly_empty: "e",
        planet_x: "x",
    }[space_object]


def difference(start, end):
    return (end - start) % SIZE


def distance(start, end):
    return min((end - start) % SIZE, (start - end) % SIZE)


@dataclass
class TheSearchForPlanetX:
    position: int = 1
    absolute_position: int = 1
    last_submission: int = 1
    papers: list[DatatypeRef] = field(default_factory=lambda: [None] * SIZE)
    paper_state: list[int] = field(default_factory=lambda: [None] * SIZE)
    completed_x_conference: bool = False

    def submit_papers(self, *items):
        for i, x in items:
            self.papers[i-1] = x
            self.paper_state[i-1] = 0
        self.last_submission += 3
        for i, _ in enumerate(self.paper_state):
            if self.paper_state[i] is not None:
                self.paper_state[i] += 1

    def confirm_hypotesys(self, i):
        self.papers[i-1] = None
        self.paper_state[i-1] = None

    def move_forward(self, steps: int):
        self.position = (self.position - 1 + steps) % SIZE + 1
        self.absolute_position += steps

    def survey(self, planet_type: DatatypeRef, begin, end, result):
        # SOLVER.add(PbEq([(get_sector(i) == planet_type, True) for i in range(begin, end+1)], result))
        if end > begin:
            sliced = BOARD[begin-1:end]
        else:
            sliced = BOARD[begin-1:] + BOARD[:end]
            # print(f"sliced = {sliced}")
            # print(f"len = {len(sliced)}")
        if planet_type == truly_empty:
            SOLVER.add(PbEq([Or(X == truly_empty, X == planet_x) for X in sliced], result))
        else:
            SOLVER.add(PbEq([(X == planet_type, True) for X in sliced], result))


        # LOG.append(f"{planet_to_char(planet_type)} {begin}-{end}\t=> {result}")
        # if difference(begin, self.position) >= SIZE // 2:
        #     raise ValueError(f"survey must start within visible sky: {begin=}")
        # if difference(self.position, end) >= SIZE // 2:
        #     raise ValueError(f"survey must end within visible sky: {end=}")
        # n_search_segments = difference(begin, end) + 1
        # # print(f"{n_search_segments = }")
        # if 1 <= n_search_segments <= 3:
        #     self.move_forward(4)
        # elif 4 <= n_search_segments <= 6:
        #     self.move_forward(3)
        # elif 7 <= n_search_segments <= 9:
        #     self.move_forward(2)
        # else:
        #     raise ValueError(
        #         f"survey must be in the visible sky segment; {n_search_segments = }")

    def target(self, sector_id: int, result: DatatypeRef):
        self.move_forward(4)

    def research(self, text=""):
        self.move_forward(1)
        LOG.append(f"Research  {text}")

    def locate_x(self):
        self.move_forward(5)

    def planet_x_conference(self, text=""):
        self.completed_x_conference = True
        LOG.append("X&G Conf")


GAME = TheSearchForPlanetX()


def get_table():
    return [[validate(Xi, object_sort) for Xi in BOARD]
            for object_sort in ALL_OBJECTS]


def print_papers():
    tmp = []
    for state_id in range(4):
        tmp.append([planet_to_char(GAME.papers[i]) if GAME.paper_state[i] == state_id else "."
                   for i in range(SIZE)])
    print(tabulate(tmp, showindex="always", tablefmt="grid"))


def print_all():
    print(tabulate(get_table(),
                   headers=[i+1 for i in range(SIZE)],
                   stralign="center",
                   showindex=ALL_OBJECTS))
    print()
    # print("=== GAME STATE ===")
    # print_papers()
    if GAME.absolute_position - GAME.last_submission >= 3:
        # print(f"{p.last_submission = }")
        print("!PLEASE SUBMIT YOUR PAPERS!")
    if GAME.absolute_position > 10 and not GAME.completed_x_conference:
        print("!TIME FOR X CONFERENCE!")
    if any(x == 3 for x in GAME.paper_state):
        print("!DON'T FORGET PEER REVIEW!")
    print(f"POS: {GAME.absolute_position}")
    print(f"SKY: {GAME.position} -> {(GAME.position + 4) % SIZE + 1}")
    print()
    print("GAME LOG:")
    # print("---")
    for line in LOG:
        print("\t", line)
    print("---")
    print()


DEFINITELY_FALSE = [None] * SIZE


def mark_not_present(planet_type: DatatypeRef, pos: int):
    DEFINITELY_FALSE[pos-1] = planet_type


def validate(space_body, expected) -> str:
    if SOLVER.check(space_body != expected) == unsat:
        return f"{planet_to_char(expected).upper()}"
    elif SOLVER.check(space_body == expected) == unsat:
        return f"-{planet_to_char(expected).lower()}-"
    else:
        return "?"


USAGE = """
    mark_not_present(GAS_CLOUD, 2)
    mark_not_present(GAS_CLOUD, 5)
    mark_not_present(DWARF, 7)
    mark_not_present(ASTEROID, 11)

    p.survey(ASTEROID, 1, 6, result=3)
    p.research("A&C")
    p.submit_papers((5, ASTEROID))
    p.survey(COMET, 5, 7, result=1)
    p.submit_papers((3, COMET))
    p.survey(ASTEROID, 9, 12, result=0)
    p.submit_papers()
    p.planet_x_conference()
    # p.research("---")
    # p.submit_papers()
    # p.target(3, result=DWARF)
    # p.research("G&A")
    # p.locate_x()

"""

# PRECONDITIONS
primes = [2, 3, 5, 7, 11]
for i in range(1, 13):
    if i not in primes:
        SOLVER.add(get_sector(i) != comet)

# s.add(PbEq([(c5, True), (c7, True)], 1))

SOLVER.add(PbEq([(get_sector(i) == asteroid, True) for i in range(12)], 4))
SOLVER.add(PbEq([(get_sector(i) == comet, True) for i in range(12)], 2))
SOLVER.add(PbEq([(get_sector(i) == dwarf, True) for i in range(12)], 1))
SOLVER.add(PbEq([(get_sector(i) == gas_cloud, True) for i in range(12)], 2))
SOLVER.add(PbEq([(get_sector(i) == truly_empty, True) for i in range(12)], 2))
SOLVER.add(PbEq([(get_sector(i) == planet_x, True) for i in range(12)], 1))

for i in range(1, 13):
    SOLVER.add(
        Or(
            Not(get_sector(i) == asteroid),
            Or(
                get_sector(i-1) == asteroid,
                get_sector(i+1) == asteroid
            )
        )
    )
    SOLVER.add(
        Or(
            Not(get_sector(i) == dwarf),
            And(
                get_sector(i-1) != planet_x,
                get_sector(i+1) != planet_x
            )
        )
    )
    SOLVER.add(
        Implies(get_sector(i) == gas_cloud,
            Or(
                get_sector(i-1) == truly_empty,
                get_sector(i+1) == truly_empty
            )
        )
    )


if __name__ == "__main__":

    # mark_not_present(GAS_CLOUD, 3)
    SOLVER.add(get_sector(3) != gas_cloud)
    # mark_not_present(ASTEROID, 5)
    SOLVER.add(get_sector(5) != asteroid)
    # mark_not_present(DWARF, 7)
    SOLVER.add(get_sector(7) != dwarf)
    # mark_not_present(DWARF, 11)
    SOLVER.add(get_sector(11) != dwarf)
    GAME.survey(asteroid, 1, 3, result=2)
    # GAME.submit_papers()
    GAME.survey(comet, 5, 7, result=1)
    # GAME.target(11, result=COMET)
    SOLVER.add(get_sector(11) == comet)
    # GAME.planet_x_conference("X&D")
    for i,_ in enumerate(BOARD):
        SOLVER.add(Implies(BOARD[i] == dwarf, BOARD[i-6] != planet_x))
    # GAME.submit_papers((11, COMET))
    # GAME.submit_papers()
    GAME.survey(asteroid, 3, 5, result=0)
    for i,Xi in enumerate(BOARD):
        for j,Xj in enumerate(BOARD):
            if i <= j:
                continue
            SOLVER.add(Implies(And(Xi == gas_cloud, distance(j,i) > 4), Xj != gas_cloud))

    GAME.survey(gas_cloud, 9, 10, result=1)
    GAME.survey(dwarf, 1, 6, result=1)


# is_gas_cloud = Function(SpaceBodySort, BitVecSort(8), BoolSort())
# SOLVER.add(ForEach([xi,xj, pos], Implies(is_gas_cloud(xi, pos) , ... )))

    # GAME.submit_papers((1, ASTEROID), (2, ASTEROID))
    # GAME.target(7, result=ASTEROID)


    print_all()


# p(x) => x > 5
