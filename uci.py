import subprocess

class StockfishEngine:
    def __init__(self, path="stockfish-windows-x86-64-avx2.exe"):
        self.engine = subprocess.Popen([path],
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
            )
        self.__init__engine()

    def send(self, command):
        self.engine.stdin.write(command + "\n")
        self.engine.stdin.flush()

    def read(self):
        return self.engine.stdout.readline().strip()

    def __init__engine(self):
        self.send("uci")
        while True:
            line = self.read()
            if line == "uciok":
                break
        
        self.send("isready")
        while True:
            line = self.read()
            if line == "readyok":
                break
        
    def get_best_move(self, depth=15):
        self.send(f"go depth {depth}")
        while True:
            line = self.read()
            if line.startswith("bestmove"):
                return self.uci_to_move(line.split()[1])
            
    def setpos(self, fen):
        self.send(f"position fen {fen}")

    def uci_to_move(self, uci):
        from utils import convert
        start = convert(uci[:2])
        end = convert(uci[2:4])
        promote = None
        if len(uci) == 5:
            promote = uci[4]
        return start, end, promote
    
    def quit(self):
        self.send("quit")
        self.engine.wait()