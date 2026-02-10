let chart;
let charts = [];

async function loadMetric() {
  const metric = document.getElementById("metric").value;
  const country = document.getElementById("country").value;
  const plan = document.getElementById("plan").value;

  let url = `http://localhost:8000/metrics?metric=${metric}`;
  if (country) url += `&country=${country}`;
  if (plan) url += `&plan=${plan}`;

  const res = await fetch(url);
  const data = await res.json();

  drawChart(metric, data.value);
}

function drawChart(label, value) {
  const ctx = document.getElementById("chart").getContext("2d");

  if (chart) chart.destroy();

  chart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: [label],
      datasets: [{
        label: label,
        data: [value]
      }]
    }
  });
}

function addChart() {
  const metric = document.getElementById("metric").value;
  const country = document.getElementById("country").value;
  const plan = document.getElementById("plan").value;

  charts.push({ metric, country, plan });
  renderChartList();
}

function renderChartList() {
  const ul = document.getElementById("chartList");
  ul.innerHTML = "";

  charts.forEach((c, i) => {
    const li = document.createElement("li");
    li.innerText = `${c.metric} | ${c.country || "ALL"} | ${c.plan || "ALL"}`;
    ul.appendChild(li);
  });
}

async function saveDashboard() {
  const name = document.getElementById("dashboardName").value;

  await fetch("http://localhost:8000/dashboard/save", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, charts })
  });

  alert("Dashboard saved");
}

async function loadDashboard() {
  const name = document.getElementById("dashboardName").value;
  const res = await fetch(`http://localhost:8000/dashboard/load?name=${name}`);
  const data = await res.json();

  charts = data.charts || [];
  renderChartList();
}
