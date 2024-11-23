// popup.js

document.addEventListener("DOMContentLoaded", () => {
  // Add a click event listener to the button with ID 'findElement'
  document.getElementById("findElement").addEventListener("click", async () => {
    try {
      // Get the active tab in the current window
      const [tab] = await chrome.tabs.query({
        active: true,
        currentWindow: true,
      });

      // Inject 'content-script.js' into the active tab
      await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ["content-script.js"],
      });

      // Send a message to the content script to execute 'findElements'
      chrome.tabs.sendMessage(
        tab.id,
        { action: "findElements" },
        (response) => {
          const resultDiv = document.getElementById("result");
          if (chrome.runtime.lastError) {
            // Handle errors during message passing
            resultDiv.innerHTML =
              "An error occurred: " + chrome.runtime.lastError.message;
          } else if (response && response.result) {
            // Display the result returned from the content script
            resultDiv.innerHTML = response.result;
          } else if (response && response.error) {
            // Display any errors returned from the content script
            resultDiv.innerHTML = "Error: " + response.error;
          } else {
            // Handle the case where no result or error is returned
            resultDiv.innerHTML = "No elements found";
          }
        }
      );
    } catch (error) {
      // Handle any unexpected errors
      document.getElementById("result").innerHTML =
        "An error occurred: " + error.message;
    }
  });
});
