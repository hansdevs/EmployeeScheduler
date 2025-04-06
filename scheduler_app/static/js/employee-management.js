// Store employees data globally for reference
let employeesData = []

// Load employees on page load
document.addEventListener("DOMContentLoaded", () => {
  loadEmployees()

  // Set up form submission
  const form = document.getElementById("addEmployeeForm") || document.getElementById("employeeForm")
  if (form) {
    form.addEventListener("submit", (e) => {
      e.preventDefault()
      addEmployee()
    })
  }
})

async function loadEmployees() {
  try {
    const statusMessage = document.getElementById("statusMessage")
    if (statusMessage) {
      statusMessage.innerHTML =
        '<div class="alert alert-info"><i class="bi bi-info-circle-fill me-2"></i>Loading employees...</div>'
    }

    const response = await fetch("../api/employees")
    if (!response.ok) {
      throw new Error("Failed to load employees")
    }

    const data = await response.json()
    employeesData = data // Store for reference
    renderEmployees(data)

    if (statusMessage) {
      statusMessage.innerHTML = ""
    }
  } catch (err) {
    console.error("Error loading employees:", err)
    const statusMessage = document.getElementById("statusMessage")
    if (statusMessage) {
      statusMessage.innerHTML = `<div class="alert alert-danger"><i class="bi bi-exclamation-triangle-fill me-2"></i>${err.message}</div>`
    }
  }
}

function renderEmployees(employees) {
  const tbody = document.getElementById("empTableBody")
  if (!tbody) return

  tbody.innerHTML = ""

  if (!employees || employees.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="5">
          <div class="empty-state">
            <i class="bi bi-people"></i>
            <h4>No employees found</h4>
            <p>Add your first employee using the form below</p>
          </div>
        </td>
      </tr>
    `
    return
  }

  employees.forEach((emp) => {
    const colorClass = emp.color || "block-blue"
    const colorName = colorClass.replace("block-", "")

    const tr = document.createElement("tr")
    tr.innerHTML = `
      <td>
        <span class="badge bg-dark">${emp.custom_id || emp.id}</span>
        ${emp.custom_id ? `<small class="text-muted d-block">(System ID: ${emp.id})</small>` : ""}
      </td>
      <td>${emp.name}</td>
      <td>${emp.type || '<span class="text-muted">Not specified</span>'}</td>
      <td>
        <span class="color-preview ${colorClass}"></span>
        ${colorName.charAt(0).toUpperCase() + colorName.slice(1)}
      </td>
      <td>
        <button class="btn btn-sm btn-outline-primary me-1" onclick="editEmployee(${emp.id})">
          <i class="bi bi-pencil me-1"></i> Edit
        </button>
        <button class="btn btn-sm btn-danger" onclick="removeEmployee(${emp.id})">
          <i class="bi bi-trash me-1"></i> Remove
        </button>
        <button class="btn btn-sm btn-outline-info" onclick="viewEmployeeTimecard(${emp.id})">
          <i class="bi bi-clock-history me-1"></i> Timecard
        </button>
      </td>
    `
    tbody.appendChild(tr)
  })
}

function addEmployee() {
  // Get form values
  const name = document.getElementById("empName").value.trim()
  const type = document.getElementById("empType").value.trim()
  const customId = document.getElementById("empId").value.trim()
  const color = document.getElementById("empColor").value

  // Validate
  if (!name) {
    showStatusMessage("Employee name is required!", "warning")
    document.getElementById("empName").focus()
    return
  }

  // Check if custom ID is already in use
  if (customId && employeesData.some((emp) => emp.custom_id === customId)) {
    showStatusMessage("This ID/Punch Code is already in use!", "warning")
    document.getElementById("empId").focus()
    return
  }

  // Show loading message
  showStatusMessage("Adding employee...", "info")

  // Create employee data
  const employeeData = {
    name: name,
    type: type,
    custom_id: customId || null,
    color: color,
  }

  // Send to server
  fetch("../api/employees", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(employeeData),
  })
    .then((response) => {
      if (!response.ok) {
        return response.text().then((text) => {
          throw new Error(text || "Failed to add employee")
        })
      }
      return response.json()
    })
    .then((data) => {
      // Clear form
      document.getElementById("empName").value = ""
      document.getElementById("empType").value = ""
      document.getElementById("empId").value = ""
      document.getElementById("empColor").value = "block-blue"

      // Show success message
      showStatusMessage("Employee added successfully!", "success")

      // Reload employees list
      loadEmployees()
    })
    .catch((error) => {
      console.error("Error adding employee:", error)
      showStatusMessage(`Error adding employee: ${error.message}`, "danger")
    })
}

function editEmployee(id) {
  // Find the employee in our data
  const employee = employeesData.find((emp) => emp.id === id)
  if (!employee) {
    alert("Employee not found!")
    return
  }

  // Create a modal for editing
  const modalHtml = `
    <div class="modal fade" id="editEmployeeModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Edit Employee</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <form id="editEmployeeForm">
              <div class="mb-3">
                <label for="editEmpName" class="form-label">Name</label>
                <input type="text" class="form-control" id="editEmpName" value="${employee.name}" required>
              </div>
              <div class="mb-3">
                <label for="editEmpType" class="form-label">Role/Type</label>
                <input type="text" class="form-control" id="editEmpType" value="${employee.type || ""}">
              </div>
              <div class="mb-3">
                <label for="editEmpId" class="form-label">ID/Punch Code</label>
                <input type="text" class="form-control" id="editEmpId" value="${employee.custom_id || ""}">
                <small class="text-muted">Used for time clock punch in/out</small>
              </div>
              <div class="mb-3">
                <label for="editEmpColor" class="form-label">Color</label>
                <select id="editEmpColor" class="form-select">
                  <option value="block-blue" ${employee.color === "block-blue" ? "selected" : ""}>Blue</option>
                  <option value="block-green" ${employee.color === "block-green" ? "selected" : ""}>Green</option>
                  <option value="block-purple" ${employee.color === "block-purple" ? "selected" : ""}>Purple</option>
                  <option value="block-orange" ${employee.color === "block-orange" ? "selected" : ""}>Orange</option>
                  <option value="block-red" ${employee.color === "block-red" ? "selected" : ""}>Red</option>
                  <option value="block-yellow" ${employee.color === "block-yellow" ? "selected" : ""}>Yellow</option>
                </select>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-primary" onclick="saveEmployeeEdit(${employee.id})">Save Changes</button>
          </div>
        </div>
      </div>
    </div>
  `

  // Remove any existing modal
  const existingModal = document.getElementById("editEmployeeModal")
  if (existingModal) {
    existingModal.remove()
  }

  // Add the modal to the document
  document.body.insertAdjacentHTML("beforeend", modalHtml)

  // Show the modal
  const modalElement = document.getElementById("editEmployeeModal")
  const modal = new bootstrap.Modal(modalElement)
  modal.show()
}

function saveEmployeeEdit(id) {
  const name = document.getElementById("editEmpName").value.trim()
  const type = document.getElementById("editEmpType").value.trim()
  const customId = document.getElementById("editEmpId").value.trim()
  const color = document.getElementById("editEmpColor").value

  // Validate
  if (!name) {
    alert("Employee name is required!")
    document.getElementById("editEmpName").focus()
    return
  }

  // Check if custom ID is already in use by another employee
  if (customId && employeesData.some((emp) => emp.id !== id && emp.custom_id === customId)) {
    alert("This ID/Punch Code is already in use by another employee!")
    document.getElementById("editEmpId").focus()
    return
  }

  // Show loading message
  showStatusMessage("Updating employee...", "info")

  // Create update data
  const updateData = {
    name: name,
    type: type,
    custom_id: customId || null,
    color: color,
  }

  // Send to server
  fetch(`../api/employees/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(updateData),
  })
    .then((response) => {
      if (!response.ok) {
        return response.text().then((text) => {
          throw new Error(text || "Failed to update employee")
        })
      }
      return response.json()
    })
    .then((data) => {
      // Close the modal
      const modalElement = document.getElementById("editEmployeeModal")
      // Access the Bootstrap modal instance using the static method
      const modal = bootstrap.Modal.getInstance(modalElement)
      modal.hide()

      // Show success message
      showStatusMessage("Employee updated successfully!", "success")

      // Reload employees list
      loadEmployees()
    })
    .catch((error) => {
      console.error("Error updating employee:", error)
      showStatusMessage(`Error updating employee: ${error.message}`, "danger")
    })
}

function removeEmployee(id) {
  // Basic confirmation
  if (!confirm("Are you sure you want to remove this employee?")) {
    return
  }

  // Show loading message
  showStatusMessage("Removing employee...", "info")

  // Send to server
  fetch(`../api/employees/${id}`, {
    method: "DELETE",
  })
    .then((response) => {
      if (!response.ok) {
        return response.text().then((text) => {
          throw new Error(text || "Failed to remove employee")
        })
      }
      return response.json()
    })
    .then((data) => {
      // Show success message
      showStatusMessage("Employee removed successfully!", "success")

      // Reload employees list
      loadEmployees()
    })
    .catch((error) => {
      console.error("Error removing employee:", error)
      showStatusMessage(`Error removing employee: ${error.message}`, "danger")
    })
}

function saveTimeclockSettings() {
  const enforceSchedule = document.getElementById("enforceSchedule").checked
  const allowRemotePunch = document.getElementById("allowRemotePunch").checked
  const requirePhoto = document.getElementById("requirePhoto").checked

  // Show loading message
  showStatusMessage("Saving time clock settings...", "info")

  // Send to server
  fetch("../api/timeclock/settings", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      enforce_schedule: enforceSchedule,
      allow_remote_punch: allowRemotePunch,
      require_photo: requirePhoto,
    }),
  })
    .then((response) => {
      if (!response.ok) {
        return response.text().then((text) => {
          throw new Error(text || "Failed to save settings")
        })
      }
      return response.json()
    })
    .then((data) => {
      // Show success message
      showStatusMessage("Time clock settings saved successfully!", "success")
    })
    .catch((error) => {
      console.error("Error saving time clock settings:", error)
      showStatusMessage(`Error saving time clock settings: ${error.message}`, "danger")
    })
}

function viewEmployeeTimecard(id) {
  // Find the employee in our data
  const employee = employeesData.find((emp) => emp.id === id)
  if (!employee) {
    alert("Employee not found!")
    return
  }

  // Create a modal for the timecard
  const modalHtml = `
    <div class="modal fade" id="timecardModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header ${employee.color || "block-blue"} text-white">
            <h5 class="modal-title">
              <i class="bi bi-clock-history me-2"></i> 
              Timecard: ${employee.name}
            </h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="row mb-3">
              <div class="col-md-6">
                <div class="input-group">
                  <span class="input-group-text">Start Date</span>
                  <input type="date" id="timecardStartDate" class="form-control">
                </div>
              </div>
              <div class="col-md-6">
                <div class="input-group">
                  <span class="input-group-text">End Date</span>
                  <input type="date" id="timecardEndDate" class="form-control">
                </div>
              </div>
            </div>
            <button class="btn btn-primary mb-3" onclick="generateTimecardReport(${id})">
              <i class="bi bi-search me-1"></i> Generate Report
            </button>
            
            <div id="timecardReport">
              <div class="alert alert-info">
                <i class="bi bi-info-circle-fill me-2"></i>
                Select a date range and click "Generate Report" to view timecard data
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            <button type="button" class="btn btn-success" onclick="exportTimecardToCsv(${id})">
              <i class="bi bi-file-earmark-excel me-1"></i> Export to CSV
            </button>
          </div>
        </div>
      </div>
    </div>
  `

  // Remove any existing modal
  const existingModal = document.getElementById("timecardModal")
  if (existingModal) {
    existingModal.remove()
  }

  // Add the modal to the document
  document.body.insertAdjacentHTML("beforeend", modalHtml)

  // Set default date range (last 7 days)
  const today = new Date()
  const lastWeek = new Date()
  lastWeek.setDate(today.getDate() - 7)

  document.getElementById("timecardEndDate").valueAsDate = today
  document.getElementById("timecardStartDate").valueAsDate = lastWeek

  // Show the modal
  const modalElement = document.getElementById("timecardModal")
  const modal = new bootstrap.Modal(modalElement)
  modal.show()
}

async function generateTimecardReport(employeeId) {
  const startDateInput = document.getElementById("timecardStartDate")
  const endDateInput = document.getElementById("timecardEndDate")

  if (!startDateInput.value || !endDateInput.value) {
    alert("Please select both start and end dates")
    return
  }

  const startDate = new Date(startDateInput.value)
  const endDate = new Date(endDateInput.value)
  endDate.setHours(23, 59, 59) // Set to end of day

  if (startDate > endDate) {
    alert("Start date must be before end date")
    return
  }

  try {
    const reportDiv = document.getElementById("timecardReport")
    reportDiv.innerHTML = `
      <div class="d-flex justify-content-center">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
    `

    // Format query parameters
    const params = new URLSearchParams()
    params.append("start_date", startDate.toISOString())
    params.append("end_date", endDate.toISOString())

    const response = await fetch(`/api/timeclock/report?${params.toString()}`)

    if (!response.ok) {
      throw new Error("Failed to generate report")
    }

    const data = await response.json()

    // Find this employee's data
    const employeeData = data.report.employees[employeeId]

    if (!employeeData) {
      reportDiv.innerHTML = `
        <div class="alert alert-info">
          <i class="bi bi-info-circle-fill me-2"></i>
          No time clock data found for this employee in the selected date range
        </div>
      `
      return
    }

    // Format the report
    let reportHtml = `
      <div class="card mb-3">
        <div class="card-body">
          <h5 class="card-title">Summary</h5>
          <p class="card-text">
            <strong>Total Hours:</strong> ${employeeData.hours}<br>
            <strong>Period:</strong> ${formatDate(startDate)} to ${formatDate(endDate)}
          </p>
        </div>
      </div>
      
      <h5>Punch Details</h5>
    `

    if (!employeeData.punch_pairs || employeeData.punch_pairs.length === 0) {
      reportHtml += `
        <div class="alert alert-info">
          <i class="bi bi-info-circle-fill me-2"></i>
          No punch pairs found for this employee in the selected date range
        </div>
      `
    } else {
      reportHtml += `
        <div class="table-responsive">
          <table class="table table-striped table-hover">
            <thead>
              <tr>
                <th>Date</th>
                <th>Punch In</th>
                <th>Punch Out</th>
                <th>Duration</th>
              </tr>
            </thead>
            <tbody>
      `

      employeeData.punch_pairs.forEach((pair) => {
        const inTime = new Date(pair.in)
        const outTime = new Date(pair.out)

        const dateStr = formatDate(inTime)
        const inTimeStr = formatTime(inTime)
        const outTimeStr = formatTime(outTime)

        const hours = Math.floor(pair.duration_minutes / 60)
        const minutes = pair.duration_minutes % 60
        const durationStr = hours > 0 ? `${hours}h ${minutes}m` : `${minutes}m`

        reportHtml += `
          <tr>
            <td>${dateStr}</td>
            <td>${inTimeStr}</td>
            <td>${outTimeStr}</td>
            <td>${durationStr}</td>
          </tr>
        `
      })

      reportHtml += `
            </tbody>
          </table>
        </div>
      `
    }

    reportDiv.innerHTML = reportHtml
  } catch (error) {
    console.error("Report generation error:", error)
    const reportDiv = document.getElementById("timecardReport")
    reportDiv.innerHTML = `
      <div class="alert alert-danger">
        <i class="bi bi-exclamation-triangle-fill me-2"></i>
        Error generating report: ${error.message}
      </div>
    `
  }
}

function exportTimecardToCsv(employeeId) {
  alert("CSV export functionality will be implemented in a future update.")
}

// Helper function to format dates
function formatDate(date) {
  return date.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  })
}

// Helper function to format times
function formatTime(date) {
  return date.toLocaleTimeString(undefined, {
    hour: "2-digit",
    minute: "2-digit",
  })
}

// Helper function to show status messages
function showStatusMessage(message, type) {
  const statusMessage = document.getElementById("statusMessage")
  if (!statusMessage) return

  statusMessage.innerHTML = `
    <div class="alert alert-${type}">
      <i class="bi bi-${getIconForType(type)} me-2"></i>
      ${message}
    </div>
  `

  // Fade out the message after 3 seconds for success messages
  if (type === "success") {
    setTimeout(() => {
      statusMessage.style.transition = "opacity 1s"
      statusMessage.style.opacity = "0"
      setTimeout(() => {
        statusMessage.innerHTML = ""
        statusMessage.style.opacity = "1"
      }, 1000)
    }, 3000)
  }
}

// Helper function to get the appropriate icon for message type
function getIconForType(type) {
  switch (type) {
    case "success":
      return "check-circle-fill"
    case "warning":
      return "exclamation-triangle-fill"
    case "danger":
      return "exclamation-triangle-fill"
    case "info":
      return "info-circle-fill"
    default:
      return "info-circle-fill"
  }
}

// Show time clock modal
function showTimeclockModal() {
  const modalElement = document.getElementById("timeclockModal")
  const modal = new bootstrap.Modal(modalElement)
  modal.show()
}

// Show API documentation
function showApiDocs() {
  alert("API documentation will be available in a future update.")
}

