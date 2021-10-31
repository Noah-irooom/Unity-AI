'''
LISTEN -> CONNECT ->ACCEPT -> SEND <-> RECV -> CLOSE

main keyword
1. 소켓 만들기 : socket.socket(socket.AF_INET, socket.SOCK_STREAM)
2. 소켓 연결하기 : socket.connect((서버주소, 포트번호)) -> True 반환
    - # (클라이언트 -> 서버(웹))
    - 예외 처리 1) socket.error 2) socket.timeout -> False 반환
3. 소켓이 받아오기 : sock.recv(length)    ->  buf.decode("ascii") #아스키 코드를 decode로 바꿔
    - # 서버(웹) -> 클라이언트
    - # 받은 데이터의 길이가 0이라면 상대가 연결을 끊은 경우.
    - 예외 처리 : sock.error -> return None
'''
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def connect(sock, addr, port):
    try:
        sock.connect((addr, port))
    except socket.error:
        print(f"Socket error : {socket.error}")
        return False
    except socket.timeout:
        print("Socket timeout")
        return False
    return True

def recv(sock, length):
    try:
        buf = sock.recv(length)
        if len(buf) == 0:
            print("Peer is disconnected")
            return None
    except sock.error:
        print(f"recv() : {socket.error}")
        return None
    return buf.decode("ascii")

if connect(sock, "www.google.com", 80):
    string = recv(sock, 100)
    if string is not None:
        print(f"Received {string}")
    sock.close()

