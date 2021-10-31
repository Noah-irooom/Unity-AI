'''1015_client.py
1. 클라이언트 소켓을 생성하여 서버로 접속(서버 주소로, 포트번호로)
2. 멀티쓰레드를 사용하여 두가지 동작을 돌림.
    1) work2는 클라이언트 소켓은
        - sock.send() : input으로 입력받은 데이터를 자신  클라이언트 소켓으로 올려.
        - 이 데이터는 서버로 전달된다.
    2) work1
        - sock.recv() : 연결된 서버가 클라이언트 소켓을 이용해 s.send() 했으므로 바로 클라이언트는 recv()하면 됨.
        

'''
import threading
import socket
import time

isRunning = True

''' 브로드 캐스트된 데이터 받기 쓰레드'''
# 서버가 접속한 클라이언트에게 그들의 소켓에 send() 부쳤으므로
# 클라이언트 소켓은 바로 자신의 소켓을 recv()해도  데이터를 받을 수있다.
def work1(sock):
    global isRunning
    while isRunning:
        try:
            data = sock.recv(1024) # 서버의 소켓은 데이터를 추출해와.
            if data == None or len(data) <= 0:
                # 데이터가 None이거나 연결이끊기면
                isRunning = False
                return
        except socket.error:
            isRunning = False
            return
        sdata = data.decode()
        print(sdata)

''' 데이터 쓰기 쓰레드'''
# 클라이언트의 데이터를 입력받아 클라이언트 소켓에 올려.
def work2(sock):
    global isRunning
    while isRunning:
        s = input(">> ")
        if s == "/quit":
            isRunning = False
            return
        sock.send(s.encode()) # 입력받으면 내용인코딩하여 자신(클라이언트) socket에다 올려줌.
        # 그러면 서버가 클라이언트가 보낸 소켓으로 sock.recv()하면 이를 디코딩하여 등록 및 mesg로 만들어
        # mesg를 만들어 다시 인코딩하여 sock.send()를 하여 소켓을 보내주면
        # 접속한 클라이언트들에게 서버의 socket으로 sock.recv

# 클라이언트 소켓을 생성한다.
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.connect(("127.0.0.1", 8888)) # 서버 주소에 +  이 포트번호로 접근한다.
    # server.py에서 client, addr = sock.accept() : addr는 주소 및 포트번호를 가짐.
except socket.error:
    print(f"Network error {socket.error}")
    quit()

print("Connection is established")
thread1 = threading.Thread(target=work1, args=(sock,)) # work1에 sock을 넣어준다.
thread1.start()
thread2 = threading.Thread(target=work2, args=(sock,))
thread2.start()
