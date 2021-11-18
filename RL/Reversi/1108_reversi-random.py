'''1108_reversi-random
GameCenter 또는 GameCenterPy에서 구동

1. " st 0002"이면 -> onStart()
    - self.turn = int(buf) # 해당 참가자에 turn 번호 부여
    
2. " bd 3333333333333333333030333331113333011233333133333333333333333333" -> onBoard()
    action() -> st, nst, p 
        - st : 현재 상태(점수판) 
        - p : 놓을 위치(무작위로 결정)
            -> preRun()
                - self.send("%04d pt %04d"%(8, p)) : p위치에 미리 놓아보기
                - sock.recv() : " pr 3333333..."
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

class Game:
    def __init__(self):
        self.gameCount = 0
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
        # 패킷의 길이 읽어옴.
        buf = b""
        while len(buf) < 4: # buffer가 받은게 없다면
            try:
                t = self.sock.recv(4-len(buf))
                if t == None or len(t) == 0: return "et", "Network closed" # 네트워크 연결이 끊긴경우
            except socket.error:
                return "et", str(socket.error)
            buf += t # 버퍼에 읽은헤더를 붙여줌.
        needed = int(buf.decode("ascii")) # 현재 버퍼는 헤더를 가짐(패킷 길이)
        print(needed)
        # 패킷 길이만큼 패킷을 읽어온다.
        buf = b""
        while len(buf) < needed: # buffer가 아직 패킷을 받지 않았다면,
            try:
                t = self.sock.recv(needed-len(buf)) # 패킷 받아
                if t == None or len(t) == 0: return "et", "Network closed" # 네트워크 연결이 끊긴 경우
            except socket.error:
                return "et", str(socket.error)
            buf += t # buffer가 패킷 내용(메시지) 받아.
        ss = buf.decode("ascii").split() # 받은 패킷 메시지를 디코딩
        if ss[0] == "ab": return "ab", "abort" # 메시지가 ab로 시작하면 abort
        return ss[0], ss[1] # 패킷 전달 내용 # cmd, buf : 명령어 + 내용

    def send(self, buf):
        self.sock.send(buf.encode("ascii")) # 메시지 인코딩해서 소켓통해 보내기.
        # 이미 buf는 헤더 + 패킷으로 구성되어 self.send()하게됨.

    # p위치에 놓아주도록 소켓 보내고, pr 소켓 메시지 받아.
    def preRun(self,p):
        # 0008 pr 0017 # 17번 위치에 놓겠다.
        self.send("%04d pr %04d"%(8, p)) # 헤더 + 패킷메시지 세트로 보냄

        # cmd : "pr", buf : 3333333333...3333
        cmd, buf = self.recv() # 소켓 메시지 서버로 부터 받아와.(GameCenter로 부터)
        if cmd != "pr": return False, None # ss[0]은 pr이어야.

        # self.turn==1 이면 (0, 1,-1, 0),  self.turn==2이면 (0, -1, 1, 0) # (Hint, white, black, no hint empty)
        ref = (0.0, (self.turn==1)*2-1.0, (self.turn==2)*2-1.0, 0.0)

        # self.turn==1 이면 333312033...133   ->  00001-1000..100 -> 자신의 turn과 같이 에피소드에 입력
        # self.turn==2 이면 333312033...133   ->  0000-11000..-100 -> 자신의 turn과 같이 에피소드에 입력
        st = np.array([ref[int(buf[i])] for i in range(64)])
        return True, st # 보드판을 보상값의 점수판(상태공간)으로 바꿔줌.

    def onStart(self, buf):
        #print("start buffer", buf)
        self.turn = int(buf) # self.turn 지정
        self.episode = []
        colors = ("", "White", "Black") # turn 1은 white, turn 2 black
        print(f"Game {self.gameCount+1} {colors[self.turn]}") # 
        
    def onQuit(self, buf):
        self.gameCount += 1 # gameCount 추가
        w = int(buf[:2]) # white
        b = int(buf[2:]) # black
        
        # white(turn1) 이 이겼을때, self.turn1이 받는 result +값, self.turn2가 받는 result - 값.
        result = w-b if self.turn == 1 else b-w # turn 1(white) white기준, 2(black) black기준
        winText = ("Lose", "Draw", "Win")
        win = (result == 0) + (result > 0)*2 # 진경우 win=0, 비긴경우: win=1, 이긴경우 win=2
        print(f"{winText[win]} W : {w}, B : {b}") # ex) Win W : , B :
        return win, result

    def onBoard(self, buf):
        st, nst, p = self.action(buf) # buf : board판 받아(33331233...)
        if p < 0: return False # p위치 제대로 받고
        
        self.send("%04d pt %04d"%(8, p)) # 0008 pt 0017 # 17번위치에
        self.episode.append((st, self.turn^3)) # 현재 점수판 상태, 상대방턴 
        self.episode.append((nst, self.turn)) # 다음 상태, 자신턴
        #print(self.episode)
        print("(%d, %d)"%(p/8, p%8), end="") # 위치 출력
        return True

    def action(self, board):
        # hints : 이번턴에서 놓을 수 있는 자리
        hints = [i for i in range(64) if board[i] == "0"]
        # turn 1: (0, -1, 1, 0),  turn 2 : (0, 1, -1, 0)
        ref = (0.0, (self.turn==2)*2-1.0, (self.turn==1)*2-1.0, 0.0)
        # 내가 turn1이면 333312033...133   ->  0000-11000..-100 -> 상대턴 turn^3을 에피소드에 같이 입력위해 거꾸로
        # turn2이면 333312033...133   ->  00001-1000..100 ->  상대턴 turn^3을 에피소드에 같이 입력위해 거꾸로
        st = np.array([ref[int(board[i])] for i in range(64)]) # 현재 상태공간(점수보상판)

        # 놓을 수 있는 자리 중 하나를 무작위로 선택
        p = random.choice(hints)
        _, nst = self.preRun(p) # p위치에 놓았을때의 다음 상태공간(점수판)
        return st, nst, p 

quitFlag = False
winlose = [0, 0, 0] # win이면 인덱스2에 1추가
game = Game()

while not quitFlag:
    # 연결이 됐다면
    if not game.connect(): break

    while True:
        cmd, buf = game.recv() # ss[0] ss[1]:  명령어 패킷내용
        if cmd == "et":   # 에러!
            print(f"Network Error!! : {buf}")
            break

        # "qt 1727"
        if cmd == "qt":   # 그만하겠다.
            w, r = game.onQuit(buf) # win0:짐, win1비김, win2이김/
                                    # result 자신의 점수 결과
            winlose[w] += 1
            # 승률 표시
            print(f"Wins: {winlose[2]}, Loses: {winlose[0]}, Draws: {winlose[1]}, {winlose[2]*100/(winlose[0]+winlose[1]+winlose[2]):.2f}%")
            break
        if cmd == "ab":
            print("Game Abort!!")
            break

        # ex) "st 0002" -> cmd, buffer
        if cmd == "st":
            game.onStart(buf) # 해당 참가자 turn번호 및 색 지정, 에피소드 설정
        # ex) "bd 33...3111333...3333"
        elif cmd == "bd":
            # board 판이 없으면 break
            if not game.onBoard(buf): break 
    game.close()
    time.sleep(1.0) # 1초동안 아무것도 실행하지 않음.

