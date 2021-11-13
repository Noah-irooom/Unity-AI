# Tic-Tae-Toe Random Game
# Random module import

''' 보드의 상태공간 - 3진법 :  3개 숫자.
Empty : 0
Circle : 1
Cross : 2
'''


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
        # all board is full
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

    # 현재의 보드 상태를 숫자로 표현 ( empty O X -> 0 1 2 )
    def GetState(self):
        state= 0
        for k in self.board:
            state = state*3 + k
        return state

    # p에다 놓았을 경우 다음상태를 반환
    def GetNextState(self, turn, p):
        nb = [k for k in self.board]
        nb[p] = turn
        state = 0
        for k in nb:
            state = state*3 + k
        return state


# 저장된 기보 불러오기
import os.path
if os.path.isfile("ttt-eg.sav"):
    with open("ttt-eg.sav", "r") as f:
        epsilon = float(f.readline())
        ss = list(map(float, f.readline().split()))

else:
    # 모든 상태에 대해서 기대값을 기록할 상태공간 생성
    ss = [ 0.0 ]*(3**9)     # 3개의 숫자가 9개 칸에.
    epsilon = 0.95          # epsilon of e-greedy

lr = 0.1                # learning rate(lambda)


#  무한하게 게임 진행
while True:
    # 1) 에피소드 초기화
    game = TicTaeToe()
    turn = 1 # 현재 턴 1로 설정

    # 에피소드를 저장할 리스트 생성
    ep = []
    
    # 2) 에피소드 반복 : 계속 게임 진행중
    while game.IsFinished() == -1:
        # 현재 상태를 에피소드에 저장 - 각 턴 마다 저장.
        ep.append(game.GetState())
        
        game.Print()
        cand = []
        for i in range(9):
            if game.board[i] == 0: cand.append(i) # 비어있는 곳 위치 후보입력
        if turn == game.aiTurn:
            if random.uniform(0.0, 1.0) < epsilon: # 입실론 만큼은 랜덤하게 선택
                p = random.choice(cand)
            else: # 입실론 외에는 가장 높은 값 선택
                p, maxv = 0, -100.0 # 시간차 학습.
                mt = (1 if game.aiTurn == 1 else -1) # 승리 패배 반대로 
                board = [k for k in game.board]
                # 둘 수 있는 후보들에 대해서
                for c in cand:
                    ns = game.GetNextState(turn, c)
                    #print(ns, ss[ns]*mt)
                    board[c] = ss[ns]*mt
                    if maxv < ss[ns]*mt:
                        maxv = ss[ns]*mt # maxv가 현재 상태공간보다 작을 때 재설정
                        p = c
                print(*board)
                # p = random.choice(cand)     # 비어 있는 곳 -> 이제는 랜덤으로 안할 것.
            game.Put(turn, p) # p는 position
        else:
            while True:
                p = int(input("pos : "))
                if p in cand: break
            game.Put(turn, p)
        turn ^= 3
        # XOR : turn ^= 1 로 놓으면 0 <-> 1 (0이면 1로, 1이면 0)
        # turn ^= 3 놓으면 1 <-> 2

    # 3) 에피소드 종료.
    
    # 결과 에피소드를 저장
    ep.append(game.GetState())

    game.Print()
    rtext = ("Draw", "O Win", "X Win")
    win = game.IsFinished()
    print(rtext[win])

    # 에피소드의 결과에 따라서 보상값을 계산한다
    if win == 1: reward = 1     # 나의 승리 = 상대의 패배
    elif win == 2: reward = -1  # 나의 패배 = 상대 승리
    else : reward = 0
    
    # 모든 에피소드에 대해서
    for e in ep:
        ss[e] += lr * (reward - ss[e])
    # 엡실론 값을 업데이트 - 점점 줄어들어 나중에는 더 높은 값을 선택 많이하게
    epsilon *= 0.95
        
    yn = input("Do you want more game : ")
    if yn != 'y' and yn != 'Y': break


# 기보 저장하기
with open("ttt-eg.sav", "w") as f:
    f.write("%s\n"%epsilon)
    f.write(" ".join(map(str, ss)))

#for i in range(0, 3**9, 9):
#    print(ss[i:i+9]) # 이겼을 공간, 졌을 공간 ..
#    # 여러번 반복해 이기면 채워지는 숫자 많아져


