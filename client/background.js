const GOOGLE_ORIGIN = 'https://enroll.wisc.edu';

chrome.sidePanel
  .setPanelBehavior({ openPanelOnActionClick: true })
  .catch((error) => console.error(error));

chrome.tabs.onUpdated.addListener(async (tabId, info, tab) => {
  if (!tab.url) return;
  const url = new URL(tab.url);
  if (url.href.startsWith(GOOGLE_ORIGIN)) {
    await chrome.sidePanel.setOptions({
      tabId,
      path: 'rateMySchedule.html',
      enabled: true
    });
  } else {
    await chrome.sidePanel.setOptions({
      tabId,
      enabled: false
    });
  }
});