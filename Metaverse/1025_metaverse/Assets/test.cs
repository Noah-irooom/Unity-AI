using System;
using System.Text;
using System.Net.Sockets;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class test : MonoBehaviour
{
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        string str = String.Format("{0,4}", 13);
        Debug.Log(Encoding.UTF8.GetBytes(str));
    }
}
