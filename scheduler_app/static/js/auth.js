/**
 * Authentication Utilities
 * Handles common authentication functionality
 */

// Add logout button to navbar
function addLogoutButton() {
  const navbar = document.querySelector(".navbar .container-fluid")
  if (!navbar) return

  // Check if logout button already exists
  if (document.getElementById("logoutBtn")) return

  // Create logout button container
  const logoutContainer = document.createElement("div")
  logoutContainer.className = "d-flex align-items-center"

  // Get the existing time display
  const timeDisplay = document.getElementById("localTime")
  if (timeDisplay) {
    timeDisplay.classList.add("me-3")
    navbar.removeChild(timeDisplay)
    logoutContainer.appendChild(timeDisplay)
  }

  // Create logout button
  const logoutBtn = document.createElement("button")
  logoutBtn.id = "logoutBtn"
  logoutBtn.className = "btn btn-sm btn-outline-light"
  logoutBtn.innerHTML = '<i class="bi bi-box-arrow-right me-1"></i> Logout'
  logoutBtn.addEventListener("click", logout)

  logoutContainer.appendChild(logoutBtn)
  navbar.appendChild(logoutContainer)
}

// Logout function
async function logout() {
  try {
    const res = await fetch("../api/logout", { credentials: "include" })
    if (res.ok) {
      window.location.href = "../pages/signin.html"
    }
  } catch (err) {
    console.error("Failed to logout:", err)
  }
}

// Get current user
async function getCurrentUser() {
  try {
    const res = await fetch("../api/user", { credentials: "include" })
    if (!res.ok) return null

    return await res.json()
  } catch (err) {
    console.error("Failed to fetch user:", err)
    return null
  }
}

// Initialize auth features
document.addEventListener("DOMContentLoaded", () => {
  addLogoutButton()
})

