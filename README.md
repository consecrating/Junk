# Batch Prompt Runner

A Chrome extension (Manifest V3) that lets you queue **many prompts** and have them
submitted to your **AI video studio** automatically, one after another, so multiple
generations run without you babysitting the page.

> **Note on "simultaneously":** The studio runs generations on its own servers and
> enforces its own per-account concurrency and quota limits. This extension can't bypass
> those. What it does is **fire off your prompts back-to-back as fast as the site allows**,
> so several videos end up processing at the same time instead of you typing/clicking each one.

---

## Features

- 📝 Paste **multiple prompts** (one per line) and submit them in sequence.
- 🔁 **Repeats per prompt** — generate N variations of each idea.
- ⏱️ Configurable **delay between submits** to stay within rate limits.
- ✅ Optional **"wait until Generate is ready"** so it doesn't click a disabled button.
- 📜 Live **log & status** of what's been submitted.
- ⏹️ **Stop** button to cancel a running batch at any time.
- 💾 Remembers your prompts and settings between sessions.

---

## Install (Load Unpacked)

1. Download / extract this folder to a stable location (not a temp/Downloads cleanup folder).
2. Open Chrome and go to `chrome://extensions`.
3. Turn on **Developer mode** (top-right toggle) — required for unpacked extensions.
4. Click **Load unpacked** and select the folder that contains `manifest.json`.
5. Pin the toolbar icon for easy access.

---

## Usage

1. Open the studio site and sign in.
2. Open the view that has the **prompt box** and **Generate** button.
3. Click the toolbar icon.
4. Enter your prompts — **one per line**, e.g.:
   ```
   A neon city at night, cinematic drone shot
   A cat surfing a giant wave, slow motion
   Timelapse of a blooming flower, macro
   ```
5. Set **delay** (seconds between submits) and **repeats per prompt**.
6. Click **Start batch**. Watch the log; use **Stop** to cancel.

---

## How it works

| File | Role |
|------|------|
| `manifest.json` | MV3 config, permissions (`storage`, `scripting`, `activeTab`), site access. |
| `popup/*` | The UI: collects prompts + settings, shows live log, talks to the content script. |
| `content.js` | Runs on the studio page. Finds the prompt box + Generate button, types each prompt, clicks Generate, and paces submissions. |

The popup injects `content.js` on demand (via `chrome.scripting`), so you never have to
reload the studio tab after installing. There is no background service worker — one less
thing to fail. The content script fills the prompt field using a **React-safe** value
setter (native setter + `input`/`change` events) so the UI registers the text.

---

## If it stops finding the buttons

The studio is an evolving app with **no stable/public selectors**, so this extension
locates the prompt box and Generate button **heuristically** (by placeholder text, ARIA
labels, and button labels like "Generate"). If the site changes its layout and automation
breaks, edit the **`SELECTOR HEURISTICS`** block near the top of `content.js`:

- `findPromptInput()` — how the prompt field is located.
- `findGenerateButton()` — how the submit button is located.

These are isolated on purpose so a fix is usually a one- or two-line change.

---

## Limitations & fair use

- ⚖️ **Respect the site's Terms of Service** and your plan's quota/rate limits.
  Automating a UI can trip abuse protections — keep delays reasonable.
- This is an **unofficial** tool, not affiliated with or endorsed by any provider.
- It automates the on-screen UI only; it does **not** use any private/undocumented API.
- Concurrency is ultimately capped by the provider, not by this extension.

---

## Regenerating icons (optional)

Icons are plain PNGs in `icons/`. To regenerate them (no dependencies needed):

```bash
python3 make_icons.py
```

---

## License

MIT — do what you like, no warranty.
