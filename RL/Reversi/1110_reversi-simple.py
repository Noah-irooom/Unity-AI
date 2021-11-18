'''1110 reversi-simple
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

    - 가중치 모두 1로 설정 =  인풋의 모든 값을더하는 것과 같은 결과.
    - 자신의 돌이 가장 많도록 하는 수(nst의 총합이 가장 크도록)
         

* 주의점
- action()의 st :
    ref = (0.0, (self.turn==2)*2-1.0, (self.turn==1)*2-1.0, 0.0)
    st = np.array([ref[int(board[i])] for i in range(64)])

    st(현재상태)는 turn^3(상대방턴)과 같이 입력할 것이므로 자신 턴의 돌은 -1로

- preRun()의 nst :
    ref = (0.0, (self.turn==1)*2-1.0, (self.turn==2)*2-1.0, 0.0)
    st = np.array([ref[int(buf[i])] for i in range(64)])

    nst(현재상태)는 turn(자신 턴)과 같이 입력할 것이므로 자신 턴의 돌은 +1 로
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
        self.buildModel() # self.model 생성하기.

    # 1. 접속하기
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
        while len(buf) < 4: # buffer가 받은게 없다면
            try:
                t = self.sock.recv(4-len(buf))
                if t == None or len(t) == 0: return "et", "Network closed" # 받은게 없으면 에러처리
            except socket.error:
                return "et", str(socket.error)
            buf += t # buffer는 4만큼(패킷 길이) 받아.
        needed = int(buf.decode("ascii"))# 디코딩
        #print(needed)
        # 패킷 길이만큼 패킷을 읽어온다.
        buf = b""
        while len(buf) < needed:
            try:
                t = self.sock.recv(needed-len(buf))
                if t == None or len(t) == 0: return "et", "Network closed"
            except socket.error:
                return "et", str(socket.error)
            buf += t
        ss = buf.decode("ascii").split() # 패킷 메시지 디코딩
        #print("needed",buf)
        if ss[0] == "ab": return "ab", "abort"
        return ss[0], ss[1]

    def send(self, buf):
        self.sock.send(buf.encode("ascii")) # 패킷 보낼때는 인코딩

    # p위치에 미리 놓고 다음상태 계산하기
    def preRun(self, p):
        self.send("%04d pr %04d"%(8, p))    # 미리 p위치에 둬서 다음상태(nst)반환
        cmd, buf = self.recv()              # recv()
        if cmd != "pr": return False, None

        # 해당 참가자가 turn1 -> (0, 1, -1, 0)
        # 333312033...133   ->  00001-1000..100
        ref = (0.0, (self.turn==1)*2-1.0, (self.turn==2)*2-1.0, 0.0) 
        st = np.array([ref[int(buf[i])] for i in range(64)]) # 보드판 -> 점수판(상태공간)
        return True, st # nst를 의미

    # ex) st 0002
    def onStart(self, buf):
        self.turn = int(buf) # self.turn 지정
        self.episode = []   
        colors = ("", "White", "Black") # turn 1은 white, turn 2 black
        print(f"Game {self.gameCount+1} {colors[self.turn]}")

    # ex) qt 1747
    def onQuit(self, buf):
        self.gameCount += 1 # gameCount 추가
        w = int(buf[:2])    # white 개수
        b = int(buf[2:])    # black 개수

        # 자신의 점수 결과
        result = w-b if self.turn == 1 else b-w
        winText = ("Lose", "Draw", "Win")
        win = (result == 0) + (result > 0)*2 # 자신이 지면 0, 비기면 1, 이기면 2
        print(f"{winText[win]}!  White : {w}개, Black : {b}개")
        return win, result

    # 실제 두는곳 (미리 다음상태가 계산된 p를 가지고)
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
        ref = (0.0, (self.turn==2)*2-1.0, (self.turn==1)*2-1.0, 0.0)
        st = np.array([ref[int(board[i])] for i in range(64)])

        ''' 핵심 '''
        # 놓을 수 있는 자리 중 가장 높은 값을 주는 것 선택
        maxp, maxnst, maxv = -1, None, -100
        for h in hints:             # 둘 수 있는 곳 전부에 대하여
            _, nst = self.preRun(h) # 자신 턴이 뒀을 때의 다음 상태 계산

        
            # 가중치 미리 설정된 모델이 Predict만 하도록
            # nst의 총 합이 최대가 되는(자신의 돌이 가장 많도록 하는 수)
            v = self.model.predict(nst.reshape(1, 64))[0, 0]  # nst.reshape(1, 64) : 인풋 크기 설정
            #print(self.model.predict(nst.reshape(1, 64)))

            #s = nst.sum()
            #print(v,s) # 서로같음(인공신경망 레이어 사용필요가 없긴함.)
            # 최대 기대값 가지는 p, nst, v 업데이트
            if v > maxv: maxp, maxnst, maxv = h, nst, v

        return st, maxnst, maxp 


    '''핵심'''
    # Neural Network model 생성 - self.model의 1)레이어, 2)컴파일, 3)가중치설정
    def buildModel(self):
        # 첫번째 레이어 input dim 64 활성함수는 linear(선형)으로 생성.
        self.model = keras.Sequential([
            keras.layers.Dense(1, input_dim=64, activation='linear'), # 출력 스칼라
            ])
        # self.model.compile(loss="mean_squared_error", optimizer=keras.optimizers.Adam())

        # 현재 모델의 weight값 확인
        #print(self.model.layers[0].get_weights()[0].shape) # 인덱스0 : weights # 64x1
        #print(self.model.layers[0].get_weights()[1].shape) # 인덱스1 : bias

        # 현재 모델의 weight 값을 설정
        weights = np.ones((64,1))   # 인풋(1x64) 과 가중치(64x1) 행렬곱 => 1x1의 스칼라 도출
        bias = np.zeros((1,))       # bias 없는 걸로 설정
        self.model.layers[0].set_weights([weights, bias]) # 가중치 임의 설정

        # 가중치 모두 1로 설정했기 때문에 행렬곱해도 그냥 인풋의 모든 값을더하는 것과 같은 결과.

quitFlag = False
winlose = [0, 0, 0] # 0:자신이 짐, 1: 비김, 2: 자신이 이김.
game = Game()

while not quitFlag:
    # 매 게임마다 소켓 접속 성공하면 계속 진행.
    if not game.connect(): break

    episode = []
    while True:
        cmd, buf = game.recv()
        if cmd == "et":
            print(f"Network Error!! : {buf}")
            break
        # qt 1727
        if cmd == "qt":
            w, r = game.onQuit(buf)
            winlose[w] += 1
            print(f"Wins: {winlose[2]}, Loses: {winlose[0]}, Draws: {winlose[1]}, {winlose[2]*100/(winlose[0]+winlose[1]+winlose[2]):.2f}%" )
            break
        if cmd == "ab":
            print("Game Abort!!")
            break
        # st 0002
        if cmd == "st":
            game.onStart(buf)
        # bd 33...3111333...3333
        elif cmd == "bd":
            if not game.onBoard(buf): break

    game.close() # 매 게임종료시 소켓 통신 종료하고 위에서 다시 접속
    time.sleep(1.0)
