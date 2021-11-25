/* GUI 건드릴 부분
1020_Main.cs
    1. Button에서 Main Scene을 등록한후 거기에서 OnButtonConnect()와 연결하기.
    2. InputField클릭이 잘안될때 Text크기가 너무커서 그런것! (Width 60, 가운데 정렬 맞춰주기)
    3. Male, Female 복붙후 -> Male/Materials/ hair double sided로 해주기
1023_Main.cs   
    1. 빈 게임오브젝트와 그이름을 생성하기
    2. myAvatar 객체를 선언하고  
    3. 빈 게임오브젝트에 Avatar.cs 컴포넌트 추가하며 동시에 인스턴스 만들어 myAvatar정의한다.
    4. myAvatar.Create() 함수 호출해 실제 아바타 모델, 그 동작을 심어준다.
    5. ChangeLook() : 옷바꾸기 함수실행
1023_Main.cs - 카메라
    1. camd : 카메라와 아바타의 직선거리(빗변)
    2. camd * cosine : xz평면에서 정사영된 카메라와 아바타의 거리(cdirv * camd * cosine : 방향까지 고려)
    3. camd * sine : y축에서의 카메라와 아바타의 거리
1025_Main.cs
    Spawn과 SocketDesc를 만들었기때문에 이에 입력 관련된 부분 작성 및 간소화
    1. Spawn에 입력값주기 -> 2. Spawn.cs는 프레임마다 업데이트하면서 반영후 아바타 동작시킴
        - Spawn.speed
        - Spawn.aspeed 
    2. socektDesc  
        - 1) OnButtonConnect() : socketDesc.Connect() 네트워크 접속하기.
        - 2) SocketDesc.cs : socketDesc가 stream의 데이터를 헤더와 메시지로 받아와
        - 3) FixedUpdate() : socketDesc.GetPacket()을 통해 메시지 내용(packet) 받아와 디코딩하여 출력(GetString) 
            - 서버 -> 유니티 클라이언트로 패킷 보냄
        - 3) Update() : socketDesc.Send() - 서버에게 mySpawn의 움직임을 완성된 패킷으로 보내줌.
            - 유니티 클라이언트 -> 서버로 패킷 보냄
    3. server, client py
        유니티 클라이언트 외에 다른 클라이언트가 접속했을 때의 상황도 유니티에 반영해야.
        - 유니티에서 클라이언트들의 Spawn들을 관리해야
1027_Main.cs
    리버시 판을 클릭하면 ray 그대로 투과하여 대상물체를 선택하도록 작성.

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
    SocketDesc socketDesc;  // 소켓 디스크립터 생성(<-SocketDesc.cs)

    Dictionary<string, Spawn> spawns; // 현재 Main.cs가 spawn manager역할도 겸함.
    Spawn mySpawn;
    Dictionary<string, WorldItem> worldItems;

    GameObject messageBox;
    GameObject toastMessage;
    float toastMessageRemain;

    void Start()
    {
        // 소켓 디스크립터를 생성한다.
        socketDesc = SocketDesc.Create();
        // spawn들을 관리할 spawns를 생성한다.
        spawns = new Dictionary<string, Spawn>();
        // world item들을 관리할 worldItems를 생성한다.
        worldItems = new Dictionary<string, WorldItem>();

        // MessageBox 찾아 안보이도록 hiding한다.
        messageBox = GameObject.Find("MessageBox").gameObject;
        messageBox.SetActive(false);

        // ToastMessage를 찾아 안보이도록
        toastMessage = GameObject.Find("ToastMessage").gameObject;
        toastMessage.SetActive(false);
        // ToastMessage 남은 시간을 -1.0으로 초기화
        toastMessageRemain = -1.0f;

    }
    void Update()
    {
        // Debug.Log(int.Parse("00"));
        // 현재 아바타가 생성되어 있지 않다면 아무 작업 안 하도록한다.
        if (mySpawn == null) return;
        
        // Update()마다 mySpawn도 Update 되면서 동작하고, SendMove()로 서버에도 move정보 전달
        // W 전진, S 후진 
        if(Input.GetKeyDown(KeyCode.W)) { mySpawn.speed = 4.0f; SendMove(); }
        else if(Input.GetKeyUp(KeyCode.W)) { mySpawn.speed = 0.0f; SendMove(); }
        if(Input.GetKeyDown(KeyCode.S)) { mySpawn.speed = -4.0f; SendMove(); }
        else if(Input.GetKeyUp(KeyCode.S)) { mySpawn.speed = 0.0f; SendMove(); }
        // A 좌회전, D 우회전
        if(Input.GetKeyDown(KeyCode.A)) { mySpawn.aspeed = -90.0f; SendMove(); }    // 1초에 1/4만큼 회전
        else if(Input.GetKeyUp(KeyCode.A)) { mySpawn.aspeed = 0.0f; SendMove(); }
        if(Input.GetKeyDown(KeyCode.D)) { mySpawn.aspeed = 90.0f; SendMove(); }
        else if (Input.GetKeyUp(KeyCode.D)) { mySpawn.aspeed = 0.0f; SendMove();}

        //  t 변수에 한 프레임의 시간 (초단위)를 저장
        var t = Time.deltaTime;

        // 카메라 줌 인 아웃 - 마우스 휠 값을 읽어와서 zoom에 적용
        zoom += Input.mouseScrollDelta.y * 0.1f;
        //Debug.Log(zoom);
        if (zoom < -1.0f) zoom = -1.0f; else if (zoom > 1.0f) zoom = 1.0f;  //한계치설정

        
        // 마우스 버튼이 0 또는 버튼 1이 눌리면 마우스의 위치를 표시
        if (Input.GetMouseButtonDown(0) || Input.GetMouseButtonDown(1))
        {
            // 1. 카메라 위치로부터 해당 마우스 위치로 가는 ray생성
            var ray = Camera.main.ScreenPointToRay(Input.mousePosition); // x,y 좌표를 가짐.
            // 2. 해당 ray를 이용하여 충돌 검사
            RaycastHit hit;
            if(Physics.Raycast(ray, out hit))
            {
                Transform ht = hit.transform;   // ray가 충돌한 물체(hit)의 transform정보 받기 (hit : 64개의 기둥)
                WorldItem wi = null;
                while(ht != null)               // 충돌한 물체가 있다면
                {
                    if (ht.gameObject.TryGetComponent<WorldItem>(out wi)) break; // WorldItem.cs 파일 가져오기 
                    ht = ht.parent;
                }
                if(wi != null)
                {
                    Debug.LogFormat("Hit : {0}", wi.name);
                    // 마우스 버튼 0이 눌렸으면 place 수행, 1이 눌렸으면 해당 아이템에 join
                    if(Input.GetMouseButtonDown(0))
                    {
                        // ex) action Noah Reversi place 33
                        var mesg = string.Format("action {0} {1} place {2}",
                            mySpawn.name, wi.name, hit.transform.name);
                        socketDesc.Send(Encoding.UTF8.GetBytes(mesg)); // string -> byte로 변환 후 서버로 소켓 보내기
                    }
                    else if(mySpawn.joinItem == wi.name) // 마우스 버튼 1이 눌리고, 해당 스폰이 참여한 게임이 Reversi라면
                    {
                        // ex) action Noah Reversi leave
                        var mesg = string.Format("{0}에서 떠나시겠습니까?", wi.name);
                        var yesMesg = string.Format("action {0} {1} leave", mySpawn.name, wi.name);
                        ShowMessageBox(mesg, yesMesg);
                    }
                    else // 마우스 버튼 1이 눌리면
                    {
                        // ex) action Noah Reversi join
                        var mesg = string.Format("{0}에 참여하시겠습니까?", wi.name);
                        var yesMesg = string.Format("action {0} {1} join", mySpawn.name, wi.name);
                        ShowMessageBox(mesg, yesMesg);
                    }
                }
            }
        }
        // 카메라 회전 - 마우스 버튼 1이 클릭된 상태에서 팬 처리
        if (Input.GetMouseButtonDown(1)) lastMousePos = Input.mousePosition;
        else if (Input.GetMouseButtonUp(1)) lastMousePos = Vector2.zero; // 마우스 위치 2차원.
        // Debug.Log(lastMousePos);
        if(lastMousePos != Vector2.zero) { 
            camoffset += Input.mousePosition.x - lastMousePos.x; // 현 마우스 위치 - 마지막 마우스 위치 차이
            camheight += (Input.mousePosition.y - lastMousePos.y)*0.01f;
            lastMousePos = Input.mousePosition;
        }
        else if(mySpawn.speed != 0.0f)
        {
            // 마우스 버튼을 떼면 lastMousePos는 영벡터가 되니까 제자리로 돌아오게 설정한다.
            if(camoffset < 0.0f) { 
                camoffset += 0.1f;  // 카메라가 제자리로 돌아오게끔 설정
                if (camoffset > 0.0f) camoffset = 0.0f; 
            }
            else if (camoffset > 0.0f)
            {
                camoffset -= 0.1f;
                if (camoffset < 0.0f) camoffset = 0.0f; 
            }
        }


        // 카메라 위치
        var camd = distance * Mathf.Pow(2.0f, zoom); // 2의 zoom제곱(1/2 ~ 2) * distance(0.5f) = (0.25 ~ 1)
        var rad = Mathf.Deg2Rad * (mySpawn.direction + camoffset); // 현재 아바타가 바라보는 각도(z축기준)를 기준으로 한 카메라 각도(즉 rad는 카메라 절대각도)
        var cdirv = new Vector3(Mathf.Sin(rad), 0, Mathf.Cos(rad)); // 카메라 방향 단위벡터
        var cameraPosAngle = Mathf.Deg2Rad * 30; // 카메라와 아바타가 이루는 각도
        var xzDistance = camd * Mathf.Cos(cameraPosAngle) * cdirv; // 빗변 * cos * 방향단위벡터 => xz 정사영
        var yDistance = new Vector3(0, camd * Mathf.Sin(cameraPosAngle) + 1.8f - camheight, 0);
        Camera.main.transform.localPosition = mySpawn.transform.localPosition - xzDistance + yDistance;
        Camera.main.transform.localEulerAngles = new Vector3(30.0f, (mySpawn.direction + camoffset), 0);  //카메라 바라보는 각도(View)

        // toastMessage 시간 업데이트
        if(toastMessageRemain > 0.0f)
        {
            // 1. 현재 프레임 타임만큼 남은 시간을 없앤다.
            toastMessageRemain -= Time.deltaTime;
            // 2. 남은 시간이 0이하면, 시간이 모두 흐른것이므로 toastMessage를 사라지게함.
            if (toastMessageRemain <= 0.0f) toastMessage.SetActive(false);
        }
    }

    // 일정시간마다 불리게 됨. - frame수와 상관없이 호출됨.
    // 즉 서버에서 클라이언트로 메시지 받아올때 일정시간마다 받아오도록.
    private void FixedUpdate()
    {
        // 1. 소켓 디스크립터가 존재하지 않으면 아무것도 안하기
        if (socketDesc == null) return;
        // 2. processNetwork가 true가 아니라면 아무것도 안하기. - 즉 헤더,메시지 다 받지 못하면 아무것도 안함.
        if (!socketDesc.ProcessNetwork()) return;
        // 3. 패킷(메시지 정보만) 가져오기 -> 헤더 메시지 다 받았으면 패킷정보 가져와
        var packet = Encoding.UTF8.GetString(socketDesc.GetPacket()); // 패킷(메시지)를 string으로 디코딩하기
        Debug.Log(packet);
        //  서버 -> 유니티 클라이언트 : 서버로 부터패킷 내용 받아와 출력. 
        // server.py에서 self.send 또는 self.broadcast한 내용이 SocketDesc에서 패킷마다 처리되어 출력

        // 서버에서 패킷형태로 날라오는 정보
        var ss = packet.Split();
        // join Noah  : 서버에 접속하기.
        if(ss[0] == "join")
        {
            if (!spawns.ContainsKey(ss[1])) // spawns의 key중 ss[1]해당 스폰(유저)이름이 없다면
            {
                var go = new GameObject();
                var spawn = go.AddComponent<Spawn>(); // 스폰 객체 생성
                spawns[ss[1]] = spawn;

                // 새로운 플레이어가 접속했다고 메시지를 토스트메시지에 올림
                var mesg = string.Format("친구 {0}이 접속했습니다. \n안녕하세요", ss[1]);
                ShowToastMessage(mesg);
            }
        }
        // leave : 게임오브젝트 제거하기
        else if(ss[0] == "leave")
        {
            if (spawns.ContainsKey(ss[1]))
            {
                var go = spawns[ss[1]].gameObject;
                GameObject.Destroy(go);     // 게임오브젝트 제거하기
                spawns.Remove(ss[1]);       // spawns에서 정보 없애기
            }
        }
        else if(ss[0] == "avatar")
        {
            if (spawns.ContainsKey(ss[1])) // 유저 이름이 등록 되었다면
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
            // 서버 -> 유니티 클라이언트 : world 정보 받고, 이에 맞춰  오브젝트 생성
            // 1. 새로운 게임오브젝트 생성(빈껍데기)
            var go = new GameObject();
            // 2. 이 오브젝트를 WorldItem 컴포넌트를 등록하고 객체 생성
            var wi = go.AddComponent<WorldItem>();
            // 3. 실제 오브젝트를 생성 - ("Reversi", 10, 10, 0) - (이름,x,z,dir)
            wi.CreateItem(ss[1], float.Parse(ss[2]), float.Parse(ss[3]), float.Parse(ss[4]));
            // 4. worldItems라는 자료구조에 해당하는 월드 아이템을 등록
            worldItems[ss[1]] = wi; // key : "Reversi", value : 객체
        }

        // 서버로부터 update 문장 패킷을 받아오면실행 : 1)평상시 onIdle에서 불리는 업데이트 정보.
        // ex) update Reversi 3333....112333 white 
        else if (ss[0] == "update")
        {
            // 1. 이름을 가지고 worlditems 항목을 찾아본다.
            if (worldItems.ContainsKey(ss[1])) // "Reversi" key가 있다면
            {
                // 2. 찾은 항목에서 UpdateItem 함수를 호출
                var wi = worldItems[ss[1]];
                wi.UpdateItem(ss[1], ss[2]); // 바둑알 activate시키기
                // Reversi 보드 판을 가져와 해당 인덱스가 1이면 white로 activate, 2이면 black으로 activate
            }
        }
        // ex) action Noah Reversi join             : 리버시판에 조인했다는메시지르 서버로 부터 받을때
        // ex) action Noah Reversi leave            : 리버시판에 나간다는 메시지를 서버로 부터 받을때
        // 2)돌을 놓았을때 보드판 정보
        else if(ss[0] == "action")
        {
            // 1. worlditems 에서 key가 Reversi인 항목을 찾는다.
            if(worldItems.ContainsKey(ss[2]))
            {
                Debug.LogFormat("action : {0}, {1}", ss[1], ss[3]);
                var wi = worldItems[ss[2]];
                // 2. 만약 world item에 join하는 명령어인 경우 해당 캐릭터를 앉도록 함.
                if(ss[3] == "join")
                {
                    var spawn = spawns[ss[1]];   // 메시지 보낸 해당스폰 찾고,
                    spawn.GetAvatar().Sit();    //  해당 아바타에 직접 접근하여 앉게함.
                    // 현재 스폰이 ss[2]에 참여했음을 표시
                    spawn.joinItem = ss[2];     // 해당스폰이 참여한 게임이 Reversi라고 등록함.
                    // 토스트 메시지 표시
                    var mesg = string.Format("{0}가 {1}에 참여했습니다.", ss[1], ss[2]);
                    ShowToastMessage(mesg);
                }
                else if(ss[3] == "leave")
                {
                    var spawn = spawns[ss[1]];
                    spawn.GetAvatar().Stand();
                    spawn.joinItem = null; // 해당 스폰이 참여한 게임이 없게함.
                    var mesg = string.Format("{0}가 {1}에 떠났습니다.", ss[1], ss[2]);
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
				// myspawn이 아닌 경우 즉 유니티 클라이언트가 아닌 경우에만 설정
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
        // 2. Find "InputField" - 이름입력부분
        var name = loginWindow.transform.Find("InputField").GetComponent<InputField>();
        // transform에서 찾아야한다.
        // 3. Print result
        Debug.LogFormat("Connect with {0}.", name.text);
        // 4. Hide Login window
        loginWindow.SetActive(false); //비활성화 시키기. (로그인창 닫아주기)

        // Spawn 만들기
        // 1. 빈껍데기의 게임오브젝트 만들고(껍데기 이름정해주기)
        var go = new GameObject(name.text);
        // 2. 빈 껍데기안에 Avatar component 추가하것으로 인스턴스 생성.(껍데기 안에 아바타 생성하기 위해))
        mySpawn = go.AddComponent<Spawn>();
        // 3. 빈 오브젝트에 Avatr 생성하기
        var model = UnityEngine.Random.Range(0, 2); // 내가 선택할수 있게 수정 필요.
        mySpawn.CreateAvatar(name.text, model);
        var hair = UnityEngine.Random.Range(0, 4);
        var body = UnityEngine.Random.Range(0, 4);
        var legs = UnityEngine.Random.Range(0, 4);
        var shoes = UnityEngine.Random.Range(0, 4);
        mySpawn.ChangeLook(hair, body, legs, shoes);
        
        // 서버에 접속하기 - 접속시(이름, 아바타, 옷 정보 서버에 보냄)
        if (socketDesc.Connect("127.0.0.1", 8888))
        {
            Debug.Log("Connected");

            // 디코딩(GetBytes)하여 보내기
            socketDesc.Send(Encoding.UTF8.GetBytes(string.Format("join {0}", name.text)));
            socketDesc.Send(Encoding.UTF8.GetBytes(string.Format("avatar {0} {1}", name.text, model)));
            socketDesc.Send(Encoding.UTF8.GetBytes(string.Format("look {0} {1} {2} {3} {4}", name.text, hair, body, legs, shoes)));
            // UTF8은 한글:3byte 영어:1byte
            
            // key : 이름, value : 스폰 -> 접속한 이름으로 관리한다.
            spawns[name.text] = mySpawn;

        }
        else
        {
            Debug.LogError("Connection is failed");
        }
    }

    // 메시지 창 관리
    string yesSendMesg; // yes버튼이 눌릴 경우 전달할 메시지
    
    // MessageBox 관리
    public void ShowMessageBox(string mesg, string yes)
    {
        // 1. MessageBox를 보이도록 함
        messageBox.SetActive(true);
        // 2. Message 오브젝트를 찾는다. 
        var messageObj = messageBox.transform.Find("Message").GetComponent<TextMeshPro>(); // using TMPro
        // 3. Message 오브젝트에 mesg값을 적는다.
        messageObj.text = mesg;                   // # mesg = {wi.name}에서 떠나시겠습니까?
        // 4. yes 버튼이 눌릴 경우 전달할 메시지를 저장
        yesSendMesg = yes;                        // action {mySpawn.name} {wi.name} leave
    }

    // TosastMessage 관리
    public void ShowToastMessage(string mesg, float duration = 5.0f)
    {
        // 1. ToastMessage를 보이도록
        toastMessage.SetActive(true);
        // 2. Message 오브젝트를 찾는다.
        var messageObj = toastMessage.transform.Find("Message").GetComponent<TextMeshPro>();
        // 3. Message 오브젝트에 mesg값을 적는다.
        messageObj.text = mesg;
        // 4. 보이는 시간을기록
        toastMessageRemain = duration; // 5초동안. 보여줌.
    }

    // Yes 버튼이 눌린 경우 - 미리 유니티의 onClick()에서 설정해줘야!
    public void OnButtonYes()
    {
        // 1. MessageBox를 숨기도록 한다.
        messageBox.SetActive(false);
        // 2. action userName Reversi join <- YES 버튼을 누르면 이 메시지를 서버로 보냄. -> 리버시 게임에 참여하기.
        socketDesc.Send(Encoding.UTF8.GetBytes(yesSendMesg));
    }
    // No 버튼이 눌린 경우 - 미리 유니티의 onClick()에서 설정해줘야!
    public void OnButtonNo()
    {
        // 1. MessageBox를 숨기도록 한다.
        messageBox.SetActive(false);
    }


    // 서버에 패킷 내용 전달하기
    void SendMove()
    {
        var mesg = string.Format("move {0} {1} {2} {3} {4} {5}",
            mySpawn.name, mySpawn.transform.localPosition.x, mySpawn.transform.localPosition.z,
            mySpawn.direction, mySpawn.speed, mySpawn.aspeed);
        socketDesc.Send(Encoding.UTF8.GetBytes(mesg)); // 인코딩하여 완성된 패킷내용(헤더+메시지)을 보내기
    }
}

