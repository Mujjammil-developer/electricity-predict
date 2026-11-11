/**
 * main.js
 * Core application interactions, sidebar toggling, live calculators, and upload handling.
 */

document.addEventListener('DOMContentLoaded', function() {
  // Mobile Sidebar Toggle
  const sidebar = document.querySelector('.sidebar');
  const toggleBtn = document.querySelector('.mobile-toggle-btn');
  
  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', function() {
      sidebar.classList.toggle('show');
    });
    
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(event) {
      if (window.innerWidth <= 992) {
        if (!sidebar.contains(event.target) && !toggleBtn.contains(event.target) && sidebar.classList.contains('show')) {
          sidebar.classList.remove('show');
        }
      }
    });
  }

  // File Upload Drag and Drop setup
  const dropzone = document.getElementById('uploadDropzone');
  const fileInput = document.getElementById('csvFileInput');
  const fileNameDisplay = document.getElementById('selectedFileName');
  const uploadForm = document.getElementById('datasetUploadForm');
  const uploadLoadingSpinner = document.getElementById('uploadLoadingSpinner');

  if (dropzone && fileInput) {
    ['dragenter', 'dragover'].forEach(eventName => {
      dropzone.addEventListener(eventName, function(e) {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.add('drag-over');
      }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropzone.addEventListener(eventName, function(e) {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.remove('drag-over');
      }, false);
    });

    dropzone.addEventListener('drop', function(e) {
      const dt = e.dataTransfer;
      const files = dt.files;
      if (files.length > 0) {
        fileInput.files = files;
        updateFileName(files[0]);
      }
    });

    dropzone.addEventListener('click', function() {
      fileInput.click();
    });

    fileInput.addEventListener('change', function() {
      if (fileInput.files.length > 0) {
        updateFileName(fileInput.files[0]);
      }
    });

    function updateFileName(file) {
      if (fileNameDisplay) {
        fileNameDisplay.innerHTML = `<i class="bi bi-file-earmark-check text-success me-1"></i> <strong>Selected File:</strong> ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
        fileNameDisplay.classList.remove('d-none');
      }
    }
  }

  if (uploadForm && uploadLoadingSpinner) {
    uploadForm.addEventListener('submit', function() {
      uploadLoadingSpinner.classList.remove('d-none');
    });
  }

  // Interactive Live Bill Calculator (Client-side fast feedback)
  const tariffInput = document.getElementById('calcTariffRate');
  const dailyKwhVal = document.getElementById('calcDailyKwh');
  const predKwhVal = document.getElementById('calcPredKwh');
  
  const resDailyCost = document.getElementById('resDailyCost');
  const resMonthlyCost = document.getElementById('resMonthlyCost');
  const resAnnualCost = document.getElementById('resAnnualCost');
  const resPredCost = document.getElementById('resPredCost');

  function updateLiveBillCalculations() {
    if (!tariffInput || !dailyKwhVal) return;
    
    const rate = parseFloat(tariffInput.value) || 0;
    const dailyKwh = parseFloat(dailyKwhVal.value) || 0;
    const predKwh = parseFloat(predKwhVal ? predKwhVal.value : dailyKwh) || dailyKwh;

    const dailyCost = dailyKwh * rate;
    const monthlyCost = dailyCost * 30;
    const annualCost = dailyCost * 365;
    const predCost = predKwh * rate;

    if (resDailyCost) resDailyCost.textContent = `₹${dailyCost.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
    if (resMonthlyCost) resMonthlyCost.textContent = `₹${monthlyCost.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
    if (resAnnualCost) resAnnualCost.textContent = `₹${annualCost.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
    if (resPredCost) resPredCost.textContent = `₹${predCost.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;

    // Update dynamic savings rows
    [5, 10, 15, 20].forEach(pct => {
      const savedKwhEl = document.getElementById(`saveKwh_${pct}`);
      const savedInrEl = document.getElementById(`saveInr_${pct}`);
      const newBillEl = document.getElementById(`newBill_${pct}`);

      if (savedKwhEl && savedInrEl && newBillEl) {
        const savedKwh = (dailyKwh * 30) * (pct / 100);
        const savedInr = savedKwh * rate;
        const newBill = monthlyCost - savedInr;

        savedKwhEl.textContent = `${savedKwh.toFixed(1)} kWh`;
        savedInrEl.textContent = `₹${savedInr.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        newBillEl.textContent = `₹${newBill.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
      }
    });
  }

  if (tariffInput) {
    tariffInput.addEventListener('input', updateLiveBillCalculations);
  }
});
