// Add workflow context function to schedule.js
function viewWorkflowContext() {
    // Show the modal
    const modalElement = document.getElementById("workflowContextModal")
    const modal = new bootstrap.Modal(modalElement)
    modal.show()
  
    // Load the workflow context data
    loadWorkflowContextData()
  }
  
  // Load workflow context data
  async function loadWorkflowContextData() {
    try {
      // In a real implementation, this would fetch from an API
      // For now, we'll use mock data
      setTimeout(() => {
        const contextContent = document.getElementById("workflowContextContent")
        if (!contextContent) return
  
        // Get the currently selected day
        const viewDay = getViewDay()
        const dayName = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][viewDay]
  
        // Mock data for workflows active on this day
        const workflows = [
          {
            name: "Sales Process",
            teams: ["Sales Team", "Finance"],
            employees: ["Bob Johnson", "Alice Williams", "Sarah Davis"],
            status: "active",
          },
          {
            name: "Customer Support",
            teams: ["Support Team", "IT Department"],
            employees: ["David Miller", "Emma Brown", "Mike Wilson"],
            status: "active",
          },
        ]
  
        // Create HTML for the context
        let contextHtml = `
          <div class="alert alert-info">
            <i class="bi bi-info-circle-fill me-2"></i>
            Showing workflow context for <strong>${dayName}</strong>. This helps you understand how your schedule aligns with active workflows.
          </div>
        `
  
        if (workflows.length === 0) {
          contextHtml += `<p class="text-muted">There are no active workflows scheduled for ${dayName}.</p>`
        } else {
          contextHtml += `<h5 class="mb-3">Active Workflows for ${dayName}</h5>`
  
          workflows.forEach((workflow) => {
            const statusClass = getStatusClass(workflow.status)
  
            contextHtml += `
              <div class="card mb-3">
                <div class="card-header d-flex justify-content-between align-items-center">
                  <h6 class="mb-0">${workflow.name}</h6>
                  <span class="badge bg-${statusClass}">${workflow.status}</span>
                </div>
                <div class="card-body">
                  <p><strong>Teams Involved:</strong> ${workflow.teams.join(", ")}</p>
                  <p><strong>Scheduled Employees:</strong></p>
                  <div>
            `
  
            workflow.employees.forEach((emp) => {
              // Check if employee is scheduled
              const isScheduled = selectedShifts.some((shift) => {
                const employee = employees.find((e) => e.id === shift.employee_id)
                return employee && employee.name === emp && shift.day === viewDay
              })
  
              contextHtml += `
                <span class="badge ${isScheduled ? "bg-success" : "bg-danger"} me-2 mb-2">
                  ${emp} ${isScheduled ? "(Scheduled)" : "(Not Scheduled)"}
                </span>
              `
            })
  
            contextHtml += `
                  </div>
                </div>
              </div>
            `
          })
        }
  
        // Add scheduling recommendations
        contextHtml += `
          <div class="card mt-4">
            <div class="card-header bg-primary text-white">
              <h6 class="mb-0">Scheduling Recommendations</h6>
            </div>
            <div class="card-body">
              <ul class="list-group list-group-flush">
                <li class="list-group-item d-flex justify-content-between align-items-center">
                  Ensure Sales and Finance teams have overlapping hours
                  <span class="badge bg-warning">Important</span>
                </li>
                <li class="list-group-item d-flex justify-content-between align-items-center">
                  Schedule at least one IT support staff during customer support hours
                  <span class="badge bg-danger">Critical</span>
                </li>
                <li class="list-group-item d-flex justify-content-between align-items-center">
                  Consider adding backup staff for Customer Support workflow
                  <span class="badge bg-info">Suggestion</span>
                </li>
              </ul>
            </div>
          </div>
        `
  
        // Update the content
        contextContent.innerHTML = contextHtml
      }, 1000) // Simulate loading delay
    } catch (error) {
      console.error("Error loading workflow context:", error)
      const contextContent = document.getElementById("workflowContextContent")
      if (contextContent) {
        contextContent.innerHTML = `
          <div class="alert alert-danger">
            <i class="bi bi-exclamation-triangle-fill me-2"></i>
            Error loading workflow context: ${error.message}
          </div>
        `
      }
    }
  }
  
  // Helper function to get status class
  function getStatusClass(status) {
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
  