using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Rotor : MonoBehaviour
{
    float GlobalAngleSpeed = 0.1f;
    // ȸ���ϴ� �ӵ�. �ʴ� ��� ȸ���Ұǰ�? 1���� 1����(����Ƽ�� ���� �Ⱦ���.)
    public float AngleSpeed = 20.0f; // �ƹ��͵� �Ⱦ���, private �����̴�.

    // Update is called once per frame
    void Update()
    {
        //1) ���� �����ӿ��� ���� �����ӱ����� �ð�.(delta time)�� �̿��ؼ� y �࿡�� ȸ���� ������ ���
        // Time.deltaTime(�ʴ����̴�.)
        var yangle = Time.deltaTime * AngleSpeed * GlobalAngleSpeed;
        // 2) x,z�� ȸ������ y�� ȸ���� �ֵ���
        transform.Rotate(0.0f, yangle, 0.0f); 
    }
}
