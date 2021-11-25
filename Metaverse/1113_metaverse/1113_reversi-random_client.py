'''
1.thread 객체 만들어 (객체에 파라미터로 실행할 함수 넣기)
2.thread.start()
3.thread.join()


1) 클라이언트가 서버로:
    server 에 접속
        - join Noah : 
        - avatar Noah 0 :
        - look Noah 0 0 0 0
    리버시판 으로 이동 :
        - 1) 이동하기 : send(sock, f"move {name} 0 0 {rangle} 4 0")
        - 서버는 클라이언트 users[sock]에 이동정보 speed = 4 저장
            - 서버는 onIdle()마다 계속 이동 시킴
        - 2) 이동 완료 : send(sock, f"move {name} {finalPosX} {finalPosY} {rangle} 0 0")
    리버시판에 참여
        - action Noah Reversi join
        - action Noah Reversi place 33
2) 서버가 클라이언트로 :
    - action Reversi join white : 리버시판에 조인할때
    - worlddata Reversi 10 10 : 클라이언트가 리버시 판으로 찾아가야하니까
    - update Reversi 3333....112333 white : 보드판 반환받아 출

*action :
    1) 클라이언트가 서버로 : 
        - action Noah Reversi join
        - action Noah Reversi place 33

    2) 서버로 부터 클라이언트로 : 서버가 클라이언트에 받고 onAction에서 Reversi.py실행후 다시 클라이언트에 놓아
        - action Reversi join white
        
'''
import threading
import socket
import time
import math
import random

isRunning = True
reversiPos = None   # 리버시 위치
turnColor = None
curTurn = "none"
hints = []

# 서버로 부터 데이터 받는 함수
def work1(sock):
    global isRunning, reversiPos, turnColor, curTurn, hints
    while isRunning:
        try:
            data = sock.recv(4)     # 헤더 읽고
            needed = int(data)        # 패킷 길이 저장
            data = sock.recv(needed)  # 패킷 길이만큼 패킷 받아.
        except socket.error:
            print("Socket error 1")
            isRunning = False
            return
        sdata = data.decode()       # 데이터 디코딩하고
        ss = sdata.split()

        # ex) update Reversi 333...112233 white(또는 none , black)
        if ss[0] == "update":       
            thints = []         # hints 저장소(둘수있는 곳 모아두기)
            for r in range(8):
                print("+---"*8+"+")
                for c in range(8):
                    if ss[2][r*8+c] == '0':     # 0 : hints -> 해당 칸 인덱스 표시
                        print(f"|{r*8+c:^3}", end="")
                        thints.append(r*8+c)
                    elif ss[2][r*8+c] == '3':   # 3 : 둘수없는곳은 빈칸으로
                        print("|   ", end="")
                    elif ss[2][r*8+c] == '1':   # turn 1 : O
                        print("| O ", end="")
                    elif ss[2][r*8+c] == '2':   # turn 2 : X
                        print("| X ", end="")
                print("|")
            print("+---"*8+"+")
            curTurn = ss[3] # 현재 턴 일단 none
            #print(curTurn)
            hints = thints      # hints

        # worlddata Reversi 10 10  메시지 받으면 리버시 위치 저장
        elif ss[0] == "worlddata":
            if ss[1] == "Reversi":
                reversiPos = (float(ss[2]), float(ss[3]))
        # action Reversi join white 메시지 받으면 자신의 돌 색깔 출력
        # <- 
        elif ss[0] == "action":
            if ss[1] == "Reversi" and ss[2] == "join":
                turnColor = ss[3]
                print("나의 돌 색깔은 %s."%turnColor)
        else:
            print(sdata)

# 서버로 데이터 전송하는 함수
def work2(sock):
    global isRunning, reversiPos, turnColor, curTurn, hints
    # {name}란 이름으로 join
    name = f"reversi_{random.randrange(1, 10000):04}"
    send(sock, f"join {name}")
    send(sock, f"avatar {name} {random.randrange(0,2)}")
    send(sock, f"look {name} {random.randrange(0,4)} {random.randrange(0,4)} {random.randrange(0,4)} {random.randrange(0,4)}")
    # 리버시 게임판으로 자동 이동하기 위해서 reversiPos 기다림
    while reversiPos == None:
        time.sleep(5.0)
    # reversi 판 있는 곳의 각도 구하기
    rangle = math.degrees(math.atan2(reversiPos[1], reversiPos[0]))
    # 리버시 판으로 이동하기.
    send(sock, f"move {name} 0 0 {rangle} 1 0") # client의 speed 4만큼으로 이동
    rdistance = math.sqrt(reversiPos[0]**2 + reversiPos[1]**2)-1.5 # 리버시판에서 1.5 정도 떨어지기
    time.sleep(rdistance) # 빠른 속도를 위해. 

    # 다 도착하면!
    finalPosX = rdistance*math.cos(math.radians(rangle))
    finalPosY = rdistance*math.sin(math.radians(rangle))
    send(sock, f"move {name} {finalPosX} {finalPosY} {rangle} 0 0") # 리버시판 방향으로 바라봄.

    while True:
        # reversi join
        send(sock, f"action {name} Reversi join")
        # 게임이 시작할때까지 기다림
        while curTurn == "none":
            time.sleep(2.5)
        # 게임이 끝날때까지 계속
        while curTurn != "none":
            # 현재의 턴이 내 턴이고 & 둘곳이있다면(안끝났다면)
            if curTurn == turnColor and len(hints) > 0:
                p = random.choice(hints)
                send(sock, f"action {name} Reversi place {p}")
            time.sleep(1.0)
        print("Quit play")
        time.sleep(2.0)
    
    """
    while isRunning:
        s = input(">> ")
        if s == "/quit":
            isRunning = False
            return
        data = s.encode()
        packet = ("%04d"%len(data)).encode()+data
        sock.send(packet)
    """

# sock으로 mesg를 보내는 함수
def send(sock, mesg):
    # packet 인코딩
    packet = ("%04d%s"%(len(mesg), mesg)).encode()
    sock.send(packet)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.connect( ("127.0.0.1", 8888) )
except socket.error:
    print(f"Network error {socket.error}")
    quit()
    
print("Connection is established")
thread1 = threading.Thread(target=work1, args=(sock,))
thread1.start()
thread2 = threading.Thread(target=work2, args=(sock,))
thread2.start()
thread1.join()
thread2.join()
