using System.Collections.Generic;
using UnityEngine;
using System.IO;

public class CarCyclistDistanceRecorder : MonoBehaviour
{
    public Transform car;
    public Transform cyclist;

    private BoxCollider carCollider;
    private BoxCollider cyclistCollider;

    private List<string> dataLog = new List<string>();
    private Vector3 lastCarPosition;
    private float carSpeed;

    // Set your custom folder path here
    public string folderPath = @"C:\Users\sapie\Creative Cloud Files\TUe\M1.2\cyclist-distance-crowdsourced\dcycl-unity\Recordings"; // Replace with your folder path

    void Start()
    {
        if (car == null || cyclist == null)
        {
            Debug.LogError("Car or cyclist is not assigned in the inspector.");
            return;
        }

        carCollider = car.GetComponent<BoxCollider>();
        cyclistCollider = cyclist.GetComponent<BoxCollider>();

        if (carCollider == null || cyclistCollider == null)
        {
            Debug.LogError("Car or cyclist does not have a BoxCollider component.");
            return;
        }

        lastCarPosition = car.position;
        dataLog.Add("Time, Distance, CarPositionX, CarPositionY, CarPositionZ, Speed");

        // Create the folder if it doesn't exist
        if (!Directory.Exists(folderPath))
        {
            Directory.CreateDirectory(folderPath);
        }
    }

    void Update()
    {
        float distance = CalculateColliderDistance();

        carSpeed = (car.position - lastCarPosition).magnitude / Time.deltaTime*3.6f;
        lastCarPosition = car.position;

        string dataEntry = $"{Time.time}, {distance}, {car.position.x}, {car.position.y}, {car.position.z}, {carSpeed}";
        dataLog.Add(dataEntry);

        Debug.Log(dataEntry);
    }

    float CalculateColliderDistance()
    {
        Vector3 closestPointOnCar = carCollider.ClosestPoint(cyclistCollider.bounds.center);
        Vector3 closestPointOnCyclist = cyclistCollider.ClosestPoint(closestPointOnCar);
        return Vector3.Distance(closestPointOnCar, closestPointOnCyclist);
    }

    void OnApplicationQuit()
    {
        string fullPath = Path.Combine(folderPath, "CarCyclistDistanceData.csv");
        SaveDataToCSV(fullPath);
    }

    public void SaveDataToCSV(string filePath)
    {
        // Check if file exists and increment name if necessary
        string baseFilePath = filePath;
        int fileCount = 1;

        while (File.Exists(filePath))
        {
            filePath = baseFilePath.Replace(".csv", $"_{fileCount}.csv");
            fileCount++;
        }

        try
        {
            File.WriteAllLines(filePath, dataLog);
            Debug.Log("Data saved to " + filePath);
        }
        catch (IOException e)
        {
            Debug.LogError("Failed to save data: " + e.Message);
        }
    }
}
