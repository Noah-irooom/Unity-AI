using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Raider : MonoBehaviour
{
    public Texture2D tex;
    public float maxRange = 50.0f;
    public bool showHit = true;
    byte[] data;
    int offset = 0;
    GameObject[,] particles;
	void Awake()
	{
	    if(tex == null)
        {
            tex = new Texture2D(256, 32, TextureFormat.R16, false);
        }
        data = tex.GetRawTextureData();
        Debug.LogFormat("texture format : {0} {1}x{2} {3}", tex.format, tex.width, tex.height, data.Length);
        var pd = new GameObject();
        pd.name = "particles";
        pd.SetActive(showHit);
        particles = new GameObject[32, 256];
        var pscale = new Vector3(0.02f, 0.02f, 0.02f);
        Material pmat = new Material(Shader.Find("Standard"));
        pmat.color = Color.yellow;
        for(int y = 0; y < 32; y++)
        {
            for(int x = 0; x < 256; x+=1)
            {
                particles[y, x] = GameObject.CreatePrimitive(PrimitiveType.Cube);
                particles[y, x].transform.parent = pd.transform;
                particles[y, x].transform.localScale = pscale;
                Destroy(particles[y, x].GetComponent("BoxCollider"));
                particles[y, x].GetComponent<Renderer>().material = pmat;
                particles[y, x].SetActive(false);
            }
        }
	}

    void FixedUpdate()
    {
        var eye = transform.position;
        var forward = transform.forward;
        var ray = new Ray(eye, forward);
        var yAngle = Mathf.Rad2Deg*Mathf.Atan2(forward.x, forward.z)+180.0f;
        for(int x = 0; x < 256; x++)
        {
            for(int y = 0; y < 32; y++)
            {
                var rot = Quaternion.Euler(20.0f-y, x*360.0f/256.0f+yAngle, 0.0f)*Vector3.forward;
                ray.direction = rot;
                float distance = maxRange;
                RaycastHit hit;
                if(Physics.Raycast(ray, out hit, maxRange))
                {
                    distance = hit.distance;
                    if(showHit && particles[y, x])
                    {
                        particles[y, x].SetActive(true);
                        particles[y, x].transform.localPosition = hit.point;
                    }
                }
                else if(showHit && particles[y, x])
                {
                    particles[y, x].SetActive(false);
                }
                ushort us = (ushort)(65000.0f - distance*60000f/maxRange);
		        data[y*512 + x*2 + 0] = (byte)(us&255);
		        data[y*512 + x*2 + 1] = (byte)(us>>8);
            }
        }
        tex.LoadRawTextureData(data);
        tex.Apply();
    }
}
