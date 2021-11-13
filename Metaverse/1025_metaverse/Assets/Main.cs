/* GUI �ǵ帱 �κ�
1020_Main.cs
    1. Button���� Main Scene�� ������� �ű⿡�� OnButtonConnect()�� �����ϱ�.
    2. InputFieldŬ���� �߾ȵɶ� Textũ�Ⱑ �ʹ�Ŀ�� �׷���! (Width 60, ��� ���� �����ֱ�)
    3. Male, Female ������ -> Male/Materials/ hair double sided�� ���ֱ�
1023_Main.cs   
    1. �� ���ӿ�����Ʈ�� ���̸��� �����ϱ�
    2. myAvatar ��ü�� �����ϰ�  
    3. �� ���ӿ�����Ʈ�� Avatar.cs ������Ʈ �߰��ϸ� ���ÿ� �ν��Ͻ� ����� myAvatar�����Ѵ�.
    4. myAvatar.Create() �Լ� ȣ���� ���� �ƹ�Ÿ ��, �� ������ �ɾ��ش�.
    5. ChangeLook() : �ʹٲٱ� �Լ�����
1023_Main.cs - ī�޶�
    1. camd : ī�޶�� �ƹ�Ÿ�� �����Ÿ�(����)
    2. camd * cosine : xz��鿡�� ���翵�� ī�޶�� �ƹ�Ÿ�� �Ÿ�(cdirv * camd * cosine : ������� ���)
    3. camd * sine : y�࿡���� ī�޶�� �ƹ�Ÿ�� �Ÿ�
1025_Main.cs
    Spawn�� SocketDesc�� ������⶧���� �̿� �Է� ���õ� �κ� �ۼ� �� ����ȭ
    1. Spawn�� �Է°��ֱ� -> 2. Spawn.cs�� �����Ӹ��� ������Ʈ�ϸ鼭 �ݿ��� �ƹ�Ÿ ���۽�Ŵ
        - Spawn.speed
        - Spawn.aspeed 
    2. socektDesc  
        - 1) OnButtonConnect() : socketDesc.Connect() ��Ʈ��ũ �����ϱ�.
        - 2) SocketDesc.cs : socketDesc�� stream�� �����͸� ����� �޽����� �޾ƿ�
        - 3) FixedUpdate() : socketDesc.GetPacket()�� ���� �޽��� ����(packet) �޾ƿ� ���ڵ��Ͽ� ���(GetString) 
            - ���� -> ����Ƽ Ŭ���̾�Ʈ�� ��Ŷ ����
        - 3) Update() : socketDesc.Send() - �������� mySpawn�� �������� �ϼ��� ��Ŷ���� ������.
            - ����Ƽ Ŭ���̾�Ʈ -> ������ ��Ŷ ����
    3. server, client py
        ����Ƽ Ŭ���̾�Ʈ �ܿ� �ٸ� Ŭ���̾�Ʈ�� �������� ���� ��Ȳ�� ����Ƽ�� �ݿ��ؾ�.
        - ����Ƽ���� Ŭ���̾�Ʈ���� Spawn���� �����ؾ�

 */

using System;
using System.Text;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class Main : MonoBehaviour
{
    
    float distance = 5.0f;  // camera distance
    float zoom;             // camera zoom
    float camoffset;        // camera offset angle
    float camheigth;
    Vector2 lastMousePos;   // last mouse position

    SocketDesc socketDesc;  // ���� ��ũ���� ����(<-SocketDesc.cs)

    Dictionary<string, Spawn> spawns;
    Spawn mySpawn;

    void Start()
    {
        // ���� ��ũ���͸� �����Ѵ�.
        socketDesc = SocketDesc.Create();

        // spawn���� ������ spawns�� �����Ѵ�.
        spawns = new Dictionary<string, Spawn>();
    }

    void Update()
    {
        // Debug.Log(int.Parse("00"));
        // ���� �ƹ�Ÿ�� �����Ǿ� ���� �ʴٸ� �ƹ� �۾� �� �ϵ����Ѵ�.
        if (mySpawn == null) return;
        
        // Update()���� mySpawn�� Update �Ǹ鼭 �����ϰ�, SendMove()�� �������� move���� ����
        // W ����, S ���� 
        if(Input.GetKeyDown(KeyCode.W)) { mySpawn.speed = 1.0f; SendMove(); }
        else if(Input.GetKeyUp(KeyCode.W)) { mySpawn.speed = 0.0f; SendMove(); }
        if(Input.GetKeyDown(KeyCode.S)) { mySpawn.speed = -1.0f; SendMove(); }
        else if(Input.GetKeyUp(KeyCode.S)) { mySpawn.speed = 0.0f; SendMove(); }
        // A ��ȸ��, D ��ȸ��
        if(Input.GetKeyDown(KeyCode.A)) { mySpawn.aspeed = -90.0f; SendMove(); }    // 1�ʿ� 1/4��ŭ �̵�
        else if(Input.GetKeyUp(KeyCode.A)) { mySpawn.aspeed = 0.0f; SendMove(); }
        if(Input.GetKeyDown(KeyCode.D)) { mySpawn.aspeed = 90.0f; SendMove(); }
        else if (Input.GetKeyUp(KeyCode.D)) { mySpawn.aspeed = 0.0f; SendMove();}

        //  t ������ �� �������� �ð� (�ʴ���)�� ����
        var t = Time.deltaTime;

        // ī�޶� �� �� �ƿ� - ���콺 �� ���� �о�ͼ� zoom�� ����
        zoom += Input.mouseScrollDelta.y * 0.1f;
        //Debug.Log(zoom);
        if (zoom < -1.0f) zoom = -1.0f; else if (zoom > 1.0f) zoom = 1.0f;  //�Ѱ�ġ����

        // ī�޶� ȸ�� - ���콺 ��ư 1�� Ŭ���� ���¿��� �� ó��
        if (Input.GetMouseButtonDown(1)) lastMousePos = Input.mousePosition;
        else if (Input.GetMouseButtonUp(1)) lastMousePos = Vector2.zero; // ���콺 ��ġ 2����.
        // Debug.Log(lastMousePos);
        if(lastMousePos != Vector2.zero) { 
            camoffset += Input.mousePosition.x - lastMousePos.x; // �� ���콺 ��ġ�� ������ ���콺 ��ġ ����
            camheigth += (Input.mousePosition.y - lastMousePos.y)*0.01f;
            lastMousePos = Input.mousePosition;
        }
        else
        {
            // ���콺 ��ư�� ���� lastMousePos�� �����Ͱ� �Ǵϱ� ���ڸ��� ���ƿ��� �����Ѵ�.
            if(camoffset < 0.0f) { 
                camoffset += 0.1f;  // ī�޶� ���ڸ��� ���ƿ��Բ� ����
                if (camoffset > 0.0f) camoffset = 0.0f; 
            }
            else if (camoffset > 0.0f)
            {
                camoffset -= 0.1f;
                if (camoffset < 0.0f) camoffset = 0.0f; 
            }
        }
        

        // ī�޶� ��ġ
        var camd = distance * Mathf.Pow(2.0f, zoom); // 2�� zoom����(1/2 ~ 2) * distance(0.5f) = (0.25 ~ 1)
        var rad = Mathf.Deg2Rad * (mySpawn.direction + camoffset); // ���� �ƹ�Ÿ�� �ٶ󺸴� ����(z�����)�� �������� �� ī�޶� ����(�� rad�� ī�޶� ���밢��)
        var cdirv = new Vector3(Mathf.Sin(rad), 0, Mathf.Cos(rad)); // ī�޶� ���� ��������
        var cameraPosAngle = Mathf.Deg2Rad * 30; // ī�޶�� �ƹ�Ÿ�� �̷�� ����
        var xzDistance = camd * Mathf.Cos(cameraPosAngle) * cdirv; // ���� * cos * ����������� => xz ���翵
        var yDistance = new Vector3(0, camd * Mathf.Sin(cameraPosAngle) + 1.8f - camheigth, 0);
        Camera.main.transform.localPosition = mySpawn.transform.localPosition - xzDistance + yDistance;
        Camera.main.transform.localEulerAngles = new Vector3(30.0f, (mySpawn.direction + camoffset), 0);  //ī�޶� �ٶ󺸴� ����(View)

    }

    // �����ð����� �Ҹ��� ��. - frame���� ������� ȣ���.
    // �� �������� Ŭ���̾�Ʈ�� �޽��� �޾ƿö� �����ð����� �޾ƿ�����.
    private void FixedUpdate()
    {
        // 1. ���� ��ũ���Ͱ� �������� ������ �ƹ��͵� ���ϱ�
        if (socketDesc == null) return;
        // 2. processNetwork�� true�� �ƴ϶�� �ƹ��͵� ���ϱ�. - �� ���,�޽��� �� ���� ���ϸ� �ƹ��͵� ����.
        if (!socketDesc.ProcessNetwork()) return;
        // 3. ��Ŷ(�޽��� ������) �������� -> ��� �޽��� �� �޾����� ��Ŷ���� ������
        var packet = Encoding.UTF8.GetString(socketDesc.GetPacket()); // ��Ŷ(�޽���)�� string���� ���ڵ��ϱ�
        Debug.Log(packet);
        //  ���� -> ����Ƽ Ŭ���̾�Ʈ : ������ ������Ŷ ���� �޾ƿ� ���. 
        // server.py���� self.send �Ǵ� self.broadcast�� ������ SocketDesc���� ��Ŷ���� ó���Ǿ� ���
        // moveReversi 00000...

    }

    public void OnButtonConnect()
    {
        // 1. Find "LoginWindow"
        var loginWindow = GameObject.Find("LoginWindow");
        // 2. Find "InputField" - �̸��Էºκ�
        var name = loginWindow.transform.Find("InputField").GetComponent<InputField>();
        // transform���� ã�ƾ��Ѵ�.
        // 3. Print result
        Debug.LogFormat("Connect with {0}.", name.text);
        // 4. Hide Login window
        loginWindow.SetActive(false); //��Ȱ��ȭ ��Ű��. (�α���â �ݾ��ֱ�)

        // Spawn �����
        // 1. �󲮵����� ���ӿ�����Ʈ �����(������ �̸������ֱ�)
        var go = new GameObject(name.text);
        // 2. �� ������ȿ� Avatar component �߰��ϰ����� �ν��Ͻ� ����.(������ �ȿ� �ƹ�Ÿ �����ϱ� ����))
        mySpawn = go.AddComponent<Spawn>();
        // 3. �� ������Ʈ�� Avatr �����ϱ�
        var model = UnityEngine.Random.Range(0, 2); // ���� �����Ҽ� �ְ� ���� �ʿ�.
        mySpawn.CreateAvatar(name.text, model);
        var hair = UnityEngine.Random.Range(0, 4);
        var body = UnityEngine.Random.Range(0, 4);
        var legs = UnityEngine.Random.Range(0, 4);
        var shoes = UnityEngine.Random.Range(0, 4);
        mySpawn.ChangeLook(hair, body, legs, shoes);
        
        // ������ �����ϱ� - ���ӽ�(�̸�, �ƹ�Ÿ, �� ���� ������ ����)
        if (socketDesc.Connect("127.0.0.1", 8888))
        {
            Debug.Log("Connected");

            // ���ڵ�(GetBytes)�Ͽ� ������
            socketDesc.Send(Encoding.UTF8.GetBytes(string.Format("join {0}", name.text)));
            socketDesc.Send(Encoding.UTF8.GetBytes(string.Format("avatar {0} {1}", name.text, model)));
            socketDesc.Send(Encoding.UTF8.GetBytes(string.Format("look {0} {1} {2} {3} {4}", name.text, hair, body, legs, shoes)));
            // UTF8�� �ѱ�:3byte ����:1byte
            
            // key : �̸�, value : ���� -> ������ �̸����� �����Ѵ�.
            spawns[name.text] = mySpawn;

        }
        else
        {
            Debug.LogError("Connection is failed");
        }
    }

    // ������ ��Ŷ ���� �����ϱ�
    void SendMove()
    {
        var mesg = string.Format("move {0} {1} {2} {3} {4} {5}",
            mySpawn.name, mySpawn.transform.localPosition.x, mySpawn.transform.localPosition.z,
            mySpawn.direction, mySpawn.speed, mySpawn.aspeed);
        socketDesc.Send(Encoding.UTF8.GetBytes(mesg)); // ���ڵ��Ͽ� �ϼ��� ��Ŷ����(���+�޽���)�� ������
    }
}

