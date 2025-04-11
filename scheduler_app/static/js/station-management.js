/**
 * Station Management
 * Handles position/station data management functionality
 */

// Store stations data globally for reference
let stationsData = []

// Load stations on page load
document.addEventListener("DOMContentLoaded", () => {
  loadStations()

  // Make the type select searchable if Select2 is available
  try {
    const typeSelect = document.getElementById("stationType")
    if (typeSelect && typeof $.fn.select2 !== "undefined") {
      $(typeSelect).select2({
        tags: true,
        placeholder: "Select or type a category",
        allowClear: true,
      })
    }

    const editTypeSelect = document.getElementById("editStationType")
    if (editTypeSelect && typeof $.fn.select2 !== "undefined") {
      $(editTypeSelect).select2({
        tags: true,
        placeholder: "Select or type a category",
        allowClear: true,
        dropdownParent: $("#editStationModal"),
      })
    }
  } catch (e) {
    console.log("Select2 not available, using standard select inputs")
  }
})

async function loadStations() {
  try {
    document.getElementById("statusMessage").innerHTML =
      '<div class="alert alert-info"><i class="bi bi-info-circle-fill me-2"></i>Loading positions/stations...</div>'

    const response = await fetch("../api/stations")
    if (!response.ok) {
      throw new Error("Failed to load positions/stations")
    }

    const stations = await response.json()
    stationsData = stations // Store for reference
    renderStations(stations)

    document.getElementById("statusMessage").innerHTML = ""
  } catch (error) {
    console.error(error)
    document.getElementById("statusMessage").innerHTML =
      `<div class="alert alert-danger"><i class="bi bi-exclamation-triangle-fill me-2"></i>${error.message}</div>`
  }
}

function renderStations(stations) {
  const tbody = document.getElementById("stationsBody")
  tbody.innerHTML = "" // clear existing rows

  if (!stations || stations.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="4">
          <div class="empty-state">
            <i class="bi bi-building"></i>
            <h4>No positions/stations yet</h4>
            <p>Add your first position/station using the form below</p>
          </div>
        </td>
      </tr>
    `
    return
  }

  stations.forEach((st) => {
    const row = document.createElement("tr")
    row.innerHTML = `
      <td>${st.id}</td>
      <td>${st.name}</td>
      <td>${st.type ? `<span class="station-badge">${st.type}</span>` : '<span class="text-muted">Not specified</span>'}</td>
      <td>
        <button class="btn btn-sm btn-outline-primary me-1" onclick="editStation(${st.id})">
          <i class="bi bi-pencil me-1"></i> Edit
        </button>
        <button class="btn btn-sm btn-danger" onclick="deleteStation(${st.id})">
          <i class="bi bi-trash me-1"></i> Delete
        </button>
        <button class="btn btn-sm btn-outline-info" onclick="viewStationWorkflow(${st.id})">
          <i class="bi bi-diagram-3 me-1"></i> Workflow
        </button>
      </td>
    `
    tbody.appendChild(row)
  })
}

async function addStation() {
  const name = document.getElementById("stationName").value.trim()
  const type = document.getElementById("stationType").value.trim()

  if (!name) {
    document.getElementById("statusMessage").innerHTML =
      '<div class="alert alert-warning"><i class="bi bi-exclamation-triangle-fill me-2"></i>Position/station name is required!</div>'
    document.getElementById("stationName").focus()
    return
  }

  try {
    document.getElementById("statusMessage").innerHTML =
      '<div class="alert alert-info"><i class="bi bi-info-circle-fill me-2"></i>Adding position/station...</div>'

    const response = await fetch("../api/stations", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        name: name,
        type: type,
      }),
    })

    if (!response.ok) {
      throw new Error("Failed to add position/station")
    }

    const data = await response.json()
    console.log("Position/station added:", data)

    // Clear form inputs
    document.getElementById("stationName").value = ""
    document.getElementById("stationType").value = ""

    // If using Select2, reset the select
    try {
      if (typeof $.fn.select2 !== "undefined") {
        $(document.getElementById("stationType")).val("").trigger("change")
      }
    } catch (e) {
      console.log("Select2 not available")
    }

    // Show success message
    document.getElementById("statusMessage").innerHTML =
      '<div class="alert alert-success"><i class="bi bi-check-circle-fill me-2"></i>Position/station added successfully!</div>'

    // Reload the stations
    loadStations()

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
  } catch (error) {
    console.error(error)
    document.getElementById("statusMessage").innerHTML =
      `<div class="alert alert-danger"><i class="bi bi-exclamation-triangle-fill me-2"></i>${error.message}</div>`
  }
}

function editStation(id) {
  // Find the station in our data
  const station = stationsData.find((st) => st.id === id)
  if (!station) {
    alert("Position/station not found!")
    return
  }

  // Populate the edit form
  document.getElementById("editStationId").value = station.id
  document.getElementById("editStationName").value = station.name

  // Set the type in the select dropdown
  const editTypeSelect = document.getElementById("editStationType")
  editTypeSelect.value = station.type || ""

  // If using Select2, update the select
  try {
    if (typeof $.fn.select2 !== "undefined") {
      $(editTypeSelect)
        .val(station.type || "")
        .trigger("change")
    }
  } catch (e) {
    console.log("Select2 not available")
  }

  // Show the modal
  const modalElement = document.getElementById("editStationModal")
  const modal = new bootstrap.Modal(modalElement)
  modal.show()
}

async function saveStationEdit() {
  const id = Number.parseInt(document.getElementById("editStationId").value)
  const name = document.getElementById("editStationName").value.trim()
  const type = document.getElementById("editStationType").value.trim()

  if (!name) {
    alert("Position/station name is required!")
    document.getElementById("editStationName").focus()
    return
  }

  try {
    document.getElementById("statusMessage").innerHTML =
      '<div class="alert alert-info"><i class="bi bi-info-circle-fill me-2"></i>Updating position/station...</div>'

    const response = await fetch(`../api/stations/${id}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        name: name,
        type: type,
      }),
    })

    if (!response.ok) {
      throw new Error("Failed to update position/station")
    }

    const data = await response.json()
    console.log("Position/station updated:", data)

    // Close the modal
    const modalElement = document.getElementById("editStationModal")
    const modal = bootstrap.Modal.getInstance(modalElement)
    modal.hide()

    // Show success message
    document.getElementById("statusMessage").innerHTML =
      '<div class="alert alert-success"><i class="bi bi-check-circle-fill me-2"></i>Position/station updated successfully!</div>'

    // Reload the stations
    loadStations()

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
  } catch (error) {
    console.error(error)
    document.getElementById("statusMessage").innerHTML =
      `<div class="alert alert-danger"><i class="bi bi-exclamation-triangle-fill me-2"></i>${error.message}</div>`
  }
}

function deleteStation(id) {
  // Store the ID to delete
  document.getElementById("deleteStationId").value = id

  // Show the confirmation modal
  const modalElement = document.getElementById("deleteConfirmModal")
  const modal = new bootstrap.Modal(modalElement)
  modal.show()
}

async function confirmDeleteStation() {
  const id = Number.parseInt(document.getElementById("deleteStationId").value)

  try {
    document.getElementById("statusMessage").innerHTML =
      '<div class="alert alert-info"><i class="bi bi-info-circle-fill me-2"></i>Deleting position/station...</div>'

    const response = await fetch(`../api/stations/${id}`, {
      method: "DELETE",
    })

    if (!response.ok) {
      throw new Error("Failed to delete position/station")
    }

    const data = await response.json()
    console.log("Position/station deleted:", data)

    // Close the modal
    const modalElement = document.getElementById("deleteConfirmModal")
    const modalInstance = bootstrap.Modal.getInstance(modalElement)
    if (modalInstance) {
      modalInstance.hide()
    }

    // Show success message
    document.getElementById("statusMessage").innerHTML =
      '<div class="alert alert-success"><i class="bi bi-check-circle-fill me-2"></i>Position/station deleted successfully!</div>'

    // Reload the stations
    loadStations()

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
  } catch (error) {
    console.error(error)
    document.getElementById("statusMessage").innerHTML =
      `<div class="alert alert-danger"><i class="bi bi-exclamation-triangle-fill me-2"></i>${error.message}</div>`
  }
}

// Add workflow integration to station management
function viewStationWorkflow(stationId) {
  // Find the station
  const station = stationsData.find((st) => st.id === stationId)
  if (!station) {
    alert("Position/station not found!")
    return
  }

  // Create a modal for workflow context
  const modalHtml = `
    <div class="modal fade" id="stationWorkflowModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title">
              <i class="bi bi-diagram-3 me-2"></i> 
              Workflow Context: ${station.name}
            </h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="alert alert-info">
              <i class="bi bi-info-circle-fill me-2"></i>
              This shows the teams and workflows this position/station is part of.
            </div>
            
            <div id="stationWorkflowContent">
              <div class="d-flex justify-content-center p-4">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Loading workflow data...</span>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            <a href="../pages/workflow.html" class="btn btn-primary">
              <i class="bi bi-diagram-3 me-1"></i> Open Workflow Manager
            </a>
          </div>
        </div>
      </div>
    </div>
  `

  // Remove any existing modal
  const existingModal = document.getElementById("stationWorkflowModal")
  if (existingModal) {
    existingModal.remove()
  }

  // Add the modal to the document
  document.body.insertAdjacentHTML("beforeend", modalHtml)

  // Show the modal
  const modalElement = document.getElementById("stationWorkflowModal")
  const modal = new bootstrap.Modal(modalElement)
  modal.show()

  // Load the station's workflow data
  loadStationWorkflowData(station.id, station.name)
}

// Load station workflow data
async function loadStationWorkflowData(stationId, stationName) {
  try {
    // In a real implementation, this would fetch from an API
    // For now, we'll use mock data
    setTimeout(() => {
      const workflowContent = document.getElementById("stationWorkflowContent")
      if (!workflowContent) return

      // Mock data for teams this station belongs to
      const teams = [
        { id: 3, name: "Front Office", type: "operations", status: "active" },
        { id: 4, name: "Customer Service", type: "sales", status: "active" },
      ]

      // Create HTML for the teams
      let teamsHtml = `<h5 class="mb-3">Associated Teams</h5>`

      if (teams.length === 0) {
        teamsHtml += `<p class="text-muted">This position/station is not associated with any teams.</p>`
      } else {
        teamsHtml += `<div class="row">`
        teams.forEach((team) => {
          const statusClass = `status-${team.status}`
          teamsHtml += `
            <div class="col-md-6 mb-3">
              <div class="card">
                <div class="card-header bg-${getTeamColorClass(team.type)}">
                  <h6 class="mb-0 text-white">${team.name}</h6>
                </div>
                <div class="card-body">
                  <p class="mb-1"><strong>Type:</strong> ${team.type}</p>
                  <p class="mb-0">
                    <strong>Status:</strong> 
                    <span class="badge bg-${getStatusBadgeClass(team.status)}">${team.status}</span>
                  </p>
                </div>
              </div>
            </div>
          `
        })
        teamsHtml += `</div>`
      }

      // Mock data for workflows this station is involved in
      const workflows = [
        {
          name: "Customer Check-in Process",
          role: "Starting Point",
          nextStep: "Service Delivery",
          status: "active",
        },
        {
          name: "Service Delivery Workflow",
          role: "Service Point",
          nextStep: "Payment Processing",
          status: "active",
        },
      ]

      // Create HTML for the workflows
      let workflowsHtml = `<h5 class="mb-3 mt-4">Active Workflows</h5>`

      if (workflows.length === 0) {
        workflowsHtml += `<p class="text-muted">This position/station is not involved in any active workflows.</p>`
      } else {
        workflowsHtml += `<div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Workflow</th>
                <th>Role</th>
                <th>Next Step</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
        `

        workflows.forEach((workflow) => {
          workflowsHtml += `
            <tr>
              <td>${workflow.name}</td>
              <td>${workflow.role}</td>
              <td>${workflow.nextStep}</td>
              <td><span class="badge bg-${getStatusBadgeClass(workflow.status)}">${workflow.status}</span></td>
            </tr>
          `
        })

        workflowsHtml += `
            </tbody>
          </table>
        </div>`
      }

      // Add a link to the workflow manager
      const linkHtml = `
        <div class="text-center mt-4">
          <a href="../pages/workflow.html" class="btn btn-outline-primary">
            <i class="bi bi-diagram-3 me-1"></i> Manage Team Workflows
          </a>
        </div>
      `

      // Update the content
      workflowContent.innerHTML = teamsHtml + workflowsHtml + linkHtml
    }, 1000) // Simulate loading delay
  } catch (error) {
    console.error("Error loading workflow data:", error)
    const workflowContent = document.getElementById("stationWorkflowContent")
    if (workflowContent) {
      workflowContent.innerHTML = `
        <div class="alert alert-danger">
          <i class="bi bi-exclamation-triangle-fill me-2"></i>
          Error loading workflow data: ${error.message}
        </div>
      `
    }
  }
}

// Helper function to get team color class
function getTeamColorClass(type) {
  switch (type) {
    case "management":
      return "primary"
    case "sales":
      return "success"
    case "operations":
      return "danger"
    case "hr":
      return "purple" // Custom color
    case "finance":
      return "warning"
    case "it":
      return "info"
    case "marketing":
      return "pink" // Custom color
    default:
      return "secondary"
  }
}

// Helper function to get status badge class
function getStatusBadgeClass(status) {
  switch (status) {
    case "active":
      return "success"
    case "pending":
      return "warning"
    case "blocked":
      return "danger"
    default:
      return "secondary"
  }
}
