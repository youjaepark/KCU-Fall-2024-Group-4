// Wait until the DOM is fully loaded
document.addEventListener('DOMContentLoaded', async function () {
    try {
      getCourseData(); // Function to fetch and display course data

      const receivedTableData = {
        schedule: {
          "1": {
            course: {
              name: "INTER-LS 145",
              credit: "1.00",
              description: "How to Succeed in College",
              cumulativeGpa: "3.83",
              url: "https://example.com/course-145",
            },
            time: {
              LEC: "Online",
              DIS: "None",
            },
            instructor: {
              name: "Leonora Neville",
              "instructor Rating": "4.4",
              url: "https://example.com/course-167",
            },
          },
          "2": {
            course: {
              name: "ED POL 140",
              credit: "3.00",
              description: "Introduction to Education",
              cumulativeGpa: "3.64",
              url: "https://example.com/course-140",
            },
            time: {
              LEC: "MW 11:00 AM–11:50 AM",
              DIS: "F 9:55 AM–10:45 AM",
            },
            instructor: {
              name: "Matthew",
              "instructor Rating": "None",
              url: "onono",
            },
          },
        },
      };
  
      console.log("Fetching API data...");
      await fetchScoreAPI();
      console.log("API data fetched successfully");
  
      const tableContent = formatTable(receivedTableData);

      fillTable(tableContent);
      console.log("Table filled successfully");
  
    } catch(error) {
      console.error("Error during initialization:", error);
    }
  });
  
  async function fetchScoreAPI() {
    const apiURL = "http://127.0.0.1:5000/evaluate";
    try {
      console.log("Calling API...");
      const response = await fetch(apiURL, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          "schedule": {
            "1": {
              "course": {
                "name": "INTER-LS 145",
                "credit": "1.00",
                "description": "How to Succeed in College",
                "cumulativeGpa": "2.7"
              },
              "time": {
                "LEC": "Online",
                "DIS": "None"
              },
              "instructor": {
                "name": "Leonora Neville",
                "instructor Rating": "1.4"
              }
            },
            "2": {
              "course": {
                "name": "ED POL 140",
                "credit": "3.00",
                "description": "Introduction to Education",
                "cumulativeGpa": "1.64"
              },
              "time": {
                "LEC": "MW 11:00 AM–11:50 AM",
                "DIS": "F 9:55 AM–10:45 AM"
              },
              "instructor": {
                "name": "None",
                "instructorRating": "None"
              }
            },
            "3": {
              "course": {
                "name": "ENGL 100",
                "credit": "3.00",
                "description": "Introduction to College Composition",
                "cumulativeGpa": "3.76"
              },
              "time": {
                "LEC": "MW 2:30 PM–3:45 PM",
                "DIS": "None"
              },
              "instructor": {
                "name": "Vatcharit Chantajinda",
                "instructorRating": "None"
              }
            },
            "4": {
              "course": {
                "name": "ANTHRO 104",
                "credit": "3.00",
                "description": "Cultural Anthropology and Human Diversity",
                "cumulativeGpa": "40.2%"
              },
              "time": {
                "LEC": "TR 11:00 AM–11:50 AM",
                "DIS": "R 12:05 PM–12:55 PM"
              },
              "instructor": {
                "name": "Claire Wendland",
                "instructorRating": "3.3"
              }
            },
            "5": {
              "course": {
                "name": "MATH 375",
                "credit": "5.00",
                "description": "Topics in Multi-Variable Calculus and Linear Algebra",
                "cumulativeGpa": "3.43"
              },
              "time": {
                "LEC": "TR 9:30 AM–10:45 AM",
                "DIS": "MW 12:05 PM–12:55 PM"
              },
              "instructor": {
                "name": "Caglar Uyanik",
                "instructorRating": "3"
              }
            },
            "6": {
              "course": {
                "name": "COMP SCI 300",
                "credit": "3.00",
                "description": "Programming II",
                "cumulativeGpa": "3.52"
              },
              "time": {
                "LEC": "MWF 1:20 PM–2:10 PM",
                "DIS": "None"
              },
              "instructor": {
                "name": "Hobbes Legault",
                "instructorRating": "2.6"
              }
            }
          }
        }),
      });
  
      if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
      }
  
      const data = await response.json();
      console.log("API response data:", data);
  
      // for scores
      const comment = data.comment;
      const courseScore = parseInt(data.course) * 10;
      const instructorScore = parseInt(data.instructor) * 10;
      const scheduleBalance = parseInt(data["schedule balance"]) * 10;
      const overallScore = parseInt(data.overall) * 10;
  
      updateScores(overallScore, courseScore, instructorScore, scheduleBalance, comment);
  
    } catch(error) {
      console.error("Failed to fetch API data:", error);
    }
  }
  
  function updateScores(newScorePercent, newCourseScore, newInstructorScore, newScheduleBalance, newComment) {
    const scorePercentVal = document.getElementById("scorePercent");
    const courseScoreVal = document.getElementById("courseScore");
    const instructorScoreVal = document.getElementById("instructorScore");
    const scheduleBalanceVal = document.getElementById("scheduleBalance");
    const commentPar = document.getElementById("commentParagraph");
  
    scorePercentVal.innerHTML = "";
    courseScoreVal.innerHTML = "";
    instructorScoreVal.innerHTML = "";
    scheduleBalanceVal.innerHTML = "";
    commentPar.innerHTML = "";
  
    scorePercentVal.textContent = newScorePercent;
    courseScoreVal.textContent = newCourseScore;
    instructorScoreVal.textContent = newInstructorScore;
    scheduleBalanceVal.textContent = newScheduleBalance;
    commentPar.textContent = newComment;
  
    const circle = document.querySelector(".percent svg circle:nth-child(2)");
    const newDashOffset = 440 - (440 * newScorePercent) / 100;
  
    circle.style.strokeDashoffset = newDashOffset;
  }

  function formatTable(tableData) {
    const tableContent = [];
    for (const key in tableData.schedule) {
        const entry = tableData.schedule[key];
        tableContent.push({
            courseName: entry.course.name,
            gpa: entry.course.cumulativeGpa,
            courseUrl: entry.course.url,
            instructorRating: entry.instructor["instructor Rating"],
            instructorUrl: entry.instructor.url,
        });
    }
    return tableContent;
  }
  
  function fillTable(tableContent) {
    const tableBody = document.getElementById("courseTableBody");
    tableBody.innerHTML = "";
  
    tableContent.forEach((course) => {
        const row = document.createElement("tr");
  
        const courseNameCell = document.createElement("td");
        courseNameCell.textContent = course.courseName;
  
        const gpaCell = document.createElement("td");
        const gpaLink = document.createElement("a");
        gpaLink.textContent = course.gpa;
        gpaLink.href = course.courseUrl;
        gpaLink.target = "_blank";
        gpaCell.appendChild(gpaLink);
  
        const ratingCell = document.createElement("td");

        if (course.instructorRating !== "None" && course.instructorUrl) {
          const ratingLink = document.createElement("a");
          ratingLink.textContent = course.instructorRating;
          ratingLink.href = course.instructorUrl;
          ratingLink.target = "_blank";
          ratingCell.appendChild(ratingLink)
        } else {
          ratingCell.textContent = course.instructorRating;
        }
        
        row.appendChild(courseNameCell);
        row.appendChild(gpaCell);
        row.appendChild(ratingCell);
  
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
