// Select the button on the page by its class name or other attributes
const buttonGenerateSchedules = document.querySelector('.generate-schedules-btn');

// Log to see if the button is correctly found
if (buttonGenerateSchedules) {
  console.log('Button found! Adding click event listener...');
  buttonGenerateSchedules.addEventListener('click', () => {
    console.log('Button clicked!'); // Log when the button is clicked

    // Send the message to background or service worker
    chrome.runtime.sendMessage({ action: 'openSidePanel' }, (response) => {
      if (chrome.runtime.lastError) {
        console.error('Error sending message:', chrome.runtime.lastError);
      } else {
        console.log('Response from background:', response); // Log the response from the background
      }
    });
  });
} else {
  console.log('Button not found!'); // Log if the button is not found
}


// This will execute in the context of the page
function extractCourseDataFromPage() {
  const courses = [];
  const courseItems = document.querySelectorAll('.course-item');  // Adjust selector

  courseItems.forEach(item => {
    const className = item.querySelector('.class-name').innerText;
    const classDetails = item.querySelector('.class-details').innerText;
    courses.push({ className, classDetails });
  });

  return courses;
}

// Send the data back to the popup.js for display
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "getCourses") {
    const courses = extractCourseDataFromPage();
    sendResponse(courses);
  }
});
