using UnityEngine;

public class EndSimulation : MonoBehaviour
{
    private void OnTriggerEnter(Collider other)
    {
        // Check if the object entering the trigger is the car
        if (other.CompareTag("ManualCar"))
        {
            Debug.Log("Simulation ended.");
            
            // End the simulation logic
            EndSim();
        }
    }

    private void EndSim()
    {
        // Perform your desired actions to end the simulation
        // For example, stop the car, load a new scene, or show a results screen.
        
        // Example: Quit the application or stop play mode
        #if UNITY_EDITOR
        UnityEditor.EditorApplication.isPlaying = false;
        #else
        Application.Quit();
        #endif
    }
}
