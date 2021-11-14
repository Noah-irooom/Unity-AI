''''
1103_mc.py - 격자세계에서 몬테카를로 기법 적용
mc : 모든 경우의 수를 다 고려해서

# 용어
- nr, nc : next row, next column 다음 행, 열
- self.agent : (0,0) 부터 시작
- self.map : [[0000]
                [0000]
                [0000]
                [0000]]
# 맵 데이터
- map0.txt
4 4   # 한계치 
0 0   # 싲작 위치
2 2   # 도착 위치
0000 
0010
0100
0000
'''
import random # 몬테카를로 기법에서 사용할 무작위 수 모듈

# 격자 세계를 읽고 프로세스할 클래스
class GridWorld:
    # 생성자
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

    # 도착하였는지 체크
    def isFinish(self):
        return self.agent == self.end 

    # 격자 세계 출력하기
    def print(self, ss):
        print("-"*(9*self.m)) # 구분선
        for r in range(self.n): # 행 돌면서
            line = ""
            for c in range(self.m): # 열 돌면서
                # self.map에서 
                if self.map[r][c] == 1:
                    line += " [#####] " # 장애물 표시
                # ss : 상태공간(state space)에서 
                elif ss[r][c][1] == 0:
                    line += "       "      # 한번도 거치지 않은 곳.
                # 거치지 않은곳, 장애물이 아니라면 
                else:
                    line += "{:^9.2f}".format(ss[r][c][0]/ss[r][c][1]) # 상태 표시
                    # 각 칸에서 종료지점까지 가는데 평균 보상점수.(얼마나 더가야/이곳은 몇번
            print(line)
        print("-"*(9*self.m)) 

mapName = input(" Map name : ")
env  = GridWorld(mapName)
iterCount = int(input("iteration Count : ")) # 몇번 시행? - 즉 몇번의 에피소드를 만들것인가?

# [현지점에서 종료지점에 가려면 몇번 스텝을 더 가야 , 현지점을 몇번 거쳤는가] -> 총 4 * 4 상태공간으로 표시
ss = [[(0,0)] * env.m for _ in range(env.n)] 

# print(env.init())
for _ in range(iterCount):
    # 한 에피소드 만들기 # ex) [(0,0),(1,0),(1,1),(2,1),(3,1),(3,2),(2,2)]
    episode = [env.init()] # 첫 episode에 self.agent의 첫 위치 입력

    # 도착하지 않았으면 계속 agent 움직임.
    while not env.isFinish():
        dir = random.randrange(4) # 0 1 2 3 동일한 비율로 랜덤하게 골라
        episode.append(env.move(dir)) # episode에 self.agent 위치 튜플 형태 반환
    # 에피소드의 값을 가지고 상태값 수정하기
    reward = 0.0
    for s in episode[::-1]: # episode를 역순으로 뽑아내기
        # ss[s[0]][s[1]] : 상태공간에서의 agent의 위치(s[0] : row, s[1] : col)
        # ss[s[0]][s[1]][0] : 종료 지점에 몇번 만에 도착하는지 reward로 입력. = 각 step마다 reward = -1 누적
        # ss[s[0]][s[1]][1] : 각 칸에 거칠때마다 +1 입력
        ss[s[0]][s[1]] = (ss[s[0]][s[1]][0]+reward, ss[s[0]][s[1]][1]+1) # 종료지점은 (0,1)  # 각 에피소드 결과 누적하기 
        reward += -1
    #print(episode)
    print(ss)
    env.print(ss) # 각 에피소드 마다 생겨나는 경로를 누적하여 상태공간을 만든다.

        
        
