using System.Collections;
using System.Collections.Generic;
using UnityEngine;

#if MULTIOSCONTROLS
    using MOSC;
#endif

public interface IVehicle
{
    bool Handbrake { get; }
    float Speed { get; }
}

namespace VehicleBehaviour {
    [RequireComponent(typeof(Rigidbody))]
    public class CarVehicle : MonoBehaviour, IVehicle {
        public PlayerAvatar playerAvatar;
        public bool countdownActive = false;

        [Header("Inputs")]
    #if MULTIOSCONTROLS
        [SerializeField] PlayerNumber playerId;
    #endif
        [SerializeField] bool isPlayer = true;
        public bool IsPlayer { get { return isPlayer; } set { isPlayer = value; } }

        [SerializeField] string throttleInput = "Throttle";
        [SerializeField] string brakeInput = "Brake";
        [SerializeField] string turnInput = "Horizontal";
        [SerializeField] string jumpInput = "Jump";
        [SerializeField] string driftInput = "Drift";
        [SerializeField] string boostInput = "Boost";

        public Transform steeringWheel;
        public float steeringWheelMul = -2;
        private float steeringWheelAngle = 0;

        [SerializeField] string blinkersLeftInput = "blinker_left";
        [SerializeField] string blinkersRightInput = "blinker_right";
        [SerializeField] string blinkersClearInput = "blinker_clear";

        [SerializeField] AnimationCurve turnInputCurve = AnimationCurve.Linear(-1.0f, -1.0f, 1.0f, 1.0f);

        [Header("Wheels")]
        [SerializeField] WheelCollider[] driveWheel;
        public WheelCollider[] DriveWheel { get { return driveWheel; } }
        [SerializeField] WheelCollider[] turnWheel;
        public WheelCollider[] TurnWheel { get { return turnWheel; } }

        bool isGrounded = false;
        int lastGroundCheck = 0;
        public bool IsGrounded {
            get {
                if (lastGroundCheck == Time.frameCount)
                    return isGrounded;

                lastGroundCheck = Time.frameCount;
                isGrounded = true;
                foreach (WheelCollider wheel in wheels)
                {
                    if (!wheel.gameObject.activeSelf || !wheel.isGrounded)
                        isGrounded = false;
                }
                return isGrounded;
            }
        }

        [Header("Behaviour")]
        [SerializeField] AnimationCurve motorTorque = new AnimationCurve(new Keyframe(0, 200), new Keyframe(50, 300), new Keyframe(200, 0));
        [SerializeField] AnimationCurve deaccelerateMotorTorque = new AnimationCurve(new Keyframe(0, 400), new Keyframe(200, 600));

        [Range(2, 16)]
        [SerializeField] float diffGearing = 4.0f;
        public float DiffGearing { get { return diffGearing; } set { diffGearing = value; } }

        [SerializeField] float brakeForce = 1500.0f;
        public float BrakeForce { get { return brakeForce; } set { brakeForce = value; } }

        [Range(0f, 50.0f)]
        [SerializeField] float steerAngle = 30.0f;
        public float SteerAngle { get { return steerAngle; } set { steerAngle = Mathf.Clamp(value, 0.0f, 50.0f); } }

        [Range(0.001f, 1.0f)]
        [SerializeField] float steerSpeed = 0.2f;
        public float SteerSpeed { get { return steerSpeed; } set { steerSpeed = Mathf.Clamp(value, 0.001f, 1.0f); } }

        [Range(1f, 1.5f)]
        [SerializeField] float jumpVel = 1.3f;
        public float JumpVel { get { return jumpVel; } set { jumpVel = Mathf.Clamp(value, 1.0f, 1.5f); } }

        [Range(0.0f, 2f)]
        [SerializeField] float driftIntensity = 1f;
        public float DriftIntensity { get { return driftIntensity; } set { driftIntensity = Mathf.Clamp(value, 0.0f, 2.0f); }}

        Vector3 spawnPosition;
        Quaternion spawnRotation;

        [SerializeField] Transform centerOfMass;

        [Range(0.5f, 10f)]
        [SerializeField] float downforce = 1.0f;
        public float Downforce { get { return downforce; } set { downforce = Mathf.Clamp(value, 0, 5); } }

        float steering;
        public float Steering { get { return steering; } set { steering = Mathf.Clamp(value, -1f, 1f); } }

        float throttle;
        public float Throttle { get { return throttle; } set { throttle = Mathf.Clamp(value, -1f, 1f); } }

        [SerializeField] bool handbrake;
        public bool Handbrake { get { return handbrake; } set { handbrake = value; } }
        
        [HideInInspector] public bool allowDrift = true;
        bool drift;
        public bool Drift { get { return drift; } set { drift = value; } }

        [SerializeField] float speed = 0.0f;
        public float Speed { get { return speed; } }

        [Header("Particles")]
        [SerializeField] ParticleSystem[] gasParticles;

        [Header("Boost")]
        [HideInInspector] public bool allowBoost = true;
        [SerializeField] float maxBoost = 10f;
        public float MaxBoost { get { return maxBoost; } set { maxBoost = value; } }

        [SerializeField] float boost = 10f;
        public float Boost { get { return boost; } set { boost = Mathf.Clamp(value, 0f, maxBoost); } }

        [Range(0f, 1f)]
        [SerializeField] float boostRegen = 0.2f;
        public float BoostRegen { get { return boostRegen; } set { boostRegen = Mathf.Clamp01(value); } }

        [SerializeField] float boostForce = 5000;
        public float BoostForce { get { return boostForce; } set { boostForce = value; } }

        public bool boosting = false;

        public float breaking;
        public bool jumping = false;

        [SerializeField] ParticleSystem[] boostParticles;
        [SerializeField] AudioClip boostClip;
        [SerializeField] AudioSource boostSource;
        [SerializeField] CarBlinkers blinkers;

        Rigidbody _rb;
        WheelCollider[] wheels;

        void Start() {
    #if MULTIOSCONTROLS
            Debug.Log("[ACP] Using MultiOSControls");
    #endif
            if (boostClip != null) {
                boostSource.clip = boostClip;
            }

            boost = maxBoost;

            _rb = GetComponent<Rigidbody>();
            spawnPosition = transform.position;
            spawnRotation = transform.rotation;

            if (_rb != null && centerOfMass != null) {
                _rb.centerOfMass = centerOfMass.localPosition;
            }

            wheels = GetComponentsInChildren<WheelCollider>();

            foreach (WheelCollider wheel in wheels) {
                wheel.motorTorque = 0.0001f;
            }
        }

        bool reverse = false;

        void Update() {
            foreach (ParticleSystem gasParticle in gasParticles) {
                gasParticle.Play();
                ParticleSystem.EmissionModule em = gasParticle.emission;
                em.rateOverTime = handbrake ? 0 : Mathf.Lerp(em.rateOverTime.constant, Mathf.Clamp(150.0f * throttle, 30.0f, 100.0f), 0.1f);
            }

            if (isPlayer && allowBoost) {
                boost += Time.deltaTime * boostRegen;
                if (boost > maxBoost) { boost = maxBoost; }
            }
        }

        void FixedUpdate() {
            speed = transform.InverseTransformDirection(_rb.velocity).z * 3.6f;

            if (countdownActive) {
                Vector3 forwardMovement = transform.forward * (30f / 3.6f);
                _rb.velocity = new Vector3(0, _rb.velocity.y, forwardMovement.z);
                steering = 0;
                breaking = 0;
            } else if (isPlayer) {
                throttle = GetInput(throttleInput) * (reverse ? -1f : 1);
                breaking = Mathf.Clamp01(GetInput(brakeInput));
                steering = turnInputCurve.Evaluate(GetInput(turnInput)) * steerAngle;
            }

            steeringWheelAngle = Mathf.Lerp(steeringWheelAngle, steering * steeringWheelMul, steerSpeed);
            if (steeringWheel != null) {
                steeringWheel.localRotation = Quaternion.AngleAxis(steeringWheelAngle, Vector3.forward);
            }

            if (!countdownActive) {
                foreach (WheelCollider wheel in driveWheel) {
                    wheel.motorTorque = throttle * motorTorque.Evaluate(speed) * diffGearing / driveWheel.Length;
                }

                foreach (WheelCollider wheel in turnWheel) {
                    wheel.steerAngle = steering;
                }

                foreach (WheelCollider wheel in wheels) {
                    wheel.brakeTorque = Mathf.Abs(breaking) * brakeForce;
                }
            }
        }

        public void ResetPos() {
            transform.position = spawnPosition;
            transform.rotation = spawnRotation;
            _rb.velocity = Vector3.zero;
            _rb.angularVelocity = Vector3.zero;
        }

        public void toogleHandbrake(bool h) {
            handbrake = h;
        }

#if MULTIOSCONTROLS
        private static MultiOSControls _controls;
#endif

        private float GetInput(string input) {
#if MULTIOSCONTROLS
            return MultiOSControls.GetValue(input, playerId);
#else
            return Input.GetAxis(input);
#endif
        }
    }
}
