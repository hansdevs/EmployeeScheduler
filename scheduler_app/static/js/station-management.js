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
    const modal = bootstrap.Modal.getInstance(modalElement)
    modal.hide()

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

