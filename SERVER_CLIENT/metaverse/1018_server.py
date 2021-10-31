''' 사용자의 움직임 처리 + 리버시 판의 동작(서버, 클라이언트, world.txt, Reversi.py)
world.txt
    Reversi 10 10 0
    Sofa 20 20 90

1. Word data 로드하기
    - world.txt 정보를 dict형태로 바꾸기.
    - self.worldData 에 그 dict정보를 넣어주기.
    - self.loadWorld()로

self.reads : sock.accept() 하여 self.reads.append(client) - 소켓 등록
self.users : sock.recv() 하여 데이터를 받고 사용자 정보 등록할때 (<-join noah)

/join 사용자이름
/move 속도
/turn 각속도
/world : dict길이
/worlddata : data 내용
/action 

'''
import socket
import select
import time
import math
import os.path  # file or directory 검사용

class Server:
    TimeTick = 5.0      # 하나의 틱 길이 (초단위)
    
    # Constructor
    def __init__(self, port):
        self.port = port
        self.running = False
        self.users = dict()

    # Start server
    def start(self, worldData):
        # 1. world data 저장하고 world 로드 하기
        self.worldData = worldData
        self.loadWorld()

        # 2. 리슨소켓 만들기
        self.listenSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listenSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
        # 3. Bind address to listen socket
        self.listenSock.bind(('', self.port))

        # 4. Listen socket
        self.listenSock.listen(5)

        # 5. Connected client sockets
        self.reads = [self.listenSock]

        # 6. time tick 설정을 위해서 현재 시간을 제거합니다.
        self.timeOffset = time.time()
        self.curTick = 0
        
        # 7. select() -> sock.accept(), sock.recv()
        self.running = True
        while self.running:
            self.select()

        # 8. listenSock close()
        print("Shutdown")
        self.listenSock.close()

    # Load world
    def loadWorld(self):
        for k in self.worldData:      # world.txt를 dict형식으로 만들었으니까
            if os.path.isfile(f"{k}.py"):
                wd = self.worldData[k]
                pyMod = __import__(k)
                wd[3] = getattr(pyMod, k)() # 3번째에는 인스턴스 넣어놓기

    # 현재 진행되는 시간 가져오기              
    def getTick(self):
        return int((time.time() - self.timeOffset)/Server.TimeTick)

    # on connect
    def onConnect(self, sock):
        # 요청이 온 클라이언트에 대하여 접속 수락
        client, addr = sock.accept()
        print(f"Connected from {addr}")
        self.reads.append(client) # 새로 접속요청한 클라이언트 소켓을 담아.

    # on close
    def onClose(self, sock):
        self.reads.remove(sock)
        del self.users[sock]

    # on packet : 데이터를 사용자 정보에 등록하는 부분
    def onPacket(self, sock, sdata): # 이벤트 발생한 클라이언트 소켓에 대하여
        ss = sdata.split()
        
        # join Noah : (이미 self.reads에 등록된 상태에서 self.users에 사용자 정보 등록하려고)
        if ss[0][1:] == "join":
            
            # 1. 이미 접속한 다른유저 정보 받기
            for k in self.users:
                u = self.users[k]
                mesg = f"/move {u['name']} {u['pos']} {u['dir']} {u['speed']}"
                sock.send(mesg.encode())
            self.users[sock] = {"name":ss[1], "pos":(0,0), "dir":0, "speed":0, "aspeed":0}

            # 2. 접속한 새 클라이언트 등록하기
            u = self.users[sock]

            # 3. broadcast 해주기  
            mesg = f"/move {u['name']} {u['pos']} {u['dir']} {u['speed']}"
            self.broadcast(mesg.encode())
            return

        # 데이터 보낸 클라이언트가 사용자 정보가 없는 소켓이면 에러 표시
        if sock not in self.users:
            print("Error : Unknown user message")
            return 

        # 사용자 정보 등록.
        user = self.users[sock] # data보낸 클라이언트 소켓
        if ss[0][1:] == "shutdown":
            self.running = False
        elif ss[0][1:] == "move":
            user['speed'] = int(ss[1])
        elif ss[0][1:] == "turn":
            user['aspeed'] = int(ss[1])

        # /world   ->  dict 길이  (-> 2)
        elif ss[0][1:] == "world":
            mesg = f"/world {len(self.worldData)}"
            sock.send(mesg.encode())

        # /worlddata 0   -> 0번째 줄의 데이터
        elif ss[0][1:] == "worlddata":
            idx = int(ss[1])
            key = list(self.worldData.keys())[idx]
            wd = self.worldData[key]
            mesg = f"/worlddata {key} {wd[0]} {wd[1]} {wd[2]}"
            sock.send(mesg.encode())

        # /action : Reversi 객체의 함수를 실행하겠다.
        # ex) /action Reversi : 해당 사용자 이름으로 join
        # ex) /action Reversi 17 : 해당 사용자가 Reversi 17번에 돌을 놓는다.
        elif ss[0][1:] == "action":
            if ss[1] not in self.worldData:
                mesg = f"/error {ss[1]} is not world object"
                sock.send(mesg.encode())
                return
            obj = self.worldData[ss[1]][3] # Reversi.py 의 클래스 인스턴스 저장됨.
            if len(ss) == 2:
                ret = obj.runCommand(f"join {user['name']}")
                print(ret)
            elif len(ss) == 3:
                ret = obj.runCommand(f"put {user['name']} {ss[2]}")
                print(ret)
            sock.send(ret.encode()) # 데이터를 보낸 클라이언트 소켓에게 다시 전달.

    # on recv
    def onRecv(self, sock):
        try:
            data = sock.recv(1024)
            if data == None or len(data) <= 0:
                print("closed by peer")
                self.onClose(sock)
                return
        except socket.error:
            print("socket error")
            self.onClose(sock)
            return

        sdata = data.decode()
        
        # mycode : Anonymous 처리하려면.
        # self.users[sock] = {"name":"Anonymous", "pos":(0,0), "dir":0, "speed":0, "aspeed":0}
        
        if sdata[0] == "/":
            self.onPacket(sock, sdata)
            return
        
        user = self.users[sock]['name']
        mesg = f"{user} : {sdata}"
        print(mesg)
        self.broadcast(mesg.encode())

    # 유저의 이동 -> broadcast , Reversi판 정보 -> broadcast 
    def onIdle(self):
        print(f"onIdle({self.curTick})")

        # 유저 이동 정보
        for k in self.users:
            u = self.users[k]
            # 유저의 속도와 각속도가 모두 0이면 무시 onIdle에서도 더 이상 이동정보 표시 안함.
            if u['speed'] == 0 and u['aspeed'] == 0: continue
            u['dir'] = u['dir'] + u['aspeed'] * Server.TimeTick
            # 각도를 라디안으로 변경
            theta = u['dir'] * math.pi / 180
            x = u['pos'][0] + u['speed'] * math.cos(theta) * Server.TimeTick
            y = u['pos'][1] + u['speed'] * math.sin(theta) * Server.TimeTick
            u['pos'] = (x, y)
            mesg = f"/move {self.curTick} {u['name']} {u['pos']} {u['dir']} {u['speed']}"
            self.broadcast(mesg.encode())
        for k in self.worldData:
            wd = self.worldData[k]
            if wd[3] == None: continue
            ret = wd[3].runCommand("board")
            mesg = f"{k} {ret}"
            print(mesg)
            self.broadcast(mesg.encode())

    # Select
    def select(self):
        event_reads, _, _ = select.select(self.reads, [], [], Server.TimeTick/2)

        # for every socket events
        for s in event_reads:
            # if s is listen socket
            if s == self.listenSock: self.onConnect(s)
            # if s is not listen socket
            else: self.onRecv(s)

        # time tick이 현재 있는지 검사
        ctick = self.getTick() # 000...11...222..33...
        if self.curTick < ctick:
            self.onIdle()
            self.curTick += 1 # 결국 5초 마다!
                
    # Broadcast
    def broadcast(self, data):
        for s in self.users:
            s.send(data)

server = Server(8888)
worldData = dict()
with open("world.txt") as f:
    while True:
        line = f.readline()

        # 한 라인에 정보가 없으면 스탑
        if line == None: break

        # 한 라인에 정보가 부족하면 스탑
        ss = line.split()
        if len(ss) < 4: break

        worldData[ss[0]] = [float(ss[1]), float(ss[2]), float(ss[3]), None]
        # 맨마지막 None은 loadWorld()에서 Reversi 객체만들어 저장할 곳임.

for k in worldData:
    print(k, worldData[k])
server.start(worldData)

