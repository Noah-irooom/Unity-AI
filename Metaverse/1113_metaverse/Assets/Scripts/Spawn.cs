/*
1025_Spawn.cs
    1. Spawn은 붕어빵.  Avatar는 붕어빵 틀.  Main은 입력전달 및 카메라 관리
        1) Avatar : 모델 및 컨트롤러, 생성함수 옷변경 함수
        2) Spawn : 아바타 생성, 동작 지정, 생성하기 함수, 옷변경하기 함수 등
        3) Main : 아바타에게 입력 주기
 */
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Spawn : MonoBehaviour
{

    Avatar avatar;                  // 아바타 오브젝트
    public float speed;             // 걸어가는 속도
    public float direction;         // z축기준에서 시계방향 바라보는 각도
    public float aspeed;            // 회전 속도
    GameObject nameGo;              // 이름판용 게임 오브젝트

    void Start()
    {
    }

    void Update()
    {
        // 1.avatar가 현재 없다면 아무것도 안하도록.
        if (avatar == null) return;
        // 2. frame 시간을 가져온다.
        var t = Time.deltaTime;
        // 3. 애니메이션 적용
        if (speed > 0.0f || speed < 0.0f) avatar.Walk();
        else avatar.Stand();
        // 4. 회전 이동
        direction += t * aspeed;
        avatar.transform.localEulerAngles = new Vector3(0, direction, 0);
        // 5. 위치이동 = 현위치 + 시*속*방
        var rad = Mathf.Deg2Rad * direction;
        var dirv = new Vector3(Mathf.Sin(rad), 0, Mathf.Cos(rad)); // 방향 단위 벡터
        avatar.transform.localPosition += t * speed * dirv;
        // 6. 이름판이 항상 카메라 바라보도록 회전(Billboard 구현)
        nameGo.transform.LookAt(nameGo.transform.position +
            Camera.main.transform.rotation * Vector3.forward,
            Camera.main.transform.rotation * Vector3.up);
    }

    // 현재 이 스폰의 아바타를 얻어 오는 함수.
    public Avatar GetAvatar() { return avatar; }

    // 아바타 생성 함수
    public void CreateAvatar(string name, int model)
    {
        // 1. 아바타를 생성한다.
        avatar = gameObject.AddComponent<Avatar>(); // 여기서 gameObject는 Main의 go(빈껍데기) 가리킴
        avatar.Create(model);
        // 2.이름판 만들기
        nameGo = new GameObject("Text");
        var nameText = nameGo.AddComponent<TextMesh>();
        nameText.text = name;
        // 3. 본 게임오브젝트(상위 껍데기)에 이름판 껍데기 붙이기
        nameGo.transform.parent = gameObject.transform;
        nameGo.transform.localPosition = new Vector3(0, 1.9f, 0);
        nameGo.transform.localScale = new Vector3(0.15f, 0.15f, 0.15f);
        nameText.anchor = TextAnchor.MiddleCenter;

    }
    // 아바타의 옷을 변경.
    public void ChangeLook(int hair, int body, int legs, int shoes)
    {
        avatar.ChangeLook(hair, body, legs, shoes);
    }
}
