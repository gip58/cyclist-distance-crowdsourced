using UnityEngine;
using UnityEngine.UI;
using System.Collections;

public class CountdownTimer : MonoBehaviour
{
    public Text countdownText;  // Link this in the Inspector
    public int countdownTime = 3;  // Set the starting countdown number

    public MonoBehaviour carController;  // Drag the car's movement script here
    public MonoBehaviour cyclistController;  // Drag the cyclist's movement script here

    private void Start()
    {
        // Disable functionality of car and cyclist at the start
        if (carController != null) carController.enabled = false;
        if (cyclistController != null) cyclistController.enabled = false;

        StartCoroutine(StartCountdown());
    }

    private IEnumerator StartCountdown()
    {
        // Loop to decrease the countdown each second
        while (countdownTime > 0)
        {
            countdownText.text = countdownTime.ToString();  // Update the UI
            yield return new WaitForSeconds(1);  // Wait for a second
            countdownTime--;  // Decrease the countdown
        }

        countdownText.text = "Go!";  // Display "Go!" at the end
        yield return new WaitForSeconds(1);  // Keep "Go!" on screen briefly
        countdownText.gameObject.SetActive(false);  // Hide the text after countdown

        EnableCarAndCyclist();  // Enable functionality
    }

    private void EnableCarAndCyclist()
    {
        // Enable the movement functionality of the car and cyclist
        if (carController != null) carController.enabled = true;
        if (cyclistController != null) cyclistController.enabled = true;
    }
}
