
/*
 * This code is part of Arcade Car Physics for Unity by Saarg (2018)
 * 
 * This is distributed under the MIT Licence (see LICENSE.md for details)
 */
using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

#if MULTIOSCONTROLS
    using MOSC;
#endif

namespace VehicleBehaviour {
    [RequireComponent(typeof(Rigidbody))]
    public class WheelVehicleNoClamp : MonoBehaviour, IVehicle {
        public PlayerAvatar playerAvatar;

        [Header("Inputs")]
    #if MULTIOSCONTROLS
        [SerializeField] PlayerNumber playerId;
    #endif
        [SerializeField] bool isPlayer = true;
        public bool IsPlayer { get { return isPlayer; } set { isPlayer = value; } }

        [SerializeField] string throttleInput = "Vertical";
        [SerializeField] string brakeInput = "Jump"; // Changed from "Brake" to "Jump" to avoid missing input axis
        [SerializeField] string turnInput = "Horizontal";
        [SerializeField] string jumpInput = "Jump";
        [SerializeField] string driftInput = "Drift";

        [Header("Vehicle Settings")]
        [SerializeField] float motorTorque = 1500f;
        [SerializeField] float brakeForce = 3000f;
        [SerializeField] float maxSteerAngle = 30f;

        [Header("Wheels")]
        public WheelCollider[] driveWheels;
        public WheelCollider[] steerWheels;

        Rigidbody rb;
        float throttle;
        float steer;
        float brake;

        void Start() {
            rb = GetComponent<Rigidbody>();
            // Use existing center of mass for better stability
            rb.centerOfMass = new Vector3(0, -0.9f, 0); // Adjust as needed
        }

        void Update() {
            throttle = Input.GetAxis(throttleInput);
            steer = Input.GetAxis(turnInput);
            brake = Input.GetAxis(brakeInput);
            Debug.Log("Current Speed: " + Speed.ToString("F2") + " km/h, Throttle Input: " + throttle.ToString("F2") + ", Steering Input: " + steer.ToString("F2"));

        }

        void FixedUpdate() {
            ApplyThrottle();
            ApplySteering();
            ApplyBrakes();
        }

        void ApplyThrottle() {
            foreach (WheelCollider wheel in driveWheels) {
                wheel.motorTorque = throttle * motorTorque;
            }
        }

        void ApplySteering() {
            foreach (WheelCollider wheel in steerWheels) {
                wheel.steerAngle = steer * maxSteerAngle;
            }
        }

        void ApplyBrakes() {
            foreach (WheelCollider wheel in driveWheels) {
                wheel.brakeTorque = brake > 0 ? brake * brakeForce : 0f;
            }
        }

        public float Speed {
            get {
                // Removed Mathf.Clamp to allow unrestricted speed
                return rb.velocity.magnitude * 3.6f; // Convert to km/h
            }
        }

        public bool Handbrake {
            get {
                return brake > 0;
            }
        }
    }
}

