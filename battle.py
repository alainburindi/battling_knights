import json
from pprint import pprint
from enum import Enum


class STATUS(Enum):
    LIVE = 'LIVE'
    DEAD = 'DEAD'
    DROWNED = 'DROWNED'


class Knight:
    def __init__(self, code, name, position, status, item, attack, defence):
        self.code = code
        self.name = name
        self.position = position
        self.status = status
        self.item = item
        self.attack = attack
        self.defence = defence

    def fight(self, defender):
        # Fight a defender and return the looser.
        total_attack = self.attack + 0 if self.item is None else self.item.attack + 0.5
        total_defence = defender.defence + \
            0 if defender.item is None else defender.item.defence

        return defender if total_attack > total_defence else self

    def to_json(self):
        return [
            self.position, self.status.name, self.item.name if self.item is not None else None,
            self.attack, self.defence
        ]


class Item:
    def __init__(self, code, name, attack, defence, priority, position, equipped):
        self.code = code
        self.name = name
        self.attack = attack
        self.defence = defence
        self.priority = priority
        self.position = position
        self.equipped = equipped

    def to_json(self):
        return [
            self.position, self.equipped
        ]


R = Knight('R', 'Red', [0, 0], STATUS.LIVE, None, 1, 1)
B = Knight('B', 'Blue', [7, 0], STATUS.LIVE, None, 1, 1)
G = Knight('G', 'Green', [7, 7], STATUS.LIVE, None, 1, 1)
Y = Knight('Y', 'Yellow', [0, 7], STATUS.LIVE, None, 1, 1)

A = Item('A', 'Axe', 2, 0, 1, [2, 2], False)
M = Item('M', 'MagicStaff', 1, 1, 2, [5, 2], False)
D = Item('D', 'Dagger', 1, 0, 3, [2, 5], False)
H = Item('H', 'Helmet', 0, 1, 4, [5, 5], False)

knights = [R, B, G, Y]
# this items order is important to avoid sorting by priority
items = [A, M, D, H]


def kill_knight(knight, status=STATUS.DEAD):
    # Function to kill knight.
    knight.status = status
    knight.item = None
    knight.attack = 0
    knight.defence = 0
    return True


def drwon_knight(knight):
    # Function to drwon knight.
    if knight.item is not None:
        drop = knight.item
        drop.holder = None
        drop.equipped = False
        drop.position = list(knight.position)
    knight.position = None
    kill_knight(knight, status=STATUS.DROWNED)
    return True


"""
    Directions illustrating the outcomes of each move.
        x=row, y=column
        N: Same column, row above. (x-1, y)
        S: Same column, row below. (x+1, y)
        E: Same row, column to the right. (x, y+1)
        W: Same row, column to the left. (x, y-1)
"""
directions = {'N': [-1, 0], 'S': [1, 0], 'E': [0, 1], 'W': [0, -1]}


def execute_move(move):
    # Get move_knight
    for knight in knights:
        if move[0] == knight.code:
            move_knight = knight

    direction = directions.get(move[2])

    # Check if move inputs are valid
    if move_knight and move_knight.status == STATUS.LIVE and direction:
        current_position = move_knight.position
        new_position = [current_position[0] + direction[0],
                        current_position[1] + direction[1]]

        if new_position[0] in range(8) and new_position[1] in range(8):
            # Check if knight does not have an item and moves onto a square with item on it.
            if move_knight.item is None:
                for item in items:
                    if item.position == new_position:
                        move_knight.item = item
                        item.equipped = True
                        item.position = None

            # Fight triggered if knight moves to other knight's square
            for defender in knights:
                if defender != move_knight and defender.position == new_position and defender.status == STATUS.LIVE:
                    looser = move_knight.fight(defender)
                    kill_knight(looser)
            move_knight.position = new_position
        else:
            drwon_knight(move_knight)

    return True


data = open('moves.txt').read().split('\n')
moves = data[data.index('GAME-START') + 1:data.index('GAME-END')]

# Iterate through moves,
for move in moves:
    execute_move(move)

knights_state = {
    knight.name.lower(): knight.to_json() for knight in knights
}
items_state = {item.name.lower(): item.to_json() for item in items}

final_state = {**knights_state, **items_state}
pprint(final_state, sort_dicts=False)

# Write final game state to JSON file
with open('final_state.json', 'w') as f:
    json.dump(final_state, f)
