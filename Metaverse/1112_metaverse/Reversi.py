# Reversi.py
"""
"join": return self.onJoin(ss)
"board": return self.onBoard() # 보드판 출력
"place": return self.onPlace(ss)
"leave": return self.onLeave(ss) 

join Noah
1. onJoin() -> onStart() :
    - 플레이어1, 2 모두 참가시 onStart()
    - onStart() :
        - 보드판 세팅(
        - 처음 턴(white) 지정 : self.turn = 1
        - 처음 턴(white)가 둘수 있는 곳 - 4곳
    - self.players[1] 이 먼저 플레이!(플레이어 참가 순서대록)

place Noah 22
2. onPlace():
    - 차례에 맞는! 현재 턴이 '위치' 메시지를 보내면, 해당위치에 돌을 놓는다.
    - Reversi.getFlips() : 플립될 돌의 위치를 계산하고 돌을 플립시킴.
    - self.turn ^= 3 : 다음 턴으로 바꾸기
    - Reversi.getHints() : 다음 턴에서 둘수 있는 위치가 있는지 확인
        - 둘 곳이 있다면 -> self.onBoard()
        - 둘 곳이 없다면 -> self.onQuit() # 게임종료
            onQuit() : 한 게임종료후 players정보 초기화

leave Noah
3. onLeave():
    - 게임을 그만하려는 플레이어가 self.players에서 정보 지울 수 있게.

"""
class Reversi:
    def __init__(self):
        self.board = [3]*64
        self.players = [0, None, None]  # 플레이어들 접속 상태 표시
                                        # 접속한 플레이어 수, player1, player2
        self.turn = 1

    def onStart(self):
        # 보드판 : 33333..333
        self.board = [3]*64
        # 초기 보드판 세팅(white 2개, black 2개)
        self.board[27], self.board[28] = 1, 2 # 27 white, 28 black
        self.board[35], self.board[36] = 2, 1
        self.board[20], self.board[29] = 0, 0 # white(turn1)이 둘 수 있는 곳(hints)
        self.board[34], self.board[43] = 0, 0
        # 처음 턴 self.turn 은 1로 지정하여 스타트!
        self.turn = 1
        # 처음턴인 turn1이 둘수있는 hint 수는 4곳.
        self.hintCount = 4

    # ex) join Noah
    def onJoin(self, ss):
        if self.players[1] == None:
            self.players[1] = ss[1]     # Noah
            ret = f"{ss[1]} join white" # Noah join white
            self.players[0] += 1        # 플레이어 수 추가
        elif self.players[2] == None:
            self.players[2] = ss[1]
            ret = f"{ss[1]} join black"
            self.players[0] += 1
        else: return f"ss[1] join refuse" # Noah join refuse
        print(f"ss[1]이 게임에 {ret}로 참여합니다.")
        # 현재 플레이어에 2명이 모였으면 플레이를 시작
        if self.players[0] == 2: self.onStart()
        return ret

    def onBoard(self):
        # 숫자열의 보드판을 문자열로
        ret = "".join(list(map(str, self.board)))
        return ret
    
    def onQuit(self):
        # 한 게임 종료 후 스코어 기록
        w, b = 0, 0
        for t in self.board: # 최종 보드판을 가지고 백,흑 개수 세기
            if t == 1: w += 1
            elif t == 2: b += 1

        # 참가한 플레이어 정보 초기화함.
        self.players=[0,None,None]

        # 결과값을 만든다.
        mesg = f"quit {w} {b} {self.onBoard()}"
            # ex) quit 17 47 1122111122211211122...11
        return mesg

    # ex) leave Noah 
    # 플레이어가 게임을 그만뒀을때
    def onLeave(self, ss):
        # ss[1]이 플레이어에 있는지 검사
        for i in range(1, 3):
            if self.players[i] == ss[1]: #그만두고자 하는 플레이어 찾기
                self.players[i] = None
                self.players[0] -= 1
                return f"leave {ss[1]} success"
        return f"leave {ss[1]} fail" # 그만두려는 플레이어가 self.players에는 없어.

    # ex) place Noah 22
    def onPlace(self, ss):
        # place 명령을 실행한 플레이어가 현재 턴이 아니면 무시 # 차례대로 돌 놓을 수 있게
        if self.players[self.turn] != ss[1]: return f"{ss[1]} fail"
        p = int(ss[2]) # 놓을 위치

        # 놓을 수 없는 위치인 경우 무시. # 무조건 hints여야함.
        if self.board[p] != 0: return f"{ss[1]} fail"

        # 현재 턴이 보드의 p위치에 돌을 놓는다.
        self.board[p] = self.turn 

        # p위치에 돌을 놓을 경우, 바뀌어야 할 돌들의 "위치 리스트"를 얻어온다.
        flips = Reversi.getFlips(self.board, p, self.turn)
        
        # 플립될 돌들이 자신의 돌로 플립되도록함.
        for ft in flips: self.board[ft] = self.turn

        # 다음 턴으로 바꾸고, 다음 턴에서 놓을 수 있는 위치 계산
        self.turn ^= 3
        if Reversi.getHints(self.board, self.turn) > 0: return self.onBoard()
        
        # 두 턴 모두 놓을 수 있는 위치가 없으므로 게임을 종료한다.
        return self.onQuit()

    def runCommand(self, s):
        ss = s.split()
        if ss[0] == "join": return self.onJoin(ss)
        if ss[0] == "board": return self.onBoard() # 보드판 출력
        if ss[0] == "place": return self.onPlace(ss)
        if ss[0] == "leave": return self.onLeave(ss)

    #  클래스 함수 - 플립될돌의 위치를 계산해서 반환
    def getFlips(board, p, turn):
        # 8개의 방향에 대한 dx, dy를 튜플로 작성
        dxy = ((1,0), (1,1), (0,1), (-1,1), (-1,0), (-1,-1), (0,-1), (1,-1))
            # 오른쪽 돌, 오른아래, 아래, 왼아래, 왼, 왼위, 위, 오른위
        flips = []

        # 모든 8개의 방향에 대해 처리
        for dx, dy in dxy:
            x, y = p%8, p//8    # ex) p=26 -> x,y(3,3)를 계산
            nx, ny = x+dx, y+dy # ex) dx,dy = 1,0  -> nx, ny = 4,3 (오른쪽 돌 검사)

            # temporal flips
            tf = []          # 해당 방향에 대해서 임시로, 플립될 돌을 저장할 변수 tf 초기화
            isFlip = False   # 해당 방향에 대해서 플립이 실제로 이루어질 것인지 변수

            # 해당 방향으로 한칸씩 진행하면서 검사 - 갈수있는 곳이라면!
            while nx >= 0 and nx < 8 and ny >= 0 and ny < 8:
                np = ny*8+nx            # 좌표 값을 -> 인덱스 값으로
                # 1) 내 턴의 돌인지
                if board[np] == turn:   # 내 턴의 돌인 경우 플립이 완성
                    isFlip = True
                    break
                # 2) 중간에 빈 돌(0, 3)
                if board[np] != (turn^3):break # 내턴도 상대턴도 아닌 0or3 빈곳이라면

                # 3) 상대 턴의 돌이면 임시플립tf에 집어넣기.
                tf.append(np)

                nx, ny = nx+dx, ny+dy # 이동했던 방향으로 한칸 더 가기.
                
            #  임시플립 ->  최종 플립 저장소에 저장
            if isFlip: flips += tf # 상대턴이 한번 나와야 isFlip True됨.
        return flips

    # 다음 상대턴이 되었을 때, 해당 턴이 둘 수 있는 곳 위치 계산
    def getHints(board, turn):
        hintCount = 0 # 놓을 수 있는 hints의 개수

        # 8X8 모든 위치에 대해서 플립될 돌이 있는지 확인 - 있으면 둘 수 있는 곳이다.
        for i in range(64):

            # 1) 빈곳이어야 함. + 플립될 돌이 있어야함.
            if board[i] == 1 or board[i] == 2: continue # 현재 돌 있는 경우 무시
            flips = Reversi.getFlips(board, i, turn)    # i 위치에 turn 돌을 놓아 플립될 돌 가져오기

            # 2) flips 개수가 있는 경우면 둘수 있는 후보가 될 수 있다.
            if len(flips) > 0:
                hintCount += 1
                board[i] = 0 # 보드판에 둘수 있다고 표시해줌.
            else:
                board[i] = 3 # 둘수없다고 표시함
        return hintCount
            
            
