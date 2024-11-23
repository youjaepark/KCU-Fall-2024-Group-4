chrome.runtime.onInstalled.addListener(() => {
  console.log("RateMySchedule extension installed!");
});

chrome.sidePanel
  .setPanelBehavior({ openPanelOnActionClick: true })
  .then(() => console.log("Side panel behavior set."))
  .catch((err) => console.error("Error setting side panel behavior:", err));