/*
1025_Spawn.cs
    1. Spawn�� �ؾ.  Avatar�� �ؾ Ʋ.  Main�� �Է����� �� ī�޶� ����
        1) Avatar : �� �� ��Ʈ�ѷ�, �����Լ� �ʺ��� �Լ�
        2) Spawn : �ƹ�Ÿ ����, ���� ����, �����ϱ� �Լ�, �ʺ����ϱ� �Լ� ��
        3) Main : �ƹ�Ÿ���� �Է� �ֱ�
 */
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Spawn : MonoBehaviour
{

    Avatar avatar;                  // �ƹ�Ÿ ������Ʈ
    public float speed;             // �ɾ�� �ӵ�
    public float direction;         // z����ؿ��� �ð���� �ٶ󺸴� ����
    public float aspeed;            // ȸ�� �ӵ�
    GameObject nameGo;              // �̸��ǿ� ���� ������Ʈ

    void Start()
    {
    }

    void Update()
    {
        // 1.avatar�� ���� ���ٸ� �ƹ��͵� ���ϵ���.
        if (avatar == null) return;
        // 2. frame �ð��� �����´�.
        var t = Time.deltaTime;
        // 3. �ִϸ��̼� ����
        if (speed > 0.0f || speed < 0.0f) avatar.Walk();
        else avatar.Stand();
        // 4. ȸ�� �̵�
        direction += t * aspeed;
        avatar.transform.localEulerAngles = new Vector3(0, direction, 0);
        // 5. ��ġ�̵� = ����ġ + ��*��*��
        var rad = Mathf.Deg2Rad * direction;
        var dirv = new Vector3(Mathf.Sin(rad), 0, Mathf.Cos(rad)); // ���� ���� ����
        avatar.transform.localPosition += t * speed * dirv;
        // 6. �̸����� �׻� ī�޶� �ٶ󺸵��� ȸ��(Billboard ����)
        nameGo.transform.LookAt(nameGo.transform.position +
            Camera.main.transform.rotation * Vector3.forward,
            Camera.main.transform.rotation * Vector3.up);
    }

    // ���� �� ������ �ƹ�Ÿ�� ��� ���� �Լ�.
    public Avatar GetAvatar() { return avatar; }

    // �ƹ�Ÿ ���� �Լ�
    public void CreateAvatar(string name, int model)
    {
        // 1. �ƹ�Ÿ�� �����Ѵ�.
        avatar = gameObject.AddComponent<Avatar>(); // ���⼭ gameObject�� Main�� go(�󲮵���) ����Ŵ
        avatar.Create(model);
        // 2.�̸��� �����
        nameGo = new GameObject("Text");
        var nameText = nameGo.AddComponent<TextMesh>();
        nameText.text = name;
        // 3. �� ���ӿ�����Ʈ(���� ������)�� �̸��� ������ ���̱�
        nameGo.transform.parent = gameObject.transform;
        nameGo.transform.localPosition = new Vector3(0, 1.9f, 0);
        nameGo.transform.localScale = new Vector3(0.15f, 0.15f, 0.15f);
        nameText.anchor = TextAnchor.MiddleCenter;

    }
    // �ƹ�Ÿ�� ���� ����.
    public void ChangeLook(int hair, int body, int legs, int shoes)
    {
        avatar.ChangeLook(hair, body, legs, shoes);
    }
}
