
class FluidSession:
    def __init__(self):
        self.docid = ""
        self.sessid = ""

class FluidTag:
    def __init__(self):
        self.lus = []
        self.tag = ""
        self.sessid = ""
        self.ranges = []

class FluidSegments:
    def __init__(self):
        self.sessid = ""
        self.segments = []
