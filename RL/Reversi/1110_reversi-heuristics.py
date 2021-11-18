'''1110 reversi-heuristics
GameCenter 또는 GameCenterPy에서 구동

1. " st 0002"이면 -> onStart()
    - self.turn = int(buf) # 해당 참가자에 turn 번호 부여
    
2. " bd 3333333333333333333030333331113333011233333133333333333333333333" -> onBoard()
    action() -> st, nst, p 
        - st : 현재 상태(점수판) 
        - p : 최대기대값을 가지는 maxp 도출(인공신경망self.model or 총합sum 이용)
            -> preRun()
                - self.send("%04d pt %04d"%(8, p)) : p위치에 미리 놓아보기
                    ex) 0008 pt 0023
                - - sock.recv() : " pr 3333333..."
                - nst : p위치에 놓았을때의 다음 상태(점수판) 미리 계산


    다시 onBoard()
        - 실제로 미리계산된p 위치에 놓고 (현재 계산된 p는 그냥 랜덤 계산.)
            self.send("%04d pt %04d"%(8, p))          
        - 상대방 턴이 놓고 난 후의 현재상태 기록
            self.episode.append(st, self.turn^3) : 현재상태, 다음턴
        - 자신의 턴이 놓고 난 후의 다음상태 기록
            self.episode.append(nst, self.turn) : 다음상태, 현재턴

3. " qt 1747" -> onQuit() (게임이 종료될때)
    17 : white 돌 개수
    47 : black 돌 개수
    승패 결과 표시 :
        - result = w-b if self.turn == 1 else b-w : result 자신의 점수결과
        - win = 0 : 자신이 짐, win=1 비김, win = 2 자신이 이김.

4. buildModel()
    - self.model 생성하기  ->  action에서 이용
         1)레이어, 2)컴파일, 3)가중치설정
    - input_dim = 64, output_dim = 1

    - 가중치를 휴리스틱하게 설정.
    - 가중치가 적용된 nst의 총합이 가장 크도록
         

* 주의점
- action()의 st :
    ref = (0.0, (self.turn==2)*2-1.0, (self.turn==1)*2-1.0, 0.0)
    st = np.array([ref[int(board[i])] for i in range(64)])

    st(현재상태)는 turn^3(상대방턴)과 같이 입력할 것이므로 자신 턴의 돌은 -1로

- preRun()의 nst :
    ref = (0.0, (self.turn==1)*2-1.0, (self.turn==2)*2-1.0, 0.0)
    st = np.array([ref[int(buf[i])] for i in range(64)])

    nst(현재상태)는 turn(자신 턴)과 같이 입력할 것이므로 자신 턴의 돌은 +1 로

* recv()
- 매 자신 turn마다 recv()받아 ' bd 3331012233..'입력받으면 onBoard()실
- preRun에서 둘 수 있는 모든 hints를 돌면서 상태값 받아오는데 recv()
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
        print(needed)
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
        # hints : 이번턴에서 놓을 수 있는 자리
        hints = [i for i in range(64) if board[i] == "0"]
        random.shuffle(hints)
        ref = (0.0, (self.turn==2)*2-1.0, (self.turn==1)*2-1.0, 0.0)
        st = np.array([ref[int(board[i])] for i in range(64)])

        # 놓을 수 있는 자리 중 가장 자신의 돌이 많도록 하는 수(nst의 총합이 가장 크도록 하는 수)
        maxp, maxnst, maxv = -1, None, -100
        for h in hints:
            ret, nst = self.preRun(h) # 미리 h위치에 두고 다음상태(nst)값 받아와
            if not ret: return None, None, -1
            v = self.model.predict(nst.reshape(1, 64))[0, 0]
            if v > maxv: maxp, maxnst, maxv = h, nst, v
            
            
        return st, nst, maxp
    

    # 인공신경망 모델을 생성합니다.
    def buildModel(self):
        # keras sequential을 만드는데
        # 첫번째 레이어는 64x1 형태이고
        # 활성함수는 linear(선형)으로 생성합니다.
        self.model = keras.Sequential([
            keras.layers.Dense(1, input_dim=64, activation='linear'),
            ])
        #self.model.compile(loss='mean_squared_error',optimizer=keras.optimizers.Adam())

        # 현재 모델의 웨이트 값을 읽어옵니다.
        #print(self.model.layers[0].get_weights()[0].shape) 
        #print(self.model.layers[0].get_weights()[1].shape)

        # 경험을 바탕으로 각 꼭짓점 부근은 가중치르 높게주는 등 휴리스틱하게 설정.
        # 현재 모델의 weight 값을 설정합니다.
        w = (
            10, 1, 3, 2, 2, 3, 1, 10,
            1, -5, -1, -1, -1, -1, -5, 1,
            3, -1, 0, 0, 0, 0, -1, 3,
            2, -1, 0, 0, 0, 0, -1, 2,
            2, -1, 0, 0, 0, 0, -1, 2,
            3, -1, 0, 0, 0, 0, -1, 3,
            1, -5, -1, -1, -1, -1, -5, 1,
            10, 1, 3, 2, 2, 3, 1, 10)
        weights = np.array(w, dtype=float).reshape(64, 1) # 인풋(1x64)과 가중치(64x1) -> 아웃풋 스칼라
        bias = np.zeros((1, ))
        self.model.layers[0].set_weights([weights, bias])
        
        
        
quitFlag = False
winlose = [0, 0, 0]
game = Game()

while not quitFlag:
    if not game.connect(): break

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
