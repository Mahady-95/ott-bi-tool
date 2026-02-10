let chart = null;

async function loadMetric() {
  const metric = document.getElementById("metric").value;
  const country = document.getElementById("country").value;
  const plan = document.getElementById("plan").value;

  let url = `http://127.0.0.1:8000/metrics?metric=${metric}`;
  if (country) url += `&country=${country}`;
  if (plan) url += `&plan=${plan}`;

  const res = await fetch(url);
  const data = await res.json();

  renderChart(metric, data.value);
}

function renderChart(metric, value) {
  const ctx = document.getElementById("chart").getContext("2d");

  if (chart) chart.destroy();

  chart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: [metric.toUpperCase()],
      datasets: [{
        label: metric.toUpperCase(),
        data: [value]
      }]
    }
  });
}
