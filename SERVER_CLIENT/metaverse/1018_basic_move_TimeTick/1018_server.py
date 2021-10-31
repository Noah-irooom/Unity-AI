import socket   # Network connection을 위한 디스크립터
import select   # Network event 선택자
import time     # 시간 관련된 내용
import math     # math module

'''
Time Tick : 서버가 계속 일할 수 없으므로 일정시간마다 일을 처리해야한다.
    - 그 일정시간을 Time Tick이라한다.
    - 메타버스는 보통 100ms마다 일처리하게 하는데 Time Tick은 0.1로 설정.

방향 : 현재 방향 + (각속도 * 시간)

'''
'''
1. 소켓을 만든다. ( 서버의 리슨을 위한 소켓)
    - socket.socket(socket.AF_INET, soket.SOCK_STREAM) # 소켓 생성
    - listenSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # 소켓 옵션 설정ㄹ
        - SO_REUSEADDR : 연결이 종료 되어도 접근 가능하게?
2. 서버 '주소'와 '포트번호'를 바인딩(하나로 묶어줌) - 이 포트는 이 주소로 연결!
    - listenSock.bind(('', self.port))
3. 소켓으로 Listen 한다 ( 이것을 위해서!)
    - listenSock.listen(5)  # 현재 클라이언트가 요청한 것을 하드웨어적으로 5개 처리 가능
    - 다 받아주면 계속 더 받을 수 있어(1이라도)
4. 클라이언트 요청을 읽을 리슨 소켓을 담는다.
    - self.reads = [self.listensSock]
    - self.reads는 소켓을 담는통이다
        - 서버의 리슨 소켓 + 클라이언트 소켓 : 모두 담아.
5. 리슨소켓이 클라이언트의 요청을 수락하고 + 클라이언트의 데이터를 받는다..
    - (connection accept, data recv) : 무한루프 돌며
    - self.select() -> select.select(), sock.accept(), sock.recv() 
    5.1. select.select() - 이벤트가 발생한 리슨 소켓 선택하여 self.reads에 모아놔
            - 너무 빠르게 돌지 않도록 10초 시간을 두면서 이벤트 받아둬.
        5.1.1. sock.accept() - 이벤트발생 리슨소켓은 "클라이언트소켓"과 그 "addr"를 받아둬.
            - onConnect()
            - self.users[client] = 클라이언트 정보 리스트["이름","번호"]  : key는 클라이언트 소켓, value는 정보 담아.
        5.1.2. sock.recv(1024) - 클라이언트 소켓이라면, 그 소켓으로 부터 데이터를 추출함.
            - onRecv()
        5.1.3. self.reads.remove(sock) - 받은 데이터가 0이거나 없다면 쓸모없는 클라이언트이므로 self.reads
            - onClose() (<-onRecv()에서 데이터 없거나 짧으면, 또는 에러나면)
        5.1.4. sdata = data.decode() - 클라이언트 소켓으로부터 추출한 데이터를 decode()해야함.
            - onRecv()
            - sdata를 디코딩하면 split사용하여 정보 받아 users[client sock]에 등록 가능
            - self.users[sock] == sdata_split[1] users 클라이언트 소켓에 등록한다.
        5.1.5. s.send(mesg.encode()) #
            - broadcast() (<- onRecv())
            - 클라이언트소켓의 데이터를 받아 디코딩(sdata)한 후에 등록 및 mesg를 만들고 다시 인코딩하여
            - (self.reads는 접속한 모든클라이언트 소켓들 있어)
            - 접속해 있는 모든 클라이언트들의 그들의 소켓을 사용해 다시 s.send()
    5.2. 이벤트 발생하지 않으면
        - onIdle() 실행.
        - curTick < getTick() : 서버가 일정 시간에만 onIdle 실행되도록 해줌.
        
    
6. 리슨소켓을 닫아준다.
    - listenSock.close()
'''


class Server:
    
    TimeTick = 5.0 # 하나의 틱길이 (초단위)

    def __init__(self, port):
        self.port = port
        self.running = False
        self.users = dict()

    def start(self):
        # 1. create socket
        self.listenSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listenSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 2. bind address to listen socket
        self.listenSock.bind(('', self.port))
        # 3. listen socket
        self.listenSock.listen(5)
        # 4. connected client sockets list
        self.reads = [self.listenSock]

        # 5. time tick 설정을 위해서 "첫 기록 시간"을 제거한다. 
        self.timeOffset = time.time()
        self.curTick = 0

        # 6. select()
        self.running = True
        while self.running:
            self.select()

        # 7. close()
        print("Shutdown")
        self.listenSock.close()

    
    def getTick(self):
        # 첫기록 시작 부터 5초가 되기 전까지는 0만 반환.
        # (현재 진행 시간 -  첫 기록 시간) / 5.0  -> 00..00112..22..333..44 
        return int((time.time() - self.timeOffset) / Server.TimeTick)

    def onConnect(self, sock):
        client, addr = sock.accept()
        print(f"Connected from {addr}")
        # 1. 이미 접속한 다른 유저의 정보를 새로 접속한 client socket에 보내줌.(이동정보)
        for k in self.users:
            u = self.users[k]
            mesg = f"/move {u['name']} {u['pos']} {u['dir']} {u['speed']}"
            client.send(mesg.encode())
        # 2. 새로 접속한 클라이언트 소켓 등록 하기
        # 이번엔 dict로 구성
        self.reads.append(client)
        self.users[client] = {
            'name': "Anonymous",
            "pos" : (0,0),
            "dir" : 0,
            "speed" : 0,
            "aspeed" : 0,
        }

        # 3. 새로 접속한 클라이언트 정보를 
        u = self.users[client]
        mesg = f"/move {u['name']} {u['pos']} {u['dir']} {u['speed']}"
        self.broadcast(mesg.encode())

    # on close
    def onClose(self, sock):
        self.reads.remove(sock) # self.reads에 해당 클라이언트 소켓을 제거
        del self.users[sock]    # self.users에 클라이언트 소켓을 키로하는 사용자 정보 제거

    # on packet
    def onPacket(self, user, sdata):
        ss = sdata.split()
        if ss[0][1:] == "name":
            print(f"Change name {user['name']} -> {ss[1]}")
            user['name'] = ss[1]
        elif ss[0][1:] == "shutdown":
            self.running = False        # 서버를 중단시킴.
        elif ss[0][1:] == "move":
            user['speed'] = int(ss[1])
        elif ss[0][1:] == "turn":
            user['aspeed'] = int(ss[1]) # aspeed를 조절하여 방향 조정


    # on recv
    def onRecv(self, sock):
        # 클라이언트로부터 온 데이터를 수신한다.
        try:
            data = sock.recv(1024)
            if data == None or len(data) <= 0:
                print("closed by peer") # 다른 클라이언트가 나간 경우
                mesg = f"{self.users[sock]['name']}님이 퇴장했습니다."
                print(mesg)
                self.broadcast(mesg.encode())
                self.onClose(sock) # 클라이언트 소켓정보(self.reads) + 사용자 정보(self.users) 모두 없앰.
                return
        except socket.error:
            print("socket error")
            self.onClose(sock)
            return

        sdata = data.decode()
        if sdata[0] == "/":
            self.onPacket(self.users[sock], sdata)
            return
        
        user = self.users[sock]['name']
        mesg = f"{user}: {sdata}" # ex) Noah : 안녕하세요.
        print(mesg)
        self.broadcast(mesg.encode())

    # 유저의 위치 계산 로직 - TimeTick마다 계산 
    def onIdle(self):
        for k in self.users:
            u = self.users[k]
            # 유저의 속도와 각속도 모두 0이면 무시
            if u['speed'] == 0 and u['aspeed'] == 0: continue
            # 방향 결정
            u['dir'] = u['dir'] + u['aspeed'] * Server.TimeTick
            # 위치 결정
            theta = u['dir'] * math.pi / 180
            x = u['pos'][0] + u['speed'] * math.cos(theta) * Server.TimeTick
            y = u['pos'][1] + u['speed'] * math.sin(theta) * Server.TimeTick
            u['pos'] = (x,y)
            mesg = f"/move {self.curTick} {u['name']} {u['pos']} {u['dir']} {u['speed']}"
            self.broadcast(mesg.encode())

    # Select
    def select(self):
        reads, _, _ = select.select(self.reads, [], [], Server.TimeTick/2)
        # TimeTick의 절반(2.5초) 계속 이벤트 발생했는지 체크
        # 반면 이동정보는 5초만큼 바뀌어
        # -> 어쨌든 5초마다 업데이트 되니 5초마다 onIdle시행
        
        # for every socket events
        for s in reads:
            # if s is listen socket
            if s == self.listenSock: self.onConnect(s)
            # if s is not listen socket
            else: self.onRecv(s)

        # time tick이 현재 있는지 검사
        ctick = self.getTick() # 첫기록 시작 부터 5초가 되기 전까지는 0만 반환.
        if self.curTick < ctick:
            self.onIdle()
            self.curTick += 1
                
    # Broadcast
    def broadcast(self, data):
        for s in self.reads:
            if s != self.listenSock:
                s.send(data)

server = Server(8888)
server.start()















        
