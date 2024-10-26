using System;
using System.IO;
using UnityEngine;
using UnityEngine.UI;

public class UnitySaveScreenShot : MonoBehaviour
{
    // Start is called before the first frame update (C: => Users => "user" => AppData => LocalLow => CodeThisLab => "product name" => "gnek") il product name si cambia nei edit/project settings/player
    void Start()
    {
			Run.After(2,
			()=>{
				ScreenCapture.CaptureScreenshot(Application.persistentDataPath+"/gnek.png");
			}
		);
        
    }
}
