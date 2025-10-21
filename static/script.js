// Set today's date as default
document.getElementById("date").valueAsDate = new Date()

// Event listeners
document.getElementById("state").addEventListener("change", handleStateChange)
document.getElementById("district").addEventListener("change", handleDistrictChange)
document.getElementById("complex").addEventListener("change", handleComplexChange)
document.getElementById("refreshCaptcha").addEventListener("click", refreshCaptcha)
document.getElementById("scrapperForm").addEventListener("submit", handleFormSubmit)

// Fetch states on page load
async function initializeStates() {
  try {
    const response = await fetch("/fetch_dropdowns", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    })
    const data = await response.json()

    if (data.states) {
      const stateSelect = document.getElementById("state")
      data.states.forEach((state) => {
        const option = document.createElement("option")
        option.value = state
        option.textContent = state
        stateSelect.appendChild(option)
      })
    }
  } catch (error) {
    showStatus("Error loading states: " + error.message, "danger")
  }
}

async function handleStateChange() {
  const state = document.getElementById("state").value
  const districtSelect = document.getElementById("district")
  const complexSelect = document.getElementById("complex")
  const courtSelect = document.getElementById("court")

  // Reset dependent selects
  districtSelect.innerHTML = '<option value="">Select District</option>'
  complexSelect.innerHTML = '<option value="">Select Court Complex</option>'
  courtSelect.innerHTML = '<option value="">Select Court</option>'
  districtSelect.disabled = true
  complexSelect.disabled = true
  courtSelect.disabled = true

  if (!state) return

  try {
    const response = await fetch("/fetch_dropdowns", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ state }),
    })
    const data = await response.json()

    if (data.districts) {
      data.districts.forEach((district) => {
        const option = document.createElement("option")
        option.value = district
        option.textContent = district
        districtSelect.appendChild(option)
      })
      districtSelect.disabled = false
    }
  } catch (error) {
    showStatus("Error loading districts: " + error.message, "danger")
  }
}

async function handleDistrictChange() {
  const state = document.getElementById("state").value
  const district = document.getElementById("district").value
  const complexSelect = document.getElementById("complex")
  const courtSelect = document.getElementById("court")

  complexSelect.innerHTML = '<option value="">Select Court Complex</option>'
  courtSelect.innerHTML = '<option value="">Select Court</option>'
  complexSelect.disabled = true
  courtSelect.disabled = true

  if (!district) return

  try {
    const response = await fetch("/fetch_dropdowns", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ state, district }),
    })
    const data = await response.json()

    if (data.complexes) {
      data.complexes.forEach((complex) => {
        const option = document.createElement("option")
        option.value = complex
        option.textContent = complex
        complexSelect.appendChild(option)
      })
      complexSelect.disabled = false
    }
  } catch (error) {
    showStatus("Error loading complexes: " + error.message, "danger")
  }
}

async function handleComplexChange() {
  const state = document.getElementById("state").value
  const district = document.getElementById("district").value
  const complex = document.getElementById("complex").value
  const courtSelect = document.getElementById("court")

  courtSelect.innerHTML = '<option value="">Select Court</option>'
  courtSelect.disabled = true

  if (!complex) return

  try {
    const response = await fetch("/fetch_dropdowns", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ state, district, complex }),
    })
    const data = await response.json()

    if (data.courts) {
      data.courts.forEach((court) => {
        const option = document.createElement("option")
        option.value = court
        option.textContent = court
        courtSelect.appendChild(option)
      })
      courtSelect.disabled = false
    }
  } catch (error) {
    showStatus("Error loading courts: " + error.message, "danger")
  }
}

async function refreshCaptcha() {
  try {
    const response = await fetch("/get_captcha", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    })
    const data = await response.json()

    if (data.captcha) {
      document.getElementById("captchaImage").src = data.captcha
      document.getElementById("captcha").value = ""
    }
  } catch (error) {
    showStatus("Error loading captcha: " + error.message, "danger")
  }
}

async function handleFormSubmit(e) {
  e.preventDefault()

  const state = document.getElementById("state").value
  const district = document.getElementById("district").value
  const complex = document.getElementById("complex").value
  const court = document.getElementById("court").value
  const date = document.getElementById("date").value
  const captcha = document.getElementById("captcha").value
  const bulkDownload = document.getElementById("bulkDownload").checked

  if (!state || !district || !complex || !court || !date || !captcha) {
    showStatus("Please fill all fields", "danger")
    return
  }

  const submitBtn = document.querySelector('button[type="submit"]')
  submitBtn.disabled = true
  submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...'

  try {
    const endpoint = bulkDownload ? "/download_all" : "/download_pdf"
    const response = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ state, district, complex, court, date, captcha }),
    })

    const data = await response.json()

    if (bulkDownload && data.success) {
      showBulkDownloadResults(data)
    } else if (data.success) {
      showStatus(`PDF downloaded successfully: ${data.filename}`, "success")
      showDownloadLink(data.filename)
    } else {
      showStatus("Error: " + (data.error || "Unknown error"), "danger")
    }
  } catch (error) {
    showStatus("Error: " + error.message, "danger")
  } finally {
    submitBtn.disabled = false
    submitBtn.innerHTML = "Download PDF"
  }
}

function showStatus(message, type) {
  const statusDiv = document.getElementById("statusMessage")
  statusDiv.className = `alert alert-${type}`
  statusDiv.textContent = message
  statusDiv.classList.remove("d-none")

  setTimeout(() => {
    statusDiv.classList.add("d-none")
  }, 5000)
}

function showDownloadLink(filename) {
  const linksDiv = document.getElementById("downloadLinks")
  const link = document.createElement("a")
  link.href = `/file/${filename}`
  link.className = "download-link"
  link.textContent = `Download: ${filename}`
  link.download = filename
  linksDiv.appendChild(link)
}

function showBulkDownloadResults(data) {
  const message = `Downloaded ${data.downloaded}/${data.total} PDFs successfully`
  showStatus(message, data.downloaded === data.total ? "success" : "info")

  const linksDiv = document.getElementById("downloadLinks")
  linksDiv.innerHTML = "<h6>Download Results:</h6>"

  data.results.forEach((result) => {
    if (result.status === "success") {
      const link = document.createElement("a")
      link.href = `/file/${result.filename}`
      link.className = "download-link"
      link.textContent = `✓ ${result.filename}`
      link.download = result.filename
      linksDiv.appendChild(link)
    } else {
      const failedItem = document.createElement("div")
      failedItem.className = "download-link"
      failedItem.style.color = "var(--danger-color)"
      failedItem.textContent = `✗ ${result.court}: ${result.reason}`
      linksDiv.appendChild(failedItem)
    }
  })
}

// Initialize on page load
window.addEventListener("load", () => {
  initializeStates()
  refreshCaptcha()
})
