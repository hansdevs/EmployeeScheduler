// Store employees data globally for reference
let employeesData = []

async function loadEmployees() {
  try {
    document.getElementById("statusMessage").innerHTML =
      '<div class="alert alert-info"><i class="bi bi-info-circle-fill me-2"></i>Loading employees...</div>'

    const res = await fetch("/api/employees")
    if (!res.ok) {
      throw new Error("Failed to load employees")
    }

    const data = await res.json()
    employeesData = data // Store for reference
    renderEmployees(data)

    document.getElementById("statusMessage").innerHTML = ""
  } catch (err) {
    console.error(err)
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

async function addEmployee() {
  const nameInput = document.getElementById("empName")
  const typeInput = document.getElementById("empType")
  const idInput = document.getElementById("empId")
  const colorInput = document.getElementById("empColor")

  const newName = nameInput.value.trim()
  const newType = typeInput.value.trim()
  const newId = idInput.value.trim()
  const newColor = colorInput.value

  if (!newName) {
    document.getElementById("statusMessage").innerHTML =
      '<div class="alert alert-warning"><i class="bi bi-exclamation-triangle-fill me-2"></i>Employee name is required!</div>'
    nameInput.focus()
    return
  }

  // Check if custom ID is already in use
  if (newId && employeesData.some((emp) => emp.custom_id === newId)) {
    document.getElementById("statusMessage").innerHTML =
      '<div class="alert alert-warning"><i class="bi bi-exclamation-triangle-fill me-2"></i>This ID/Punch Code is already in use!</div>'
    idInput.focus()
    return
  }

  try {
    document.getElementById("statusMessage").innerHTML =
      '<div class="alert alert-info"><i class="bi bi-info-circle-fill me-2"></i>Adding employee...</div>'

    const res = await fetch("/api/employees", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: newName,
        type: newType,
        custom_id: newId || null,
        color: newColor,
      }),
    })

    if (!res.ok) {
      throw new Error("Failed to add employee")
    }

    const data = await res.json()
    console.log("Employee added:", data)

    // Clear input fields
    nameInput.value = ""
    typeInput.value = ""
    idInput.value = ""
    colorInput.value = "block-blue"

    // Show success message
    document.getElementById("statusMessage").innerHTML =
      '<div class="alert alert-success"><i class="bi bi-check-circle-fill me-2"></i>Employee added successfully!</div>'

    // Reload the employees list
    loadEmployees()

    // Fade out the message after 3 seconds
    setTimeout(() => {
      const msgDiv = document.getElementById("statusMessage")
      msgDiv.style.transition = "opacity 1s"
      msgDiv.style.opacity = "0"
      setTimeout(() => {
        msgDiv.innerHTML = ""
        msgDiv.style.opacity = "1"
      }, 1000)
    }, 3000)
  } catch (err) {
    console.error(err)
    document.getElementById("statusMessage").innerHTML =
      `<div class="alert alert-danger"><i class="bi bi-exclamation-triangle-fill me-2"></i>${err.message}</div>`
  }
}

function editEmployee(id) {
  // Find the employee in our data
  const employee = employeesData.find((emp) => emp.id === id)
  if (!employee) {
    alert("Employee not found!")
    return
  }

  // For now, we'll use a simple prompt-based approach
  // In a real app, you'd use a modal form similar to the add form
  const newName = prompt("Enter new name:", employee.name)
  if (newName === null) return // User cancelled

  const newType = prompt("Enter new role/type:", employee.type || "")
  const newId = prompt("Enter new ID/Punch Code:", employee.custom_id || "")

  // Check if the new ID is already in use by another employee
  if (newId && employeesData.some((emp) => emp.id !== id && emp.custom_id === newId)) {
    alert("This ID/Punch Code is already in use by another employee!")
    return
  }

  // Update the employee
  updateEmployee(id, {
    name: newName.trim(),
    type: newType.trim(),
    custom_id: newId.trim() || null,
  })
}

async function updateEmployee(id, updates) {
  try {
    document.getElementById("statusMessage").innerHTML =
      '<div class="alert alert-info"><i class="bi bi-info-circle-fill me-2"></i>Updating employee...</div>'

    const res = await fetch(`/api/employees/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updates),
    })

    if (!res.ok) {
      throw new Error("Failed to update employee")
    }

    // Show success message
    document.getElementById("statusMessage").innerHTML =
      '<div class="alert alert-success"><i class="bi bi-check-circle-fill me-2"></i>Employee updated successfully!</div>'

    // Reload the employees list
    loadEmployees()

    // Fade out the message after 3 seconds
    setTimeout(() => {
      const msgDiv = document.getElementById("statusMessage")
      msgDiv.style.transition = "opacity 1s"
      msgDiv.style.opacity = "0"
      setTimeout(() => {
        msgDiv.innerHTML = ""
        msgDiv.style.opacity = "1"
      }, 1000)
    }, 3000)
  } catch (err) {
    console.error(err)
    document.getElementById("statusMessage").innerHTML =
      `<div class="alert alert-danger"><i class="bi bi-exclamation-triangle-fill me-2"></i>${err.message}</div>`
  }
}

async function removeEmployee(id) {
  // Basic confirmation
  if (!confirm("Are you sure you want to remove this employee?")) {
    return
  }

  try {
    document.getElementById("statusMessage").innerHTML =
      '<div class="alert alert-info"><i class="bi bi-info-circle-fill me-2"></i>Removing employee...</div>'

    const res = await fetch("/api/employees/" + id, {
      method: "DELETE",
    })

    if (!res.ok) {
      throw new Error("Failed to remove employee")
    }

    console.log(`Employee ${id} removed`)

    document.getElementById("statusMessage").innerHTML =
      '<div class="alert alert-success"><i class="bi bi-check-circle-fill me-2"></i>Employee removed successfully!</div>'

    // Reload the employees list
    loadEmployees()

    // Fade out the message after 3 seconds
    setTimeout(() => {
      const msgDiv = document.getElementById("statusMessage")
      msgDiv.style.transition = "opacity 1s"
      msgDiv.style.opacity = "0"
      setTimeout(() => {
        msgDiv.innerHTML = ""
        msgDiv.style.opacity = "1"
      }, 1000)
    }, 3000)
  } catch (err) {
    console.error(err)
    document.getElementById("statusMessage").innerHTML =
      `<div class="alert alert-danger"><i class="bi bi-exclamation-triangle-fill me-2"></i>${err.message}</div>`
  }
}

// Time Clock Modal Functions
let timeclockModal

function showTimeclockModal() {
  // Initialize the modal if not already done
  if (!timeclockModal) {
    timeclockModal = new bootstrap.Modal(document.getElementById("timeclockModal"))
  }

  // Update the current time and date
  updateTimeclockTime()

  // Show the modal
  timeclockModal.show()

  // Focus the input field
  setTimeout(() => {
    document.getElementById("punchIdInput").focus()
  }, 500)
}

function updateTimeclockTime() {
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

// Start the clock update interval when the modal is shown
document.addEventListener("DOMContentLoaded", () => {
  const timeclockModalEl = document.getElementById("timeclockModal")
  if (timeclockModalEl) {
    timeclockModalEl.addEventListener("shown.bs.modal", () => {
      window.timeclockInterval = setInterval(updateTimeclockTime, 1000)
    })

    // Clear the interval when the modal is hidden
    timeclockModalEl.addEventListener("hidden.bs.modal", () => {
      clearInterval(window.timeclockInterval)
    })
  }
})

async function processPunch() {
  const punchId = document.getElementById("punchIdInput").value.trim()
  if (!punchId) {
    showPunchStatus("Please enter your ID/Punch Code", "warning")
    return
  }

  // Find the employee by custom_id or regular id
  const employee = employeesData.find((emp) => String(emp.custom_id) === punchId || String(emp.id) === punchId)

  if (!employee) {
    showPunchStatus("Invalid ID/Punch Code. Please try again.", "danger")
    return
  }

  try {
    // In a real app, this would call the API
    // For now, we'll simulate a successful punch

    // Determine if this is a punch in or out (randomly for demo)
    const isPunchIn = Math.random() > 0.5

    showPunchStatus(`${isPunchIn ? "Punch IN" : "Punch OUT"} successful for ${employee.name}!`, "success")

    // Clear the input for the next punch
    document.getElementById("punchIdInput").value = ""
    document.getElementById("punchIdInput").focus()
  } catch (err) {
    console.error(err)
    showPunchStatus("Error processing punch. Please try again.", "danger")
  }
}

function showPunchStatus(message, type) {
  const statusDiv = document.getElementById("punchStatus")
  statusDiv.className = `alert alert-${type}`
  statusDiv.innerHTML = message
  statusDiv.classList.remove("d-none")

  // Clear the status after 5 seconds
  setTimeout(() => {
    statusDiv.classList.add("d-none")
  }, 5000)
}

function saveTimeclockSettings() {
  const enforceSchedule = document.getElementById("enforceSchedule").checked
  const allowRemotePunch = document.getElementById("allowRemotePunch").checked
  const requirePhoto = document.getElementById("requirePhoto").checked

  // In a real app, this would save to the API
  // For now, just show a success message
  document.getElementById("statusMessage").innerHTML =
    '<div class="alert alert-success"><i class="bi bi-check-circle-fill me-2"></i>Time clock settings saved successfully!</div>'

  // Fade out the message after 3 seconds
  setTimeout(() => {
    const msgDiv = document.getElementById("statusMessage")
    msgDiv.style.transition = "opacity 1s"
    msgDiv.style.opacity = "0"
    setTimeout(() => {
      msgDiv.innerHTML = ""
      msgDiv.style.opacity = "1"
    }, 1000)
  }, 3000)
}

function showApiDocs() {
  alert("API documentation would open here in a real application.")
}

// Auto-load employees when the page loads
document.addEventListener("DOMContentLoaded", () => {
  loadEmployees()
})

