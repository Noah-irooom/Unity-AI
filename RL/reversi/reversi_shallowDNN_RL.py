'''
game center 실행후
1. reversi-random :
    무작위로 돌놓기
2. reversi-simple : -> 굳이 인공 신경말 할 필요는 없었음.(학습 안했으니)
    나의 돌이 많아지는 쪽으로 놓기(inference만) 
3. reversi-heuristic : -> 굳이 인공 신경말 할 필요는 없었음.(학습 안했으니)
    점수판을 이용해서 내 점수가 많아지는 쪽으로 돌 놓기
4. ANN - ML -RL 사용(shallow)
    인공 신경망을 이용해서 학습
    인공신경망이 상태를 기록한다 생각하면됨.
    각 에피소드마다 보상이 짝지어지고 매번 새로운 상태의 에피소드를 학습하면서 보상을 보정해나감(alpha값으로)
        - 즉 새로운 상태라고해서 보상이 확 바뀌지 않고 조금만 반영한다.
    random을 70% 이상 이기려면 이걸로 충분히 가능.
5. DNN
*  강화학습은 굳이 keras checkpoint를 사용할 필요는 없다
    - 데이터가 크진 않아서.
*  loss값의 변동이 크면
    - random과 대결하는 것처럼 패턴이 없는데이터일 수 있다.
    - 패턴이 없는데 10^30을 돌리는 건 불가능.
'''
import socket
import random
import time
import numpy as np
import tensorflow as tf
from tensorflow import keras
import os.path

class Game:
    # 학습할 데이터를 저장할 파일 패스를 설정한다.
    cpPath = "deep/cp_{0:06}.ckpt"
    def __init__(self):
        self.gameCount = 0


        # 머신러닝을 위한 파라미터들
        self.epochs = 5         # epoch마다 optimizer에 의해 loss의 '해' 로 근접해 가니까.
        self.batch_size = 32    # batch 마다 weight가 변경이 되는 것. 한번의 epoch은 여러번 weight업데이트된다.
        
        # 강화학습을 위한 파라미터
        self.alpha = 0.1        # 학습률
        self.gamma = 0.99       # 현재 보상을 미래에  얼만큼 반영할지

        # e-greedy(입실론 탐욕) 파라미터들
        self.epsilon = 1.0      # 초기 입실론
        self.epsilonDecay = 0.999 # 입실론 값을 매 에피소드마다 얼마씩 줄어들게 할지
        self.epsilonMin = 0.01  # 학습이 계속될 때의 최소 입실론 값(이정도로는 무조건 랜덤시행하겠다) - 창발성!

        # 인공신경망을 만든다.
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
        self.episode = [] # 놓을때마다 episode 기록
        colors = ("", "White", "Black")
        print(f"Game {self.gameCount+1} {colors[self.turn]}")

    # 한 에피소드가 끝나면 불림
    # 한 에피소드 끝나고 결과에 대한 처리
    def onQuit(self, buf):
        self.gameCount += 1
        w,b = int(buf[:2]), int(buf[2:])
        win = (w > b) - (w < b)
        result = win+1 if self.turn == 1 else 1-win
        winText = ("Lose", "Draw", "Win")
        print(f"{winText[result]} W : {w}, B : {b}")
        # 최종 보상을 선택-  1 : 이긴경우, 0 : 진 경우, 0.5 : 비긴 경우
        # 마지막에 sigmoid를 사용했으니
        reward = result/2
        # 마지막 상태는 더이상 값이 필요 없는 상태
        self.episode[-1] = (self.episode[-1][0], reward)
        # 학습을 위해서 데이터 처리
        x, y = [], []
        # 에피소드를 거꾸로 거슬러 올라가야한다.
        for st, v in self.episode[::-1]:
            rw = (1-self.alpha)*v + self.alpha*reward # 이미 리워드는 그 전의 보상을 반영한 것들.
            x.append(st)
            y.append(rw)
            reward = self.gamma*rw # 현재의 리워드가 미래에 어느정도 반영?
        # 에피소드 값을 이용해서 리플레이를 하도록 한다.
        self.replay(x, y) # 시행에 대한 결과가 리플레이 담겨져 있고 이를 이용해 학습한다.
        return result

    # 여기서 놓을때마다 에피소드르 기록한다.
    def onBoard(self, buf):
        nst, p, v = self.action(buf)
        if p < 0: return False
        self.send("%04d pt %4d"%(8, p))
        self.episode.append((nst, v))
        print("(%d, %d)"%(p/8, p%8), end="")
        return True

    def action(self, board):
        # hints : 이번 턴에서 놓을 수 있는 자리 - board 값.
        # 0 : 놓을 수 있는 empty, 1 : white, 2 : black, 3 : 놓을수 없는 empty
        hints = [i for i in range(64) if board[i] == "0"]
     

        # e-greedy에 의해 입실론 값 확률로 랜덤하게 선택
        if np.random.rand() <= self.epsilon:
            r = random.choice(hints) # 둘 수 있는 곳을 랜덤하게 선택.
            ret, nst = self.preRun(r) # preRun: 미리 돌리기 -> next status : 다음 보드의 모습 나타냄.
            if not ret: return None, -1, 0
            v = self.model.predict(nst.reshape(1, 64))[0, 0] # nst가지고 predict함.
            return nst, r, v
        
        # 놓을 수 있는 자리중 가장 높은 값을 주는 것을 선택
        maxp, maxnst, maxv = -1, None, -100 # maxv가 -1을 다합해도 -64이니까.
        for h in hints:
            ret, nst = self.preRun(h)
            if not ret: return None, -1, 0
            v = self.model.predict(nst.reshape(1,64))[0,0] # nst 1차원(64) -> reshape:(64,1)
            if v > maxv: maxp, mxnst, maxv = h, nst, v                                                
        return nst, maxp, maxv
    

    # 인공신경망 모델을 생성.
    def buildModel(self):
        # keras sequential 
        self.model = keras.Sequential([
                keras.layers.Dense(1024, input_dim=64, activation='sigmoid'),
                keras.layers.Dense(1024, activation='sigmoid'),
                keras.layers.Dense(1024, activation='sigmoid'),
                keras.layers.Dense(1024, activation='sigmoid'),
                keras.layers.Dense(1, activation='sigmoid'),
            ])
        # 설정한 모델을 컴파일 한다.
        self.model.compile(loss='mean_squared_error',
                           optimizer=keras.optimizers.Adam())

        # 학습한 데이터를 읽어서 모델에 적용한다.
        dir = os.path.dirname(Game.cpPath)
        latest = tf.train.latest_checkpoint(dir) # 가장 최근에 저장한 걸 가져와
        # 현재 학습한 것이 없는 경우는 무시하도록 함
        if not latest : return
        print(f"Load weights {latest}")
        # 현재 인공신경망 모델에 저장된 웨이트를 로드한다.
        self.model.load_weights(latest)
        # cp_000000.ckpt, cp_001001.ckpt : 숫자의미 - 현재 학습한 회수.
        idx = latest.find("cp_")
        self.gameCount = int(latest[idx+3:idx+9]) # 뒤의 숫자 가져와도!
        # e-greedy의 입실론 값을 gameCount를 이용해서 업데이트한다.
        self.epsilon *= self.epsilonDecay**self.gameCount
        if self.epsilon < self.epsilonMin: self.epsilon = self.epsilonMin

    # 인공신경망으로 학습을 하기 위한 리플레이
    def replay(self, x, y):
        xarray = np.array(x)
        yarray = np.array(y)

        # xarray 입력, yarray 출력을 이용하여 학습을 진행
        r = self.model.fit(xarray, yarray, epochs = self.epochs, batch_size = self.batch_size)

        # e-greedy 에서 입실론 값을 업데이트 한다.
        if self.epsilon >= self.epsilonMin:
            self.epsilon *= self.epsilonDecay

        # 현재까지 학습한 데이터를 자동 저장한다.
        if self.gameCount%10 != 0: return # 매 열판마다 저장
        saveFile = Game.cpPath.format(self.gameCount)
        print(f"Save weights {saveFile}")
        self.model.save_weights(saveFile)

        
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
            w = game.onQuit(buf)
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
