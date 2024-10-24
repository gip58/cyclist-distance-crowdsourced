using UnityEngine;
using PathCreation;

public class CyclistFollowPath : MonoBehaviour
{
    public PathCreator pathCreator;
    public EndOfPathInstruction end;
    public float speed;
    float dstTravelled;

    void Update()
    {
        dstTravelled += speed * Time.deltaTime;
        transform.position = pathCreator.path.GetPointAtDistance(dstTravelled, end);

        // Get the rotation from the path
        Quaternion pathRotation = pathCreator.path.GetRotationAtDistance(dstTravelled, end);

        // Apply the rotation correction if necessary (assuming cyclist's forward axis is Z)
        transform.rotation = pathRotation * Quaternion.Euler(0, 90, 0); // Adjust the angle if necessary
    }
}
