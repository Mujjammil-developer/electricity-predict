/**
 * charts.js
 * Chart.js utility helpers for Electricity Consumption Prediction System.
 * Consistent theme: Dark Navy Blue (#0f172a, #1e293b) & Electric Green (#00e676, #10b981).
 */

const CHART_COLORS = {
  navy: '#0f172a',
  navyMedium: '#1e293b',
  electricGreen: '#10b981',
  electricGreenLight: '#34d399',
  electricGreenSoft: 'rgba(16, 185, 129, 0.15)',
  skyBlue: '#0284c7',
  skyBlueSoft: 'rgba(2, 132, 199, 0.15)',
  amber: '#f59e0b',
  rose: '#f43f5e',
  gridBorder: '#e2e8f0',
  textColor: '#475569'
};

// Global chart options default
Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif';
Chart.defaults.color = CHART_COLORS.textColor;

function renderDailyLineChart(canvasId, labels, data) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;
  
  return new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Daily Electricity Consumption (kWh)',
        data: data,
        borderColor: CHART_COLORS.electricGreen,
        backgroundColor: CHART_COLORS.electricGreenSoft,
        borderWidth: 2,
        fill: true,
        tension: 0.25,
        pointRadius: 2,
        pointHoverRadius: 5,
        pointBackgroundColor: CHART_COLORS.electricGreen
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: CHART_COLORS.navy,
          padding: 10,
          callbacks: {
            label: function(context) {
              return ` ${context.parsed.y.toLocaleString()} kWh`;
            }
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { maxTicksLimit: 12 }
        },
        y: {
          grid: { color: CHART_COLORS.gridBorder },
          title: { display: true, text: 'Consumption (kWh)' }
        }
      }
    }
  });
}

function renderMonthlyBarChart(canvasId, labels, data) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;
  
  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Total Monthly Consumption (kWh)',
        data: data,
        backgroundColor: CHART_COLORS.navyMedium,
        hoverBackgroundColor: CHART_COLORS.electricGreen,
        borderRadius: 6,
        borderWidth: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: CHART_COLORS.navy,
          padding: 10,
          callbacks: {
            label: function(context) {
              return ` ${context.parsed.y.toLocaleString()} kWh`;
            }
          }
        }
      },
      scales: {
        x: { grid: { display: false } },
        y: {
          grid: { color: CHART_COLORS.gridBorder },
          title: { display: true, text: 'Total Consumption (kWh)' }
        }
      }
    }
  });
}

function renderHourlyChart(canvasId, labels, meanData) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;
  
  return new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Average Hourly Load (kWh)',
          data: meanData,
          borderColor: CHART_COLORS.skyBlue,
          backgroundColor: CHART_COLORS.skyBlueSoft,
          borderWidth: 2.5,
          fill: true,
          tension: 0.3,
          pointRadius: 4,
          pointBackgroundColor: CHART_COLORS.skyBlue
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: true, position: 'top' },
        tooltip: {
          backgroundColor: CHART_COLORS.navy,
          padding: 10,
          callbacks: {
            label: function(context) {
              return ` ${context.dataset.label}: ${context.parsed.y} kWh`;
            }
          }
        }
      },
      scales: {
        x: { grid: { display: false } },
        y: {
          grid: { color: CHART_COLORS.gridBorder },
          title: { display: true, text: 'Load (kWh)' }
        }
      }
    }
  });
}

function renderActualVsPredictedChart(canvasId, labels, actualData, predictedData) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;
  
  return new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Actual Consumption (kWh)',
          data: actualData,
          borderColor: CHART_COLORS.navy,
          backgroundColor: 'transparent',
          borderWidth: 2,
          pointRadius: 2,
          tension: 0.2
        },
        {
          label: 'Predicted Consumption (RF Model)',
          data: predictedData,
          borderColor: CHART_COLORS.electricGreen,
          backgroundColor: 'transparent',
          borderWidth: 2,
          borderDash: [4, 4],
          pointRadius: 2,
          tension: 0.2
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: true, position: 'top' },
        tooltip: {
          backgroundColor: CHART_COLORS.navy,
          padding: 10,
          callbacks: {
            label: function(context) {
              return ` ${context.dataset.label}: ${context.parsed.y} kWh`;
            }
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { maxTicksLimit: 14 }
        },
        y: {
          grid: { color: CHART_COLORS.gridBorder },
          title: { display: true, text: 'Consumption (kWh)' }
        }
      }
    }
  });
}

function renderDistributionChart(canvasId, labels, counts) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;
  
  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Frequency of Readings',
        data: counts,
        backgroundColor: 'rgba(30, 41, 59, 0.85)',
        hoverBackgroundColor: CHART_COLORS.electricGreen,
        borderRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: CHART_COLORS.navy,
          callbacks: {
            label: function(context) {
              return ` ${context.parsed.y} occurrences`;
            }
          }
        }
      },
      scales: {
        x: {
          title: { display: true, text: 'Consumption Range (kWh)' },
          grid: { display: false }
        },
        y: {
          title: { display: true, text: 'Frequency (Hours)' },
          grid: { color: CHART_COLORS.gridBorder }
        }
      }
    }
  });
}

function renderFutureForecastChart(canvasId, labels, values) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;
  
  return new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Predicted Next 24-Hour Load (kWh)',
        data: values,
        borderColor: CHART_COLORS.electricGreen,
        backgroundColor: CHART_COLORS.electricGreenSoft,
        borderWidth: 2.5,
        fill: true,
        pointBackgroundColor: CHART_COLORS.electricGreen,
        pointRadius: 4,
        tension: 0.3
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: true, position: 'top' },
        tooltip: {
          backgroundColor: CHART_COLORS.navy,
          padding: 10,
          callbacks: {
            label: function(context) {
              return ` Forecast: ${context.parsed.y} kWh`;
            }
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          title: { display: true, text: 'Hour Ahead' }
        },
        y: {
          grid: { color: CHART_COLORS.gridBorder },
          title: { display: true, text: 'Predicted Consumption (kWh)' }
        }
      }
    }
  });
}

function renderFeatureImportanceChart(canvasId, labels, importances) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;
  
  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Feature Importance (%)',
        data: importances,
        backgroundColor: CHART_COLORS.skyBlue,
        borderRadius: 4
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: CHART_COLORS.navy,
          callbacks: {
            label: function(context) {
              return ` ${context.parsed.x}% Importance`;
            }
          }
        }
      },
      scales: {
        x: {
          grid: { color: CHART_COLORS.gridBorder },
          title: { display: true, text: 'Relative Importance (%)' }
        },
        y: { grid: { display: false } }
      }
    }
  });
}
