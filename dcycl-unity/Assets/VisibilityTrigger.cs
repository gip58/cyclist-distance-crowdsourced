using System.Collections;
using UnityEngine;

public class VisibilityTrigger : MonoBehaviour
{
    private MeshRenderer childRenderer;

    // Time in seconds after which the object should appear
    [SerializeField] private float delayBeforeShow = 5.0f;
    [SerializeField] private float displayDuration = 3.0f;

    void Start()
    {
        // Get the Mesh Renderer from the child object
        childRenderer = GetComponentInChildren<MeshRenderer>();

        // Ensure the child object is invisible at the start
        if (childRenderer != null)
        {
            childRenderer.enabled = false;
        }
    }

    private void OnTriggerEnter(Collider other)
    {
        // Check if the object entering the trigger is the car
        if (other.CompareTag("ManualCar")) // replace "Car" with the tag of your car object
        {
            // Start the coroutine to handle visibility
            StartCoroutine(ToggleVisibility());
        }
    }

    private IEnumerator ToggleVisibility()
    {
        // Wait for the specified delay before showing the object
        yield return new WaitForSeconds(delayBeforeShow);

        // Enable the Mesh Renderer on the child object (make it visible)
        if (childRenderer != null)
        {
            childRenderer.enabled = true;
        }

        // Wait for the object to remain visible for the specified duration
        yield return new WaitForSeconds(displayDuration);

        // Disable the Mesh Renderer again (make the child object invisible)
        if (childRenderer != null)
        {
            childRenderer.enabled = false;
        }

        // Optional: disable the collider if you want this to happen only once
        // GetComponent<Collider>().enabled = false;
    }
}
