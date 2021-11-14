'''1103_dp
dp :
4가지 방향을 모두 동일한 비율로 고려하여 현재 상태공간(위치)을 업데이트함.
현재상태공간(ss)과 다음 상태공간(nss)를 구별하여 ss가 nss를 그대로 가져와 업데이트 하는 식.
상태공간 값이 커지면(기대값?) 근처에 있다는 의미!
'''
class GridWorld:
    def __init__(self, fname):
        self.map = []
        with open(fname) as f:
            self.n, self.m = map(int, f.readline().split())
            self.start = tuple(map(int, f.readline().split()))
            self.end = tuple(map(int, f.readline().split()))
            for _ in range(self.n):
                self.map.append([0 if k == '0' else 1 for k in f.readline() if k == '0' or k == '1'])

    # s 상태에서 dir로 움직일 경우 다음 상탤
    def nextState(self, s, dir):
        # dir 값에 따라 움직여할 위치 계산
        dxy = [(0,1), (1,0), (0,-1), (-1,0)]
        nr, nc = s[0] + dxy[dir][0], s[1] + dxy[dir][1]
        # 움직일 수 있는 위치인지 파악
        if nr < 0 or nr >= self.n or nc < 0 or nc >= self.m or self.map[nr][nc] != 0:
            nr, nc = s # 움직일 수 없으면 현재 위치 값 반환
        return (nr, nc)

    # 결과값 출력하기
    def print(self, ss):
        print("-"*(9*self.m))
        for r in range(self.n):
            line = ""
            for c in range(self.m):
                if self.map[r][c] == 1:
                    line += " [-----] "
                else:
                    line += "{:^9.2f}".format(ss[r][c])
            print(line)
        print("-"*(9*self.m))
                    

mapName = input(" Map name : ")
errLimit = 0.0001  # 여기까지만 상태를 업데이트 하겠다.
env = GridWorld(mapName)

# 상태공간 생성
ss = [[0] * env.m for _ in range(env.n)]
while True:
    # 현재 값을 저장할 상태공간 생성
    nss = [[0] * env.m for _ in range(env.n)]
    # 모든 상태에 대해서
    for r in range(env.n):
        for c in range(env.m):
            # 현재 상태
            s = (r, c)
            # 현재 상태가 목적지인 경우 무시
            if s == env.end:
                continue
            # 갈 수 있는 모든 상태(방향)에 대해서
            for d in range(4):
                ns = env.nextState(s, d)
                nss[r][c] += (-1 + ss[ns[0]][ns[1]])/4
    # 에러를 계산한다.
    errSum = 0.0
    for r in range(env.n):
        for c in range(env.m):
            errSum += (nss[r][c] - ss[r][c])**2
    print("평균 오차 : ",errSum/(env.n*env.m))
    env.print(ss)
    ss = nss # 각 상태 업데이트
    
    # 여기까지만 상태를 업데이트 하겠다.
    if errSum < errLimit*env.n*env.m:
        break

#env.print(ss)


        
        
