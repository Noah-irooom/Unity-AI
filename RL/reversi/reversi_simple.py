'''
game center 실행후
랜덤하게 두기 -> 딥러닝은 랜덤한것을 70 이기도록
'''
import socket
import random
import time
import numpy as np
import tensorflow as tf
from tensorflow import keras

class Game:
    def __init__(self):
        self.gameCount = 0
        self.buildModel()

    def connect(self):
        while True:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.sock.connect(("127.0.0.1", 8791))
            except socket.error:
                print(f"Socket.error : {socket.error.errno}")
                return False
            except socket.timeout:
                print("Socket timeout")
                time.sleep(1.0)
                continue
            break
        return True

    def close(self):
        self.sock.close()

    def recv(self):
        # 패킷의 길이를 읽어온다.
        buf = b""
        while len(buf) < 4:
            try:
                t = self.sock.recv(4-len(buf))
                if t == None or len(t) == 0: return "et", "Network closed"
            except socket.error:
                return "et", str(socket.error)
            buf += t
        needed = int(buf.decode("ascii"))
        # 패킷 길이만큼 패킷을 읽어온다.
        buf = b""
        while len(buf) < needed:
            try:
                t = self.sock.recv(needed-len(buf))
                if t == None or len(t) == 0: return "et", "Network closed"
            except socket.error:
                return "et", str(socket.error)
            buf += t
        ss = buf.decode("ascii").split()
        if ss[0] == "ab": return "ab", "abort"
        return ss[0], ss[1]

    def send(self, buf):
        self.sock.send(buf.encode("ascii"))

    def preRun(self, p):
        self.send("%04d pr %04d"%(8, p))
        cmd, buf = self.recv()
        if cmd != "pr": return False, None
        ref = (0.0, (self.turn==1)*2-1.0, (self.turn==2)*2-1.0, 0.0)
        st = np.array([ref[int(buf[i])] for i in range(64)])
        return True, st

    def onStart(self, buf):
        self.turn = int(buf)
        self.episode = []
        colors = ("", "White", "Black")
        print(f"Game {self.gameCount+1} {colors[self.turn]}")

    def onQuit(self, buf):
        self.gameCount += 1
        w = int(buf[:2])
        b = int(buf[2:])
        result = w-b if self.turn == 1 else b-w
        winText = ("Lose", "Draw", "Win")
        win = (result == 0) + (result > 0)*2
        print(f"{winText[win]} W : {w}, B : {b}")
        return win, result

    def onBoard(self, buf):
        st, nst, p = self.action(buf)
        if p < 0: return False
        self.send("%04d pt %4d"%(8, p))
        self.episode.append((st, self.turn^3))
        self.episode.append((nst, self.turn))
        print("(%d, %d)"%(p/8, p%8), end="")
        return True

    def action(self, board):
        # hints : 이번 턴에서 놓을 수 있는 자리 - board 값.
        # 0 : 놓을 수 있는 empty, 1 : white, 2 : black, 3 : 놓을수 없는 empty
        hints = [i for i in range(64) if board[i] == "0"]
        ref = (0.0, (self.turn==2)*2-1.0, (self.turn==1)*2-1.0, 0.0) # 흰돌인 것 처럼 속이기 위해서. 
            # self.turn==2은 0 or 1이다.
            # ref는 현재 인공지능이 흰돌이든 검은돌이든 모두 자기턴이 흰돌인 것으로 변환하도록 참조
            # 본인이 검은돌(2)이다. (0, 1, -1, 0)
            # 본인이 흰돌(1)이다. (0, -1, 1, 0)
            # (처음:hints, ,못놓는empty)
        
        st = np.array([ref[int(board[i])] for i in range(64)]) 

        # 놓을 수 있는 자리중 가장 높은 값을 주는 것을 선택
        maxp, maxnst, maxv = -1, None, -100 # maxv가 -1을 다합해도 -64이니까.
        for h in hints:
            _, nst = self.preRun(h)
            #print(nst)
            #maxp = h
            v = self.model.predict(nst.reshape(1,64))[0,0] # nst 1차원(64) -> reshape:(64,1)
                                                            # (0,0) 번째의 점수 값을 지정

            #s = nst.sum() # 더 편한 방법이긴한데 인공신경망을 이용해.
            #print(v, s) # v와 s는 모두 같다.
            if v > maxv: maxp, mxnst, maxv = h, nst, v                                                
        return st, nst, maxp
    

    # 인공신경망 모델을 생성.
    def buildModel(self):
        # keras sequential 을 만드는데, 첫번째 레이어는 64x1 형태이고
        # 활성함수는 linear(선형)으로 설정.
        self.model = keras.Sequential([
                keras.layers.Dense(1, input_dim=64, activation='linear'),
            ])
        # 설정한 모델을 컴파일 한다.
        self.model.compile(loss='mean_squared_error',
                           optimizer=keras.optimizers.Adam())
        # 현재 모델의 웨이트값을 읽어온다. 
        #print(self.model.layers[0].get_weights()[0].shape)# 입력노드에 대한 웨이트
        #print(self.model.layers[0].get_weights()[1].shape)# 바이어스에 대한 웨이트
        # layers[0] : 첫번째 레이어.

        # 현재 모델의 웨이트값을 설정한다.
        weights = np.ones((64,1)) # 입력노드의 웨이트 모두 1로
        bias = np.zeros((1,))     # 바이어스에 대한 웨이트 0으로 설정.
        self.model.layers[0].set_weights([weights,bias])
        # 지금은 weight를 업데이트하지않고 1들과 0으로 정해 inference로만!
        # 자기돌이 많은 쪽으로 두는 방법이니까.
        # 학습이 돼있다 가정하고!
        
    
quitFlag = False
winlose = [0, 0, 0]
game = Game()

while not quitFlag: # 계속 GameCenter에 접속하도록.
    if not game.connect(): break

    episode = []
    while True:
        cmd, buf = game.recv()
        if cmd == "et":
            print(f"Network Error!! : {buf}")
            break
        if cmd == "qt":
            w, r = game.onQuit(buf)
            winlose[w] += 1
            print(f"Wins: {winlose[2]}, Loses: {winlose[0]}, Draws: {winlose[1]}, {winlose[2]*100/(winlose[0]+winlose[1]+winlose[2]):.2f}%" )
            break
        if cmd == "ab":
            print("Game Abort!!")
            break
        if cmd == "st":
            game.onStart(buf)
        elif cmd == "bd":
            if not game.onBoard(buf): break

    game.close()
    time.sleep(1.0)
