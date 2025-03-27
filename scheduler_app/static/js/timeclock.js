// Global variable to store employee data
let employeesData = []

// Update the current time display
function updateTimeDisplay() {
  const now = new Date()

  // Format time as HH:MM:SS
  const hours = String(now.getHours()).padStart(2, "0")
  const minutes = String(now.getMinutes()).padStart(2, "0")
  const seconds = String(now.getSeconds()).padStart(2, "0")
  document.getElementById("currentTime").textContent = `${hours}:${minutes}:${seconds}`

  // Format date as Day of Week, Month Day, Year
  const options = { weekday: "long", year: "numeric", month: "long", day: "numeric" }
  document.getElementById("currentDate").textContent = now.toLocaleDateString(undefined, options)
}

// Start the clock update interval
function initClock() {
  setInterval(updateTimeDisplay, 1000)
  updateTimeDisplay()
}

// Keypad functions
function appendToInput(value) {
  const input = document.getElementById("punchIdInput")
  input.value += value
}

function clearInput() {
  document.getElementById("punchIdInput").value = ""
}

// Load employees data
async function loadEmployees() {
  try {
    const response = await fetch("/api/employees")
    if (!response.ok) {
      throw new Error("Failed to load employees")
    }

    const data = await response.json()
    employeesData = data // Store globally
    console.log("Loaded employees:", employeesData)
    return data
  } catch (err) {
    console.error("Error loading employees:", err)
    return []
  }
}

// Process punch in/out
async function processPunch() {
  const punchId = document.getElementById("punchIdInput").value.trim()
  if (!punchId) {
    showPunchStatus("Please enter your ID/Punch Code", "warning")
    return
  }

  try {
    console.log(`Attempting to punch with ID/Code: ${punchId}`)

    // Reload employees to ensure we have the latest data
    await loadEmployees()

    // Find the employee by either custom_id or system id
    let matchedEmployee = null

    // First try to match by custom_id (string comparison)
    matchedEmployee = employeesData.find((emp) => emp.custom_id === punchId)

    // If not found, try to match by system id (numeric comparison)
    if (!matchedEmployee) {
      const numericId = Number.parseInt(punchId, 10)
      if (!isNaN(numericId)) {
        matchedEmployee = employeesData.find((emp) => emp.id === numericId)
      }
    }

    if (!matchedEmployee) {
      throw new Error(`No employee found with ID/Code: ${punchId}`)
    }

    console.log("Found employee:", matchedEmployee)

    // Try to use the custom_id if that's what was entered, otherwise use system id
    const idToUse = punchId === matchedEmployee.custom_id ? punchId : matchedEmployee.id

    // Now attempt the punch
    const response = await fetch("/api/timeclock/punch", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        employee_id: idToUse,
        employee_system_id: matchedEmployee.id, // Send both IDs to help the backend
        employee_custom_id: matchedEmployee.custom_id,
        employee_name: matchedEmployee.name, // Send name to help with debugging
        timestamp: new Date().toISOString(),
      }),
    })

    console.log(`Received response with status: ${response.status}`)

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || `Failed to process punch (status ${response.status})`)
    }

    const data = await response.json()
    console.log(`Response data:`, data)

    // Show success message
    const punchType = data.punch && data.punch.type === "in" ? "IN" : "OUT"
    const employeeName = data.employee ? data.employee.name : matchedEmployee.name
    showPunchStatus(`${employeeName} successfully punched ${punchType}!`, "success")

    // Clear the input for the next punch
    clearInput()

    // Refresh the activity displays
    loadRecentActivity()
    loadClockedInEmployees()
  } catch (error) {
    console.error("Punch error:", error)
    showPunchStatus(error.message || "Error processing punch. Please try again.", "danger")
  }
}

function showPunchStatus(message, type) {
  const statusDiv = document.getElementById("punchStatus")
  statusDiv.className = `alert alert-${type} mt-3`
  statusDiv.innerHTML = message
  statusDiv.classList.remove("d-none")

  // Clear the status after 5 seconds
  setTimeout(() => {
    statusDiv.classList.add("d-none")
  }, 5000)
}

// Load recent activity
async function loadRecentActivity() {
  try {
    const response = await fetch("/api/timeclock/activity")

    if (!response.ok) {
      throw new Error("Failed to load recent activity")
    }

    const data = await response.json()
    const activityDiv = document.getElementById("recentActivity")

    if (!data.activity || data.activity.length === 0) {
      activityDiv.innerHTML = `
        <div class="activity-empty">
          <i class="bi bi-clock"></i>
          <p>No recent activity</p>
        </div>
      `
      return
    }

    let activityHtml = ""
    data.activity.forEach((item) => {
      const timestamp = new Date(item.timestamp)
      const timeString = timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
      const dateString = timestamp.toLocaleDateString([], { month: "short", day: "numeric" })

      activityHtml += `
        <div class="activity-item ${item.type === "in" ? "activity-in" : "activity-out"}">
          <div class="activity-time">${timeString}<br><small>${dateString}</small></div>
          <div class="activity-details">
            <div class="activity-name">${item.employee_name}</div>
            <div class="activity-type">Punched ${item.type.toUpperCase()}</div>
          </div>
        </div>
      `
    })

    activityDiv.innerHTML = activityHtml
  } catch (error) {
    console.error(error)
    document.getElementById("recentActivity").innerHTML = `
      <div class="alert alert-danger">
        <i class="bi bi-exclamation-triangle-fill me-2"></i>
        Error loading activity: ${error.message}
      </div>
    `
  }
}

// Load currently clocked in employees
async function loadClockedInEmployees() {
  try {
    const response = await fetch("/api/timeclock/clocked-in")

    if (!response.ok) {
      throw new Error("Failed to load clocked in employees")
    }

    const data = await response.json()
    const clockedInDiv = document.getElementById("clockedInEmployees")

    if (!data.employees || data.employees.length === 0) {
      clockedInDiv.innerHTML = `
        <div class="activity-empty">
          <i class="bi bi-person-slash"></i>
          <p>No employees currently clocked in</p>
        </div>
      `
      return
    }

    let employeesHtml = ""
    data.employees.forEach((emp) => {
      const punchTime = new Date(emp.punch_time)
      const timeString = punchTime.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })

      employeesHtml += `
        <div class="clocked-in-item">
          <div class="employee-avatar ${emp.color || "block-blue"}">
            ${emp.name.charAt(0).toUpperCase()}
          </div>
          <div class="employee-details">
            <div class="employee-name">${emp.name}</div>
            <div class="employee-time">Since ${timeString}</div>
          </div>
        </div>
      `
    })

    clockedInDiv.innerHTML = employeesHtml
  } catch (error) {
    console.error(error)
    document.getElementById("clockedInEmployees").innerHTML = `
      <div class="alert alert-danger">
        <i class="bi bi-exclamation-triangle-fill me-2"></i>
        Error loading clocked in employees: ${error.message}
      </div>
    `
  }
}

// Initialize on page load
document.addEventListener("DOMContentLoaded", async () => {
  initClock()

  // Load employees first to ensure we have the data
  await loadEmployees()

  loadRecentActivity()
  loadClockedInEmployees()

  // Focus the input field
  document.getElementById("punchIdInput").focus()

  // Add keyboard support for the punch input
  document.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      processPunch()
    }
  })
})

