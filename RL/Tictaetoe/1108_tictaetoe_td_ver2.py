# Tic-Tae-Toe Temporal Difference Game
'''
1108_tictaetoe_random
time difference 이용
- 1. 매 턴마다 둘 수있는 후보 위치들을 모두 미리 둬보고(다음상태)
- 2. 그 다음상태값을 10진법의 상태공간에서 확인하여 최대 보상값(기대값)을 갖는 위치를 찾아
- 3. 최대기대값인 곳에 실제 Put한다.

'''
import random
class TicTaeToe:
    def __init__(self):
        self.board = [0]*9
        self.aiTurn = random.randrange(1, 3)
    # turn이 pos위치에 놓는다.
    def Put(self, turn, pos):
        self.board[pos] = turn

    def IsFinished(self):
        # 가로 검사
        for i in range(3):
            x = self.board[i*3]
            if x == 0: continue # empty이면 더 검사 필요 없음
            isFinish = True
            for j in range(3):
                if x != self.board[i*3+j]:
                    isFinish = False
                    break
            if isFinish: return x # turn값(1 또는 2) 반환
        # 세로 검사
        for i in range(3):
            x = self.board[i]
            if x == 0: continue
            isFinish = True
            for j in range(3):
                if x != self.board[i+j*3]:
                    isFinish = False
                    break
            if isFinish: return x
        # 대각선 검사 : upper left -> lower right
        isFinish = True
        x = self.board[0]
        if x != 0:
            for i in range(3):
                if x != self.board[i*4]:
                    isFinish = False
                    break
            if isFinish: return x
            

        #  대각선 검사 : upper right -> lower left
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
        for k in self.board: # board는 3진법으로 9자리수
            state = state*3 + k # 3진법 -> 10진법 변환
        return state # 10진법으로 나타낸 상태

    # p에다 놓았을 경우 다음 상태를 반환 (next board)
    def GetNextState(self, turn, p):
        nb = [k for k in self.board] # 기존 보드 판을 그대로 가져와 
        nb[p] = turn                 # p위치에 turn값을 놓아
        state = 0
        for k in nb:
            state = state*3 + k      # next board(다음상태)판에 기록된 상태를 10진법으로 반환
        return state

# 모든 상태에 대해서 기대값을 기록할 상태공간 생성

import os.path
filename = "ttt-td.sav" # 저장된 상태값 가져오기
if os.path.isfile(filename):
    with open(filename, 'r') as f:
        ss = list(map(float, f.readline().split())) # 3**9차원 벡터(10진법 상태)에 각각에 대한 보상값을 가져와
else:
    ss = [0.0]*(3**9) # 파일 없으면 초기화된 상태공간 생성

lr = 0.1    # learning rate (lambda)

# 무한하게 게임 진행
while True:
    game = TicTaeToe()
    turn = 1
    ep = []
    while game.IsFinished() == -1:
        # 매 turn 둘 때마다 상태값 에피소드를 저장
        ep.append(game.GetState())
        game.Print() # 현재 보드 출력하기
        cand = []

        for i in range(9):
            if game.board[i] == 0: cand.append(i) # 빈곳이면 후보에 등록하기

        # ai turn이면 
        if turn == game.aiTurn:
            p, maxv = 0, -100.0                 # ai turn이면 최대 기대값을 선택하여
            board = [k for k in game.board] # 현재 게임보드 값 그대로 복제.
            # 둘 수 있는 후보들에 대해서
            for c in cand:
                # 둘수 있는 후보들 모두 다음 상태를 미리 계산하여 최대 기대값 찾아.
                ns = game.GetNextState(turn, c) # turn이 c위치에 놓았을때의 10진법 상태(다음 상태)
                board[c] = ss[ns]
                if maxv < ss[ns]: p, maxv = c, ss[ns] # 다음상태를 미리계산하고 거기서의 보상값을 가져와
            print(*board)
            game.Put(turn, p) # 실제 두기.
        else:
            while True:
                p = int(input("pos : "))
                if p in cand: break
            game.Put(turn, p)
        turn ^= 3
        
    # 결과 에피소드를 저장
    ep.append(game.GetState()) # 마지막 에피소드
    game.Print()
    rtext = ("Draw", "O Win", "X Win")
    win = game.IsFinished()
    print(rtext[win])

    # 에피소드의 결과에 따라서 보상값을 계산
    if win == 1 or win == 2 : reward = 1
    else: reward = 0

    print(ep)
        
    # 모든 에피소드에 대해서
    for e in ep[::-1]:
        ss[e] += lr * (reward - ss[e])
        reward *= -1 # 이긴 에피소드는 학습률 적용한 보상값 +, 지면 -
        print(e,':', ss[e])
    yn = input("Do you want more game : ")
    if yn != 'y' and yn != 'Y': break

with open("ttt-td.sav", "w") as f:
    f.write(" ".join(map(str, ss)))
