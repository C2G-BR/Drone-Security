from time import time
from datetime import datetime, timedelta
from PIL import Image

class Camera(object):
    def __init__(self):
        self.frames = [Image.open(str(f) + '.jpg') for f in range(1, 4)]
        self.length = len(self.frames)

    def get_frame(self):
        return self.frames[int(time()) % self.length]

class Energy(object):
    def __init__(self):
        self.last_date = datetime.today()
        self.last_energy = 100

    def get_energy(self):
        day = self.last_date.strftime("%Y-%m-%d")
        energy = self.last_energy
        self.last_energy *= 0.95
        self.last_date += timedelta(days=1)
        return day, energy