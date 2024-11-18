  chrome.action.onClicked.addListener((tab) => {
    chrome.scripting.executeScript({
      target: { tabId: tab.id },
      files: ['content.js']
    });
  });
  
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    
    if (message.action === 'openSidePanel') {
      // Code to open the side panel
      chrome.sidePanel.setOptions({
        path: 'rateMySchedule.html', // Specify the path to your side panel content
        enabled: true // Make sure the side panel is enabled
      });
  
      // Optionally, you can send a response back to the content script if needed
      sendResponse({ status: 'success', message: 'Side panel opened' });
    }
  });