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
        // Reversi�� �ƴ϶��(Sofa���)
        else
        {
            // 1. item�� ����� ���ӿ�����Ʈ�� ����. - Sofa 
            var item = GameObject.CreatePrimitive(PrimitiveType.Cube);
            // 2. ������ �������� ���� ������Ʈ�� �ڽ����� ���.
            item.transform.parent = transform;
            item.name = "0";
        }
        name = itemName;
        
        // 3. ��ġ�� ����. - �󲮵����� ��ġ�� �����ϴ� ��.
        transform.localPosition = new Vector3(x, 0, y);
        transform.localEulerAngles = new Vector3(0, dir, 0);
        return true;
    }
    void CreateReversi(Transform transform)
    {
        // �������� 8x8 ���� �����.
        for(int i = 0; i < 8; i++)
        {
            for (int j = 0; j < 8; j++)
            {
                // ���簢�� Cube ������ ��ġ �� ũ��  ����
                var go = GameObject.CreatePrimitive(PrimitiveType.Cube);
                go.transform.localScale = new Vector3(0.19f, 1, 0.19f);
                go.transform.localPosition = new Vector3(0.2f * j - 0.8f, 0.0f, 0.2f * i - 0.8f);
                go.transform.parent = transform;
                
                // materials �����ϱ� - Renderer �̿�.
                var rend = go.GetComponent<Renderer>();
                rend.material = mtlBoard;
                go.name = string.Format("{0}", i * 8 + j); //0 ~ 63

                // �ٵϾ� ������Ʈ �����ϱ�.  -  �ϴ� SetActive(false) : �������� ����.
                go = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                go.transform.localScale = new Vector3(0.18f, 0.05f, 0.18f);
                go.transform.localPosition = new Vector3(0.2f * j - 0.8f, 0.5f, 0.2f * i - 0.8f);
                go.transform.parent = transform;
                go.name = string.Format("c{0}", i * 8 + j);
                go.SetActive(false); // default �� ����.
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
            // Reversi, place, 333311..223333-> UpdateItem(Reversi, 333..112.333) # �̹� �������� ���ٲ��Ŀ� ó��
            else UpdateItem(name, data);
        }
        else if (cmd == "join") Debug.LogFormat("Join Reversi with {0}", data);
    }
    // deactivate ��Ų �ٵϾ��� activate ��Ű��
    // ex) UpdateItem("Reversi", "0001200...001") : ���������� Ŭ���Ѵ�. turn 1����(white)
    public void UpdateItem(string name, string data)
    {
        if (name != "Reversi") return; // Reversi�ƴϸ� ������� �ʰ�
        for(int i = 0; i < transform.childCount; i++) // ���� reversi ���� �󲮵���(transform)�� child : 64+64
        {
            var t = transform.GetChild(i);
            if(t.name[0] == 'c')
            {
                //c0~c64 -> 0~64
                var idx = int.Parse(t.name.Substring(1));
                
                // turn 1�� �� �ٵϵ��� white�� �� �ٲٱ�
                if(data[idx] == '1')
                {
                    t.gameObject.SetActive(true); // �ٵϾ� activate ��Ű��
                    var rend = t.gameObject.GetComponent<Renderer>();
                    rend.material = mtlList[1];
                }
                // turn 2���� �ٵϵ���  black���� �� �ٲٱ�
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
