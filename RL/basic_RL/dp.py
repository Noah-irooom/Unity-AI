'''map0.txt
4 4    # 격자크기 
0 0    # 시작 위치
2 2    # 도착 위치
0000   # 장애물
0010
0100
0000
'''

'''
alpha 필요 없어
'''


# 격자세계를 읽고 프로세스할 클래스
class GridWorld:
    # 생성자
    def __init__(self, fname):
        # 비어있는 맵으로 초기화
        self.map = []
        # fname으로 파일을 열어서 처리
        with open(fname) as f:
            self.n, self.m = map(int, f.readline().split())
            self.start = tuple(map(int, f.readline().split()))
            self.end = tuple(map(int, f.readline().split()))
            for _ in range(self.n):
                self.map.append(
                    [0 if k == '0' else 1 for k in f.readline()
                         if k == '0' or k == '1'])


    # s상태에서 dir로 움직일 경우 다음 상태
    def nextState(self, s, dir):
        # dir값에 따라 움직여야할 에이전트 위치를 계산한다.
        dxy = [ (0, 1), (1, 0), (0, -1), (-1, 0) ] # direction 설정 오른쪽, 아래, 왼쪽, 위로

        nr, nc = s[0]+dxy[dir][0], s[1]+dxy[dir][1]
        # 움직일 수 있는 위치인지 파악한다.
        if nr<0 or nr>=self.n or nc<0 or nc>=self.m or self.map[nr][nc]!=0:
            nr, nc = s
        return (nr, nc)

    # 결과값 출력하기
    def print(self, ss):
        print("-"*(9*self.m))
        for r in range(self.n):
            line = ""
            for c in range(self.m):
                if self.map[r][c] == 1: line += " [#####] "
                else: line += "{:^9.2f}".format(ss[r][c])
            print(line)
        print("-"*(9*self.m))

mapName = input("Map name : ")
errLimit = 0.0001
env = GridWorld(mapName)

# 상태공간을 만들자
ss = [ [0]*env.m for _ in range(env.n) ]
while True:
    # 현재 값을 저장할 상태공간을 만들자
    nss = [ [0]*env.m for _ in range(env.n) ]
    # 모든 상태에 대해서
    for r in range(env.n):
        for c in range(env.m):
            # 현재 상태
            s = (r,c)
            # 현재 상태가 목적지인 경우 무시
            if s == env.end: continue
            # 갈 수 있는 모든 상태에 대해서
            for d in range(4):
                ns = env.nextState(s, d) #s 에서 d로 가는 것.
                nss[r][c] += (-1+ ss[ns[0]][ns[1]])/4
                #리워드 값 더하고 각 방향마다 0.25의 확률로.
                # 한번 이동하면 한 스텝을 소모했다는 의미(-1 : 리워드)

    # 에러 계산을 한다.
    errSum = 0.0
    for r in range(env.n):
        for c in range(env.m):
            errSum += (nss[r][c] - ss[r][c])**2 # 에러 섬 계산
            # 수렴할 것으로 가정
            # 현상태를 기초로 새 상태공간을 만드는데,
    print(errSum/(env.n*env.m))
    ss = nss
    # error square mean value is under errLimit.
    if errSum < errLimit*env.n*env.m: break  # 0.0001보다 작아지면 이제 그만하자.

env.print(ss)

# td는 왔다갔다 많이 하지 않기때문에 값이 커지진 않음.
# 갔던 데 또 안감(최선의 길을 선택하여 움직이는 거니까)


