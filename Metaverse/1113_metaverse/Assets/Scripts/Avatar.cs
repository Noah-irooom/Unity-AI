/*
 * 1. Create - 모델 생성하기.
    * 1) models에 남자, 여자 아바타 넣고. anims에 남자 여자 컨트롤러 넣어놓기 ( 목록으로 생각))
    * 2) fbx model을 인스턴스화 하여 생성하기 - Instantiate()
    * 3) go.transform.parent = transform : 부모 설정하기
    * 4) animator = go.GetComponent<Animator>(); 속성가져와 animator.runtimeAnimatorController 설정
    * 5) 이름설정, 동작 함수 정의, 옷 바꾸기
        * t.gameObject.SetActive(idx == hair) : 아닌건 옷 비활성화하기.  맞는건 활성화하기 
 * 2. Init
    * models : 실제 아바타 자체 fbx
    * anims : 아바타 동작 controller
    * model 밑 게임 오브젝트를 선택하려면, models[0].transform.Find()으로 집어야함..
*/

using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Avatar : MonoBehaviour
{
    static GameObject[] models;                 // 남자 여자 아바타(2개)
    static RuntimeAnimatorController[] anims;   // 남자 여자 동작(2개)
    Animator animator;
    public static void Init()
    {
        models = new GameObject[2];
        models[0] = Resources.Load("Male/male", typeof(GameObject)) as GameObject;  // fbx 확장자!
        models[1] = Resources.Load("Female/female", typeof(GameObject)) as GameObject;

        anims = new RuntimeAnimatorController[2];
        anims[0] = Resources.Load("Male/male", typeof(RuntimeAnimatorController)) as RuntimeAnimatorController; // controller 확장자
        anims[1] = Resources.Load("Female/female", typeof(RuntimeAnimatorController)) as RuntimeAnimatorController;

        // 문제가 있는 모델의 파트(바디) 이름 수정
        var part = models[0].transform.Find("male_leg01 1");
        if (part != null) part.name = "male_leg00";
        var part2 = models[1].transform.Find("Object012");
        if (part2 != null) part2.name = "female_hair04";
        
        // 각 model에 있는 게임오브젝트 돌면서 male 또는 female로 시작하면 앞글자 male_ , female_ 글자 제거
        for(int i = 0; i< models[0].transform.childCount; i++)
        {
            var t = models[0].transform.GetChild(i);
            if (t.name.StartsWith("male_"))
                t.name = t.name.Substring(5);
        }
        for (int i = 0; i < models[1].transform.childCount; i++)
        {
            var t = models[1].transform.GetChild(i);
            if (t.name.StartsWith("female_"))
                t.name = t.name.Substring(7);
        }


        
    }

    void Start()
    {        
    }
    void Update()
    {    
    }

    // 아바타 생성하기
    public void Create(int model)
    {
        if (models == null) Init();             // 모델 없으면 모델
        var go = Instantiate(models[model]);    // models에서 0 또는 1번째 선택하여 인스턴스화 하기

        // 인스턴스화된 오브젝트의 부모를 현재 오브젝트(Main.cs의 빈껍데기)로 설정한다.
        go.transform.parent = transform;        // 나의 transform을 부모의 transform으로 : 즉 귀속시킴. 여기서 transform은 부모를 말함.
        go.name = "model";                      // 인스턴스화된 아바타 이름 생성
        animator = go.GetComponent<Animator>(); // Animator 가져와 이것으로 인스턴스 생성.
        animator.runtimeAnimatorController = anims[model];
    }

    // 동작함수 정의
    public void Walk() { animator.SetInteger("animation", 1);  }
    public void Sit() { animator.SetInteger("animation", 3);  }
    public void Work() { animator.SetInteger("animation", 2);  }
    public void Stand() { animator.SetInteger("animation", 0); }

    // 옷 바꾸기
    public void ChangeLook(int hair, int body, int legs, int shoes)
    {
        var trans = transform.Find("model"); // 현재 부모 오브젝트에서 인스턴스화된 모델 찾아.
        for (int i = 0; i < trans.childCount; i++)
        {
            var t = trans.GetChild(i); // 인스턴스 모델의 옷 관련 게임오브젝트
            if (!t.name.StartsWith("hair")) continue;
            var idx = int.Parse(t.name.Substring(4)); // hair01이면 01만 따로 파싱하여 int로 나타냄..
            t.gameObject.SetActive(idx == hair);
        }
        for (int i = 0; i < trans.childCount; i++)
        {
            var t = trans.GetChild(i);
            if (!t.name.StartsWith("body") || t.name.Length <= 4) continue;
            var idx = int.Parse(t.name.Substring(4));
            t.gameObject.SetActive(idx == body);
        }
        for (int i = 0; i < trans.childCount; i++)
        {
            var t = trans.GetChild(i);
            if (!t.name.StartsWith("leg")) continue;
            var idx = int.Parse(t.name.Substring(3));
            t.gameObject.SetActive(idx == legs);
        }
        for (int i=0; i < trans.childCount; i++)
        {
            var t = trans.GetChild(i);
            if (!t.name.StartsWith("shoes")) continue;
            var idx = int.Parse(t.name.Substring(5));
            t.gameObject.SetActive(idx == shoes);
        }

    }

}
