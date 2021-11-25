/*
 * 1. Create - �� �����ϱ�.
    * 1) models�� ����, ���� �ƹ�Ÿ �ְ�. anims�� ���� ���� ��Ʈ�ѷ� �־���� ( ������� ����))
    * 2) fbx model�� �ν��Ͻ�ȭ �Ͽ� �����ϱ� - Instantiate()
    * 3) go.transform.parent = transform : �θ� �����ϱ�
    * 4) animator = go.GetComponent<Animator>(); �Ӽ������� animator.runtimeAnimatorController ����
    * 5) �̸�����, ���� �Լ� ����, �� �ٲٱ�
        * t.gameObject.SetActive(idx == hair) : �ƴѰ� �� ��Ȱ��ȭ�ϱ�.  �´°� Ȱ��ȭ�ϱ� 
 * 2. Init
    * models : ���� �ƹ�Ÿ ��ü fbx
    * anims : �ƹ�Ÿ ���� controller
    * model �� ���� ������Ʈ�� �����Ϸ���, models[0].transform.Find()���� �������..
*/

using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Avatar : MonoBehaviour
{
    static GameObject[] models;                 // ���� ���� �ƹ�Ÿ(2��)
    static RuntimeAnimatorController[] anims;   // ���� ���� ����(2��)
    Animator animator;
    public static void Init()
    {
        models = new GameObject[2];
        models[0] = Resources.Load("Male/male", typeof(GameObject)) as GameObject;  // fbx Ȯ����!
        models[1] = Resources.Load("Female/female", typeof(GameObject)) as GameObject;

        anims = new RuntimeAnimatorController[2];
        anims[0] = Resources.Load("Male/male", typeof(RuntimeAnimatorController)) as RuntimeAnimatorController; // controller Ȯ����
        anims[1] = Resources.Load("Female/female", typeof(RuntimeAnimatorController)) as RuntimeAnimatorController;

        // ������ �ִ� ���� ��Ʈ(�ٵ�) �̸� ����
        var part = models[0].transform.Find("male_leg01 1");
        if (part != null) part.name = "male_leg00";
        var part2 = models[1].transform.Find("Object012");
        if (part2 != null) part2.name = "female_hair04";
        
        // �� model�� �ִ� ���ӿ�����Ʈ ���鼭 male �Ǵ� female�� �����ϸ� �ձ��� male_ , female_ ���� ����
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

    // �ƹ�Ÿ �����ϱ�
    public void Create(int model)
    {
        if (models == null) Init();             // �� ������ ��
        var go = Instantiate(models[model]);    // models���� 0 �Ǵ� 1��° �����Ͽ� �ν��Ͻ�ȭ �ϱ�

        // �ν��Ͻ�ȭ�� ������Ʈ�� �θ� ���� ������Ʈ(Main.cs�� �󲮵���)�� �����Ѵ�.
        go.transform.parent = transform;        // ���� transform�� �θ��� transform���� : �� �ͼӽ�Ŵ. ���⼭ transform�� �θ� ����.
        go.name = "model";                      // �ν��Ͻ�ȭ�� �ƹ�Ÿ �̸� ����
        animator = go.GetComponent<Animator>(); // Animator ������ �̰����� �ν��Ͻ� ����.
        animator.runtimeAnimatorController = anims[model];
    }

    // �����Լ� ����
    public void Walk() { animator.SetInteger("animation", 1);  }
    public void Sit() { animator.SetInteger("animation", 3);  }
    public void Work() { animator.SetInteger("animation", 2);  }
    public void Stand() { animator.SetInteger("animation", 0); }

    // �� �ٲٱ�
    public void ChangeLook(int hair, int body, int legs, int shoes)
    {
        var trans = transform.Find("model"); // ���� �θ� ������Ʈ���� �ν��Ͻ�ȭ�� �� ã��.
        for (int i = 0; i < trans.childCount; i++)
        {
            var t = trans.GetChild(i); // �ν��Ͻ� ���� �� ���� ���ӿ�����Ʈ
            if (!t.name.StartsWith("hair")) continue;
            var idx = int.Parse(t.name.Substring(4)); // hair01�̸� 01�� ���� �Ľ��Ͽ� int�� ��Ÿ��..
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
