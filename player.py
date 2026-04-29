class Player:
    def __init__(self, player_id, name):
        self.player_id = player_id
        self.name = name
        self.score = 0
        self.is_drawer = False

    def add_point(self):
        self.score += 1

    def set_drawer_status(self, status):
        self.is_drawer = status

    def __str__(self):
        return f"{self.name}: {self.score} point(s)"