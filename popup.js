// Wait until the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function () {
    getCourseData(); // Function to fetch and display course data
    // Sample course data (to be replaced w/ backend)
    const tableContent = [
      {
          courseName: "STAT 309",
          madgrades: "3.22",
          rateMyProfessor: "1.9/5",
      },
      {
          courseName: "COMP SCI 400",
          madgrades: "3.32",
          rateMyProfessor: "3.5/5",
      },
      {
          courseName: "COMP SCI 354",
          madgrades: "3.10",
          rateMyProfessor: "4.2/5",
      },
      {
        courseName: "STAT 424",
        madgrades: "3.43",
        rateMyProfessor: "3.2/5",
      }
  ];

    updateScores(78, 85, 91, 90);
    fillTable(tableContent);
  });

  function updateScores(newScorePercent, newCourseScore, newInstructorScore, newScheduleBalance) {
    const scorePercentVal = document.getElementById("scorePercent");
    const courseScoreVal = document.getElementById("courseScore");
    const instructorScoreVal = document.getElementById("instructorScore");
    const scheduleBalanceVal = document.getElementById("scheduleBalance");

    scorePercentVal.innerHTML = "";
    courseScoreVal.innerHTML = "";
    instructorScoreVal.innerHTML = "";
    scheduleBalanceVal.innerHTML = "";

    scorePercentVal.textContent = newScorePercent;
    courseScoreVal.textContent = newCourseScore;
    instructorScoreVal.textContent = newInstructorScore;
    scheduleBalanceVal.textContent = newScheduleBalance;

    const circle = document.querySelector(".percent svg circle:nth-child(2)");
    const newDashOffset = 440 - (440 * newScorePercent) / 100;

    circle.style.strokeDashoffset = newDashOffset;
  }

  function fillTable(tableContent) {
    const tableBody = document.getElementById("courseTableBody");
    tableBody.innerHTML = "";

    tableContent.forEach((course) => {
        const row = document.createElement("tr");

        const courseNameCell = document.createElement("td");
        courseNameCell.textContent = course.courseName;

        const madgradesCell = document.createElement("td");
        madgradesCell.textContent = course.madgrades;

        const rmfCell = document.createElement("td");
        rmfCell.textContent = course.rateMyProfessor;

        row.appendChild(courseNameCell);
        row.appendChild(madgradesCell);
        row.appendChild(rmfCell);

        tableBody.appendChild(row);
    });
  }
  
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
