''' 1016 server.py
# ** 1. 패킷의 움직임 **
(1) Client to Server : 데이터 보내기
    - /move speed
        speed  - 1 : 걷기 ,  0 : 정지
    - /turn direction
        direction - 1 : 반시계 방향, -1 : 시계방향, 0 : 멈춤
(2) Server to Client : 현재 상태 반환하기??
    - /move name curposition direction speed
        - curpostion: x, y
        - direction: (angle)0 ~ 359
        - speed 1: 걷기
        - speed 0: 정지
    - /turn name direction
        - direction 1: 반시계방향
        - direction -1: 시계방향
        - direction 0: 멈춤

# ** 2. 사용해야할 삼각함수들 **
    1. math 라이브러리
        - cos(rad), sin(rad), atan2(float,float) -> 결과는 라디안


# **3. 서버의 동작 방식**
    (1) 새로 클라이언트가 접속할때 할일
        1. sock.accept() : 접속수락
        2. 다른 사용자 정보 가져오기
            - 월드에 들어와 있는 다른 사용자 정보를 가져오기(이동정보 표기)
            - self.users : 사용자 등록 (key : client socket, value : 이름, phone, cur_position, direction, speed)
        3. 새로 접속한 사용자 정보 등록 ( self.users에 업데이트 하기)
        4. 월드에 들어와 있는 다른 사용자에게 새로이 접속한 사용자 보내주기

    (2) 명령어가 왔을때
        1. 사용자 정보 업데이트
        2. 월드에 들어와있는 다른 사용자에게 해당 명령어를 보내주기

    (3) Idle 동작 시
        1. 업데이트가 필요한 사용자에 대해서
            - 해당 사용자 업데이트 (시뮬레이션)
            - 업데이트된 내용을 월드에 접속해 있는 사용자에게 보내주기
    (4) select 함수를 빠져나오는 경우
        1. 네트워크 이벤트가 발생했을때
        2. 타임아웃이 걸린경우

    (5) 문제가 되는경우
        - time 0000: select 함수 호출(타임아웃 100)
        - time 0080: 네트워크 이벤트가 발생
        - time 0080: select 함수 호출(타임아웃 100)
        - time 0120: 네트워크 이벤트 발생
        - time 0120: select 함수 호출(타임아웃 100)

'''
import socket # network connection 위한 디스크립터
import select   # Network event 선택자
import time     # 시간 관련된 내용
import math     # math module


class Server:
    def __init__(self, port):
        self.port = port
        self.running = False
        self.users = dict() # 사용자 프로파일

    # Start server
    def start(self):
        # 서버의 리슨 소켓 만들기
        self.listenSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listenSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # 리슨 소켓에 접속위한, 서버 주소와 포트번호 바인딩
        self.listenSock.bind(('', self.port))

        # 리슨하기
        self.listenSock.listen(5)

        # 접속한 클라이언트의 소켓들
        self.reads = [self.listenSock]

        # 5. select() -> sock.accept(), sock.recv()
        self.running = True
        while self.running:
            self.select()

        # 6. sock.close()
        print("Shutdown")
        self.listenSock.close()

    # on Connect
    def onConnect(self, sock):
        #  1. 요청이 온 클라이언트에 대하여 접속 수락
        client, addr = sock.accept()
        print(f"Connected from {addr}")

        # 2. 이미 접속해 있는 다른 유저의 이동 정보 받기.
        for k in self.users:
            u = self.users[k] # users에 등록된  접속한 클라이언트 소켓
            mesg = f"/move {u[0]} {u[2]} {u[3]} {u[4]}" # 이름 현위치 방향 속도
            client.send(mesg.encode())  # 새로 요청이 온 소켓에 데이터 전송
        self.reads.append(client) # 새로 요청온 클라이언트 소켓 등록하기

        # 3. 새로 접속한 클라이언트 소켓 등록
        self.users[client] = ["Anonymous", "0000", (0, 0), 0, 0, 0] # 이름 번호 현위치 방향 속도 각속도

        # 4. 다른 사용자들에게 브로드캐스팅
        u = self.users[client]
        mesg = f"/move {u[0]} {u[2]} {u[3]} {u[4]}"
        self.broadcast(mesg.encode())

    # on close
    def onClose(self, sock):
        self.reads.remove(sock) # 연결 끊긴 클라이언트는 그 소켓을 제거해준다.
        del self.users[sock]

    # on packet
    # 기존의 클라이언트가 보낸 데이터가 디코딩된 후 부터 처리.
    def onPacket(self, user, sdata):
        # user는 self.users[sock], sdata = data.decode()
        ss = sdata.split()
        if ss[0][1:] == "name":
            print(f"Change name {user[0]} --> {ss[1]}") # user[0] : 이름(처음 : Anonymous)
            user[0] = ss[1]
        elif ss[0][1:] == "phone":
            user[1] = ss[1]
        elif ss[0][1:] == "shutdown":
            self.running = False
        elif ss[0][1:] == "move":
            user[4] = int(ss[1]) # /move speed

    # on recv
    def onRecv(self, sock):
        # 클라이언트로부터 온 데이터를 수신한다.
        try:
            data = sock.recv(1024)
            if data == None or len(data) <= 0:
                print("closed by other client peer")
                self.onClose(sock) # 연결이 끊긴 클라이언트 소켓은 self.users에서 제거
                return
        except socket.error:
            print("socket error")
            self.onClose(sock)
            return
        # 읽은 데이터 패킷을 self.users에 등록해줘야 한다.
        sdata = data.decode()
        if sdata[0] == "/":
            self.onPacket(self.users[sock], sdata) # onPacket이 self.users에 등록
            return
        user = self.users[sock][0]
        phone = self.users[sock][1]
        mesg = f"{user}({phone}) : {sdata}"
        print(mesg)
        self.broadcast(mesg.encode())


    # 유저들의 위치 이동 로직 - 계속 1초마다 업데이트 해서 정보 띄워줌
    # self.users에 등록된 움직임 정보로 현재 위치를 계산한다.
    def onIdle(self):
        # print("metaverse server is alive")

        # 유저들 위치 이동
        for k in self.users:
            u = self.users[k]

            # 유저의 속도와 각속도가 모두 0이면 무시 - 움직임 변화도, 방향변화도 없으니
            if u[4] == 0 and u[5] == 0: continue
            u[3] = u[3] + u[5] * 1.0 # 방향은 (현방향 + 각속도 * 시간)
            # 참고로 select 업데이트 시간이 1초 이므로 :1초 마다 각속도 만큼 업데이트

            # 각도를 라디안으로 변경
            theta = u[3] * math.pi / 180
            # 1초마다 이 방향으로 이 속도만큼 움직이겠다. ( 세타는 x 축기준)
            x = u[2][0] + u[4] * math.cos(theta) * 1.0 # 현위치(x) + 속도 * 방향 * 시간  
            y = u[2][1] + u[4] * math.sin(theta) * 1.0
            
            u[2] = (x, y) # 현위치 등록
            print(f"{u[0]} : pos = {u[2]}, direction = {u[3]}")
            mesg = f"/move {u[0]} {u[2]} {u[3]} {u[4]}"
            self.broadcast(mesg.encode())

    # Select
    def select(self):
        event_reads, _, _ = select.select(self.reads, [], [], 1.0) # 이벤트 발생한 것만 reads에 담겨
        for s in event_reads:
            if s == self.listenSock: self.onConnect(s)
            else: self.onRecv(s)

        # timeout event
        # 이벤트가 발생하지 않은 경우면(1초 동안) onIdle 실행하여 위치정보 반환!
        if len(event_reads) == 0:
            self.onIdle()

    # Broadcast
    def broadcast(self, data):
        for s in self.reads:
            if s != self.listenSock:
                s.send(data) # self.reads에 있는 모든 클라이언트 소켓들에게 전달

server = Server(8888)
server.start()





























