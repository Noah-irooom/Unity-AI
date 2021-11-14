'''
1103_td.py - 시간차 학습법
td :
1. 고려할 수 있는 모든 방향 고려
2. 각 방향중 최대 기대값을 가지는 곳(다음 상태 공간)을 선택
3. 현재 위치한 상태공간의 기대값을 업데이트 -> 이건 나중에(다음 위치 고려시 또는 다음 에피소드 시) 고려
4. 선택한 다음상태 공간으로 이동.

# alpha : Learning rate - 기대값을 결정한다.

'''


# 격자 세계를 읽고 프로세스 할 클래스
class GridWorld:
    def __init__(self, fname):
        # 비어있는 맵으로 초기화
        self.map = []
        # fname으로 파일을 열어 처리
        with open(fname) as f:
            self.n, self.m = map(int, f.readline().split()) # 4 4 - 한계치
            self.start = tuple(map(int, f.readline().split())) # 0 0 - 시작
            self.end = tuple(map(int, f.readline().split())) # 2 2 - 도착

            # 실제 맵 읽기 - 장애물인지 갈수 있는 곳인지. int 형으로 표시
            for _ in range(self.n):
                self.map.append([0 if k == '0' else 1 for k in f.readline() if k == '0' or k == '1'])

    def init(self):
        # 에이전트의 위치를 시작지점으로 초기화시킴.
        self.agent = self.start # (0,0)
        return self.agent

    # 에이전트를 움직인다.
    def move(self, dir):
        # 1. dir 값에 따라 움직여야할 에이전트 위치를 계산.
        dxy = [(0,1), (1,0), (0,-1), (-1,0)] # 0오른쪽, 1아래쪽, 2왼쪽, 3위쪽 # 움직임 방향
        nr, nc = self.agent[0] + dxy[dir][0], self.agent[1] + dxy[dir][1] 

        # 2. 움직일 수 있는 위치인지 파악한다. - 한계치 범위내 + 장애물이 아닌곳
        # - 움직일 수 없는 위치라면
        if nr < 0 or nr >= self.n or nc < 0 or nc >= self.m or self.map[nr][nc] != 0:
            nr, nc = self.agent # 움직일 수없는 위치라면 원래 self.agent위치로 다시 반환.

        # - 움직일 수 있는 위치라면 self.agent위치 수정
        self.agent = (nr, nc)
        return self.agent

    # dir로 움직일 경우 에이전트의 "다음 상태"
    def nextState(self, dir):
        # 1. dir 값에 따라 움직여야할 에이전트 위치를 계산한다.
        dxy = [(0,1), (1,0), (0,-1), (-1,0)]
        nr, nc = self.agent[0] + dxy[dir][0], self.agent[1] + dxy[dir][1]
        # 2. 움직일 수 있는 위치인지 파악.
        if nr < 0 or nr >= self.n or nc < 0 or nc >= self.m or self.map[nr][nc] != 0:
            nr, nc = self.agent # 움직일 수 없는 위치라면 원래 self.agent위치 반환.
        return (nr, nc) # self.agent위치를 업데이트하지 않고 다음상태만 반환

    # 목적지 도착여부 검사
    def isFinish(self):
        return self.agent == self.end # 도착하였는가? 아니면 계속 움직임.

    # 결과값 출력하기
    def print(self, ss):
        print("-"*(9*self.m))
        for r in range(self.n):
            line = ""
            for c in range(self.m):
                if self.map[r][c] == 1: # 장애물인 경우
                    line += " [-----] "
                else:
                    line += "{:^9.2f}".format(ss[r][c])
            print(line)
        print("-"*(9*self.m))

mapName = input(" Map name : ")
iterCount = int((input("iteration Count : ")))
alpha = float(input("Learning rate: "))
env = GridWorld(mapName)

ss = [[0]*env.m for _ in range(env.n)] # 상태공간 지정 - 일단 모두 0으로 
for _ in range(iterCount):
    env.init()
    while not env.isFinish():
        # 어디로 갈지 결정
        maxv, dir = -10**9, 0
        for d in range(4):  # 오른 아래 왼 위 다 가보면서 다음상태 값을 받아.
            ns = env.nextState(d) # (0,0) -> (0,1),(1,0), / (0,1) -> (0,2),(1,1),(0,0)
            if maxv < ss[ns[0]][ns[1]]:
                maxv, dir = ss[ns[0]][ns[1]], d  # 최대 기대값 업데이트

        # 현재의 상태값을 업데이트 한다.
        ss[env.agent[0]][env.agent[1]] = (1-alpha) * ss[env.agent[0]][env.agent[1]] + alpha * (-1 + maxv)

        # 선택한 dir로 움직인다.
        env.move(dir)
        
        env.print(ss)
        print(env.agent) # 최종 위
    #print(ss[0][0])
#env.print(ss)

        
        
