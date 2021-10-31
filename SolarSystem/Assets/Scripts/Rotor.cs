using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Rotor : MonoBehaviour
{
    float GlobalAngleSpeed = 0.1f;
    // 회전하는 속도. 초당 몇도가 회전할건가? 1도에 1도씩(유니티는 라디안 안쓴다.)
    public float AngleSpeed = 20.0f; // 아무것도 안쓰면, private 변수이다.

    // Update is called once per frame
    void Update()
    {
        //1) 이전 프레임에서 지금 프레임까지의 시간.(delta time)을 이용해서 y 축에서 회전할 각도를 계산
        // Time.deltaTime(초단위이다.)
        var yangle = Time.deltaTime * AngleSpeed * GlobalAngleSpeed;
        // 2) x,z축 회전없고 y축 회전만 있도록
        transform.Rotate(0.0f, yangle, 0.0f); 
    }
}
