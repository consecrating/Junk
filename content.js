/*
 * Flow Batch — content script
 * Runs on https://labs.google/* and automates Google Flow's prompt box + Generate button.
 *
 * Google Flow is a React app with no stable public selectors, so we locate elements
 * heuristically (placeholder text, ARIA labels, button text). If Google changes the UI,
 * update the SELECTOR HEURISTICS block below — that's the only part that should need edits.
 */

(() => {
  if (window.__flowBatchInjected) return;
  window.__flowBatchInjected = true;

  const state = {
    running: false,
    cancel: false,
    statusText: "Idle.",
  };

  /* ---------------- messaging helpers ---------------- */

  function toPopup(msg) {
    chrome.runtime.sendMessage(msg).catch(() => {});
  }
  const logInfo = (message, level = "") =>
    toPopup({ type: "BATCH_LOG", message, level });
  function setStatus(statusText) {
    state.statusText = statusText;
    toPopup({ type: "BATCH_STATUS", statusText });
  }

  /* ---------------- generic utils ---------------- */

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  function visible(el) {
    if (!el) return false;
    const rect = el.getBoundingClientRect();
    const style = getComputedStyle(el);
    return (
      rect.width > 0 &&
      rect.height > 0 &&
      style.visibility !== "hidden" &&
      style.display !== "none"
    );
  }

  async function waitFor(fn, { timeout = 15000, interval = 300 } = {}) {
    const start = Date.now();
    while (Date.now() - start < timeout) {
      if (state.cancel) return null;
      const result = fn();
      if (result) return result;
      await sleep(interval);
    }
    return null;
  }

  /* ---------------- SELECTOR HEURISTICS ----------------
   * Adjust these if Google Flow's DOM changes.
   */

  function findPromptInput() {
    // 1) Obvious candidates: textareas / contenteditable prompt boxes.
    const candidates = [
      ...document.querySelectorAll(
        'textarea, [contenteditable="true"], input[type="text"]'
      ),
    ].filter(visible);

    // Prefer ones whose placeholder / aria-label mentions a prompt-like word.
    const hints = /prompt|describe|idea|generate|type|text|scene|video/i;
    const scored = candidates
      .map((el) => {
        const meta = [
          el.getAttribute("placeholder"),
          el.getAttribute("aria-label"),
          el.getAttribute("title"),
          el.getAttribute("name"),
        ]
          .filter(Boolean)
          .join(" ");
        let score = 0;
        if (hints.test(meta)) score += 5;
        if (el.tagName === "TEXTAREA") score += 3;
        if (el.isContentEditable) score += 2;
        // Bigger boxes are more likely to be the main prompt field.
        score += Math.min(el.getBoundingClientRect().width / 200, 3);
        return { el, score };
      })
      .sort((a, b) => b.score - a.score);

    return scored.length ? scored[0].el : null;
  }

  function findGenerateButton() {
    const buttons = [
      ...document.querySelectorAll(
        'button, [role="button"], [type="submit"]'
      ),
    ].filter(visible);

    const label = /^\s*(generate|create|render|run)\b/i;
    // Exact-ish label match first.
    let match = buttons.find((b) =>
      label.test((b.innerText || b.getAttribute("aria-label") || "").trim())
    );
    if (match) return match;

    // Fallback: an arrow/submit button near the prompt input.
    const input = findPromptInput();
    if (input) {
      const near = buttons
        .map((b) => {
          const rb = b.getBoundingClientRect();
          const ri = input.getBoundingClientRect();
          const dist = Math.hypot(rb.left - ri.right, rb.top - ri.top);
          return { b, dist };
        })
        .sort((a, b) => a.dist - b.dist);
      if (near.length && near[0].dist < 400) return near[0].b;
    }
    return null;
  }

  /* ---------------- input setting (React-safe) ---------------- */

  function setNativeValue(el, value) {
    if (el.isContentEditable) {
      el.focus();
      el.textContent = value;
      el.dispatchEvent(new InputEvent("input", { bubbles: true }));
      return;
    }
    const proto =
      el.tagName === "TEXTAREA"
        ? window.HTMLTextAreaElement.prototype
        : window.HTMLInputElement.prototype;
    const setter = Object.getOwnPropertyDescriptor(proto, "value").set;
    el.focus();
    setter.call(el, "");
    el.dispatchEvent(new Event("input", { bubbles: true }));
    setter.call(el, value);
    el.dispatchEvent(new Event("input", { bubbles: true }));
    el.dispatchEvent(new Event("change", { bubbles: true }));
  }

  function isDisabled(btn) {
    return (
      btn.disabled ||
      btn.getAttribute("aria-disabled") === "true" ||
      btn.getAttribute("disabled") !== null
    );
  }

  /* ---------------- one submission ---------------- */

  async function submitPrompt(prompt, index, total, config) {
    setStatus(`(${index}/${total}) Preparing…`);

    const input = await waitFor(findPromptInput, { timeout: 15000 });
    if (!input) {
      logInfo(`✗ Couldn't find the prompt box for: "${prompt}"`, "err");
      return false;
    }

    setNativeValue(input, prompt);
    await sleep(400);

    let button = findGenerateButton();
    if (config.waitForIdle) {
      button = await waitFor(
        () => {
          const b = findGenerateButton();
          return b && !isDisabled(b) ? b : null;
        },
        { timeout: 15000 }
      );
    }

    if (!button) {
      logInfo(`✗ Generate button not found for: "${prompt}"`, "err");
      return false;
    }

    // Try Enter first (many Flow builds submit on Enter), then click as fallback.
    button.click();
    await sleep(300);

    logInfo(`✓ Submitted (${index}/${total}): ${prompt}`, "ok");
    return true;
  }

  /* ---------------- batch runner ---------------- */

  async function runBatch(config) {
    state.running = true;
    state.cancel = false;

    const queue = [];
    for (const p of config.prompts) {
      for (let r = 0; r < config.repeats; r++) queue.push(p);
    }

    logInfo(
      `Starting batch: ${config.prompts.length} prompt(s) × ${config.repeats} = ${queue.length} generation(s).`
    );

    let done = 0;
    for (let i = 0; i < queue.length; i++) {
      if (state.cancel) {
        logInfo("Batch stopped by user.", "err");
        break;
      }
      const ok = await submitPrompt(queue[i], i + 1, queue.length, config);
      if (ok) done++;

      if (i < queue.length - 1 && !state.cancel) {
        const secs = Math.round(config.delayMs / 1000);
        setStatus(`Waiting ${secs}s before next submit…`);
        // Cancellable wait.
        const start = Date.now();
        while (Date.now() - start < config.delayMs) {
          if (state.cancel) break;
          await sleep(200);
        }
      }
    }

    state.running = false;
    const finalText = state.cancel
      ? `Stopped. ${done}/${queue.length} submitted.`
      : `Done. ${done}/${queue.length} submitted.`;
    setStatus(finalText);
    toPopup({ type: "BATCH_DONE", statusText: finalText });
  }

  /* ---------------- message listener ---------------- */

  chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
    if (msg.type === "GET_STATE") {
      sendResponse({ running: state.running, statusText: state.statusText });
      return true;
    }
    if (msg.type === "START_BATCH") {
      if (state.running) {
        sendResponse({ error: "A batch is already running in this tab." });
        return true;
      }
      runBatch(msg.config);
      sendResponse({ ok: true });
      return true;
    }
    if (msg.type === "STOP_BATCH") {
      state.cancel = true;
      sendResponse({ ok: true });
      return true;
    }
  });
})();
