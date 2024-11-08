using System.Collections;
using UnityEngine;

public class SetActiveOnOff : MonoBehaviour
{
    private MeshRenderer childRenderer;

    // Time in seconds after which the object should appear
    [SerializeField] private float timeToAppear = 5.0f;
    [SerializeField] private float visibleDuration = 3.0f;

    // Use this for initialization
    void Start()
    {
        // Get the Mesh Renderer from the child object
        childRenderer = GetComponentInChildren<MeshRenderer>();

        // Ensure the child object is invisible at the start
        if (childRenderer != null)
        {
            childRenderer.enabled = false;
        }

        // Start the coroutine to make the child object appear and disappear
        StartCoroutine(ShowAndHideObject());
    }

    private IEnumerator ShowAndHideObject()
    {
        // Wait for the specified time before showing the child object
        yield return new WaitForSeconds(timeToAppear);

        // Enable the Mesh Renderer on the child object (make it visible)
        if (childRenderer != null)
        {
            childRenderer.enabled = true;
        }

        // Wait for the object to remain visible for the specified duration
        yield return new WaitForSeconds(visibleDuration);

        // Disable the Mesh Renderer again (make the child object invisible)
        if (childRenderer != null)
        {
            childRenderer.enabled = false;
        }
    }
}
