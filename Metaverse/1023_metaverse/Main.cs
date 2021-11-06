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
    4. 

 */

using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class Main : MonoBehaviour
{
    Avatar myAvatar;        // avatar ������Ʈ
    float speed;            // �ɾ�� �ӵ�
    float direction;        // z���� �������� �ð�������� ��ŭ ȸ���ϴ���
    float aspeed;           // ȸ���ӵ�
    float distance = 5.0f;  // camera distance
    float zoom;             // camera zoom
    float camoffset;        // camera offset angle
    float camheigth;
    Vector2 lastMousePos;   // last mouse position
    GameObject nameGo;      // �̸��ǿ� ���ӿ�����Ʈ

    void Start()
    {
    }

    void Update()
    {
        // Debug.Log(int.Parse("00"));
        // ���� �ƹ�Ÿ�� �����Ǿ� ���� �ʴٸ� �ƹ� �۾� �� �ϵ����Ѵ�.
        if (myAvatar == null) return;
        if (Input.GetKeyDown(KeyCode.Alpha0)) myAvatar.Stand();
        else if (Input.GetKeyDown(KeyCode.Alpha1)) myAvatar.Walk();
        else if (Input.GetKeyDown(KeyCode.Alpha2)) myAvatar.Work();
        else if (Input.GetKeyDown(KeyCode.Alpha3)) myAvatar.Sit();

        // WŰ�� ���� ����, S ����
        if(Input.GetKeyDown(KeyCode.W)) { speed = 1.0f; myAvatar.Walk(); }
        else if(Input.GetKeyUp(KeyCode.W)) { speed = 0.0f; myAvatar.Stand(); }
        if(Input.GetKeyDown(KeyCode.S)) { speed = -1.0f; myAvatar.Walk(); }
        else if(Input.GetKeyUp(KeyCode.S)) { speed = 0.0f; myAvatar.Stand(); }
        // A ��ȸ��, D ��ȸ��
        if(Input.GetKeyDown(KeyCode.A)) { aspeed = -90.0f; }    // 1�ʿ� 1/4��ŭ �̵�
        else if(Input.GetKeyUp(KeyCode.A)) { aspeed = 0.0f; }
        if(Input.GetKeyDown(KeyCode.D)) { aspeed = 90.0f; }
        else if (Input.GetKeyUp(KeyCode.D)) { aspeed = 0.0f; }

        //  t ������ �� �������� �ð� (�ʴ���)�� ����
        var t = Time.deltaTime;

        // �ƹ�Ÿ ȸ�� �̵�
        direction += t * aspeed; // 1�ʿ� ���ӵ� ��ŭ ȸ�� // direction : �ƹ�Ÿ�� ���� �ٶ󺸴� ����(z�� ����)
        myAvatar.transform.localEulerAngles = new Vector3(0, direction, 0); // y�� �߽����� z�࿡�� �ð���� ȸ��

        // �ƹ�Ÿ ��ġ �̵�
        var rad = Mathf.Deg2Rad * direction; // �Ǵ� Mathf.Deg2Rad * direction
        var dirv = new Vector3(Mathf.Sin(rad), 0, Mathf.Cos(rad)); // ���� �������ͼ���
        myAvatar.transform.localPosition += dirv * speed * t; // �� �������� �� �ӵ���ŭ �����ð����� ���ڴ�.


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
                if (camoffset < 0.0f) camoffset = 0.0f; //????
            }
        }
        

        // ī�޶� ��ġ
        var camd = distance * Mathf.Pow(2.0f, zoom); // 2�� zoom����(1/2 ~ 2) * distance(0.5f) = (0.25 ~ 1)
        rad = Mathf.Deg2Rad * (direction + camoffset); // ���� �ƹ�Ÿ�� �ٶ󺸴� ����(z�����)�� �������� �� ī�޶� ����(�� rad�� ī�޶� ���밢��)
        var cdirv = new Vector3(Mathf.Sin(rad), 0, Mathf.Cos(rad)); // ī�޶� ���� ��������
        var cameraPosAngle = Mathf.Deg2Rad * 30; // ī�޶�� �ƹ�Ÿ�� �̷�� ����
        var xzDistance = camd * Mathf.Cos(cameraPosAngle) * cdirv; // ���� * cos * ����������� => xz ���翵
        var yDistance = new Vector3(0, camd * Mathf.Sin(cameraPosAngle) + 1.8f - camheigth, 0);
        Camera.main.transform.localPosition = myAvatar.transform.localPosition - xzDistance + yDistance;
        Camera.main.transform.localEulerAngles = new Vector3(30.0f, (direction + camoffset), 0);  //ī�޶� �ٶ󺸴� ����(View)

        // �̸����� �׻� ī�޶� �ٶ󺸵��� ȸ���Ѵ�. (Billboard ����)
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
        // 2. Find "InputField" - �̸��Էºκ�
        var name = loginWindow.transform.Find("InputField").GetComponent<InputField>();
        // transform���� ã�ƾ��Ѵ�.
        // 3. Print result
        Debug.LogFormat("Connect with {0}.", name.text);
        // 4. Hide Login window
        loginWindow.SetActive(false); //��Ȱ��ȭ ��Ű��. (�α���â �ݾ��ֱ�)

        // Avatar �÷� ����
        // 1. �󲮵����� ���ӿ�����Ʈ �����(������ �̸������ֱ�)
        var go = new GameObject(name.text);
        // 2. �� ������ȿ� Avatar component �߰��ϰ����� �ν��Ͻ� ����.(������ �ȿ� �ƹ�Ÿ �����ϱ� ����))
        myAvatar = go.AddComponent<Avatar>();
        // 3. �� ������Ʈ�� Avatr �����ϱ�
        myAvatar.Create(Random.Range(0, 2));
        myAvatar.ChangeLook(Random.Range(0, 4), Random.Range(0, 4), Random.Range(0, 4), Random.Range(0, 4));
        // 4. �̸��� �����
        nameGo = new GameObject("Text");                // �̸��� ������ �����ϰ� �� �󲮵��� �̸� �ٿ�..
        var nameText = nameGo.AddComponent<TextMesh>(); // �̸��� �����⿡ TextMesh ������Ʈ �����°����� �ν��Ͻ� ����
        nameText.text = name.text;
        // 5. �ƹ�Ÿ ������Ʈ�� �̸��� ���̱�
        nameGo.transform.parent = go.transform; // �󲮵��� ������ �ͼӽ�Ŵ. (���⼭ �׳� transform�� �ƴ� ����: Main�� �ͼӵǴϱ�)
        nameGo.transform.localPosition = new Vector3(0, 1.9f, 0);
        nameGo.transform.localScale = new Vector3(0.15f, 0.15f, 0.15f);
        nameText.anchor = TextAnchor.MiddleCenter;
    }
}

