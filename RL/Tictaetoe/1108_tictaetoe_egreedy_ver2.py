'''1108_tictaetoe_egreedy
exploration and exploitation : 탐색과 시행
-> decaying epsilon exploration
    - 입실론만큼 탐색을 하되, 점점 줄여나가는 방식으로

'''
# Tic-Tae-Toe e-greedy Game
import random

class TicTaeToe:
    def __init__(self):
        self.board = [0]*9
        self.aiTurn = random.randrange(1, 3)

    # turn이 pos 위치에 놓는다.
    def Put(self, turn, pos):
        self.board[pos] = turn

    # 경기가 끝났는지 검사
    def IsFinished(self):
        #  가로 검사
        for i in range(3):
            x = self.board[i*3]
            if x == 0: continue
            isFinish = True
            for j in range(3):
                if x != self.board[i*3+j]:
                    isFinish = False
                    break
            if isFinish: return x
        #   세로 검사
        for i in range(3):
            x = self.board[i]
            if x == 0: continue
            isFinish = True
            for j in range(3):
                if x != self.board[i+j*3]:
                    isFinish = False
                    break
            if isFinish: return x
        #  대각선 검사
        isFinish = True
        x = self.board[0]
        if x != 0:
            for i in range(3):
                if x != self.board[i*4]:
                    isFinish = False
                    break
            if isFinish: return x
        #  대각선 검사
        isFinish = True
        x = self.board[2]
        if x != 0:
            for i in range(3):
                if x != self.board[i*2+2]:
                    isFinish = False
                    break
            if isFinish: return x
        # 모든 판이 다 차면 -> 비긴 것으로 간주
        isFinish = True
        for i in range(9):
            if self.board[i] == 0:
                isFinish = False
                break
        if isFinish: return 0
        return -1

    def Print(self):
        tt = (" ", "O", "X")
        print("+---+---+---+")
        print(f"| {tt[self.board[0]]} | {tt[self.board[1]]} | {tt[self.board[2]]} |") 
        print("+---+---+---+")
        print(f"| {tt[self.board[3]]} | {tt[self.board[4]]} | {tt[self.board[5]]} |") 
        print("+---+---+---+")
        print(f"| {tt[self.board[6]]} | {tt[self.board[7]]} | {tt[self.board[8]]} |") 
        print("+---+---+---+")

    # 현재의 보드 상태를 숫자로 변환
    def GetState(self):
        state = 0
        for k in self.board:
            state = state*3 + k
        return state

    # p에다 놓았을 경우 다음 상태를 반환
    def GetNextState(self, turn, p):
        nb = [k for k in self.board] # 기존 보드 판을 그대로 가져와
        nb[p] = turn                 # p위치에 turn값을 놓아
        state = 0
        for k in nb:
            state = state*3 + k # next board(다음상태)판에 기록된 상태를 10진법으로 반환
        return state

# 모든 상태에 대해서 기대값을 기록할 상태공간 생성
import os.path
filename = "ttt-eg.sav" 
if os.path.isfile(filename):
    with open(filename, "r") as f:
        epsilon = float(f.readline())               # 초기 입실론 읽어오기
        ss = list(map(float, f.readline().split())) # 3**9 차원 상태공간 가져와.
else:
    ss = [ 0.0 ]*(3**9)
    epsilon = 0.95  # epsilon of e-greedy
lr = 0.1            # learning rate (lambda)

# 무한하게 게임 진행
while True:
    game = TicTaeToe()
    turn = 1
    ep = []

    while game.IsFinished() == -1: # 게임 계속 진행중 - 매 턴 마다.
        # 현재 상태를 에피소드에 저장
        ep.append(game.GetState())
        game.Print()
        cand = [] # 매 턴마다 빈곳 확인하기.
        for i in range(9):
            if game.board[i] == 0: cand.append(i)
        # ai turn이면 
        if turn == game.aiTurn:
            # epsilon 만큼은 랜덤하게 선택
            if random.uniform(0.0, 1.0) < epsilon:
                p = random.choice(cand)
            # time difference : 최대 기대값을 선택.
            else:
                p, maxv = 0, -100.0
                #mt = (1 if game.aiTurn == 1 else -1)
                board = [k for k in game.board]
                for c in cand:
                    ns = game.GetNextState(turn, c)
                    board[c] = ss[ns]
                    if maxv < ss[ns]: p, maxv = c, ss[ns]
                print(*board)
            game.Put(turn,p)
        else:
            while True:
                p = int(input("pos : "))
                if p in cand: break
            game.Put(turn, p)
        turn ^= 3

    # 결과 에피소드를 저장
    ep.append(game.GetState())
    game.Print()
    rtext = ("Draw", "O Win", "X Win")
    win = game.IsFinished()
    print(rtext[win])
                     
    # 에피소드의 결과에 따라서 보상값을 계산한다.
    if win == 1 or win == 2: reward = 1
    else: reward = 0
    # 모든 에피소드에 대해서
    for e in ep:
        ss[e] += lr * (reward - ss[e])
        reward *= -1
        print(e,':', ss[e])
    # 엡실론 값을 업데이트한다.
    epsilon *= 0.95
    yn = input("Do you want more game : ")
    if yn != 'y' and yn != 'Y': break

with open("ttt-eg.sav", "w") as f:
    f.write("%s\n"%epsilon)
    f.write(" ".join(map(str, ss)))
