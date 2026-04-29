import random


class TurnManager:
    def __init__(self, players):
        self.players = players
        self.turn_order = players[:]
        self.current_drawer_index = 0

    def assign_turn_order(self, randomize=False):
        if randomize:
            random.shuffle(self.turn_order)

        return self.turn_order

    def get_turn_order_names(self):
        return [player.name for player in self.turn_order]

    def get_current_drawer(self):
        for player in self.players:
            player.set_drawer_status(False)

        drawer = self.turn_order[self.current_drawer_index]
        drawer.set_drawer_status(True)
        return drawer

    def move_to_next_drawer(self):
        self.current_drawer_index += 1

        if self.current_drawer_index >= len(self.turn_order):
            self.current_drawer_index = 0