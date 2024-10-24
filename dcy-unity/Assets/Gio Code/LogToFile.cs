using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.IO;

public class LogToFile : MonoBehaviour
{
    private string logFilePath;

    void Start()
    {
        // Define the path for the log file (creates a log file in the application data folder)
        logFilePath = Application.persistentDataPath + "/GameLog.txt";
        
        // Add log event handler
        Application.logMessageReceived += Log;
        
        // Optional: Clear log file when starting
        File.WriteAllText(logFilePath, "Log Started at " + System.DateTime.Now + "\n\n");
    }

    // Log handler function
    void Log(string logString, string stackTrace, LogType type)
    {
        // Append logs to the file
        using (StreamWriter writer = new StreamWriter(logFilePath, true))
        {
            writer.WriteLine("[" + type.ToString() + "] : " + logString);
        }
    }

    void OnDestroy()
    {
        // Remove log event handler when the object is destroyed
        Application.logMessageReceived -= Log;
    }
}
