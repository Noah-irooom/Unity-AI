'''1113_server.py
유니티클라이언트와 reversi-random(random으로 두는 클라이언트)

onConnect() -> sock.accept()

self.users[sock] = {"name" : ss[1],
                    "pos" : (0, 0),
                    "dir": 0,
                    "speed" : 0,
                    "aspeed" : 0,
                    "avatar" : 0,
                    "look" : (0,0,0,0),
                    "attend" : None  # attend :"Reversi"
                    "leave" : }   
'''
import socket   # Network connection을 위한 디스크립터
import select   # Network event 선택자
import time
import math
import os.path

class Server:
    TimeTick = 1.0      # 하나의 틱 길이 (초단위)
    # Constructor
    def __init__(self, port):
        self.port = port
        self.running = False
        self.users = dict()

    def start(self, worldData):
        # 1. 월드데이터 로드 하기
        self.worldData = worldData
        self.loadWorld()
        
        # 2. Create a socket for listen
        self.listenSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listenSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # 3. Bind address to listen socket
        self.listenSock.bind(('', self.port))

        # 4. Listen socket
        self.listenSock.listen(5)

        # 5. Connected client sockets
        self.reads = [self.listenSock]

        # 6. time tick 설정을 위해서 현재 시간을 제거합니다.
        self.timeOffset = -time.time()
        self.curTick = 0
        
        # Infinite loop
        self.running = True
        while self.running:
            self.select()

        print("Shutdown")
        self.listenSock.close()


    # Load world
    def loadWorld(self):
        for k in self.worldData:
            if os.path.isfile(f"{k}.py"):
                wd = self.worldData[k]
                pyMod = __import__(k)
                #print(pyMod)
                wd[3] = getattr(pyMod, k)()
                
    def getTick(self):
        return int((time.time() + self.timeOffset)/Server.TimeTick)

    # on connect
    def onConnect(self, sock):
        # 요청이 온 클라이언트에 대하여 접속 수락
        client, addr = sock.accept()
        print(f"Connected from {addr}")
        self.reads.append(client) # 소켓등록

    # on close
    def onClose(self, sock):
        self.reads.remove(sock)
        if sock not in self.users: return # 사용자 정보에 이미 없다면 종료

        user = self.users[sock]
        print(f"{user['name']} is closed")
        mesg = f"leave {user['name']}"      # 클라이언트가 소켓 종료.
        self.broadcast(mesg.encode())       # 나갔다는 메시지 띄워주기(그냥 내용역할만함)

        if user['attend'] != None:
            self.onAction(user, [None, None, user['attend'], "leave"]) # user, ss
        del self.users[sock]

    # 리버시 게임에 참여하기
    def onJoin(self, sock, ss):
        # 1. 이미 접속해 있는 다른 유저의 아바타 정보 및 이동정보 한꺼번에  받기
        for k in self.users:
            u = self.users[k]
            mesg = f"join {u['name']}"
            self.send(sock, mesg.encode())
            mesg = f"avatar {u['name']} {u['avatar']}"
            self.send(sock, mesg.encode())
            look = " ".join(map(str, u['look']))
            mesg = f"look {u['name']} {look}"
            self.send(sock, mesg.encode())
            mesg = f"move {u['name']} {u['pos'][0]} {u['pos'][1]} {u['dir']} {u['speed']} {u['aspeed']}"
            self.send(sock, mesg.encode())

        # 2. 새로접속한 클라이언트의 사용자 정보 등록하기.
        self.users[sock] = {"name" : ss[1],
                            "pos" : (0, 0),
                            "dir": 0,
                            "speed" : 0,
                            "aspeed" : 0,
                            "avatar" : 0,
                            "look" : (0,0,0,0),
                            "attend" : None}
        # 3. 새로 접속한 클라이언트의 사용자 정보 브로드캐스팅하기.
        u = self.users[sock]
        mesg = f"move {u['name']} {u['pos'][0]} {u['pos'][1]} {u['dir']} {u['speed']} {u['aspeed']}"
        self.broadcast(mesg.encode())

        
        # 4. 월드 데이터 위치 정보 보낸다. Reversi 10 10 0
        for k in self.worldData:
            wd = self.worldData[k]
            mesg = f"worlddata {k} {wd[0]} {wd[1]} {wd[2]}" # reversi 위치0 위치1 dir
            self.send(sock, mesg.encode())

    # on action : Reversi.py의 구문 실행 : join, leave 명령어
    # ex) 들어올때 : self.onAction(user, ss=["action", "Noah", Reversi","join"])
    # ex) 돌놓을때 : self.onAction(user, ss=["action", "Noah", Reversi","place","16"])
    # ex) 나갈때 : self.onAction(user, [None, None, user['attend'], "leave"])
    def onAction(self, user, ss):

        # ss[2] : user['attend'], 
        if ss[2] not in self.worldData:
            return f"error {ss[2]} is not world object"
        obj = self.worldData[ss[2]][3]              # 생성했던 객체 가져와.
        if obj == None:                             # 리버시 객체가 없다면 에러
            return f"error {ss[2]} has no action"
        # join 
        if ss[3] == "join":
            user['attend'] = ss[2]
            return obj.runCommand(f"join {user['name']}") # join Noah -> 리버시 players에 등록됨.
        # leave 
        if ss[3] == "leave":
            user['leave'] = ss[2]
            return obj.runCommand(f"leave {user['name']}") # leave Noah -> 리버시판에서 나가기
        # place 
        return obj.runCommand(f"{ss[3]} {user['name']} {ss[4]}") # place Noah 16

    # on packet : 패킷 메시지 처리
    def onPacket(self, sock, sdata):
        ss = sdata.split()
        # join Noah
        if ss[0] == "join":
            self.onJoin(sock, ss)
            return
        # 사용자정보에 해당 소켓이 없다면?
        if sock not in self.users:
            print("Error : Unknown user message")
            return
        user = self.users[sock]
        if ss[0] == "shutdown":
            self.running = False
        # 사용자 이동 정보 등록
        elif ss[0] == "move":
            user['pos'] = (float(ss[2]), float(ss[3]))
            user['dir'] = float(ss[4])
            user['speed'] = float(ss[5])
            user['aspeed'] = float(ss[6])
        # ex) ss : action Noah Reversi join
        # ex) ss : action Noah Reversi place 29
        elif ss[0] == "action":
            mesg = f"action {ss[2]} {ss[3]} "+self.onAction(user, ss) # join 또는 place 함.
                # mesg = action Reversi join white
                # mesg = action Reversi place 33333..1122..333
            self.send(sock, mesg.encode())
        elif ss[0] == "avatar":
            user['avatar'] = int(ss[2])
        elif ss[0] == "look":
            user['look'] = tuple(map(int, ss[2:]))        

    # on recv : 
    def onRecv(self, sock):
        # 클라이언트로부터 온 데이터를 수신한다.
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
        needed = int(data.decode())
        try:
            data = sock.recv(needed)
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

    # 소켓에 아무런 이벤트가 발생하지 않으면
    # 1. move 정보 브로드 캐스팅
    # 2. 보드판 정보 update Reversi 3333..1122333 white(또는 none 또는 black)
    def onIdle(self):
        #print(f"onIdle({self.curTick})")
        # 유저들 위치 이동
        for k in self.users:
            u = self.users[k]
            # 유저의 속도와 각속도가 모두 0이면 무시
            if u['speed'] == 0 and u['aspeed'] == 0: continue
            u['dir'] = u['dir'] + u['aspeed'] * Server.TimeTick
            # 각도를 라디안으로 변경
            theta = u['dir'] * math.pi / 180
            x = u['pos'][0] + u['speed'] * math.cos(theta) * Server.TimeTick
            y = u['pos'][1] + u['speed'] * math.sin(theta) * Server.TimeTick
            u['pos'] = (x, y)
            mesg = f"move {u['name']} {u['pos'][0]} {u['pos'][1]} {u['dir']} {u['speed']} {u['aspeed']}"
            self.broadcast(mesg.encode())
        for k in self.worldData:
            wd = self.worldData[k]
            if wd[3] == None: continue
            ret = wd[3].runCommand("board")
            mesg = f"update {k} {ret}"
            self.broadcast(mesg.encode())

    # Select
    def select(self):
        reads, _, _ = select.select(self.reads, [], [], Server.TimeTick/2)

        # for every socket events
        for s in reads:
            # if s is listen socket
            if s == self.listenSock: self.onConnect(s)
            # if s is not listen socket
            else: self.onRecv(s)

        # time tick이 현재 있는지 검사
        ctick = self.getTick()
        if self.curTick < ctick:
            self.onIdle()
            self.curTick += 1

    # Send
    def send(self, sock, data):
        packet = ("%04d"%len(data)).encode()+data
        try:
            sock.send(packet)
        except socket.error:
            pass
                
    # Broadcast
    def broadcast(self, data):
        for s in self.users:
            self.send(s, data)

server = Server(8888)
worldData = dict()
with open("world.txt") as f:
    while True:
        line = f.readline()
        if line == None: break
        ss = line.split()
        if len(ss) < 4: break
        worldData[ss[0]] = [ float(ss[1]), float(ss[2]), float(ss[3]), None ]
for k in worldData:
    print(k, worldData[k])
server.start(worldData)


                
