'''1110 reversi-deep neural network

GameCenter 또는 GameCenterPy에서 구동
강화학습
    1. 피처 : action 후 nst(다음상태)
    2. 정답 : action 후 보상(보상 = 0.9x현재 기대값 + 0.1x미래 보상(미래가치 반영비율 적용된))

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
        - 1) 탐색 : 랜덤한 위치선택해 학습된 가중치로 기대값 v(0~1) 도출
        - 2) 시행 :
            - model.predict() : (0.9x현재 기대값과 0.1x미래 보상)을 모두 고려한 기대값
            - 모든 hints에 대해 학습된 가중치로 기대값v(0~1) 도출후
            - 가장 높은 기대값 선택( 지도학습에서의 1로 주는 것과 같은 효과)
        


    다시 onBoard()
        - 실제로 미리계산된p 위치에 놓고 (현재 계산된 p는 그냥 랜덤 계산.)
            self.send("%04d pt %04d"%(8, p))          
        - 자신의 턴이 놓고 난 후의 다음상태 기록
            self.episode.append(nst, v) : 자신이 둔 다음상태, 다음상태에서 기대값


3. " qt 1747" -> onQuit() (게임이 종료될때)
    17 : white 돌 개수
    47 : black 돌 개수
    - 승패 결과 표시 :
        - result = 2 : 이겼다, 1 :  비겼을 경우 , 0: 졌을 경우
        - reward = 1 : 이겼다, 0.5 : 비겼을 경우, 0 : 졌다
    - onQuit() -> replay()
        onQuit() :
            - 에피소드의 마지막 상태(nst, v) -> (nst, reward) 로 바꿔
            - reward : 이기면 1, 지면 0, 비기면 0.5
            - 마지막 상태를 시작으로 돌면서, 보상값 정책 설정
                보상 = 0.9*기대값 + 0.1*(미래가치 반영비율gamma이 적용된 보상값)
                    # 보상 =  (현재 가치 + 미래가치)
            - 다음상태 -> x, 보상 -> y  
        replay() : 학습 하기 ( 게임종료 후 상태갑과 보상값으로 학습)
            - 상태(x) : 피쳐(입력)
            - 보상(y) : 정답값(출력)
            - self.model.fit(상태x, 보상y)
                epochs : 전체 에피소드들(한 게임) 5번 학습
                batch_size : 한 epoch중 에피소드들을 배치사이즈(32)만큼 잘라서 학습

4. buildModel()
    - self.model 생성하기  ->  action에서 이용
         1)레이어, 2)컴파일, 3)가중치설정
    - input_dim = 64, output_dim = 1

    - 가중치는 인공신경망으로 학습 시키고,
    - 최종 output은 sigmoid 거쳐 0~1사이값 도출
         

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

import os.path
import socket
import random
import time
import numpy as np
import tensorflow as tf
from tensorflow import keras

class Game:
    cpPath = "deep/cp_{0:06}.ckpt"
    
    def __init__(self):
        self.gameCount = 0

        # 머신러닝을 위한 파라미터들
        self.epochs = 5
        self.batch_size = 32

        # 강화학습을 위한 파라미터들
        self.alpha = 0.1        # 학습률
        self.gamma = 0.99       # 미래 가치 반영률

        # e-greedy(입실론 탐욕) 파라미터들
        self.epsilon = 1.0      # 초기 입실론
        self.epsilonDecay = 0.999   # 입실론 값을 매 에피소드마다 얼마씩?
        self.epsilonMin = 0.01  # 학습이 계속될때 최소 입실론 값
        
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
        w, b = int(buf[:2]), int(buf[2:])
        win = (w > b) - (w < b)
        result = win+1 if self.turn == 1 else 1-win
        winText = ("Lose", "Draw", "Win")
        print(f"{winText[result]} W : {w}, B : {b}")
        # 최종 보상을 선택 : 1 : 이겼다, 0 : 졌다, 0.5 : 비겼을 경우
        reward = result/2
        # 마지막 상태는 더 이상 값이 필요 없는 상태
        self.episode[-1] = (self.episode[-1][0], reward)
        # 학습을 위해서 데이터 처리
        x, y = [], []
        # 에피소드를 거꾸로 거슬러 올라가야한다.
        for st, v in self.episode[::-1]:
            rw = (1-self.alpha)*v + self.alpha*reward
            x.append(st)
            y.append(rw)
            reward = self.gamma*rw
        # 에피소드값을 이용하여 리플레이를 하도록 합니다.
        self.replay(x, y)
        return result

    def onBoard(self, buf):
        nst, p, v = self.action(buf)
        if p < 0: return False
        self.send("%04d pt %4d"%(8, p))
        self.episode.append((nst, v))
        print("(%d, %d)"%(p/8, p%8), end="")
        return True


    def action(self, board):
        # hints : 이번턴에서 놓을 수 있는 자리
        hints = [ i for i in range(64) if board[i] == "0"]
        
        # 1) 탐색 :  e-greedy에 의해 입실론 값 확률로 랜덤하게 선택
        if np.random.rand() <= self.epsilon:
            r = random.choice(hints)        # 랜덤하게 위치 선택
            ret, nst = self.preRun(r)       # 랜덤하게 놓았을 때의 다음 상태 계산
            if not ret: return None, -1, 0  # preRun() 오류시 에러 처리

            # 모델에 미리 설정된 가중치 적용해 기대값 도출(랜덤한 기대값)
            v = self.model.predict(nst.reshape(1, 64))[0, 0]
            return nst, r, v # 랜덤하게 얻은 다음상태nst, 랜덤위치r, 랜덤기대값v

        # 2) 시행 : 미리 설정한 가중치로 계산했을 때 가장 높은 기대값인 상태를 선택
        maxp, maxnst, maxv = -1, None, -100
        for h in hints:                     # 둘수 있는 모든 위치에 대해
            ret, nst = self.preRun(h)       # 미리 다음상태 계산하고
            if not ret: return None, -1, 0
            v = self.model.predict(nst.reshape(1,64))[0, 0]
                # 미리 학습된 가중치 적용하여 기대값 도출
                # v는 sigmoid통해 0~1 사이값이됨.
            if v > maxv: maxp, maxnst, maxv = h, nst, v
        return maxnst, maxp, maxv
    
    
    def buildModel(self):
        self.model = keras.Sequential([
            keras.layers.Dense(1024, input_dim=64, activation='sigmoid'),
            keras.layers.Dense(1024, activation='sigmoid'),
            keras.layers.Dense(1024, activation='sigmoid'),
            keras.layers.Dense(1024, activation='sigmoid'),
            keras.layers.Dense(1, activation='sigmoid'),
        ])
        # 설정한 모델을 컴파일
        self.model.compile(loss='mean_squared_error',optimizer=keras.optimizers.Adam())

        # 학습한 데이터를 읽어서 모델 적용
        dir_pth = os.path.dirname(Game.cpPath)
        latest = tf.train.latest_checkpoint(dir_pth)

        # 현재 학습한 것이 없는 경우는 무시.
        if not latest: return
        print(f"Load weights {latest}")

        # 인공 신경망 모델에 저장된 weight를 로드
        self.model.load_weights(latest)

        # cp_000000.ckpt, cp_001001.ckpt 뒤에 있는 숫자 : 현재 학습한 횟수
        idx = latest.find("cp_")
        self.gameCount = int(latest[idx+3:idx+9])

        # Decaying : 입실론 값을 gameCount를 이용해 업데이트        
        self.epsilon *= self.epsilonDecay**self.gameCount
            # 아직은 모델이 저장되고 다시 불릴때 한번만 decay해주게 되어있음.
        if self.epsilon < self.epsilonMin: self.epsilon = self.epsilonMin

        
    # 인공신경망으로 학습하기 위한 리플레이
    def replay(self, x, y):
        xarray = np.array(x) # 자신이 두고난 상태(다음상태) -> 피처
        yarray = np.array(y) # 자신이 뒀을 때의 보상값(0.9x현 기대값 + 0.1x미래보상) -> 정답

        # xarray : 입력(피처), yarray :출력(정답) -> 학습
        # epochs : 전체 에피소드들(한 게임) 5번 학습
        # batch_size : 한 epoch중 에피소드를 배치사이즈(32)만큼 잘라서 학습
        r = self.model.fit(xarray, yarray, epochs=self.epochs, batch_size = self.batch_size)

        # 한 게임종료후 학습하고 -> e-greedy에서 입실론 값 업데이트
        if self.epsilon > self.epsilonMin:
            self.epsilon *= self.epsilonDecay

        # 현재까지 학습한 데이터 자동 저장
        if self.gameCount%10 != 0: return               # 10번마다 저장
        saveFile = Game.cpPath.format(self.gameCount)   # 저장할 파일명
        print(f"Save weights {saveFile}")
        self.model.save_weights(saveFile)               # 웨이트 값 저장하기
        
quitFlag = False
winlose = [0, 0, 0]
game = Game()

while not quitFlag:
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
