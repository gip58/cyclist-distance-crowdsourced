using UnityEngine;
using PathCreation;

public class PathFollower : MonoBehaviour
{
    public PathCreator pathCreator;
    public EndOfPathInstruction end;
    public float speed;
    private float dstTravelled;

    private Rigidbody rb;

    void Start()
    {
        rb = GetComponent<Rigidbody>();  // Get the Rigidbody component
    }

    void FixedUpdate()
    {
        Vector3 targetPosition = pathCreator.path.GetPointAtDistance(dstTravelled, end);
        Quaternion targetRotation = pathCreator.path.GetRotationAtDistance(dstTravelled, end);

        // Calculate the velocity needed to move to the next point
        Vector3 direction = (targetPosition - transform.position).normalized;
        float distance = Vector3.Distance(transform.position, targetPosition);

        // Set Rigidbody velocity based on the desired speed and direction
        rb.velocity = direction * speed;

        // Smoothly rotate towards the target rotation
        rb.MoveRotation(Quaternion.Slerp(rb.rotation, targetRotation, Time.fixedDeltaTime * 5f));

        // Update distance travelled
        dstTravelled += speed * Time.fixedDeltaTime;
    }
}
