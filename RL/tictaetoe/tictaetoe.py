# Tic-Tae-Toe Random Game
# Random module import

'''
Empty : 0
Circle : 1
Cross : 2
'''

import random

class TicTaeToe:
    def __init__(self):
        self.board = [0]*9
        self.aiTurn = random.randrange(1,3) # 인공지능 turn : 1 or 2 반환

    # turn 이 pos 위치에 놓는다
    def Put(self, turn, pos):
        self.board[pos] = turn

    # 경기가 끝났는지 검사
    def IsFinished(self):
        # 가로 검사
        for i in range(3):
            x = self.board[i*3]
            if x == 0: continue
            isFinish = True
            for j in range(3):
                if x != self.board[i*3+j]:
                    isFinish = False
                    break
            if isFinish: return x

        # 세로 검사
        for i in range(3):
            x = self.board[i*3]
            if x == 0: continue
            isFinish = True
            for j in range(3):
                if x != self.board[i+j*3]:
                    isFinish = False
                    break
            if isFinish: return x

        # 대각선 검사
        isFinish = True
        x = self.board[0]
        if x != 0:
            for i in range(3):
                if x != self.board[i+4]:
                    isFinish=False
                    break
            if isFinish: return x
        # 대각선 검사
        isFinish = True
        x = self.board[2]
        if x != 0:
            for i in range(3):
                if x != self.board[i*2+2]:
                    isFinish=False
                    break
            if isFinish: return x

        # all board is full
        isFinish = True
        for i in range(9):
            if self.board[i] == 0:
                isFinish = False
                break
        if isFinish: return 0 # 꽉 찼으면 비김(0)
        return -1 # 게임 진행중

    def Print(self):
        tt = (" ", "0", "X")
        print("+---+---+---+")
        print(f"| {tt[self.board[0]]} | {tt[self.board[1]]} | {tt[self.board[2]]}")
        print("+---+---+---+")
        print(f"| {tt[self.board[3]]} | {tt[self.board[4]]} | {tt[self.board[5]]}")
        print("+---+---+---+")
        print(f"| {tt[self.board[6]]} | {tt[self.board[7]]} | {tt[self.board[8]]}")
        print("+---+---+---+")


# 무한하게 게임 진행
while True:
    game = TicTaeToe()
    turn = 1 # 현재 턴 1로 설정
    
    # 계속 게임 진행중
    while game.IsFinished() == -1:
        game.Print()
        cand = []
        for i in range(9):
            if game.board[i] == 0: cand.append(i) # 비어있는 곳 위치 후보입력
        if turn == game.aiTurn:
            p = random.choice(cand)     # 비어 있는 곳
            game.Put(turn, p) # p는 position
        else:
            while True:
                
                p = int(input("pos : "))
                if p in cand: break
            game.Put(turn, p)
        turn ^= 3
        # XOR : turn ^= 1 로 놓으면 0 <-> 1 (0이면 1로, 1이면 0)
        # turn ^= 3 놓으면 1 <-> 2
    rtext = ("Draw", "O Win", "X Win")
    print(rtext[game.IsFinished()])
    game.Print() # 마지막 다 두고나서 판 보여주
    
    yn = input("Do you want more game? : ")
    if yn != 'y' and yn != 'Y': break
    
