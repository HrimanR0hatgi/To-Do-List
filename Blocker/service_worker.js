const BRIDGE_URL = "http://127.0.0.1:49252/status";
const CHECK_ALARM = "check-accountability-lock";
const RULE_ID_START = 1000;

const DOMAINS = [
  "youtube.com",
  "netflix.com",
  "primevideo.com",
  "disneyplus.com",
  "twitch.tv",
  "reddit.com"
];

async function applyBlockingRules(locked) {
  const existingRules =
    await chrome.declarativeNetRequest.getDynamicRules();

  const removeRuleIds = existingRules
    .filter(rule =>
      rule.id >= RULE_ID_START &&
      rule.id < RULE_ID_START + DOMAINS.length
    )
    .map(rule => rule.id);

  const addRules = locked
    ? DOMAINS.map((domain, index) => ({
        id: RULE_ID_START + index,
        priority: 1,
        action: { type: "block" },
        condition: {
          urlFilter: `||${domain}^`,
          resourceTypes: ["main_frame"]
        }
      }))
    : [];

  await chrome.declarativeNetRequest.updateDynamicRules({
    removeRuleIds,
    addRules: []
  });

  if (addRules.length > 0) {
    await chrome.declarativeNetRequest.updateDynamicRules({
      addRules
    });
  }

  await chrome.storage.local.set({
    lockActive: locked,
    lastChecked: new Date().toISOString()
  });
}

async function checkPythonApp() {
  try {
    const response = await fetch(BRIDGE_URL, {
      cache: "no-store"
    });

    if (!response.ok) {
      throw new Error(`Bridge returned ${response.status}`);
    }

    const data = await response.json();

    if (typeof data.lock_active !== "boolean") {
      throw new Error("Invalid lock status");
    }

    await applyBlockingRules(data.lock_active);
  } catch (error) {
    // Keep existing rules if the Python bridge is unavailable.
    console.warn("Could not check My Productivity:", error.message);
  }
}

async function scheduleChecks() {
  await chrome.alarms.create(CHECK_ALARM, {
    periodInMinutes: 0.5
  });
  await checkPythonApp();
}

chrome.runtime.onInstalled.addListener(scheduleChecks);
chrome.runtime.onStartup.addListener(scheduleChecks);
chrome.alarms.onAlarm.addListener(alarm => {
  if (alarm.name === CHECK_ALARM) {
    checkPythonApp();
  }
});

checkPythonApp();