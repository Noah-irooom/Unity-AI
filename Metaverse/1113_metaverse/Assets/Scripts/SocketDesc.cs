/*
1025_SocketDesc
    1. socket  vs  desc
        - socket : ��Ʈ��ũ ���� ���
            - ���� : socket.Close() -> socket.Connect() -> socket.Connected
            - ��� ���� : socket.Shutdown()
            - ������ �ޱ� 
                - ��� �б�: socket.BeginReceive(recvBuffer) -> ReceiveComplete -> Encoding.UTF8.GetString(recvBuffer)
                    (recvBuffer�� �޾��ֱ� -> ��� ũ�� 4 -> �޽����� ���� ����)
                - �޽��� �б� : socket.BeginReceive(packet) -> ReceiveComplete -> NetworkState.Complete  
                    (���� �޽��� ������ pakcet���۰� �޾���. -> �״�� Send�� ����)
            - ������ ������
                - sendBuffer : ���� ���� �����
                    - 0 - 4 ���� : ��� ���� (�޽��� ��Ŷ�� ���� ����)
                    - 4 - ��Ŷ ���� : �޽��� ���� 
                - socket.BeginSend(sendBuffer) -> SendComplete -> socket.EndSend(ar)
        - desc : 


*/

using System;
using System.Text;
using System.Net.Sockets;
using UnityEngine;

public class SocketDesc
{
    // ��Ʈ��ũ ���¸� ���� ������(enumerator)
    enum NetworkState
    {
        Disconnect,         // ���� ��Ʈ��ũ ������ �ȵ� ����
        Ready,              // ������ �Ǿ �޼����� ���� �� �ִ� ����
        WaitForHeader,      // ���� ����� �а� �ִ� ��
        WaitForMessage,     // ���� �޼����� �а� �ִ� ��
        Complete,           // �޽��� ������ ������
        MaxNumber
    }

    // ����� ������
    Socket socket;          // ��Ʈ��ũ ������ ���� ��Ʈ��ũ �ڵ�
    byte[] packet;          // ��Ʈ��ũ �޽��� ��Ŷ
    byte[] recvBuffer;      // �ӽ÷� ������ ����
    NetworkState state;     // ��Ʈ��ũ ����

    // [1] ���� ��ũ���� ���� �Լ� - ���� ����, ��ũ���Ϳ� ����, ���� ������ũ��
    public static SocketDesc Create()
    {
        // 1. ������ ����
        Socket sock = new Socket(AddressFamily.InterNetwork,
            SocketType.Stream, ProtocolType.Tcp);
        if(sock == null) return null;
        // 2. ���� ��ũ���͸� ���� - Main.cs���� ����� �κ�.
        var desc = new SocketDesc();
        desc.socket = sock; // ���� ��ũ���Ϳ� ������ ���� �Է�
        desc.recvBuffer = new byte[4]; // ���� �� �ִ� ������ ũ��
        // 3. ���� ��ũ���͸� ��ȯ
        return desc;
    }

    // [2] ��Ʈ��ũ ����
    public bool Connect(string address, int port)
    {
        // ���� ���� ���°� ��������� �ƴϸ� ���� �ݾ��ְ� �ٽ� ����.
        if (state != NetworkState.Disconnect) socket.Close();
        try { socket.Connect(address, port); } // (�ٽ�) ����
        catch(SocketException e) 
        {
            Debug.LogFormat("Error in connect : {0}", e.Message);
            return false;
        }
        state = NetworkState.Ready; // ��Ʈ��ũ ������ �Ǿ� �޽��� ���� �� �ִ� ����.
        return socket.Connected;
    }
    
    // [3] ��Ʈ��ũ ��� ����
    public void Shutdown()
    {
        // ������ ���ų� ������ ��Ʈ��ũ ������ �� �� ���¶�� �ƹ��͵� ���Ѵ�.
        if (socket == null || !socket.Connected) return;
        socket.Shutdown(SocketShutdown.Both); // ������ ������ ����� �����Ѵ�.
        // socket.Close() ������ �ݾ���. socket.Shutdown ����� ������.
    }

    // [4] ��Ʈ��ũ���� ���۵� �����͸� ��������
    public byte[] GetPacket()
    {
        // ������ �Ϸ�� ��쿡�� packet ��ȯ. -> ��� �� �޽������� �� �޾ƾ� Complete��.
        if (state == NetworkState.Complete)
        {
            state = NetworkState.Ready; // GetPacket���� ��Ŷ ���� Main.cs�� ���������� �ٽ� ������ ���� �غ�
            return packet;
        }
        return null; // ���� �Ϸ� ���� ������ null ��ȯ
    }

    // [5] ��Ʈ��ũ ó���ϱ� - �޽��� ���� �غ� ���¶�� ��� ���� �б�
    public bool ProcessNetwork()
    {
        // 1. ������ ���ų� �񿬰� ������ ��� false ��ȯ
        if (socket == null || !socket.Connected) return false;
        // 2. ������ �Ϸ�� ��쿡�� �ƹ� �ϵ� ���ϱ�. -> ����а�, �޽����о�� Complete��.
        if (state == NetworkState.Complete) return true;
        // 3. Ready �����̸� ����� �б�
        if (state == NetworkState.Ready)
        {
            state = NetworkState.WaitForHeader; // ��� �б�� ����.
            socket.BeginReceive(recvBuffer, 0, 4, SocketFlags.None,
                new AsyncCallback(ReceiveComplete), null); // recvBuffer�� ��� ������ �޾�.
        }
        return false;
    }

    // [6] ������ �ޱⰡ �Ϸ�� ��� �Ҹ��� �ݹ� 
    void ReceiveComplete(IAsyncResult ar)
    {
        // len�� 0�� ��쿡�� ����ʿ��� ������ ���� ���
        // len�� 0���� ���� ��쿡�� ��Ʈ��ũ ������ �߻��� ���
        int len = socket.EndReceive(ar);
        if(len <= 0) { socket.Close(); state = NetworkState.Disconnect; return; }

        // ��Ʈ��ũ ���°� ����� ��ٸ��� ���
        if (state == NetworkState.WaitForHeader)
        {
            // 1. ����Ʈ ��Ʈ���� ���ڿ��� ��ȯ - ������� �޽����� ���� ���� �־�.
            string str = Encoding.UTF8.GetString(recvBuffer);
            // 2. ���� ���ڿ���  ������ ��ȯ
            int needed = Int32.Parse(str);
            // 3. needed��ŭ ������ ���� ���� ����.
            packet = new byte[needed];
            // 4. ��Ʈ��ũ ���¸� �޼����� ��ٸ��� ������ ��ȯ.
            state = NetworkState.WaitForMessage;
            // 5. ��Ʈ��ũ �б� ��û�� �Ѵ�.
            socket.BeginReceive(packet, 0, needed, SocketFlags.None,
                new AsyncCallback(ReceiveComplete), null);
        }
        else if (state == NetworkState.WaitForMessage)
        {
            // 1. ��Ʈ��ũ ���¸� �Ϸ��� �ٲ۴�.
            state = NetworkState.Complete;
        }
    }

    // [7] ��Ŷ(�޽��� ����)������ ������.
    public void Send(byte[] packet)
    {
        string str = String.Format("{0,4}", packet.Length); // ��� 0006 -> ��Ŷ���� 6
        // 1. ���� ���� ����.
        byte[] sendBuffer = new byte[4 + packet.Length]; // sendBuffer : ���� ���� ���� ����� ����.
        
        // 2. ���ۿ� ��� ����, �޽��� ���� ���.
        System.Buffer.BlockCopy(Encoding.UTF8.GetBytes(str), 0, sendBuffer, 0, 4); // sendBuffer�� 0~4�� packet���� ��� ����
        System.Buffer.BlockCopy(packet, 0, sendBuffer, 4, packet.Length); // sendBuffer�� 4~�� ���� pakcet �޽��� ���� ���

        // 3. SendBuffer ������ - 0���� 4 + ��Ŷ ���� ��ŭ.
        socket.BeginSend(sendBuffer, 0, 4 + packet.Length, SocketFlags.None,
            new AsyncCallback(SendComplete), null);
    }

    // [8] ������ �����Ⱑ �Ϸ� �ɶ� �Ҹ��� �ݹ��Լ�.
    void SendComplete(IAsyncResult ar)
    {
        socket.EndSend(ar);
    }
}
