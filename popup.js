

// Wait until the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function () {
    getCourseData(); // Function to fetch and display course data
  });
  
  // Function to retrieve course data
  async function getCourseData() {
    const courses = await fetchCourseDataFromTab(); // Fetch the courses from the current tab
  
    const courseListElement = document.getElementById('courseList');
    courseListElement.innerHTML = ''; // Clear any existing content
  
    if (courses && courses.length > 0) {
      const ul = document.createElement('ul');
      courses.forEach(course => {
        const li = document.createElement('li');
        li.textContent = `${course.className}: ${course.classDetails}`;
        ul.appendChild(li);
      });
      courseListElement.appendChild(ul);
    } else {
      courseListElement.textContent = 'No courses found.';
    }
  }
  
  // Function to fetch course data from the current tab using chrome.scripting
  async function fetchCourseDataFromTab() {
    return new Promise((resolve, reject) => {
      chrome.scripting.executeScript(
        {
          target: {tabId: chrome.tabs.TAB_ID}, // Make sure to get the current tab ID
          func: extractCourseData  // Function to extract data from the page
        },
        (result) => {
          if (chrome.runtime.lastError) {
            reject(new Error(chrome.runtime.lastError));
          } else {
            resolve(result[0].result);  // Return the extracted course data
          }
        }
      );
    });
  }
  
  // Function to extract course data from the page (scraping)
  function extractCourseData() {
    const courses = [];
    const courseItems = document.querySelectorAll('.course-item');  // Modify this selector based on actual HTML structure
  
    courseItems.forEach(item => {
      const className = item.querySelector('.class-name').innerText;
      const classDetails = item.querySelector('.class-details').innerText;
      courses.push({ className, classDetails });
    });
  
    return courses;
  }
  