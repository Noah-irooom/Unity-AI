# 1018_Reversi.py
"""
명령어
1) join playerName
   게임에 참여한다.
   ret: a.Black or White,
        b. Refuse
2) board
    '0123' 0: 놓을 수 있는곳, 1: white, 2: black, 3: 놓을 수 없는곳 empty
3) put playerName position
   리버시 position 위치에 돌을 올려 놓는다.
   ret : sucess or fail
"""

class Reversi:
    def __init__(self):
        self.board = [0]*64 # [0, 0, 0 ... 0]
        self.player = [None]*2 # [None, None]
        print("__construction__")

    def runCommand(self, s):
        ss = s.split()
        # s = join Noah
        # join 명령어가 들어왔을 때 -> 참가자 입장.
        if ss[0] == "join":
            print(f"{ss[1]}이 게임에 참여합니다.") 

            if self.player[0] == None:
                self.player[0] = ss[1] # 참가자1 이름
                ret = "white"

            elif self.player[1] == None:
                self.player[1] = ss[1] # 참가자2 이름
                ret = "black"
            else:
                ret = "refuse" # 참가자가 더들어오면 refuse하겠다.
            return ret

        # s = board
        # board 명령어가 들어왔을때 -> board 상황을 보여줌.
        elif ss[0] == "board":
            ret = "".join(list(map(str, self.board))) # map : ['0', '0',...'0']
            # "".join : '00000..00'
            return ret

        # s = put Noah 17
        # put명령어가 들어왔을때 -> 참가자 1, 2가 돌을 놓기.
        elif ss[0] == "put":
            turn = 0
            if self.player[0] == ss[1]:
                turn = 1
            elif self.player[1] == ss[1]:
                turn = 2
            # 해당 참가자1,2 가 아닌 제3자가 돌 놓으려하면 fail
            if turn == 0:
                return "fail"

            p = int(ss[2])
            self.board[p] = turn # 참가자1이 놓으면 1로, 참가자 2가놓으면 2로 놓아.
            return "success"

