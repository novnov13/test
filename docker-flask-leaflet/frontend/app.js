const map = L.map("map").setView([16.9, 121.1], 5);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png").addTo(map);

const timeSlider = document.getElementById("timeSlider");
const timeValue = document.getElementById("timeValue");
console.log("Time slider element:", timeSlider);

let geoLayer;

function loadGeoJSON(time) {
  fetch(`/api/geojson?time=${time}`)
    .then((res) => res.json())
    .then((data) => {
      if (data) {
        if (geoLayer) map.removeLayer(geoLayer);
        geoLayer = L.geoJSON(data).addTo(map);
      } else console.error("No data found for the selected time.");
    });
}

timeSlider.addEventListener("input", () => {
  const time = timeSlider.value;
  timeValue.textContent = time;
  loadGeoJSON(time);
});

// Initial load
loadGeoJSON(timeSlider.value);
