class Walker:
    def __init__(self, pos):
        self.pos = pos
        self.walking = False
        self.destination = None

    def set_destination(self, pos):
        self.destination = pos
