async function updateStatus() {
  const status = document.getElementById("status");

  try {
    const result = await chrome.storage.local.get([
      "lockActive",
      "lastChecked"
    ]);

    if (typeof result.lockActive !== "boolean") {
      status.textContent =
        "Waiting for My Productivity to connect.";
      return;
    }

    status.textContent = result.lockActive
      ? "LOCK ACTIVE — configured sites are blocked."
      : "No active lock — configured sites are available.";
  } catch {
    status.textContent = "Could not read the lock status.";
  }
}

updateStatus();