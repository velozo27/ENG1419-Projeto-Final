
class VideoResolutionHelper(object):
    def __init__(self, cap) -> None:
        self.cap = cap

    def make_1080p(self):
        self.cap.set(3, 1920)
        self.cap.set(4, 1080)

    def make_720p(self):
        self.cap.set(3, 1280)
        self.cap.set(4, 720)

    def make_480p(self):
        self.cap.set(3, 640)
        self.cap.set(4, 480)

    def change_res(self, width, height):
        self.cap.set(3, width)
        self.cap.set(4, height)

    def change_capture(self, cap):
        self.cap = cap