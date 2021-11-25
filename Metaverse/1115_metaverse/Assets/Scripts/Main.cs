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
1027_Main.cs
    ������ ���� Ŭ���ϸ� ray �״�� �����Ͽ� ���ü�� �����ϵ��� �ۼ�.

 */

using System;
using System.Text;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class Main : MonoBehaviour
{
    float distance = 5.0f;  // camera distance
    float zoom;             // camera zoom in and out
    float camoffset;        // camera offset angle
    float camheight;
    Vector2 lastMousePos;   // last mouse position
    SocketDesc socketDesc;  // ���� ��ũ���� ����(<-SocketDesc.cs)

    Dictionary<string, Spawn> spawns; // ���� Main.cs�� spawn manager���ҵ� ����.
    Spawn mySpawn;
    Dictionary<string, WorldItem> worldItems;

    GameObject messageBox;
    GameObject toastMessage;
    float toastMessageRemain;

    void Start()
    {
        // ���� ��ũ���͸� �����Ѵ�.
        socketDesc = SocketDesc.Create();
        // spawn���� ������ spawns�� �����Ѵ�.
        spawns = new Dictionary<string, Spawn>();
        // world item���� ������ worldItems�� �����Ѵ�.
        worldItems = new Dictionary<string, WorldItem>();

        // MessageBox ã�� �Ⱥ��̵��� hiding�Ѵ�.
        messageBox = GameObject.Find("MessageBox").gameObject;
        messageBox.SetActive(false);

        // ToastMessage�� ã�� �Ⱥ��̵���
        toastMessage = GameObject.Find("ToastMessage").gameObject;
        toastMessage.SetActive(false);
        // ToastMessage ���� �ð��� -1.0���� �ʱ�ȭ
        toastMessageRemain = -1.0f;

    }
    void Update()
    {
        // Debug.Log(int.Parse("00"));
        // ���� �ƹ�Ÿ�� �����Ǿ� ���� �ʴٸ� �ƹ� �۾� �� �ϵ����Ѵ�.
        if (mySpawn == null) return;
        
        // Update()���� mySpawn�� Update �Ǹ鼭 �����ϰ�, SendMove()�� �������� move���� ����
        // W ����, S ���� 
        if(Input.GetKeyDown(KeyCode.W)) { mySpawn.speed = 4.0f; SendMove(); }
        else if(Input.GetKeyUp(KeyCode.W)) { mySpawn.speed = 0.0f; SendMove(); }
        if(Input.GetKeyDown(KeyCode.S)) { mySpawn.speed = -4.0f; SendMove(); }
        else if(Input.GetKeyUp(KeyCode.S)) { mySpawn.speed = 0.0f; SendMove(); }
        // A ��ȸ��, D ��ȸ��
        if(Input.GetKeyDown(KeyCode.A)) { mySpawn.aspeed = -90.0f; SendMove(); }    // 1�ʿ� 1/4��ŭ ȸ��
        else if(Input.GetKeyUp(KeyCode.A)) { mySpawn.aspeed = 0.0f; SendMove(); }
        if(Input.GetKeyDown(KeyCode.D)) { mySpawn.aspeed = 90.0f; SendMove(); }
        else if (Input.GetKeyUp(KeyCode.D)) { mySpawn.aspeed = 0.0f; SendMove();}

        //  t ������ �� �������� �ð� (�ʴ���)�� ����
        var t = Time.deltaTime;

        // ī�޶� �� �� �ƿ� - ���콺 �� ���� �о�ͼ� zoom�� ����
        zoom += Input.mouseScrollDelta.y * 0.1f;
        //Debug.Log(zoom);
        if (zoom < -1.0f) zoom = -1.0f; else if (zoom > 1.0f) zoom = 1.0f;  //�Ѱ�ġ����

        
        // ���콺 ��ư�� 0 �Ǵ� ��ư 1�� ������ ���콺�� ��ġ�� ǥ��
        if (Input.GetMouseButtonDown(0) || Input.GetMouseButtonDown(1))
        {
            // 1. ī�޶� ��ġ�κ��� �ش� ���콺 ��ġ�� ���� ray����
            var ray = Camera.main.ScreenPointToRay(Input.mousePosition); // x,y ��ǥ�� ����.
            // 2. �ش� ray�� �̿��Ͽ� �浹 �˻�
            RaycastHit hit;
            if(Physics.Raycast(ray, out hit))
            {
                Transform ht = hit.transform;   // ray�� �浹�� ��ü(hit)�� transform���� �ޱ� (hit : 64���� ���)
                WorldItem wi = null;
                while(ht != null)               // �浹�� ��ü�� �ִٸ�
                {
                    if (ht.gameObject.TryGetComponent<WorldItem>(out wi)) break; // WorldItem.cs ���� �������� 
                    ht = ht.parent;
                }
                if(wi != null)
                {
                    Debug.LogFormat("Hit : {0}", wi.name);
                    // ���콺 ��ư 0�� �������� place ����, 1�� �������� �ش� �����ۿ� join
                    if(Input.GetMouseButtonDown(0))
                    {
                        // ex) action Noah Reversi place 33
                        var mesg = string.Format("action {0} {1} place {2}",
                            mySpawn.name, wi.name, hit.transform.name);
                        socketDesc.Send(Encoding.UTF8.GetBytes(mesg)); // string -> byte�� ��ȯ �� ������ ���� ������
                    }
                    else if(mySpawn.joinItem == wi.name) // ���콺 ��ư 1�� ������, �ش� ������ ������ ������ Reversi���
                    {
                        // ex) action Noah Reversi leave
                        var mesg = string.Format("{0}���� �����ðڽ��ϱ�?", wi.name);
                        var yesMesg = string.Format("action {0} {1} leave", mySpawn.name, wi.name);
                        ShowMessageBox(mesg, yesMesg);
                    }
                    else // ���콺 ��ư 1�� ������
                    {
                        // ex) action Noah Reversi join
                        var mesg = string.Format("{0}�� �����Ͻðڽ��ϱ�?", wi.name);
                        var yesMesg = string.Format("action {0} {1} join", mySpawn.name, wi.name);
                        ShowMessageBox(mesg, yesMesg);
                    }
                }
            }
        }
        // ī�޶� ȸ�� - ���콺 ��ư 1�� Ŭ���� ���¿��� �� ó��
        if (Input.GetMouseButtonDown(1)) lastMousePos = Input.mousePosition;
        else if (Input.GetMouseButtonUp(1)) lastMousePos = Vector2.zero; // ���콺 ��ġ 2����.
        // Debug.Log(lastMousePos);
        if(lastMousePos != Vector2.zero) { 
            camoffset += Input.mousePosition.x - lastMousePos.x; // �� ���콺 ��ġ - ������ ���콺 ��ġ ����
            camheight += (Input.mousePosition.y - lastMousePos.y)*0.01f;
            lastMousePos = Input.mousePosition;
        }
        else if(mySpawn.speed != 0.0f)
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
        var yDistance = new Vector3(0, camd * Mathf.Sin(cameraPosAngle) + 1.8f - camheight, 0);
        Camera.main.transform.localPosition = mySpawn.transform.localPosition - xzDistance + yDistance;
        Camera.main.transform.localEulerAngles = new Vector3(30.0f, (mySpawn.direction + camoffset), 0);  //ī�޶� �ٶ󺸴� ����(View)

        // toastMessage �ð� ������Ʈ
        if(toastMessageRemain > 0.0f)
        {
            // 1. ���� ������ Ÿ�Ӹ�ŭ ���� �ð��� ���ش�.
            toastMessageRemain -= Time.deltaTime;
            // 2. ���� �ð��� 0���ϸ�, �ð��� ��� �帥���̹Ƿ� toastMessage�� ���������.
            if (toastMessageRemain <= 0.0f) toastMessage.SetActive(false);
        }
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

        // �������� ��Ŷ���·� ������� ����
        var ss = packet.Split();
        // join Noah  : ������ �����ϱ�.
        if(ss[0] == "join")
        {
            if (!spawns.ContainsKey(ss[1])) // spawns�� key�� ss[1]�ش� ����(����)�̸��� ���ٸ�
            {
                var go = new GameObject();
                var spawn = go.AddComponent<Spawn>(); // ���� ��ü ����
                spawns[ss[1]] = spawn;

                // ���ο� �÷��̾ �����ߴٰ� �޽����� �佺Ʈ�޽����� �ø�
                var mesg = string.Format("ģ�� {0}�� �����߽��ϴ�. \n�ȳ��ϼ���", ss[1]);
                ShowToastMessage(mesg);
            }
        }
        // leave : ���ӿ�����Ʈ �����ϱ�
        else if(ss[0] == "leave")
        {
            if (spawns.ContainsKey(ss[1]))
            {
                var go = spawns[ss[1]].gameObject;
                GameObject.Destroy(go);     // ���ӿ�����Ʈ �����ϱ�
                spawns.Remove(ss[1]);       // spawns���� ���� ���ֱ�
            }
        }
        else if(ss[0] == "avatar")
        {
            if (spawns.ContainsKey(ss[1])) // ���� �̸��� ��� �Ǿ��ٸ�
            {
                var spawn = spawns[ss[1]];
                if (spawn != mySpawn) spawn.CreateAvatar(ss[1], int.Parse(ss[2]));
            }
        }
        else if(ss[0] == "look")
        {
            if(spawns.ContainsKey(ss[1]))
            {
                var spawn = spawns[ss[1]];
                spawn.ChangeLook(int.Parse(ss[2]), int.Parse(ss[3]), int.Parse(ss[4]), int.Parse(ss[5]));
            }
        }
        else if(ss[0] == "worlddata")
        {
            // ���� -> ����Ƽ Ŭ���̾�Ʈ : world ���� �ް�, �̿� ����  ������Ʈ ����
            // 1. ���ο� ���ӿ�����Ʈ ����(�󲮵���)
            var go = new GameObject();
            // 2. �� ������Ʈ�� WorldItem ������Ʈ�� ����ϰ� ��ü ����
            var wi = go.AddComponent<WorldItem>();
            // 3. ���� ������Ʈ�� ���� - ("Reversi", 10, 10, 0) - (�̸�,x,z,dir)
            wi.CreateItem(ss[1], float.Parse(ss[2]), float.Parse(ss[3]), float.Parse(ss[4]));
            // 4. worldItems��� �ڷᱸ���� �ش��ϴ� ���� �������� ���
            worldItems[ss[1]] = wi; // key : "Reversi", value : ��ü
        }

        // �����κ��� update ���� ��Ŷ�� �޾ƿ������ : 1)���� onIdle���� �Ҹ��� ������Ʈ ����.
        // ex) update Reversi 3333....112333 white 
        else if (ss[0] == "update")
        {
            // 1. �̸��� ������ worlditems �׸��� ã�ƺ���.
            if (worldItems.ContainsKey(ss[1])) // "Reversi" key�� �ִٸ�
            {
                // 2. ã�� �׸񿡼� UpdateItem �Լ��� ȣ��
                var wi = worldItems[ss[1]];
                wi.UpdateItem(ss[1], ss[2]); // �ٵϾ� activate��Ű��
                // Reversi ���� ���� ������ �ش� �ε����� 1�̸� white�� activate, 2�̸� black���� activate
            }
        }
        // ex) action Noah Reversi join             : �������ǿ� �����ߴٴ¸޽����� ������ ���� ������
        // ex) action Noah Reversi leave            : �������ǿ� �����ٴ� �޽����� ������ ���� ������
        // 2)���� �������� ������ ����
        else if(ss[0] == "action")
        {
            // 1. worlditems ���� key�� Reversi�� �׸��� ã�´�.
            if(worldItems.ContainsKey(ss[2]))
            {
                Debug.LogFormat("action : {0}, {1}", ss[1], ss[3]);
                var wi = worldItems[ss[2]];
                // 2. ���� world item�� join�ϴ� ��ɾ��� ��� �ش� ĳ���͸� �ɵ��� ��.
                if(ss[3] == "join")
                {
                    var spawn = spawns[ss[1]];   // �޽��� ���� �ش罺�� ã��,
                    spawn.GetAvatar().Sit();    //  �ش� �ƹ�Ÿ�� ���� �����Ͽ� �ɰ���.
                    // ���� ������ ss[2]�� ���������� ǥ��
                    spawn.joinItem = ss[2];     // �ش罺���� ������ ������ Reversi��� �����.
                    // �佺Ʈ �޽��� ǥ��
                    var mesg = string.Format("{0}�� {1}�� �����߽��ϴ�.", ss[1], ss[2]);
                    ShowToastMessage(mesg);
                }
                else if(ss[3] == "leave")
                {
                    var spawn = spawns[ss[1]];
                    spawn.GetAvatar().Stand();
                    spawn.joinItem = null; // �ش� ������ ������ ������ ������.
                    var mesg = string.Format("{0}�� {1}�� �������ϴ�.", ss[1], ss[2]);
                    ShowToastMessage(mesg);
                }
                wi.ActionItem(ss[1], ss[2], ss[3]);
            }
        }
        // ex) move reversi_4493 pos_x pos_z dir speed aspeed
        else if(ss[0] == "move")
        {
			if(spawns.ContainsKey(ss[1]))
			{
				var spawn = spawns[ss[1]];
				// myspawn�� �ƴ� ��� �� ����Ƽ Ŭ���̾�Ʈ�� �ƴ� ��쿡�� ����
				if(spawn != mySpawn) 
				{
					spawn.transform.localPosition = new Vector3(float.Parse(ss[2]), 0.0f, float.Parse(ss[3]));
					spawn.direction = float.Parse(ss[4]);
					spawn.speed = float.Parse(ss[5]);
					spawn.aspeed = float.Parse(ss[6]);
					Debug.LogFormat("spawn : {0}, speed = {1}, aspeed = {2}", ss[2], spawn.speed, spawn.aspeed);
				}
			}
        }
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

    // �޽��� â ����
    string yesSendMesg; // yes��ư�� ���� ��� ������ �޽���
    
    // MessageBox ����
    public void ShowMessageBox(string mesg, string yes)
    {
        // 1. MessageBox�� ���̵��� ��
        messageBox.SetActive(true);
        // 2. Message ������Ʈ�� ã�´�. 
        var messageObj = messageBox.transform.Find("Message").GetComponent<TextMeshPro>(); // using TMPro
        // 3. Message ������Ʈ�� mesg���� ���´�.
        messageObj.text = mesg;                   // # mesg = {wi.name}���� �����ðڽ��ϱ�?
        // 4. yes ��ư�� ���� ��� ������ �޽����� ����
        yesSendMesg = yes;                        // action {mySpawn.name} {wi.name} leave
    }

    // TosastMessage ����
    public void ShowToastMessage(string mesg, float duration = 5.0f)
    {
        // 1. ToastMessage�� ���̵���
        toastMessage.SetActive(true);
        // 2. Message ������Ʈ�� ã�´�.
        var messageObj = toastMessage.transform.Find("Message").GetComponent<TextMeshPro>();
        // 3. Message ������Ʈ�� mesg���� ���´�.
        messageObj.text = mesg;
        // 4. ���̴� �ð������
        toastMessageRemain = duration; // 5�ʵ���. ������.
    }

    // Yes ��ư�� ���� ��� - �̸� ����Ƽ�� onClick()���� ���������!
    public void OnButtonYes()
    {
        // 1. MessageBox�� ���⵵�� �Ѵ�.
        messageBox.SetActive(false);
        // 2. action userName Reversi join <- YES ��ư�� ������ �� �޽����� ������ ����. -> ������ ���ӿ� �����ϱ�.
        socketDesc.Send(Encoding.UTF8.GetBytes(yesSendMesg));
    }
    // No ��ư�� ���� ��� - �̸� ����Ƽ�� onClick()���� ���������!
    public void OnButtonNo()
    {
        // 1. MessageBox�� ���⵵�� �Ѵ�.
        messageBox.SetActive(false);
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

