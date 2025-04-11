/**
 * Pricing Toggle Functionality
 * Handles switching between monthly and annual pricing
 */

document.addEventListener("DOMContentLoaded", () => {
    const billingToggle = document.getElementById("billingToggle")
    const priceValues = document.querySelectorAll(".price-value")
    const billedTexts = document.querySelectorAll(".pricing-billed-text")
    const pricingPeriods = document.querySelectorAll(".pricing-period")
  
    // Billing toggle functionality
    billingToggle.addEventListener("change", () => {
      const isAnnual = billingToggle.checked
  
      // Update price values
      priceValues.forEach((priceEl) => {
        const monthlyPrice = priceEl.getAttribute("data-monthly")
        const annualPrice = priceEl.getAttribute("data-annual")
        priceEl.textContent = isAnnual ? annualPrice : monthlyPrice
      })
  
      // Update billing text
      billedTexts.forEach((textEl) => {
        textEl.textContent = isAnnual ? "Billed annually" : "Billed monthly"
      })
  
      // Update active state on pricing period labels
      pricingPeriods[0].classList.toggle("active", !isAnnual)
      pricingPeriods[1].classList.toggle("active", isAnnual)
    })
  })
  
  