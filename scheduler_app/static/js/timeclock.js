/**
 * Time Clock System
 * Handles employee clock in/out functionality
 */

// Global variables
let employeesData = []
let currentlyViewingEmployeeId = null

// Initialize the time clock system
document.addEventListener("DOMContentLoaded", async () => {
  // Start the clock display
  initClock()

  // Load employees data
  await loadEmployees()

  // Load recent activity and currently clocked in employees
  await Promise.all([loadRecentActivity(), loadClockedInEmployees()])

  // Set up event listeners
  setupEventListeners()

  // Focus the input field
  const punchIdInput = document.getElementById("punchIdInput")
  if (punchIdInput) {
    punchIdInput.focus()
  }
})

// Set up event listeners
function setupEventListeners() {
  // Add keyboard support for the punch input
  document.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      processPunch()
    }
  })

  // Add click event for employee details in the clocked-in list
  const clockedInList = document.getElementById("clockedInEmployees")
  if (clockedInList) {
    clockedInList.addEventListener("click", (event) => {
      // Find the closest clocked-in-item if any
      const clockedInItem = event.target.closest(".clocked-in-item")
      if (clockedInItem) {
        const employeeId = clockedInItem.dataset.employeeId
        if (employeeId) {
          showEmployeeDetails(Number.parseInt(employeeId, 10))
        }
      }
    })
  }
}

// Update the current time display
function updateTimeDisplay() {
  const now = new Date()

  // Format time as HH:MM:SS
  const hours = String(now.getHours()).padStart(2, "0")
  const minutes = String(now.getMinutes()).padStart(2, "0")
  const seconds = String(now.getSeconds()).padStart(2, "0")

  const timeElement = document.getElementById("currentTime")
  if (timeElement) {
    timeElement.textContent = `${hours}:${minutes}:${seconds}`
  }

  // Format date as Day of Week, Month Day, Year
  const options = { weekday: "long", year: "numeric", month: "long", day: "numeric" }

  const dateElement = document.getElementById("currentDate")
  if (dateElement) {
    dateElement.textContent = now.toLocaleDateString(undefined, options)
  }
}

// Start the clock update interval
function initClock() {
  setInterval(updateTimeDisplay, 1000)
  updateTimeDisplay()
}

// Keypad functions
function appendToInput(value) {
  const input = document.getElementById("punchIdInput")
  if (input) {
    input.value += value
  }
}

function clearInput() {
  const input = document.getElementById("punchIdInput")
  if (input) {
    input.value = ""
    input.focus()
  }
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
    showError("Failed to load employee data. Please refresh the page.")
    return []
  }
}

// Process punch in/out
async function processPunch() {
  const punchIdInput = document.getElementById("punchIdInput")
  if (!punchIdInput) return

  const punchId = punchIdInput.value.trim()
  if (!punchId) {
    showPunchStatus("Please enter your ID/Punch Code", "warning")
    return
  }

  try {
    console.log(`Attempting to punch with ID/Code: ${punchId}`)

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

    // Now attempt the punch with the system ID
    const response = await fetch("/api/timeclock/punch", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        employee_id: matchedEmployee.id,
        timestamp: new Date().toISOString(),
      }),
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || `Failed to process punch (status ${response.status})`)
    }

    const data = await response.json()
    console.log(`Response data:`, data)

    // Show success message
    const punchType = data.punch.type === "in" ? "IN" : "OUT"
    const employeeName = matchedEmployee.name

    // Calculate duration if this was a punch out
    let durationMessage = ""
    if (punchType === "OUT" && data.punch.duration_minutes) {
      const hours = Math.floor(data.punch.duration_minutes / 60)
      const minutes = data.punch.duration_minutes % 60
      durationMessage = `<br>Duration: ${hours}h ${minutes}m`
    }

    showPunchStatus(`${employeeName} successfully punched ${punchType}!${durationMessage}`, "success")

    // Play a success sound
    playPunchSound(punchType === "IN")

    // Clear the input for the next punch
    clearInput()

    // Refresh the activity displays
    await Promise.all([loadRecentActivity(), loadClockedInEmployees()])
  } catch (error) {
    console.error("Punch error:", error)
    showPunchStatus(error.message || "Error processing punch. Please try again.", "danger")

    // Play an error sound
    playErrorSound()
  }
}

// Play a sound for punch in/out
function playPunchSound(isIn) {
  // This is a placeholder - you would implement actual sound playing here
  console.log(`Playing ${isIn ? "punch in" : "punch out"} sound`)

  // Example implementation with Audio API:
  // const audio = new Audio(isIn ? '/sounds/punch-in.mp3' : '/sounds/punch-out.mp3');
  // audio.play();
}

// Play an error sound
function playErrorSound() {
  // This is a placeholder - you would implement actual sound playing here
  console.log("Playing error sound")

  // Example implementation with Audio API:
  // const audio = new Audio('/sounds/error.mp3');
  // audio.play();
}

// Show punch status message
function showPunchStatus(message, type) {
  const statusDiv = document.getElementById("punchStatus")
  if (!statusDiv) return

  statusDiv.className = `alert alert-${type} mt-3`
  statusDiv.innerHTML = message
  statusDiv.classList.remove("d-none")

  // Clear the status after 5 seconds
  setTimeout(() => {
    statusDiv.classList.add("d-none")
  }, 5000)
}

// Show a general error message
function showError(message) {
  const statusMessage = document.getElementById("statusMessage")
  if (statusMessage) {
    statusMessage.innerHTML = `
      <div class="alert alert-danger">
        <i class="bi bi-exclamation-triangle-fill me-2"></i>
        ${message}
      </div>
    `
  }
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
    if (!activityDiv) return

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

      // Format duration if available
      let durationHtml = ""
      if (item.type === "out" && item.duration_minutes) {
        const hours = Math.floor(item.duration_minutes / 60)
        const minutes = item.duration_minutes % 60
        durationHtml = `<div class="activity-duration">${hours}h ${minutes}m</div>`
      }

      activityHtml += `
        <div class="activity-item ${item.type === "in" ? "activity-in" : "activity-out"}">
          <div class="activity-time">${timeString}<br><small>${dateString}</small></div>
          <div class="activity-details">
            <div class="activity-name">${item.employee_name}</div>
            <div class="activity-type">Punched ${item.type.toUpperCase()}</div>
            ${durationHtml}
          </div>
        </div>
      `
    })

    activityDiv.innerHTML = activityHtml
  } catch (error) {
    console.error(error)
    const activityDiv = document.getElementById("recentActivity")
    if (activityDiv) {
      activityDiv.innerHTML = `
        <div class="alert alert-danger">
          <i class="bi bi-exclamation-triangle-fill me-2"></i>
          Error loading activity: ${error.message}
        </div>
      `
    }
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
    if (!clockedInDiv) return

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

      // Calculate time elapsed since punch in
      const now = new Date()
      const elapsedMinutes = Math.floor((now - punchTime) / 60000)
      const hours = Math.floor(elapsedMinutes / 60)
      const minutes = elapsedMinutes % 60
      const elapsedString = hours > 0 ? `${hours}h ${minutes}m` : `${minutes}m`

      employeesHtml += `
        <div class="clocked-in-item" data-employee-id="${emp.id}">
          <div class="employee-avatar ${emp.color || "block-blue"}">
            ${emp.name.charAt(0).toUpperCase()}
          </div>
          <div class="employee-details">
            <div class="employee-name">${emp.name}</div>
            <div class="employee-time">Since ${timeString} (${elapsedString})</div>
          </div>
        </div>
      `
    })

    clockedInDiv.innerHTML = employeesHtml
  } catch (error) {
    console.error(error)
    const clockedInDiv = document.getElementById("clockedInEmployees")
    if (clockedInDiv) {
      clockedInDiv.innerHTML = `
        <div class="alert alert-danger">
          <i class="bi bi-exclamation-triangle-fill me-2"></i>
          Error loading clocked in employees: ${error.message}
        </div>
      `
    }
  }
}

// Show employee details in a modal
function showEmployeeDetails(employeeId) {
  // Find the employee
  const employee = employeesData.find((emp) => emp.id === employeeId)
  if (!employee) {
    console.error(`Employee with ID ${employeeId} not found`)
    return
  }

  currentlyViewingEmployeeId = employeeId

  // Create modal HTML
  const modalHtml = `
    <div class="modal fade" id="employeeDetailsModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header ${employee.color || "block-blue"} text-white">
            <h5 class="modal-title">
              <i class="bi bi-person-badge me-2"></i> 
              ${employee.name}
            </h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="row">
              <div class="col-md-6">
                <h6>Employee Information</h6>
                <ul class="list-group mb-3">
                  <li class="list-group-item d-flex justify-content-between">
                    <span>ID:</span>
                    <strong>${employee.id}</strong>
                  </li>
                  ${
                    employee.custom_id
                      ? `
                    <li class="list-group-item d-flex justify-content-between">
                      <span>Punch Code:</span>
                      <strong>${employee.custom_id}</strong>
                    </li>
                  `
                      : ""
                  }
                  <li class="list-group-item d-flex justify-content-between">
                    <span>Role/Type:</span>
                    <strong>${employee.type || "Not specified"}</strong>
                  </li>
                </ul>
              </div>
              <div class="col-md-6">
                <h6>Current Status</h6>
                <div id="employeeCurrentStatus">
                  <div class="d-flex justify-content-center">
                    <div class="spinner-border text-primary" role="status">
                      <span class="visually-hidden">Loading...</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <h6 class="mt-3">Recent Activity</h6>
            <div id="employeeRecentActivity">
              <div class="d-flex justify-content-center">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            <button type="button" class="btn btn-primary" onclick="manualPunch(${employeeId})">
              <i class="bi bi-clock me-1"></i> Manual Punch
            </button>
          </div>
        </div>
      </div>
    </div>
  `

  // Remove any existing modal
  const existingModal = document.getElementById("employeeDetailsModal")
  if (existingModal) {
    existingModal.remove()
  }

  // Add the modal to the document
  document.body.insertAdjacentHTML("beforeend", modalHtml)

  // Show the modal
  const modalElement = document.getElementById("employeeDetailsModal")
  const modal = new bootstrap.Modal(modalElement)
  modal.show()

  // Load employee status and activity
  loadEmployeeStatus(employeeId)
  loadEmployeeActivity(employeeId)
}

// Load employee current status
async function loadEmployeeStatus(employeeId) {
  try {
    const response = await fetch(`/api/timeclock/status/${employeeId}`)

    if (!response.ok) {
      throw new Error("Failed to load employee status")
    }

    const data = await response.json()
    const statusDiv = document.getElementById("employeeCurrentStatus")

    if (!statusDiv) return

    const statusClass = data.status === "in" ? "success" : "secondary"
    const statusText = data.status === "in" ? "Clocked In" : "Clocked Out"
    const statusIcon = data.status === "in" ? "check-circle-fill" : "x-circle-fill"

    let timeInfo = ""
    if (data.last_punch) {
      const punchTime = new Date(data.last_punch)
      const timeString = punchTime.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
      const dateString = punchTime.toLocaleDateString([], { month: "short", day: "numeric" })

      // Calculate time elapsed if clocked in
      if (data.status === "in") {
        const now = new Date()
        const elapsedMinutes = Math.floor((now - punchTime) / 60000)
        const hours = Math.floor(elapsedMinutes / 60)
        const minutes = elapsedMinutes % 60
        const elapsedString = hours > 0 ? `${hours} hours ${minutes} minutes` : `${minutes} minutes`

        timeInfo = `<p class="mb-0">Elapsed time: ${elapsedString}</p>`
      }

      timeInfo = `
        <p class="mb-0">Last activity: ${timeString} on ${dateString}</p>
        ${timeInfo}
      `
    }

    statusDiv.innerHTML = `
      <div class="text-center">
        <div class="alert alert-${statusClass} d-inline-block">
          <i class="bi bi-${statusIcon} me-2"></i>
          <strong>${statusText}</strong>
        </div>
        ${timeInfo}
      </div>
    `
  } catch (error) {
    console.error(error)
    const statusDiv = document.getElementById("employeeCurrentStatus")
    if (statusDiv) {
      statusDiv.innerHTML = `
        <div class="alert alert-danger">
          <i class="bi bi-exclamation-triangle-fill me-2"></i>
          Error loading status: ${error.message}
        </div>
      `
    }
  }
}

// Load employee recent activity
async function loadEmployeeActivity(employeeId) {
  try {
    const response = await fetch("/api/timeclock/activity")

    if (!response.ok) {
      throw new Error("Failed to load activity")
    }

    const data = await response.json()
    const activityDiv = document.getElementById("employeeRecentActivity")

    if (!activityDiv) return

    // Filter activity for this employee
    const employeeActivity = data.activity.filter((item) => item.employee_id === employeeId)

    if (employeeActivity.length === 0) {
      activityDiv.innerHTML = `
        <div class="alert alert-info">
          <i class="bi bi-info-circle-fill me-2"></i>
          No recent activity for this employee
        </div>
      `
      return
    }

    // Create a table of activity
    let tableHtml = `
      <div class="table-responsive">
        <table class="table table-striped table-hover">
          <thead>
            <tr>
              <th>Date</th>
              <th>Time</th>
              <th>Action</th>
              <th>Duration</th>
            </tr>
          </thead>
          <tbody>
    `

    employeeActivity.forEach((item) => {
      const timestamp = new Date(item.timestamp)
      const timeString = timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
      const dateString = timestamp.toLocaleDateString([], { month: "short", day: "numeric" })

      const actionClass = item.type === "in" ? "success" : "danger"
      const actionText = item.type === "in" ? "Punch In" : "Punch Out"

      // Format duration if available
      let durationText = "—"
      if (item.type === "out" && item.duration_minutes) {
        const hours = Math.floor(item.duration_minutes / 60)
        const minutes = item.duration_minutes % 60
        durationText = hours > 0 ? `${hours}h ${minutes}m` : `${minutes}m`
      }

      tableHtml += `
        <tr>
          <td>${dateString}</td>
          <td>${timeString}</td>
          <td><span class="badge bg-${actionClass}">${actionText}</span></td>
          <td>${durationText}</td>
        </tr>
      `
    })

    tableHtml += `
          </tbody>
        </table>
      </div>
    `

    activityDiv.innerHTML = tableHtml
  } catch (error) {
    console.error(error)
    const activityDiv = document.getElementById("employeeRecentActivity")
    if (activityDiv) {
      activityDiv.innerHTML = `
        <div class="alert alert-danger">
          <i class="bi bi-exclamation-triangle-fill me-2"></i>
          Error loading activity: ${error.message}
        </div>
      `
    }
  }
}

// Manual punch for an employee (manager function)
async function manualPunch(employeeId) {
  try {
    // First confirm with the manager
    if (!confirm("Are you sure you want to record a manual punch for this employee?")) {
      return
    }

    // Perform the punch
    const response = await fetch("/api/timeclock/punch", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        employee_id: employeeId,
        timestamp: new Date().toISOString(),
        manual: true,
      }),
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || `Failed to process manual punch (status ${response.status})`)
    }

    const data = await response.json()

    // Show success message
    alert(`Manual ${data.punch.type.toUpperCase()} punch recorded successfully for ${data.employee.name}`)

    // Refresh the employee details
    loadEmployeeStatus(employeeId)
    loadEmployeeActivity(employeeId)

    // Also refresh the main displays
    loadRecentActivity()
    loadClockedInEmployees()
  } catch (error) {
    console.error("Manual punch error:", error)
    alert(`Error: ${error.message}`)
  }
}

// Generate a time clock report
async function generateReport(startDate, endDate) {
  try {
    // Format query parameters
    const params = new URLSearchParams()
    if (startDate) {
      params.append("start_date", startDate.toISOString())
    }
    if (endDate) {
      params.append("end_date", endDate.toISOString())
    }

    const response = await fetch(`/api/timeclock/report?${params.toString()}`)

    if (!response.ok) {
      throw new Error("Failed to generate report")
    }

    return await response.json()
  } catch (error) {
    console.error("Report generation error:", error)
    throw error
  }
}

