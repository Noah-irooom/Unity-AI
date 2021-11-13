/*
1025_SocketDesc
    1. socket  vs  desc
        - socket : 네트워크 접속 담당
            - 접속 : socket.Close() -> socket.Connect() -> socket.Connected
            - 통신 종료 : socket.Shutdown()
            - 데이터 받기 
                - 헤더 읽기: socket.BeginReceive(recvBuffer) -> ReceiveComplete -> Encoding.UTF8.GetString(recvBuffer)
                    (recvBuffer로 받아주기 -> 헤더 크기 4 -> 메시지의 길이 정보)
                - 메시지 읽기 : socket.BeginReceive(packet) -> ReceiveComplete -> NetworkState.Complete  
                    (실제 메시지 내용은 pakcet버퍼가 받아줌. -> 그대로 Send할 예정)
            - 데이터 보내기
                - sendBuffer : 보낼 버퍼 만들기
                    - 0 - 4 까지 : 헤더 정보 (메시지 패킷의 길이 정보)
                    - 4 - 패킷 길이 : 메시지 정보 
                - socket.BeginSend(sendBuffer) -> SendComplete -> socket.EndSend(ar)
        - desc : 


*/

using System;
using System.Text;
using System.Net.Sockets;
using UnityEngine;

public class SocketDesc
{
    // 네트워크 상태를 위한 열거형(enumerator)
    enum NetworkState
    {
        Disconnect,         // 현재 네트워크 연결이 안된 상태
        Ready,              // 연결이 되어서 메세지를 받을 수 있는 상태
        WaitForHeader,      // 현재 헤더를 읽고 있는 중
        WaitForMessage,     // 현재 메세지를 읽고 있는 중
        Complete,           // 메시지 수신이 끝났음
        MaxNumber
    }

    // 사용할 변수들
    Socket socket;          // 네트워크 접속을 위한 네트워크 핸들
    byte[] packet;          // 네트워크 메시지 패킷
    byte[] recvBuffer;      // 임시로 저장할 버퍼
    NetworkState state;     // 네트워크 상태

    // [1] 소켓 디스크립터 생성 함수 - 소켓 생성, 디스크립터에 장착, 받을 데이터크기
    public static SocketDesc Create()
    {
        // 1. 소켓을 생성
        Socket sock = new Socket(AddressFamily.InterNetwork,
            SocketType.Stream, ProtocolType.Tcp);
        if(sock == null) return null;
        // 2. 소켓 디스크립터를 생성 - Main.cs에서 사용할 부분.
        var desc = new SocketDesc();
        desc.socket = sock; // 소켓 디스크립터에 생성한 소켓 입력
        desc.recvBuffer = new byte[4]; // 받을 수 있는 데이터 크기
        // 3. 소켓 디스크립터를 반환
        return desc;
    }

    // [2] 네트워크 접속
    public bool Connect(string address, int port)
    {
        // 현재 접속 상태가 연결끊김이 아니면 먼저 닫아주고 다시 접속.
        if (state != NetworkState.Disconnect) socket.Close();
        try { socket.Connect(address, port); } // (다시) 접속
        catch(SocketException e) 
        {
            Debug.LogFormat("Error in connect : {0}", e.Message);
            return false;
        }
        state = NetworkState.Ready; // 네트워크 연결이 되어 메시지 받을 수 있는 상태.
        return socket.Connected;
    }
    
    // [3] 네트워크 통신 종료
    public void Shutdown()
    {
        // 소켓이 없거나 소켓이 네트워크 연결이 안 된 상태라면 아무것도 안한다.
        if (socket == null || !socket.Connected) return;
        socket.Shutdown(SocketShutdown.Both); // 접속한 소켓의 통신을 종료한다.
        // socket.Close() 소켓을 닫아줌. socket.Shutdown 통신을 종료함.
    }

    // [4] 네트워크에서 전송된 데이터를 가져오기
    public byte[] GetPacket()
    {
        // 전송이 완료된 경우에는 packet 반환. -> 헤더 후 메시지까지 다 받아야 Complete됨.
        if (state == NetworkState.Complete)
        {
            state = NetworkState.Ready; // GetPacket으로 패킷 정보 Main.cs에 전달했으면 다시 데이터 받을 준비
            return packet;
        }
        return null; // 전송 완료 되지 않으면 null 반환
    }

    // [5] 네트워크 처리하기 - 메시지 읽을 준비 상태라면 헤더 먼저 읽기
    public bool ProcessNetwork()
    {
        // 1. 소켓이 없거나 비연결 상태인 경우 false 반환
        if (socket == null || !socket.Connected) return false;
        // 2. 전송이 완료된 경우에는 아무 일도 안하기. -> 헤더읽고, 메시지읽어야 Complete됨.
        if (state == NetworkState.Complete) return true;
        // 3. Ready 상태이면 헤더를 읽기
        if (state == NetworkState.Ready)
        {
            state = NetworkState.WaitForHeader; // 헤더 읽기로 지정.
            socket.BeginReceive(recvBuffer, 0, 4, SocketFlags.None,
                new AsyncCallback(ReceiveComplete), null); // recvBuffer로 헤더 데이터 받아.
        }
        return false;
    }

    // [6] 데이터 받기가 완료된 경우 불리는 콜백 
    void ReceiveComplete(IAsyncResult ar)
    {
        // len이 0인 경우에는 상대쪽에서 접속을 끊은 경우
        // len이 0보다 작은 경우에는 네트워크 에러가 발생한 경우
        int len = socket.EndReceive(ar);
        if(len <= 0) { socket.Close(); state = NetworkState.Disconnect; return; }

        // 네트워크 상태가 헤더를 기다리는 경우
        if (state == NetworkState.WaitForHeader)
        {
            // 1. 바이트 스트링을 문자열로 변환 - 헤더에는 메시지의 길이 정보 있어.
            string str = Encoding.UTF8.GetString(recvBuffer);
            // 2. 숫자 문자열을  정수로 변환
            int needed = Int32.Parse(str);
            // 3. needed만큼 데이터 받을 버퍼 생성.
            packet = new byte[needed];
            // 4. 네트워크 상태를 메세지를 기다리는 것으로 전환.
            state = NetworkState.WaitForMessage;
            // 5. 네트워크 읽기 요청을 한다.
            socket.BeginReceive(packet, 0, needed, SocketFlags.None,
                new AsyncCallback(ReceiveComplete), null);
        }
        else if (state == NetworkState.WaitForMessage)
        {
            // 1. 네트워크 상태를 완료라고 바꾼다.
            state = NetworkState.Complete;
        }
    }

    // [7] 패킷(메시지 내용)내용을 보낸다.
    public void Send(byte[] packet)
    {
        string str = String.Format("{0,4}", packet.Length); // 헤더 0006 -> 패킷길이 6
        // 1. 보낼 버퍼 생성.
        byte[] sendBuffer = new byte[4 + packet.Length]; // sendBuffer : 보낼 때도 버퍼 만들어 보냄.
        
        // 2. 버퍼에 헤더 내용, 메시지 내용 담기.
        System.Buffer.BlockCopy(Encoding.UTF8.GetBytes(str), 0, sendBuffer, 0, 4); // sendBuffer의 0~4는 packet길이 헤더 정보
        System.Buffer.BlockCopy(packet, 0, sendBuffer, 4, packet.Length); // sendBuffer의 4~는 실제 pakcet 메시지 정보 담기

        // 3. SendBuffer 보내기 - 0에서 4 + 패킷 길이 만큼.
        socket.BeginSend(sendBuffer, 0, 4 + packet.Length, SocketFlags.None,
            new AsyncCallback(SendComplete), null);
    }

    // [8] 데이터 보내기가 완료 될때 불리는 콜백함수.
    void SendComplete(IAsyncResult ar)
    {
        socket.EndSend(ar);
    }
}
