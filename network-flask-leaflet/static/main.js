const map = L.map("map").setView([16, 107], 6);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png").addTo(map);

let geoLayer;

const slider = document.getElementById("slider");
const startLabel = document.getElementById("start-label");
const endLabel = document.getElementById("end-label");

const minDate = new Date("2023-01-01").getTime();
const maxDate = new Date("2024-12-31").getTime();

function formatDate(ms) {
  const d = new Date(+ms);
  return d.toISOString().split("T")[0];
}

function generatePipValues(minMs, maxMs) {
  const pips = [];
  let current = new Date(minMs);
  current.setDate(1); // Start at the 1st day of month

  while (current.getTime() <= maxMs) {
    pips.push(current.getTime());
    // Next month
    current.setMonth(current.getMonth() + 3);
  }
  return pips;
}

noUiSlider.create(slider, {
  start: [minDate, maxDate],
  connect: true,
  range: {
    min: minDate,
    max: maxDate,
  },
  step: 24 * 60 * 60 * 1000, // 1 day
  tooltips: [
    {
      to: (value) => formatDate(value),
      from: (value) => new Date(value).getTime(),
    },
    {
      to: (value) => formatDate(value),
      from: (value) => new Date(value).getTime(),
    },
  ],
  pips: {
    mode: "values", // place pips at exact values
    values: generatePipValues(minDate, maxDate), // function to generate dates for pips
    density: 4, // density of the pips
    format: {
      to: (v) => formatDate(v),
      from: (v) => new Date(v).getTime(),
    },
  },
});

let debounceTimer;
slider.noUiSlider.on("update", function (values) {
  startLabel.textContent = formatDate(values[0]);
  endLabel.textContent = formatDate(values[1]);

  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(loadData, 300);
});

function loadData() {
  const values = slider.noUiSlider.get();
  const start = formatDate(values[0]);
  const end = formatDate(values[1]);

  fetch(`/filter?start=${start}&end=${end}`)
    .then((res) => res.json())
    .then((data) => {
      const geojson = JSON.parse(data);

      if (geoLayer) map.removeLayer(geoLayer);
      geoLayer = L.geoJSON(geojson).addTo(map);

      if (geojson.features.length > 0) {
        map.fitBounds(geoLayer.getBounds());
      }

      const list = document.getElementById("info-list");
      list.innerHTML = "";

      geojson.features.forEach((f) => {
        const props = f.properties;
        const li = document.createElement("li");
        li.innerHTML = `<strong>ID:</strong> ${props.id}<br>
                                <strong>Info:</strong> ${props.info}<br>
                                <strong>Date:</strong> ${props.timestamp}`;
        list.appendChild(li);
      });
    });
}

// Load initial data
loadData();
