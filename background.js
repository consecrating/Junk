/*
 * Flow Batch — background service worker (MV3)
 *
 * Kept intentionally light. The heavy lifting happens in the content script; this worker
 * just guarantees the content script is present and gives the toolbar icon a fallback
 * behavior when the user is not on Google Flow.
 */

const FLOW_HOME = "https://labs.google/fx/tools/flow";
const FLOW_MATCH = /^https:\/\/labs\.google\//;

// On install, make sure any already-open Flow tabs get the content script
// without needing a manual reload.
chrome.runtime.onInstalled.addListener(async () => {
  try {
    const tabs = await chrome.tabs.query({ url: "https://labs.google/*" });
    for (const tab of tabs) {
      try {
        await chrome.scripting.executeScript({
          target: { tabId: tab.id },
          files: ["content.js"],
        });
      } catch (_) {
        /* some tabs (e.g. prerender) can't be injected; ignore */
      }
    }
  } catch (_) {
    /* ignore */
  }
});

// Relay any messages the content script sends to the popup. When the popup is
// closed, sendMessage rejects — we swallow that so it doesn't spam the console.
chrome.runtime.onMessage.addListener((msg) => {
  if (
    msg &&
    (msg.type === "BATCH_LOG" ||
      msg.type === "BATCH_STATUS" ||
      msg.type === "BATCH_DONE")
  ) {
    // Popup listens directly; nothing required here. Present for future logging/badges.
    if (msg.type === "BATCH_STATUS" || msg.type === "BATCH_DONE") {
      chrome.action.setTitle({ title: `Flow Batch — ${msg.statusText}` }).catch(() => {});
    }
  }
});

// If the popup can't be shown for some reason and the user is off-site, this helps them
// get to Flow quickly. (No-op while default_popup is set, but useful as a safety net.)
chrome.action.onClicked.addListener(async (tab) => {
  if (!tab || !FLOW_MATCH.test(tab.url || "")) {
    await chrome.tabs.create({ url: FLOW_HOME });
  }
});
