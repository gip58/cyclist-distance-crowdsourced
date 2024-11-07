using UnityEngine;
using UnityEngine.UI;
using System.Collections;

public class CarControlTransition : MonoBehaviour
{
    public Text countdownText;
    public float countdownTime = 3f; // Time for countdown in seconds
    public WheelVehicle carScript; // Reference to the WheelVehicle script

    private void Start()
    {
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
        countdownText.gameObject.SetActive(false);

        carScript.IsPlayer = true; // Enable player control after countdown
    }
}
