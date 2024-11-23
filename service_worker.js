const GOOGLE_ORIGIN = 'https://enroll.wisc.edu';

// Allows users to open the side panel by clicking on the action toolbar icon
chrome.sidePanel
  .setPanelBehavior({ openPanelOnActionClick: true })
  .catch((error) => console.error(error));

  chrome.tabs.onUpdated.addListener(async (tabId, info, tab) => {
    if (!tab.url) return;
    const url = new URL(tab.url);
    // Enables the side panel on google.com
    if (url.origin === GOOGLE_ORIGIN) {
      await chrome.sidePanel.setOptions({
        tabId,
        path:'rateMySchedule.html',
        enabled: true
      });
    } else {
      // Disables the side panel on all other sites
      await chrome.sidePanel.setOptions({
        tabId,
        enabled: false
      });
    }
  });



chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log("Received message:", message);
  const currentTab = sender.tab;
  if (message.action === 'openSidePanel') {
    console.log('Attempting to open the side panel...');
    chrome.sidePanel.open({tabId: currentTab.id});

    if (chrome.sidePanel) {
      console.log("Side Panel API is available.");
      
      chrome.sidePanel.setOptions({
        path: 'rateMySchedule.html',  // Path to your side panel HTML
        enabled: true
      }, (result) => {
        if (chrome.runtime.lastError) {
          console.error('Error enabling side panel:', chrome.runtime.lastError);
        } else {
          console.log('Side panel opened successfully:', result);
        }
      });
    } else {
      console.error("Side Panel API is not available.");
    }

    sendResponse({ status: 'success', message: 'Side panel opened' });
  } else {
    console.log('Unknown action:', message.action);
  }
});

// Fetch course data when the side panel is visible
async function getCourseData(tabId) {
  return new Promise((resolve, reject) => {
    chrome.scripting.executeScript(
      {
        target: { tabId: tabId },
        func: extractCourseData
      },
      (result) => {
        if (chrome.runtime.lastError) {
          reject(new Error(chrome.runtime.lastError));
        } else {
          resolve(result[0].result);
        }
      }
    );
  });
}

// Extract course data from the page
function extractCourseData() {   
  const courses = [];
  
  // Modify the selector based on the structure of the website you're scraping
  const courseElements = document.querySelectorAll('.course-item'); 
  courseElements.forEach(courseElement => {
    const course = {
      id: courseElement.querySelector('.course-id').innerText,  // Adjust selector
      name: courseElement.querySelector('.course-name').innerText,  // Adjust selector
      credits: courseElement.querySelector('.course-credits').innerText,  // Adjust selector
      schedule: courseElement.querySelector('.course-schedule').innerText  // Adjust selector
    };
    courses.push(course);
  });
  
  return courses;
}

// Listen for a request to populate the side panel with course data
chrome.runtime.onMessage.addListener(async (message, sender, sendResponse) => {
  if (message.action === 'fetchCourses') {
    const courseData = await getCourseData(sender.tab.id);
    sendResponse({ status: 'success', courseData: courseData });
  }
});
