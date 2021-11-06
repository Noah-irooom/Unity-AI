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
    4. 

 */

using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class Main : MonoBehaviour
{
    Avatar myAvatar;        // avatar 오브젝트
    float speed;            // 걸어가는 속도
    float direction;        // z축을 기준으로 시계방향으로 얼만큼 회전하는지
    float aspeed;           // 회전속도
    float distance = 5.0f;  // camera distance
    float zoom;             // camera zoom
    float camoffset;        // camera offset angle
    float camheigth;
    Vector2 lastMousePos;   // last mouse position
    GameObject nameGo;      // 이름판용 게임오브젝트

    void Start()
    {
    }

    void Update()
    {
        // Debug.Log(int.Parse("00"));
        // 현재 아바타가 생성되어 있지 않다면 아무 작업 안 하도록한다.
        if (myAvatar == null) return;
        if (Input.GetKeyDown(KeyCode.Alpha0)) myAvatar.Stand();
        else if (Input.GetKeyDown(KeyCode.Alpha1)) myAvatar.Walk();
        else if (Input.GetKeyDown(KeyCode.Alpha2)) myAvatar.Work();
        else if (Input.GetKeyDown(KeyCode.Alpha3)) myAvatar.Sit();

        // W키를 느면 전진, S 후진
        if(Input.GetKeyDown(KeyCode.W)) { speed = 1.0f; myAvatar.Walk(); }
        else if(Input.GetKeyUp(KeyCode.W)) { speed = 0.0f; myAvatar.Stand(); }
        if(Input.GetKeyDown(KeyCode.S)) { speed = -1.0f; myAvatar.Walk(); }
        else if(Input.GetKeyUp(KeyCode.S)) { speed = 0.0f; myAvatar.Stand(); }
        // A 좌회전, D 우회전
        if(Input.GetKeyDown(KeyCode.A)) { aspeed = -90.0f; }    // 1초에 1/4만큼 이동
        else if(Input.GetKeyUp(KeyCode.A)) { aspeed = 0.0f; }
        if(Input.GetKeyDown(KeyCode.D)) { aspeed = 90.0f; }
        else if (Input.GetKeyUp(KeyCode.D)) { aspeed = 0.0f; }

        //  t 변수에 한 프레임의 시간 (초단위)를 저장
        var t = Time.deltaTime;

        // 아바타 회전 이동
        direction += t * aspeed; // 1초에 각속도 만큼 회전 // direction : 아바타가 현재 바라보는 방향(z축 기준)
        myAvatar.transform.localEulerAngles = new Vector3(0, direction, 0); // y축 중심으로 z축에서 시계방향 회전

        // 아바타 위치 이동
        var rad = Mathf.Deg2Rad * direction; // 또는 Mathf.Deg2Rad * direction
        var dirv = new Vector3(Mathf.Sin(rad), 0, Mathf.Cos(rad)); // 방향 단위벡터설정
        myAvatar.transform.localPosition += dirv * speed * t; // 이 방향으로 이 속도만큼 단위시간동안 가겠다.


        // 카메라 줌 인 아웃 - 마우스 휠 값을 읽어와서 zoom에 적용
        zoom += Input.mouseScrollDelta.y * 0.1f;
        //Debug.Log(zoom);
        if (zoom < -1.0f) zoom = -1.0f; else if (zoom > 1.0f) zoom = 1.0f;  //한계치설정

        

        // 카메라 회전 - 마우스 버튼 1이 클릭된 상태에서 팬 처리
        if (Input.GetMouseButtonDown(1)) lastMousePos = Input.mousePosition;
        else if (Input.GetMouseButtonUp(1)) lastMousePos = Vector2.zero; // 마우스 위치 2차원.
        // Debug.Log(lastMousePos);
        if(lastMousePos != Vector2.zero) { 
            camoffset += Input.mousePosition.x - lastMousePos.x; // 현 마우스 위치와 마지막 마우스 위치 차이
            camheigth += (Input.mousePosition.y - lastMousePos.y)*0.01f;
            lastMousePos = Input.mousePosition;
        }
        
        else
        {
            // 마우스 버튼을 떼면 lastMousePos는 영벡터가 되니까 제자리로 돌아오게 설정한다.
            if(camoffset < 0.0f) { 
                camoffset += 0.1f;  // 카메라가 제자리로 돌아오게끔 설정
                if (camoffset > 0.0f) camoffset = 0.0f; 
            }
            else if (camoffset > 0.0f)
            {
                camoffset -= 0.1f;
                if (camoffset < 0.0f) camoffset = 0.0f; //????
            }
        }
        

        // 카메라 위치
        var camd = distance * Mathf.Pow(2.0f, zoom); // 2의 zoom제곱(1/2 ~ 2) * distance(0.5f) = (0.25 ~ 1)
        rad = Mathf.Deg2Rad * (direction + camoffset); // 현재 아바타가 바라보는 각도(z축기준)를 기준으로 한 카메라 각도(즉 rad는 카메라 절대각도)
        var cdirv = new Vector3(Mathf.Sin(rad), 0, Mathf.Cos(rad)); // 카메라 방향 단위벡터
        var cameraPosAngle = Mathf.Deg2Rad * 30; // 카메라와 아바타가 이루는 각도
        var xzDistance = camd * Mathf.Cos(cameraPosAngle) * cdirv; // 빗변 * cos * 방향단위벡터 => xz 정사영
        var yDistance = new Vector3(0, camd * Mathf.Sin(cameraPosAngle) + 1.8f - camheigth, 0);
        Camera.main.transform.localPosition = myAvatar.transform.localPosition - xzDistance + yDistance;
        Camera.main.transform.localEulerAngles = new Vector3(30.0f, (direction + camoffset), 0);  //카메라 바라보는 각도(View)

        // 이름판이 항상 카메라를 바라보도록 회전한다. (Billboard 구현)
        nameGo.transform.LookAt(nameGo.transform.position +
            Camera.main.transform.rotation * Vector3.forward,
            Camera.main.transform.rotation * Vector3.up);
        //Debug.Log(Camera.main.transform.rotation);
        //Debug.Log(Camera.main.transform.rotation * Vector3.forward);

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

        // Avatar 올려 놓기
        // 1. 빈껍데기의 게임오브젝트 만들고(껍데기 이름정해주기)
        var go = new GameObject(name.text);
        // 2. 빈 껍데기안에 Avatar component 추가하것으로 인스턴스 생성.(껍데기 안에 아바타 생성하기 위해))
        myAvatar = go.AddComponent<Avatar>();
        // 3. 빈 오브젝트에 Avatr 생성하기
        myAvatar.Create(Random.Range(0, 2));
        myAvatar.ChangeLook(Random.Range(0, 4), Random.Range(0, 4), Random.Range(0, 4), Random.Range(0, 4));
        // 4. 이름판 만들기
        nameGo = new GameObject("Text");                // 이름판 껍데기 생성하고 그 빈껍데기 이름 붙여..
        var nameText = nameGo.AddComponent<TextMesh>(); // 이름판 껍데기에 TextMesh 컴포넌트 가져온것으로 인스턴스 생성
        nameText.text = name.text;
        // 5. 아바타 오브젝트에 이름판 붙이기
        nameGo.transform.parent = go.transform; // 빈껍데기 안으로 귀속시킴. (여기서 그냥 transform이 아닌 이유: Main에 귀속되니까)
        nameGo.transform.localPosition = new Vector3(0, 1.9f, 0);
        nameGo.transform.localScale = new Vector3(0.15f, 0.15f, 0.15f);
        nameText.anchor = TextAnchor.MiddleCenter;
    }
}

