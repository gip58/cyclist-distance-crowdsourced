using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class newsteeringwheel : MonoBehaviour
{
    public Transform steeringWheel;  // The steering wheel object
    public Transform car;            // The car object
    public float maxSteeringAngle = 450f; // Maximum steering wheel rotation (for full lock)
    public float steeringMultiplier = 1.2f; // Factor to exaggerate steering wheel rotation
    public float movementThreshold = 0.1f; // Minimum movement threshold to rotate the steering wheel (increased)
    public float smoothingFactor = 0.05f; // Smoothing factor to control the transition speed
    public float smallAngleThreshold = 1f; // Threshold to round small angles to zero

    private Vector3 previousPosition;  // To track the car's previous position on the path
    private float previousSteeringAngle = 0f; // Store the previous steering angle for smoothing

    private bool initialized = false;  // To check if initial movement is significant

    void Start()
    {
        // Initialize previous position to car's starting position
        previousPosition = car.position;
    }

    void Update()
    {
        // Calculate the direction of the car's movement along the path
        Vector3 movementDirection = (car.position - previousPosition).normalized;

        // Calculate the distance moved by the car in this frame
        float distanceMoved = Vector3.Distance(car.position, previousPosition);

        // Only start adjusting steering once the car has moved a significant distance (ignores small initial movements)
        if (!initialized && distanceMoved > movementThreshold)
        {
            initialized = true;  // Now we consider the car is moving enough to start steering
        }

        if (initialized)
        {
            // Calculate the angle between the car's forward direction and its movement direction
            float angle = Vector3.SignedAngle(car.forward, movementDirection, Vector3.up);

            // Ignore very small angles by rounding them to zero
            if (Mathf.Abs(angle) < smallAngleThreshold)
            {
                angle = 0;
            }

            // Apply smoothing to the steering angle
            float smoothedSteeringAngle = Mathf.Lerp(previousSteeringAngle, angle, smoothingFactor);

            // Amplify the steering wheel rotation by the multiplier
            float steeringWheelRotation = Mathf.Clamp(smoothedSteeringAngle * steeringMultiplier * maxSteeringAngle / 90f, -maxSteeringAngle, maxSteeringAngle);

            // Apply the rotation to the steering wheel on the z-axis
            steeringWheel.localRotation = Quaternion.Euler(0, 0, steeringWheelRotation);

            // Update the previous steering angle for smoothing
            previousSteeringAngle = smoothedSteeringAngle;
        }

        // Update the previous position for the next frame
        previousPosition = car.position;
    }
}
