# Tic-Tae-Toe Random Game
'''1108_tictaetoe_random
랜덤으로 
board 에서 0 : empty, 1 : O, 2 : X
self.board = [0 0 0 0 0 0 0 0 0]

*cf)
# XOR : turn ^= 1 로 놓으면 0 <-> 1 (0이면 1로, 1이면 0)
# turn ^= 3 놓으면 1 <-> 2
'''
import random
class TicTaeToe:
    def __init__(self):
        self.board = [0]*9
        self.aiTurn = random.randrange(1,3) # 1또는 2를 선택. (1선택시 먼저 둠)

    # turn이 pos위치에 놓는다.
    def Put(self, turn, pos):
        self.board[pos] = turn

    # 경기가 끝났는지 검사
    def IsFinished(self):
        # 가로검사
        for i in range(3):
            x = self.board[i*3]
            if x == 0: continue # empty이면 더 볼 필요도 없음.
            isFinish = True
            for j in range(3):
                if x != self.board[i*3+j]: # 0 1 2 / 3 4 5 / 6 7 8
                    isFinish = False
                    break
            if isFinish: return x # turn값(1 또는 2) 반환
        # 세로검사
        for i in range(3):
            x = self.board[i]
            if x == 0: continue
            isFinish = True
            for j in range(3):
                if x != self.board[i+j*3]:
                    isFinish = False
                    break
            if isFinish: return x

        # 대각선 검사 : 좌상단 -> 우하단
        isFinish = True
        x = self.board[0]
        if x != 0: # empty가 아니라면
            for i in range(3):
                if x != self.board[i*4]:
                    isFinish = False
                    break
            if isFinish: return x

        # 대각선 검사 : 우상단 -> 좌하단
        isFinish = True
        x = self.board[2]
        if x != 0:
            for i in range(3):
                if x != self.board[i*2+2]:
                    isFinish = False
                    break
            if isFinish: return x
        
        # 모든 판이 다 찬 경우 -> 비긴 것으로 간주
        isFinish = True
        for i in range(9):
            if self.board[i] == 0:
                isFinish = False
                break
        if isFinish: return 0 # 0이면 비긴 것.
        return -1 # -1이면 계속 진행

    def Print(self):
        tt = (" ", "O", "X") # 0이면 empty
        print("+---+---+---+")
        print(f"| {tt[self.board[0]]} | {tt[self.board[1]]} | {tt[self.board[2]]} |") 
        print("+---+---+---+")
        print(f"| {tt[self.board[3]]} | {tt[self.board[4]]} | {tt[self.board[5]]} |") 
        print("+---+---+---+")
        print(f"| {tt[self.board[6]]} | {tt[self.board[7]]} | {tt[self.board[8]]} |") 
        print("+---+---+---+")

    # 현재 보드 상태를 숫자로 변환 (empty O X -> 0 1 2)
    # 3진법으로 나타낸 9자리 수. ex) 021120120
    def GetState(self):
        state = 0
        for k in self.board: # 3진법형태로 되어있는 self.board
            state = state*3 + k # 3진법 -> 10진법 형태로 변환하기.
            # cf)10진법 -> 3진법 : 반대로 3으로 나눈후 나머지들 취합
        return state

# 모든 상태에 대해서 기대값을 기록할 상태공간 생성
ss = [ 0.0 ] * (3**9) # 보드상태 0 1 2 즉 3가지 경우가 총 9개 칸에 존재 할 수 있으므로.
                      # 총 3**9차원의 벡터(상태) : 각 상태는 학습률이 적용된 보상값 기록
lr = 0.1  # learning rate(lambda)

# 무한하게 게임 진행
while True:
    game = TicTaeToe()
    turn =1
    # 한 에피소드를 저장할 리스트 생성 - 게임마다 새 에피소드 생성
    ep = []
    while game.IsFinished() == -1: # 게임진행중(-1)
        # turn 한번 둘때마다 현재 상태를 에피소드에 저장
        ep.append(game.GetState())

        game.Print()
        cand = [] # 놓을 수 있는 후보 위치

        for i in range(9):
            if game.board[i] == 0: cand.append(i) # 놓을 수 있는 곳이면 따로 보관.

        # 여기가 핵심.
        if turn == game.aiTurn: # turn 이 game.aiTurn이면(즉 O 이면)
            # 후보군 중 랜덤하게 뽑아
            p = random.choice(cand) 
            game.Put(turn, p) # aiTurn은 랜덤하게 두도록.
        else:
            while True:
                p = int(input("pos : ")) # 사용자에게 둘 위치를 받는다.
                if p in cand: break 
            game.Put(turn, p)
        turn ^= 3 # 1과 2를 switch 시키는 역할을 한다.

    # 결과 에피소드를 저장 -  isFinish로 while 빠져나오면
    ep.append(game.GetState())# 마지막 에피소드 

    game.Print()
    rtext = ("Draw","O Win", "X Win")# 0 : 비김, 1 : O이김, 2 : X 이김
    win = game.IsFinished()
    print(rtext[win])
    
    # 에피소드의 결과에 따라서 보상값을 계산한다.
    if win == 1 or win == 2: reward = 1 # 수정..
    else: reward = 0 # 비긴 경우

    print(ep)
    # 에피소드에 저장된 각 상태에 대해
    for e in ep[::-1]: #  수정(역순으로)
        # ex) ep: [0, 243, 4617, 4626, 17748, 17775, 19233] - win:2 홀수개
        # 3**9 의 상태중 10진법으로 나타낸 각 에피소드가 차지하는 특정 상태만
        ss[e] += lr * (reward - ss[e]) # win 2이라면 2번이 놓아 기록된 상태는 보상 1(0.1)로 작성
        reward *= -1
        print(e,':', ss[e])
    yn = input("Do you want more game : ")
    if yn != 'y' and yn != 'Y': break
for i in range(0, 3**9, 9):
    print(ss[i:i+9])

    
