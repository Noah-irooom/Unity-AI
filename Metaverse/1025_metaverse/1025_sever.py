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

2. server -> unity client, unity client -> server
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

        # 유니티 또는 다른 클라이언트에서 넘어온 패킷 처리
        # join Noah : (이미 self.reads에 등록된 상태에서 self.users에 사용자 정보 등록하려고)
        if ss[0] == "join":
            
            # 1. 이미 접속한 다른유저 정보 받기
            for k in self.users:
                u = self.users[k]
                mesg = f"move {u['name']} {u['pos']} {u['dir']} {u['speed']}"
                self.send(sock, mesg.encode())
            self.users[sock] = {"name":ss[1], "pos":(0,0), "dir":0, "speed":0, "aspeed":0}

            # 2. 접속한 새 클라이언트 등록하기
            u = self.users[sock]

            # 3. 접속한 새 클리언트 정보 broadcast 해주기  
            mesg = f"move {u['name']} {u['pos']} {u['dir']} {u['speed']}" # move Noah (0,0) 0 0
            self.broadcast(mesg.encode())
            return

            # 4. 접속하면 월드 데이터를 보낸다.
            for k in self.worldData:
                wd = self.worldData[k]
                mesg = f"worlddata {k} {wd[0]} {wd[1]} {wd[2]}"
                self.send(sock, mesg.encode())
            return

        # 데이터 보낸 클라이언트가 사용자 정보가 없는 소켓이면 에러 표시
        if sock not in self.users:
            print("Error : Unknown user message")
            return 

        # 사용자 정보 등록.
        user = self.users[sock] # data보낸 클라이언트 소켓
        if ss[0] == "shutdown":
            self.running = False
        elif ss[0] == "move": # 유니티 클라이언트가 보낸 패킷 내용 따라.
            user['pos'] = (float(ss[2]), float(ss[3]))
            user["direction"] = float(ss[4])
            user['speed'] = float(ss[5])
            user['aspeed'] = float(ss[6])
        elif ss[0] == "turn":
            user['aspeed'] = int(ss[1])

        # world   ->  dict 길이  (-> 2)
        elif ss[0] == "world":
            mesg = f"world {len(self.worldData)}"
            self.send(sock, mesg.encode()) #물어본 클라이언트에 대해서만

        # worlddata 0   -> 0번째 줄의 데이터
        elif ss[0] == "worlddata":
            idx = int(ss[1])
            key = list(self.worldData.keys())[idx]
            wd = self.worldData[key]
            mesg = f"worlddata {key} {wd[0]} {wd[1]} {wd[2]}"
            self.send(sock, mesg.encode())

        # action : Reversi 객체의 함수를 실행하겠다.
        # ex) action Reversi : 해당 사용자 이름으로 join
        # ex) action Reversi 17 : 해당 사용자가 Reversi 17번에 돌을 놓는다.
        elif ss[0] == "action":
            if ss[1] not in self.worldData:
                mesg = f"error {ss[1]} is not world object"
                self.send(sock, mesg.encode())
                return
            obj = self.worldData[ss[1]][3] # Reversi.py 의 클래스 인스턴스 저장됨.
            if len(ss) == 2:
                ret = obj.runCommand(f"join {user['name']}")
                print(ret)
            elif len(ss) == 3:
                ret = obj.runCommand(f"put {user['name']} {ss[2]}")
                print(ret)
            self.send(sock, ret.encode()) # 데이터를 보낸 클라이언트 소켓에게 다시 전달.

        # 유니티클라이언트에서 넘어온 패킷 처리
        elif ss[0] == "avatar":
            user['avatar'] = int(ss[2]) # avatar 성별 정보
        elif ss[0] == "look":
            user["look"] = tuple(map(int, ss[2:]))
        self.broadcast(sdata.encode())

    # on recv
    def onRecv(self, sock):
        #ex)   9join Noah  13avatar Noah 1  17look Noah 0 2 3 2
        # 위와 같은 형태로 데이터 전달하는데, 앞의 헤더(0009)따로받고, 9만큼의 길이의 패킷을 따로받기
        # 따라서 위의 긴 데이터를 패킷 길이만큼 잘라서 출력하게 됨.
        try:
            data = sock.recv(4)
            if data == None or len(data) <= 0:
                print("closed by peer")
                self.onClose(sock)
                return
        except socket.error:
            print("socket error")
            self.onClose(sock)
            return
        needed = int(data.decode()) # 헤더 : 뒤 패킷의 길이 정보담아. 
        try:
            data = sock.recv(needed) # 패킷 길이 맞춰서 그만큼만 받아.
            if data == None or len(data) <= 0:
                print("closed by peer")
                self.onClose(sock)
                return
        except socket.error:
            print("socket error")
            self.onClose(sock)
            return
        sdata = data.decode()
        print(sdata)
        self.onPacket(sock, sdata)
        return
        

    # 유저의 이동 -> broadcast , Reversi판 정보 -> broadcast 
    def onIdle(self):
        # print(f"onIdle({self.curTick})")

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
            # print(mesg)
            self.broadcast(mesg.encode()) # 모든 클라이언트에 board판 출력되게.

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

    # Send
    # 데이터를 보내줄때 : 헤더+메시지 형태로 보내주도록.
    def send(self, sock, data): # 이미 data는 encode()된 상태로 넘겨받
        packet = ("%04d"%len(data)).encode()+data # 길이(헤더) + 메시지 패킷
        sock.send(packet)
                
    # Broadcast
    def broadcast(self, data):
        for s in self.users: # 모든 등록된 사용자 소켓들에 대해
            self.send(s, data)

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
