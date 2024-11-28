// Reads the schedule from the page
async function readCourseSchedule() {
  try {
    const schedule = {};
    let counter = 1;

    // Get all course wrapper elements
    const courseWrappers = document.querySelectorAll("button.wrapper");
    console.log("Found course wrappers:", courseWrappers.length); // Debug log

    if (courseWrappers.length === 0) {
      throw new Error("No course wrappers found on page");
    }

    for (const wrapper of courseWrappers) {
      // Check if the checkbox is checked
      const checkbox = wrapper.querySelector(
        ".left.checkbox .mat-mdc-checkbox"
      );
      if (!checkbox?.classList.contains("mat-mdc-checkbox-checked")) {
        continue;
      }

      // Get course details
      const courseName =
        wrapper.querySelector(".left.grow.catalog")?.textContent.trim() || "";
      const courseTitle =
        wrapper.querySelector(".row.title .left.grow")?.textContent.trim() ||
        "";
      const creditElement =
        wrapper.querySelector(".right.credits")?.textContent.trim() || "";
      const credits = parseFloat(creditElement) || 0;

      // Find and click the blue button with the course code
      const courseCode = courseName.trim();
      const infoButton = Array.from(
        document.querySelectorAll("button.block")
      ).find((btn) => {
        const title = btn.querySelector(".block-title");
        return title && title.textContent.includes(courseCode);
      });

      if (infoButton) {
        // Click the button to open dialog
        infoButton.click();

        // Wait for dialog to appear
        await new Promise((resolve) => setTimeout(resolve, 500));

        let instructorName = "";
        let times = {};

        // Find the dialog content
        const dialogContent = document.querySelector("mat-dialog-content");
        if (dialogContent) {
          // Get instructor name
          const headers = dialogContent.querySelectorAll("h4.header");
          for (const header of headers) {
            if (header.textContent.includes("Instructors")) {
              const instructorElement = header.nextElementSibling;
              if (instructorElement && instructorElement.tagName === "P") {
                instructorName = instructorElement.textContent.trim();
                break;
              }
            }

            // Get class times
            if (header.textContent.includes("Day/Time")) {
              let currentElement = header.nextElementSibling;
              while (
                currentElement &&
                currentElement.tagName === "P" &&
                currentElement.classList.contains("ng-star-inserted")
              ) {
                const strong = currentElement.querySelector("strong");
                if (strong) {
                  const section = strong.textContent.trim();
                  const timeText = currentElement.textContent
                    .replace(strong.textContent, "")
                    .replace(":", "")
                    .trim();
                  times[section] = timeText;
                }
                currentElement = currentElement.nextElementSibling;
              }
            }
          }
        }

        schedule[counter] = {
          course: {
            name: courseName,
            title: courseTitle,
            credit: credits,
          },
          time: times,
          instructor: {
            name: instructorName,
          },
        };

        // Find and click the close button
        const closeButton = document.querySelector("button[mat-dialog-close]");
        if (closeButton) {
          closeButton.click();
        }

        // Wait for dialog to close
        await new Promise((resolve) => setTimeout(resolve, 200));
      }

      counter++;
    }

    return { schedule }; // Return JSON data
  } catch (error) {
    throw new Error(`Error while fetching course schedule: ${error.message}`);
  }
}
// Format full schedule from API
async function fetchSchedule() {
  try {
    // Get current tab
    const [tab] = await chrome.tabs.query({
      active: true,
      currentWindow: true,
    });
    if (!tab) {
      throw new Error("No active tab found");
    }

    const apiURL = "https://ratemyscheduleapi.vercel.app/returnrating";
    const result = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: readCourseSchedule,
    });

    // Add detailed logging
    const scheduleData = result[0].result;
    console.log(
      "Sending schedule data to API:",
      JSON.stringify(scheduleData, null, 2)
    );

    const response = await fetch(apiURL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(scheduleData),
    });

    if (!response.ok) {
      // Add more detailed error information
      const errorText = await response.text();
      throw new Error(
        `API request failed: ${response.status}\nResponse: ${errorText}`
      );
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Full error details:", error);
    throw new Error(`Failed to fetch schedule: ${error.message}`);
  }
}
async function fetchScoreAPI(completeSchedule) {
  const apiURL = "https://ratemyscheduleapi.vercel.app/evaluate";
  try {
    console.log("Calling API...");

    const response = await fetch(apiURL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(completeSchedule),
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status}`);
    }

    const data = await response.json();
    console.log("API response data:", data);

    // for scores
    const comment = data.comment;
    const courseScore = Math.round(parseFloat(data.course) * 10);
    const instructorScore = Math.round(parseFloat(data.instructor) * 10);
    const scheduleBalance = Math.round(
      parseFloat(data["schedule balance"]) * 10
    );
    const overallScore = Math.round(parseFloat(data.overall) * 10);

    updateScores(
      overallScore,
      courseScore,
      instructorScore,
      scheduleBalance,
      comment
    );
  } catch (error) {
    console.error("Failed to fetch API data:", error);
  }
}

// Updates the scores on the page
function updateScores(
  newScorePercent,
  newCourseScore,
  newInstructorScore,
  newScheduleBalance,
  newComment
) {
  const scorePercentVal = document.getElementById("scorePercent");
  const courseScoreVal = document.getElementById("courseScore");
  const instructorScoreVal = document.getElementById("instructorScore");
  const scheduleBalanceVal = document.getElementById("scheduleBalance");
  const commentPar = document.getElementById("commentParagraph");
  const circle = document.querySelector(".percent svg circle:nth-child(2)");

  // Clear existing values
  scorePercentVal.innerHTML = "";
  courseScoreVal.innerHTML = "";
  instructorScoreVal.innerHTML = "";
  scheduleBalanceVal.innerHTML = "";
  commentPar.innerHTML = "";

  // Animation setup
  const duration = 500; // 0.5 second duration
  const startTime = performance.now();
  const circumference = 2 * Math.PI * 85; // 2πr where r=85

  // Pre-calculate the final circle offset
  const finalOffset = circumference * (1 - newScorePercent / 100);
  const initialOffset = circumference;
  const totalOffsetChange = initialOffset - finalOffset;

  function animateScore(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);

    // Use easeOutQuad easing function for smoother animation
    const easeProgress = 1 - (1 - progress) * (1 - progress);

    // Calculate current values using eased progress
    const currentOverallScore = Math.round(easeProgress * newScorePercent);
    const currentCourseScore = Math.round(easeProgress * newCourseScore);
    const currentInstructorScore = Math.round(
      easeProgress * newInstructorScore
    );
    const currentScheduleBalance = Math.round(
      easeProgress * newScheduleBalance
    );

    // Update score values
    scorePercentVal.textContent = currentOverallScore;
    courseScoreVal.textContent = currentCourseScore;
    instructorScoreVal.textContent = currentInstructorScore;
    scheduleBalanceVal.textContent = currentScheduleBalance;

    // Update circle animation using the same eased progress
    const currentOffset = initialOffset - totalOffsetChange * easeProgress;
    circle.style.strokeDasharray = `${circumference}`;
    circle.style.strokeDashoffset = currentOffset;

    if (progress < 1) {
      requestAnimationFrame(animateScore);
    } else {
      // Set final values
      commentPar.textContent = newComment;
    }
  }

  // Initialize circle properties
  circle.style.strokeDasharray = `${circumference}`;
  circle.style.strokeDashoffset = circumference;

  requestAnimationFrame(animateScore);
}
// Formats the table data for the table
function formatTable(tableData) {
  const tableContent = [];
  for (const key in tableData.schedule) {
    const entry = tableData.schedule[key];
    tableContent.push({
      courseName: entry.course.name,
      gpa: entry.course.cumulativeGpa,
      courseUrl: entry.course.url,
      instructorRating: entry.instructor.instructorRating,
      instructorUrl: entry.instructor.url,
    });
  }
  return tableContent;
}

// Fills the table with the schedule
function fillTable(tableContent) {
  const tableBody = document.getElementById("courseTableBody");
  tableBody.innerHTML = "";

  tableContent.forEach((course) => {
    const row = document.createElement("tr");

    // Course name cell remains unchanged
    const courseNameCell = document.createElement("td");
    courseNameCell.textContent = course.courseName;

    // GPA cell - only create link if not N/A
    const gpaCell = document.createElement("td");
    if (course.gpa === "N/A") {
      gpaCell.textContent = course.gpa;
    } else {
      const gpaLink = document.createElement("a");
      gpaLink.textContent = course.gpa;
      gpaLink.href = course.courseUrl;
      gpaLink.target = "_blank";
      gpaCell.appendChild(gpaLink);
    }
    // Rating cell - only create link if not N/A
    const ratingCell = document.createElement("td");
    if (course.instructorRating === "N/A") {
      ratingCell.textContent = course.instructorRating;
    } else {
      const ratingLink = document.createElement("a");
      ratingLink.textContent = course.instructorRating;
      ratingLink.href = course.instructorUrl;
      ratingLink.target = "_blank";
      ratingCell.appendChild(ratingLink);
    }
    row.appendChild(courseNameCell);
    row.appendChild(gpaCell);
    row.appendChild(ratingCell);

    tableBody.appendChild(row);
  });
}

// Modify the event listener to run immediately if DOM is already loaded
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initializeApp);
} else {
  initializeApp();
}
function formatAiInput(receivedTableData) {
  const completeSchedule = {
    schedule: receivedTableData.schedule,
  };
  // Remove "url" from each item
  for (let key in completeSchedule.schedule) {
    delete completeSchedule.schedule[key].course.url;
    delete completeSchedule.schedule[key].instructor.url;
  }
  return completeSchedule;
}

// Separate the initialization logic into its own function
async function initializeApp() {
  try {
    const loadingScreen = document.getElementById("loadingScreen");
    const mainContent = document.getElementById("mainContent");

    if (!loadingScreen || !mainContent) {
      console.error("Required DOM elements not found");
      return;
    }

    loadingScreen.style.display = "flex";
    mainContent.style.display = "none";
    console.log("Loading screen...");

    const receivedTableData = await fetchSchedule();
    console.log("Schedule data:", receivedTableData); // Debug log
    const tableContent = formatTable(receivedTableData);
    fillTable(tableContent);
    console.log("Table filled successfully");

    console.log("Fetching API data...");
    const completeSchedule = formatAiInput(receivedTableData);
    console.log("Complete schedule:", completeSchedule);
    await fetchScoreAPI(completeSchedule);
    console.log("API data fetched successfully");

    loadingScreen.style.display = "none";
    mainContent.style.display = "block";
    console.log("Data loaded successfully!");
  } catch (error) {
    console.error("Error during initialization:", error);
  }
}
