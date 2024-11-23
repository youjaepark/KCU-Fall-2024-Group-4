// content-script.js

// Include Firebase SDKs in the content script
// Since content scripts cannot use import statements, we need to include Firebase in a way that's compatible.

// Create script elements to load Firebase SDKs
const firebaseAppScript = document.createElement("script");
firebaseAppScript.src = chrome.runtime.getURL("firebase-app.js");
firebaseAppScript.onload = () => {
  const firebaseFirestoreScript = document.createElement("script");
  firebaseFirestoreScript.src = chrome.runtime.getURL("firebase-firestore.js");
  firebaseFirestoreScript.onload = () => {
    // Initialize Firebase after both scripts are loaded
    initializeFirebase();
  };
  document.head.appendChild(firebaseFirestoreScript);
};
document.head.appendChild(firebaseAppScript);

function initializeFirebase() {
  // Your Firebase configuration
  const firebaseConfig = {
    apiKey: "AIzaSyA3_v6ZaVv5TSjQD4lGfu7H_F9BpM2idnQ",
    authDomain: "ratemyschedule-c9fab.firebaseapp.com",
    databaseURL: "https://ratemyschedule-c9fab-default-rtdb.firebaseio.com",
    projectId: "ratemyschedule-c9fab",
    storageBucket: "ratemyschedule-c9fab.firebasestorage.app",
    messagingSenderId: "556409279427",
    appId: "1:556409279427:web:d63b41188a64bf66f2e376",
    measurementId: "G-Y10BB59QJP",
  };

  // Initialize Firebase
  firebase.initializeApp(firebaseConfig);
  const db = firebase.firestore();

  // Now set up the message listener
  setupMessageListener(db);
}

function setupMessageListener(db) {
  // Listen for messages from popup.js
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "findElements") {
      findElements(db)
        .then((result) => {
          sendResponse({ result });
        })
        .catch((error) => {
          console.error("Error in findElements:", error);
          sendResponse({ error: error.message });
        });
      // Return true to indicate that the response will be sent asynchronously
      return true;
    }
  });
}

async function fetchCourseDetails(db, courseName) {
  try {
    const coursesRef = db.collection("courses");
    const q = coursesRef.where(
      "subjectCode",
      "array-contains",
      courseName.split(" ")[0]
    );
    const querySnapshot = await q.get();

    if (!querySnapshot.empty) {
      const courseData = querySnapshot.docs[0].data();
      return {
        cumulativeGpa: courseData.cumulativeGpa || "N/A",
        courseUrl: courseData.courseUrl,
      };
    }
    return { cumulativeGpa: "N/A", courseUrl: null };
  } catch (error) {
    console.error("Error fetching course details:", error);
    return { cumulativeGpa: "N/A", courseUrl: null };
  }
}

async function fetchProfessorRating(db, instructorName) {
  try {
    const formattedName = instructorName
      .toLowerCase()
      .split(" ")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");

    const professorsRef = db.collection("professors");
    const q = professorsRef.where("name", "==", formattedName);
    const querySnapshot = await q.get();

    if (!querySnapshot.empty) {
      const profData = querySnapshot.docs[0].data();
      return {
        rating: profData.rating || "N/A",
        url: profData.url,
      };
    }
    return { rating: "N/A", url: null };
  } catch (error) {
    console.error("Error fetching professor rating:", error);
    return { rating: "N/A", url: null };
  }
}

async function findElements(db) {
  try {
    const schedule = {};
    let counter = 1;

    // Get all course wrapper elements
    const courseWrappers = document.querySelectorAll("button.wrapper");

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

    // Enhance schedule with additional information
    for (const [key, courseData] of Object.entries(schedule)) {
      const courseDetails = await fetchCourseDetails(
        db,
        courseData.course.name
      );
      const profRating = await fetchProfessorRating(
        db,
        courseData.instructor.name
      );

      schedule[key] = {
        ...courseData,
        course: {
          ...courseData.course,
          cumulativeGpa: courseDetails.cumulativeGpa,
          courseUrl: courseDetails.courseUrl,
        },
        instructor: {
          ...courseData.instructor,
          rating: profRating.rating,
          url: profRating.url,
        },
      };
    }

    // Create table HTML
    const tableHTML = `
        <table style="width:100%; border-collapse: collapse; margin-top: 15px;">
          <thead>
            <tr>
              <th style="border:1px solid #ddd; padding:8px;">Order</th>
              <th style="border:1px solid #ddd; padding:8px;">Course Name</th>
              <th style="border:1px solid #ddd; padding:8px;">MadGrade Rating</th>
              <th style="border:1px solid #ddd; padding:8px;">RMP Rating</th>
            </tr>
          </thead>
          <tbody>
            ${Object.entries(schedule)
              .map(
                ([key, data]) => `
              <tr>
                <td style="border:1px solid #ddd; padding:8px;">${key}</td>
                <td style="border:1px solid #ddd; padding:8px;">${data.course.name}</td>
                <td style="border:1px solid #ddd; padding:8px;">${data.course.cumulativeGpa}</td>
                <td style="border:1px solid #ddd; padding:8px;">${data.instructor.rating}</td>
              </tr>
            `
              )
              .join("")}
          </tbody>
        </table>
      `;

    return (
      tableHTML +
      `<pre style="
        background-color: #f5f5f5;
        padding: 15px;
        border-radius: 5px;
        font-family: monospace;
        white-space: pre-wrap;
        word-wrap: break-word;
        font-size: 14px;
        line-height: 1.4;
        color: #333;
        border: 1px solid #ddd;
        margin: 10px 0;
      ">${JSON.stringify({ schedule }, null, 4)
        .replace(/\n/g, "<br>")
        .replace(/ /g, "&nbsp;")}</pre>`
    );
  } catch (error) {
    console.error("Error in findElements:", error);
    return `Error: ${error.message}`;
  }
}
