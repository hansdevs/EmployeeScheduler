// Store employees data globally for reference
let employeesData = []

// Load employees on page load
document.addEventListener("DOMContentLoaded", () => {
  loadEmployees()

  // Set up form submission
  const form = document.getElementById("addEmployeeForm")
  if (form) {
    form.addEventListener("submit", (e) => {
      e.preventDefault()
      addEmployee()
    })
  }
})

async function loadEmployees() {
  try {
    document.getElementById("statusMessage").innerHTML =
      '<div class="alert alert-info"><i class="bi bi-info-circle-fill me-2"></i>Loading employees...</div>'

    const response = await fetch("/api/employees")
    if (!response.ok) {
      throw new Error("Failed to load employees")
    }

    const data = await response.json()
    employeesData = data // Store for reference
    renderEmployees(data)

    document.getElementById("statusMessage").innerHTML = ""
  } catch (err) {
    console.error("Error loading employees:", err)
    document.getElementById("statusMessage").innerHTML =
      `<div class="alert alert-danger"><i class="bi bi-exclamation-triangle-fill me-2"></i>${err.message}</div>`
  }
}

function renderEmployees(employees) {
  const tbody = document.getElementById("empTableBody")
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
    document.getElementById("statusMessage").innerHTML =
      '<div class="alert alert-warning"><i class="bi bi-exclamation-triangle-fill me-2"></i>Employee name is required!</div>'
    document.getElementById("empName").focus()
    return
  }

  // Check if custom ID is already in use
  if (customId && employeesData.some((emp) => emp.custom_id === customId)) {
    document.getElementById("statusMessage").innerHTML =
      '<div class="alert alert-warning"><i class="bi bi-exclamation-triangle-fill me-2"></i>This ID/Punch Code is already in use!</div>'
    document.getElementById("empId").focus()
    return
  }

  // Show loading message
  document.getElementById("statusMessage").innerHTML =
    '<div class="alert alert-info"><i class="bi bi-info-circle-fill me-2"></i>Adding employee...</div>'

  // Create employee data
  const employeeData = {
    name: name,
    type: type,
    custom_id: customId || null,
    color: color,
  }

  // Send to server using jQuery AJAX
  $.ajax({
    url: "/api/employees",
    type: "POST",
    contentType: "application/json",
    data: JSON.stringify(employeeData),
    success: (response) => {
      // Clear form
      document.getElementById("empName").value = ""
      document.getElementById("empType").value = ""
      document.getElementById("empId").value = ""
      document.getElementById("empColor").value = "block-blue"

      // Show success message
      document.getElementById("statusMessage").innerHTML =
        '<div class="alert alert-success"><i class="bi bi-check-circle-fill me-2"></i>Employee added successfully!</div>'

      // Reload employees list
      loadEmployees()

      // Fade out message after 3 seconds
      setTimeout(() => {
        const msgDiv = document.getElementById("statusMessage")
        msgDiv.style.transition = "opacity 1s"
        msgDiv.style.opacity = "0"
        setTimeout(() => {
          msgDiv.innerHTML = ""
          msgDiv.style.opacity = "1"
        }, 1000)
      }, 3000)
    },
    error: (xhr, status, error) => {
      console.error("Error adding employee:", xhr.responseText)
      document.getElementById("statusMessage").innerHTML =
        `<div class="alert alert-danger"><i class="bi bi-exclamation-triangle-fill me-2"></i>Error adding employee: ${xhr.responseText}</div>`
    },
  })
}

function editEmployee(id) {
  // Find the employee in our data
  const employee = employeesData.find((emp) => emp.id === id)
  if (!employee) {
    alert("Employee not found!")
    return
  }

  // For now, we'll use a simple prompt-based approach
  const newName = prompt("Enter new name:", employee.name)
  if (newName === null) return // User cancelled

  const newType = prompt("Enter new role/type:", employee.type || "")
  const newId = prompt("Enter new ID/Punch Code:", employee.custom_id || "")

  // Check if the new ID is already in use by another employee
  if (newId && employeesData.some((emp) => emp.id !== id && emp.custom_id === newId)) {
    alert("This ID/Punch Code is already in use by another employee!")
    return
  }

  // Show loading message
  document.getElementById("statusMessage").innerHTML =
    '<div class="alert alert-info"><i class="bi bi-info-circle-fill me-2"></i>Updating employee...</div>'

  // Create update data
  const updateData = {
    name: newName.trim(),
    type: newType.trim(),
    custom_id: newId.trim() || null,
  }

  // Send to server using jQuery AJAX
  $.ajax({
    url: `/api/employees/${id}`,
    type: "PUT",
    contentType: "application/json",
    data: JSON.stringify(updateData),
    success: (response) => {
      // Show success message
      document.getElementById("statusMessage").innerHTML =
        '<div class="alert alert-success"><i class="bi bi-check-circle-fill me-2"></i>Employee updated successfully!</div>'

      // Reload employees list
      loadEmployees()

      // Fade out message after 3 seconds
      setTimeout(() => {
        const msgDiv = document.getElementById("statusMessage")
        msgDiv.style.transition = "opacity 1s"
        msgDiv.style.opacity = "0"
        setTimeout(() => {
          msgDiv.innerHTML = ""
          msgDiv.style.opacity = "1"
        }, 1000)
      }, 3000)
    },
    error: (xhr, status, error) => {
      console.error("Error updating employee:", xhr.responseText)
      document.getElementById("statusMessage").innerHTML =
        `<div class="alert alert-danger"><i class="bi bi-exclamation-triangle-fill me-2"></i>Error updating employee: ${xhr.responseText}</div>`
    },
  })
}

function removeEmployee(id) {
  // Basic confirmation
  if (!confirm("Are you sure you want to remove this employee?")) {
    return
  }

  // Show loading message
  document.getElementById("statusMessage").innerHTML =
    '<div class="alert alert-info"><i class="bi bi-info-circle-fill me-2"></i>Removing employee...</div>'

  // Send to server using jQuery AJAX
  $.ajax({
    url: `/api/employees/${id}`,
    type: "DELETE",
    success: (response) => {
      // Show success message
      document.getElementById("statusMessage").innerHTML =
        '<div class="alert alert-success"><i class="bi bi-check-circle-fill me-2"></i>Employee removed successfully!</div>'

      // Reload employees list
      loadEmployees()

      // Fade out message after 3 seconds
      setTimeout(() => {
        const msgDiv = document.getElementById("statusMessage")
        msgDiv.style.transition = "opacity 1s"
        msgDiv.style.opacity = "0"
        setTimeout(() => {
          msgDiv.innerHTML = ""
          msgDiv.style.opacity = "1"
        }, 1000)
      }, 3000)
    },
    error: (xhr, status, error) => {
      console.error("Error removing employee:", xhr.responseText)
      document.getElementById("statusMessage").innerHTML =
        `<div class="alert alert-danger"><i class="bi bi-exclamation-triangle-fill me-2"></i>Error removing employee: ${xhr.responseText}</div>`
    },
  })
}

function saveTimeclockSettings() {
  const enforceSchedule = document.getElementById("enforceSchedule").checked
  const allowRemotePunch = document.getElementById("allowRemotePunch").checked
  const requirePhoto = document.getElementById("requirePhoto").checked

  // Show loading message
  document.getElementById("statusMessage").innerHTML =
    '<div class="alert alert-info"><i class="bi bi-info-circle-fill me-2"></i>Saving time clock settings...</div>'

  // Send to server using jQuery AJAX
  $.ajax({
    url: "/api/timeclock/settings",
    type: "POST",
    contentType: "application/json",
    data: JSON.stringify({
      enforce_schedule: enforceSchedule,
      allow_remote_punch: allowRemotePunch,
      require_photo: requirePhoto,
    }),
    success: (response) => {
      // Show success message
      document.getElementById("statusMessage").innerHTML =
        '<div class="alert alert-success"><i class="bi bi-check-circle-fill me-2"></i>Time clock settings saved successfully!</div>'

      // Fade out message after 3 seconds
      setTimeout(() => {
        const msgDiv = document.getElementById("statusMessage")
        msgDiv.style.transition = "opacity 1s"
        msgDiv.style.opacity = "0"
        setTimeout(() => {
          msgDiv.innerHTML = ""
          msgDiv.style.opacity = "1"
        }, 1000)
      }, 3000)
    },
    error: (xhr, status, error) => {
      console.error("Error saving time clock settings:", xhr.responseText)
      document.getElementById("statusMessage").innerHTML =
        `<div class="alert alert-danger"><i class="bi bi-exclamation-triangle-fill me-2"></i>Error saving time clock settings: ${xhr.responseText}</div>`
    },
  })
}

