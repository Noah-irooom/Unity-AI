using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class WorldItem : MonoBehaviour
{
    Material[] mtlList;
    Material mtlBoard;
    void Awake()
    {
        mtlList = new Material[3];
        mtlList[1] = Resources.Load("Materials/White") as Material;
        mtlList[2] = Resources.Load("Materials/Black") as Material;
        mtlBoard = Resources.Load("Materials/Board", typeof(Material)) as Material;
    }

    void Update()
    {
    }
    // ex) CreateItem("Reversi", 10, 10, 0), CreateItem("Reversi", 20, 20, 90)
    public bool CreateItem(string itemName, float x, float y, float dir)
    {
        if (itemName == "Reversi") CreateReversi(transform);
        // Reversi가 아니라면(Sofa라면)
        else
        {
            // 1. item을 사용할 게임오브젝트를 생성. - Sofa 
            var item = GameObject.CreatePrimitive(PrimitiveType.Cube);
            // 2. 생성한 아이템을 현재 오브젝트의 자식으로 등록.
            item.transform.parent = transform;
            item.name = "0";
        }
        name = itemName;
        
        // 3. 위치를 지정. - 빈껍데기의 위치를 조정하는 것.
        transform.localPosition = new Vector3(x, 0, y);
        transform.localEulerAngles = new Vector3(0, dir, 0);
        return true;
    }
    void CreateReversi(Transform transform)
    {
        // 리버시의 8x8 판을 만든다.
        for(int i = 0; i < 8; i++)
        {
            for (int j = 0; j < 8; j++)
            {
                // 직사각형 Cube 생성후 위치 및 크기  조정
                var go = GameObject.CreatePrimitive(PrimitiveType.Cube);
                go.transform.localScale = new Vector3(0.19f, 1, 0.19f);
                go.transform.localPosition = new Vector3(0.2f * j - 0.8f, 0.0f, 0.2f * i - 0.8f);
                go.transform.parent = transform;
                
                // materials 설정하기 - Renderer 이용.
                var rend = go.GetComponent<Renderer>();
                rend.material = mtlBoard;
                go.name = string.Format("{0}", i * 8 + j); //0 ~ 63

                // 바둑알 오브젝트 생성하기.  -  일단 SetActive(false) : 해제시켜 놓기.
                go = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                go.transform.localScale = new Vector3(0.18f, 0.05f, 0.18f);
                go.transform.localPosition = new Vector3(0.2f * j - 0.8f, 0.5f, 0.2f * i - 0.8f);
                go.transform.parent = transform;
                go.name = string.Format("c{0}", i * 8 + j);
                go.SetActive(false); // default 는 해제.
            }
        }
    }
    // ex)action Reversi join white -> wi.ActionItem(Reversi, join, white);
    // ex)action Reversi place 33333..1122..333 -> wi.ActionItem(Reversi, place,  33333..1122..333 );
    // ex)action Reversi place fail -> wi.ActionItem(Reversi, place, fail); 
    public void ActionItem(string name, string cmd, string data)
    {
        if (name != "Reversi") return;
        if (cmd == "place")
        {
            // Reversi, place, fail
            if (data == "fail") Debug.Log("Placing is failed");
            // Reversi, place, 333311..223333-> UpdateItem(Reversi, 333..112.333) # 이미 서버에서 돌바꾼후에 처리
            else UpdateItem(name, data);
        }
        else if (cmd == "join") Debug.LogFormat("Join Reversi with {0}", data);
    }
    // deactivate 시킨 바둑알을 activate 시키기
    // ex) UpdateItem("Reversi", "0001200...001") : 리버시판을 클릭한다. turn 1번이(white)
    public void UpdateItem(string name, string data)
    {
        if (name != "Reversi") return; // Reversi아니면 진행되지 않게
        for(int i = 0; i < transform.childCount; i++) // 현재 reversi 판의 빈껍데기(transform)의 child : 64+64
        {
            var t = transform.GetChild(i);
            if(t.name[0] == 'c')
            {
                //c0~c64 -> 0~64
                var idx = int.Parse(t.name.Substring(1));
                
                // turn 1번 인 바둑돌은 white로 색 바꾸기
                if(data[idx] == '1')
                {
                    t.gameObject.SetActive(true); // 바둑알 activate 시키기
                    var rend = t.gameObject.GetComponent<Renderer>();
                    rend.material = mtlList[1];
                }
                // turn 2번인 바둑돌은  black으로 색 바꾸기
                else if (data[idx] == '2')
                {
                    t.gameObject.SetActive(true);
                    var rend = t.gameObject.GetComponent<Renderer>();
                    rend.material = mtlList[2];
                }
                else
                {
                    t.gameObject.SetActive(false);
                }
            }
        }
    }
}
