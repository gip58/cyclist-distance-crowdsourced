using UnityEngine;
using UnityEngine.UI;
using System.Collections;
using VehicleBehaviour;

public class CarControlTransition : MonoBehaviour
{
    public Text countdownText;
    public float countdownTime = 3f; // Time for countdown in seconds
    public CarVehicle carScript; // Reference to the CarVehicle script

    private void Start()
    {
        carScript.countdownActive = true; // Enable countdown mode initially
        carScript.IsPlayer = false; // Disable player control initially
        StartCoroutine(CountdownCoroutine());
    }

    private IEnumerator CountdownCoroutine()
    {
        float time = countdownTime;
        while (time > 0)
        {
            countdownText.text = Mathf.Ceil(time).ToString(); // Show countdown
            yield return new WaitForSeconds(1f);
            time--;
        }

        countdownText.text = "Go!";
        yield return new WaitForSeconds(1f);
        countdownText.gameObject.SetActive(false); // Hide countdown text

        carScript.countdownActive = false; // Disable countdown mode
        carScript.IsPlayer = true; // Enable player control
    }
}
