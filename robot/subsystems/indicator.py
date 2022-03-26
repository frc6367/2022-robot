import magicbot
import wpilib


# 12v blinkin colors
SOLID_HOTPINK = 0.57
SOLID_DARKRED = 0.59
SOLID_RED = 0.61
SOLID_REDORANGE = 0.63
SOLID_ORANGE = 0.65
SOLID_GOLD = 0.67
SOLID_YELLOW = 0.69
SOLID_LAWNGREEN = 0.71
SOLID_LIME = 0.73
SOLID_DARKGREEN = 0.75
SOLID_GREEN = 0.77
SOLID_BLUEGREEN = 0.79
SOLID_AQUA = 0.81
SOLID_SKYBLUE = 0.83
SOLID_DARKBLUE = 0.85
SOLID_BLUE = 0.87
SOLID_BLUEVIOLET = 0.89
SOLID_VIOLET = 0.91
SOLID_WHITE = 0.93
SOLID_GRAY = 0.95
SOLID_DARKGRAY = 0.97
SOLID_BLACK = 0.99

NOBALL = [SOLID_BLACK]
ONEBALL = [SOLID_YELLOW]
TWOBALL = [SOLID_GREEN]
REVERSING = [SOLID_RED]
SHOOTING = [SOLID_GOLD, SOLID_ORANGE, SOLID_REDORANGE, SOLID_RED]
CLIMBING = [SOLID_VIOLET]


class Indicator:
    blinkies: wpilib.Spark

    colors = magicbot.will_reset_to(NOBALL)
    blink = magicbot.will_reset_to(False)

    def setup(self) -> None:
        self.timer = wpilib.Timer()
        self.timer.start()

        self.idx = 0
        self.color = self.colors[0]

    def on_enable(self):
        self.timer.reset()

    # these should actually be flags and be combined..

    def set_one_ball(self):
        if self.colors is not SHOOTING:
            self.colors = ONEBALL

    def set_two_balls(self):
        if self.colors is not SHOOTING:
            self.colors = TWOBALL

    def set_shooting(self):
        self.colors = SHOOTING
        self.blink = False

    def set_climbing(self):
        self.colors = CLIMBING

    def set_reversing(self):
        self.colors = REVERSING
        self.blink = True

    def set_in_range(self):
        self.blink = True

    def execute(self):
        if self.timer.advanceIfElapsed(0.2):
            self.idx += 1

            colorIdx = int(self.idx / 2)
            if colorIdx >= len(self.colors):
                self.idx = 0
                colorIdx = 0
                blink = False
            else:
                blink = self.idx % 2

            if blink and self.blink:
                self.color = SOLID_BLACK
            else:
                self.color = self.colors[colorIdx]

        self.blinkies.set(self.color)