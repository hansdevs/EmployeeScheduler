/**
 * Workflow Data Service
 * Handles data operations for the workflow management feature
 */

class WorkflowDataService {
    /**
     * Fetch teams from the API
     * @returns {Promise<Array>} Promise resolving to an array of teams
     */
    async getTeams() {
      try {
        const response = await fetch("/api/workflow/teams")
        if (!response.ok) {
          throw new Error("Failed to load teams")
        }
        return await response.json()
      } catch (error) {
        console.error("Error loading teams:", error)
        throw error
      }
    }
  
    /**
     * Fetch connections from the API
     * @returns {Promise<Array>} Promise resolving to an array of connections
     */
    async getConnections() {
      try {
        const response = await fetch("/api/workflow/connections")
        if (!response.ok) {
          throw new Error("Failed to load connections")
        }
        return await response.json()
      } catch (error) {
        console.error("Error loading connections:", error)
        throw error
      }
    }
  
    /**
     * Save teams to the API
     * @param {Array} teams Array of team objects
     * @returns {Promise<Object>} Promise resolving to the save result
     */
    async saveTeams(teams) {
      try {
        const response = await fetch("/api/workflow/teams", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(teams),
        })
        if (!response.ok) {
          throw new Error("Failed to save teams")
        }
        return await response.json()
      } catch (error) {
        console.error("Error saving teams:", error)
        throw error
      }
    }
  
    /**
     * Save connections to the API
     * @param {Array} connections Array of connection objects
     * @returns {Promise<Object>} Promise resolving to the save result
     */
    async saveConnections(connections) {
      try {
        const response = await fetch("/api/workflow/connections", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(connections),
        })
        if (!response.ok) {
          throw new Error("Failed to save connections")
        }
        return await response.json()
      } catch (error) {
        console.error("Error saving connections:", error)
        throw error
      }
    }
  
    /**
     * Get workflow data for an employee
     * @param {number} employeeId The employee ID
     * @returns {Promise<Object>} Promise resolving to the employee workflow data
     */
    async getEmployeeWorkflow(employeeId) {
      try {
        const response = await fetch(`/api/workflow/employee/${employeeId}`)
        if (!response.ok) {
          throw new Error("Failed to load employee workflow data")
        }
        return await response.json()
      } catch (error) {
        console.error("Error loading employee workflow data:", error)
        throw error
      }
    }
  
    /**
     * Get workflow data for a station
     * @param {number} stationId The station ID
     * @returns {Promise<Object>} Promise resolving to the station workflow data
     */
    async getStationWorkflow(stationId) {
      try {
        const response = await fetch(`/api/workflow/station/${stationId}`)
        if (!response.ok) {
          throw new Error("Failed to load station workflow data")
        }
        return await response.json()
      } catch (error) {
        console.error("Error loading station workflow data:", error)
        throw error
      }
    }
  
    /**
     * Get current workflow status
     * @returns {Promise<Object>} Promise resolving to the workflow status data
     */
    async getWorkflowStatus() {
      try {
        const response = await fetch("/api/workflow/status")
        if (!response.ok) {
          throw new Error("Failed to load workflow status")
        }
        return await response.json()
      } catch (error) {
        console.error("Error loading workflow status:", error)
        throw error
      }
    }
  
    /**
     * Get workflow context for scheduling
     * @param {number} day The day of the week (0-6)
     * @returns {Promise<Object>} Promise resolving to the workflow context data
     */
    async getWorkflowContext(day) {
      try {
        const response = await fetch(`/api/workflow/context?day=${day}`)
        if (!response.ok) {
          throw new Error("Failed to load workflow context")
        }
        return await response.json()
      } catch (error) {
        console.error("Error loading workflow context:", error)
        throw error
      }
    }
  }
  
  // Create a singleton instance
  const workflowService = new WorkflowDataService()
  