/* Popup controller: collects prompts + settings, talks to the content script. */

const els = {
  prompts: document.getElementById("prompts"),
  delay: document.getElementById("delay"),
  repeats: document.getElementById("repeats"),
  waitForIdle: document.getElementById("waitForIdle"),
  startBtn: document.getElementById("startBtn"),
  stopBtn: document.getElementById("stopBtn"),
  status: document.getElementById("status"),
  log: document.getElementById("log"),
  notOnFlow: document.getElementById("notOnFlow"),
};

const FLOW_URL_MATCH = /^https:\/\/labs\.google\//;

function setRunning(running) {
  els.startBtn.disabled = running;
  els.stopBtn.disabled = !running;
  els.prompts.disabled = running;
  els.delay.disabled = running;
  els.repeats.disabled = running;
  els.waitForIdle.disabled = running;
}

function log(message, type = "") {
  const li = document.createElement("li");
  li.textContent = message;
  if (type) li.className = type;
  els.log.prepend(li);
}

function setStatus(text) {
  els.status.textContent = text;
}

async function getActiveTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab;
}

/* Make sure the content script is present in the tab. It guards against
   double-injection internally, so calling this repeatedly is safe. */
async function ensureContentScript(tabId) {
  try {
    await chrome.scripting.executeScript({
      target: { tabId },
      files: ["content.js"],
    });
    return true;
  } catch (e) {
    return false;
  }
}

/* Persist form state */
async function saveState() {
  await chrome.storage.local.set({
    formState: {
      prompts: els.prompts.value,
      delay: els.delay.value,
      repeats: els.repeats.value,
      waitForIdle: els.waitForIdle.checked,
    },
  });
}

async function restoreState() {
  const { formState } = await chrome.storage.local.get("formState");
  if (formState) {
    els.prompts.value = formState.prompts ?? "";
    els.delay.value = formState.delay ?? 8;
    els.repeats.value = formState.repeats ?? 1;
    els.waitForIdle.checked = formState.waitForIdle ?? true;
  }
}

async function init() {
  await restoreState();
  const tab = await getActiveTab();
  const onFlow = tab && FLOW_URL_MATCH.test(tab.url || "");
  els.notOnFlow.classList.toggle("hidden", !!onFlow);

  // Ask content script whether a batch is already running.
  if (onFlow) {
    chrome.tabs.sendMessage(tab.id, { type: "GET_STATE" }, (resp) => {
      if (chrome.runtime.lastError) return; // content script not ready
      if (resp && resp.running) {
        setRunning(true);
        setStatus(resp.statusText || "Batch running…");
      }
    });
  }
}

els.startBtn.addEventListener("click", async () => {
  const tab = await getActiveTab();
  if (!tab || !FLOW_URL_MATCH.test(tab.url || "")) {
    els.notOnFlow.classList.remove("hidden");
    return;
  }

  const prompts = els.prompts.value
    .split("\n")
    .map((p) => p.trim())
    .filter(Boolean);

  if (prompts.length === 0) {
    log("Add at least one prompt.", "err");
    return;
  }

  const config = {
    prompts,
    delayMs: Math.max(1, Number(els.delay.value) || 8) * 1000,
    repeats: Math.max(1, Number(els.repeats.value) || 1),
    waitForIdle: els.waitForIdle.checked,
  };

  await saveState();
  setRunning(true);
  els.log.innerHTML = "";
  setStatus("Starting batch…");

  // Inject on demand so the user never has to reload the Flow tab first.
  await ensureContentScript(tab.id);

  chrome.tabs.sendMessage(tab.id, { type: "START_BATCH", config }, (resp) => {
    if (chrome.runtime.lastError) {
      log("Could not reach the page. Reload Flow and try again.", "err");
      setRunning(false);
      return;
    }
    if (resp && resp.error) {
      log(resp.error, "err");
      setRunning(false);
    }
  });
});

els.stopBtn.addEventListener("click", async () => {
  const tab = await getActiveTab();
  chrome.tabs.sendMessage(tab.id, { type: "STOP_BATCH" }, () => {});
  setStatus("Stopping…");
});

/* Live updates from the content script */
chrome.runtime.onMessage.addListener((msg) => {
  if (msg.type === "BATCH_LOG") {
    log(msg.message, msg.level || "");
  } else if (msg.type === "BATCH_STATUS") {
    setStatus(msg.statusText);
  } else if (msg.type === "BATCH_DONE") {
    setRunning(false);
    setStatus(msg.statusText || "Done.");
  }
});

document.addEventListener("DOMContentLoaded", init);
