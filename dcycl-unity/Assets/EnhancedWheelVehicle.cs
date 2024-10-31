using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class EnhancedWheelVehicle : MonoBehaviour, IVehicle {
    public PlayerAvatar playerAvatar;

    [Header("Inputs")]
    [SerializeField] bool isPlayer = true;
    public bool IsPlayer { get { return isPlayer; } set { isPlayer = value; } }

    [SerializeField] string throttleInput = "Vertical";
    [SerializeField] string brakeInput = "Brake";
    [SerializeField] string turnInput = "Horizontal";
    [SerializeField] string blinkersLeftInput = "blinker_left";
    [SerializeField] string blinkersRightInput = "blinker_right";
    [SerializeField] string blinkersClearInput = "blinker_clear";
    [SerializeField] private float throttleMultiplier = 1.0f;
    [SerializeField] private float brakeForce = 1500.0f;

    [SerializeField] AnimationCurve turnInputCurve = AnimationCurve.Linear(-1.0f, -1.0f, 1.0f, 1.0f);

    [Header("Wheels")]
    [SerializeField] WheelCollider[] driveWheel;
    public WheelCollider[] DriveWheel { get { return driveWheel; } }
    [SerializeField] WheelCollider[] turnWheel;

    public WheelCollider[] TurnWheel { get { return turnWheel; } }

    [Header("Behaviour")]
    [SerializeField] AnimationCurve motorTorque = new AnimationCurve(new Keyframe(0, 200), new Keyframe(50, 300), new Keyframe(200, 0));
    [Range(2, 16)] [SerializeField] float diffGearing = 4.0f;
    public float DiffGearing { get { return diffGearing; } set { diffGearing = value; } }
    [Range(0f, 50.0f)] [SerializeField] float steerAngle = 30.0f;
    public float SteerAngle { get { return steerAngle; } set { steerAngle = Mathf.Clamp(value, 0.0f, 50.0f); } }
    [Range(0.001f, 1.0f)] [SerializeField] float steerSpeed = 0.2f;
    public float SteerSpeed { get { return steerSpeed; } set { steerSpeed = Mathf.Clamp(value, 0.001f, 1.0f); } }

    Vector3 spawnPosition;
    Quaternion spawnRotation;
    [SerializeField] Transform centerOfMass;
    
    // Progressive throttle values
    float throttle;
    float throttleRate = 0.5f; // Rate of throttle increase/decrease

    // Braking
    float braking = 0;

    // Steering properties
    float steering;
    public float Steering { get { return steering; } set { steering = Mathf.Clamp(value, -1f, 1f); } }

    [Header("Steering Wheel Inside Cockpit")]
    [SerializeField] Transform steeringWheel;  // Assign the steering wheel inside the car
    float steeringWheelAngle = 0;
    float steeringWheelMul = -2;

    // Blinkers
    [SerializeField] CarBlinkers blinkers;
    
    Rigidbody _rb;
    WheelCollider[] wheels;

    // Interface-required properties
    private bool handbrake = false;
    public bool Handbrake { get { return handbrake; } set { handbrake = value; } }
    public float Speed => _rb ? _rb.velocity.magnitude * 3.6f : 0; // Speed in km/h

    void Start() {
        _rb = GetComponent<Rigidbody>();
        spawnPosition = transform.position;
        spawnRotation = transform.rotation;

        if (_rb != null && centerOfMass != null)
        {
            _rb.centerOfMass = centerOfMass.localPosition;
        }

        wheels = GetComponentsInChildren<WheelCollider>();
        foreach (WheelCollider wheel in wheels)
        {
            wheel.motorTorque = 0.0001f; // Start with a very small torque
        }
    }

    void Update()
    {
        HandleInputs();
    }

    void HandleInputs() {
        // Smooth throttle increase only when pressing the throttle key
        if (Input.GetAxis(throttleInput) > 0) {
            throttle = Mathf.Clamp(throttle + throttleRate * Time.deltaTime, 0, 1);
        } else {
            throttle = 0; // Reset throttle if not pressing the throttle key
        }

        // Braking if pressing the brake key
        braking = Input.GetButton(brakeInput) ? brakeForce : 0;

        // Adjust steering
        steering = turnInputCurve.Evaluate(Input.GetAxis(turnInput)) * steerAngle;

        // Toggle blinkers
        if (Input.GetButtonDown(blinkersLeftInput)) {
            if (blinkers.State != BlinkerState.Left) {
                blinkers.StartLeftBlinkers();
            } else {
                blinkers.Stop();
            }
        }
        else if (Input.GetButtonDown(blinkersRightInput)) {
            if (blinkers.State != BlinkerState.Right) {
                blinkers.StartRightBlinkers();
            } else {
                blinkers.Stop();
            }
        }
        else if (Input.GetButtonDown(blinkersClearInput)) {
            blinkers.Stop();
        }
    }

    void FixedUpdate() {
        // Apply motor torque based on throttle
        foreach (WheelCollider wheel in driveWheel) {
            wheel.motorTorque = throttle * throttleMultiplier * motorTorque.Evaluate(Speed) * diffGearing / driveWheel.Length;
        }

        // Apply braking force to all wheels
        foreach (WheelCollider wheel in wheels) {
            wheel.brakeTorque = braking;
        }

        // Apply steering to wheels
        foreach (WheelCollider wheel in turnWheel) {
            wheel.steerAngle = Mathf.Lerp(wheel.steerAngle, steering, steerSpeed);
        }

        // Adjust the steering wheel rotation inside the cockpit
        if (steeringWheel != null) {
            steeringWheelAngle = Mathf.Lerp(steeringWheelAngle, steering * steeringWheelMul, steerSpeed);
            steeringWheel.localRotation = Quaternion.AngleAxis(steeringWheelAngle, Vector3.forward);
        }
    }
}
