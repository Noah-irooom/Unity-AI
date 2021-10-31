''' server.py
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
    5.2. sock.accept() - 이벤트발생 리슨소켓은 "클라이언트소켓"과 그 "addr"를 받아둬.
        - onConnect()
        - self.users[client] = 클라이언트 정보 리스트["이름","번호"]  : key는 클라이언트 소켓, value는 정보 담아.
    5.3. sock.recv(1024) - 클라이언트 소켓이라면, 그 소켓으로 부터 데이터를 추출함.
        - onRecv()
    5.4. self.reads.remove(sock) - 받은 데이터가 0이거나 없다면 쓸모없는 클라이언트이므로 self.reads
        - onClose() (<-onRecv()에서 데이터 없거나 짧으면, 또는 에러나면)
    5.5. sdata = data.decode() - 클라이언트 소켓으로부터 추출한 데이터를 decode()해야함.
        - onRecv()
        - sdata를 디코딩하면 split사용하여 정보 받아 users[client sock]에 등록 가능
        - self.users[sock] == sdata_split[1] users 클라이언트 소켓에 등록한다.
    5.6. s.send(mesg.encode()) #
        - broadcast() (<- onRecv())
        - 클라이언트소켓의 데이터를 받아 디코딩(sdata)한 후에 등록 및 mesg를 만들고 다시 인코딩하여
        - (self.reads는 접속한 모든클라이언트 소켓들 있어)
        - 접속해 있는 모든 클라이언트들의 그들의 소켓을 사용해 다시 s.send()
    
6. 리슨소켓을 닫아준다.
    - listenSock.close()

# Server 클래스 :
    - (1) 포트 받아 생성함.
    - (2) server.start() : 메인 골자! (나머지는 함수정리)
    - (3) self.select 함수 만들어 실행 - 주요 부분.
'''

import socket # Network connection을 위한 디스크립터
import select # Network event 선택자
import time   # 시간 관련된 내용

class Server:
    # Constructor
    def __init__(self, port):
        self.port = port
        self.running = False # 계속 받을 것인가.

        # 사용자 프로파일
        self.users = dict()

    # Start server
    def start(self):
        # 1. 서버의 LISTEN 위한 소켓을 만든다.
        self.listenSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listenSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # 2. 소켓을 듣기 위해 '주소'와 '포트'를 바인드 한다.
        self.listenSock.bind(('', self.port)) # 이주소와 8888포트 묶기

        # 3. 소켓으로 이제 듣는다.
        self.listenSock.listen(5)

        # 4. 클라이언트 요청을 읽을 리슨 소켓을 담는다.
        self.reads = [self.listenSock]

        # 5. 리슨소켓에 요청한 클라이언트를 받아준다.(connection accept, data recv)
        self.running = True
        while self.running:
            self.select() # 이벤트 발생한 리슨소켓을 선택하고 reads에 담아
        # 10초 동안 이벤트가 발생하지 않으면 ( 즉, data를 주지 않으면)
        # running=True에 의해 계속 select실행됨 event_reads에는 아무것도 없어

        # 6. 리슨 소켓을 닫아준다.
        print("Shutdown")
        self.listenSock.close() # 



    # on connect
    # 현재 리슨소켓이라면, accept()한다.
    def onConnect(self, sock):
        # 요청이 온 클라이언트에 대하여 접속 수락
        client, addr = sock.accept()
        print(f"Connected from {addr}")
        self.reads.append(client) # 리슨소켓만 있던 reads에 클라이언트 소켓 등록.
        self.users[client] = ["Anonymous", "0000"] # user(dict)에 key : 클라이언트 소켓, value: 다음 정보들
        
    # on close
    def onClose(self,sock):
        self.reads.remove(sock)
        del self.users[sock]

    # on recv
    # 데이터를 받고 확인하여 쓸모없는 클라이언트는 제거한다.
    def onRecv(self, sock):
        try:
            data = sock.recv(1024) # 클라언트로 소켓이 클라이언트의 데이터를 추출
            if data == None or len(data) <= 0:
                print("closed by peer") # 다른 클라이언트가 /quit했을때.
                self.broadcast("다른 클라이언트가 방을 나갔습니다.".encode())
                self.onClose(sock)
                return
        except socket.error:
            print("socket error")
            self.onClose(sock)
            return
        sdata = data.decode()

        if sdata[0] == "/":
            ss = sdata.split()
            if ss[0][1:] == "name": # /name -> name
                print(f"Change name {self.users[sock][0]} --> {ss[1]}")
                self.users[sock][0] = ss[1] # "Anonymous" -> 클라이언트 이름
            elif ss[0][1:] == "phone":
                self.users[sock][1] = ss[1]
            elif ss[0][1:] == "shutdown":
                self.running = False
            return
            
        user = self.users[sock][0]
        phone = self.users[sock][1]
        mesg = f"{user}({phone}) : {sdata}"
        print(mesg)
        self.broadcast(mesg.encode()) # 메시지를 송수신 할 때는 encode()해야한다.!

    # Select : 네트워크 이벤트가 발생한 리슨 소켓을 선택한다.
    def select(self):
        event_reads, _, _ = select.select(self.reads, [], [], 10.0)

        # 모든 소켓 이벤트에 대하여
        for s in event_reads:
            # 만약 리슨 소켓이면 클라이언트 소켓의 요청을 받아줌.
            if s == self.listenSock: self.onConnect(s)
            # 만약 클라이언트 소켓이라면, 클라이언트의 데이터를 받아줌.
            else: self.onRecv(s)

        # 10초 동안 이벤트가 발생하지 않으면 ( 즉, data를 주지 않으면) running=True에 의해 계속 select실행됨
        print("기다리는 중")

    # Broadcast
    def broadcast(self, data):
        # data는 encode된 형태로 전달됨.
        for s in self.reads:
            # 접속해 있는 모든 클라이언트들에게(self.reads에 있는 모든 소켓들에게)
            if s != self.listenSock:# 클라이언트 소켓만 보낸다.
                s.send(data)
                # 클라이언트의 데이터를 받아 디코딩한 후에
                # 등록 및 mesg를 만들고
                # 다시 인코딩하여 클라이언트(자신) 소켓에다 올림.
                

server = Server(8888) # Server 인스턴스 생성
server.start()
