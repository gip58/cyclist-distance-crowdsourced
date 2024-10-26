using UnityEngine;
using System.Collections;
using System.Collections.Generic;

public class CarController : MonoBehaviour
{
    public List<Transform> waypoints; // List of waypoints the car will follow
    public float speed = 10f;
    public float waypointThreshold = 2f; // How close the car needs to be to consider reaching the waypoint
    public float rotationSpeed = 5f; // How fast the car rotates to face the direction of movement
    public float overtakingSpeedBoost = 1.5f; // Multiplier for speed during overtaking
    public float overtakingLaneOffset = 3f; // Horizontal shift for overtaking

    private int currentWaypointIndex = 0;
    private bool isOvertaking = false;
    private Vector3 originalLanePosition;

    void Start()
    {
        // Set the original lane position (this will be used to return after overtaking)
        originalLanePosition = transform.position;
    }

    void Update()
    {
        // Move towards the next waypoint
        MoveAlongPath();
    }

    // Function to move along the waypoints
    void MoveAlongPath()
    {
        if (currentWaypointIndex >= waypoints.Count) return;

        // Get the target waypoint
        Transform targetWaypoint = waypoints[currentWaypointIndex];
        Vector3 direction = (targetWaypoint.position - transform.position).normalized;
        float currentSpeed = speed;

        // If overtaking, adjust the speed and lateral movement
        if (isOvertaking)
        {
            currentSpeed *= overtakingSpeedBoost;
            direction.x += overtakingLaneOffset; // Shift the car to overtake
        }

        // Smoothly rotate the car to face the direction of movement
        Quaternion targetRotation = Quaternion.LookRotation(direction);
        transform.rotation = Quaternion.Slerp(transform.rotation, targetRotation, rotationSpeed * Time.deltaTime);

        // Move the car forward in the direction it's facing
        transform.Translate(Vector3.forward * currentSpeed * Time.deltaTime);

        // Check if the car is close enough to the current waypoint
        if (Vector3.Distance(transform.position, targetWaypoint.position) < waypointThreshold)
        {
            currentWaypointIndex++; // Move to the next waypoint
        }
    }

    // Trigger detection for the cyclist
    void OnTriggerEnter(Collider other)
    {
        // Check if the car has entered a trigger and the object is the cyclist
        if (other.gameObject.CompareTag("Cyclist"))
        {
            // Start overtaking when the cyclist is detected
            StartCoroutine(OvertakeCyclist());
        }
    }

    // Coroutine to handle the overtaking process
    IEnumerator OvertakeCyclist()
    {
        isOvertaking = true;

        // Move to the overtaking lane
        Vector3 overtakingPosition = transform.position + new Vector3(overtakingLaneOffset, 0, 0);
        while (Vector3.Distance(transform.position, overtakingPosition) > 0.1f)
        {
            transform.position = Vector3.Lerp(transform.position, overtakingPosition, Time.deltaTime * speed);
            yield return null;
        }

        // Continue overtaking for a set duration
        yield return new WaitForSeconds(2f); // Adjust this based on how long the overtake should take

        // Return to the original lane
        while (Vector3.Distance(transform.position, originalLanePosition) > 0.1f)
        {
            transform.position = Vector3.Lerp(transform.position, originalLanePosition, Time.deltaTime * speed);
            yield return null;
        }

        // Reset overtaking flag
        isOvertaking = false;
    }
}
