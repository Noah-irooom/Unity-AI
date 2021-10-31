using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Jupyter : MonoBehaviour
{
    
    // ȸ���ϴ� �ӵ�. �ʴ� ��� ȸ���Ұǰ�? 1���� 1����(����Ƽ�� ���� �Ⱦ���.)
    public float AngleSpeed = 80.0f; // �ƹ��͵� �Ⱦ���, private �����̴�.
    float xangleSpeed = 0.01f;
    float zangleSpeed = 0.01f;
    // Update is called once per frame
    void Update()
    {
        //1) ���� �����ӿ��� ���� �����ӱ����� �ð�.(delta time)�� �̿��ؼ� y �࿡�� ȸ���� ������ ���
        // Time.deltaTime(�ʴ����̴�.)
        var yangle = Time.deltaTime * AngleSpeed;
        var xangle = Time.deltaTime * xangleSpeed;
        var zangle = Time.deltaTime * zangleSpeed;
        // 2) x,z�� ȸ������ y�� ȸ���� �ֵ���
        transform.Rotate(xangle, yangle, zangle);
    }
}

