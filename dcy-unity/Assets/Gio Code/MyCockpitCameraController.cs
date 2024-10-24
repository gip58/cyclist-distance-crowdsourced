using UnityEngine;

public class MyCockpitCameraController : MonoBehaviour
{
    public Camera cockpitCamera; // Drag the cockpit camera here
    public Camera otherCamera;   // Optional: another camera to disable at the start

    // Start is called before the first frame update
    void Start()
    {
        // Enable the cockpit camera
        if (cockpitCamera != null)
        {
            cockpitCamera.gameObject.SetActive(true);
        }

        // Disable other cameras if necessary
        if (otherCamera != null)
        {
            otherCamera.gameObject.SetActive(false);
        }
    }
}
