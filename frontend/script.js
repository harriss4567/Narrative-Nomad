// Select HTML elements
const tripForm = document.getElementById('tripForm');
const storySection = document.getElementById('storySection');
const planTitle = document.getElementById('planTitle');
const planSummary = document.getElementById('planSummary');
const chaptersDiv = document.getElementById('chapters');
const mapDiv = document.getElementById('map');
const styleInput = document.getElementById('style');
const themeButtons = document.querySelectorAll('.theme-btn');

let map, markersLayer;

// Theme button click behavior
themeButtons.forEach(btn => {
  btn.addEventListener('click', () => {
    // Remove 'selected' class from all buttons
    themeButtons.forEach(b => b.classList.remove('selected'));
    // Add 'selected' class to the clicked button
    btn.classList.add('selected');
    // Update the hidden input value
    styleInput.value = btn.dataset.style;
  });
});

// Listen for form submission
tripForm.addEventListener('submit', async e => {
  e.preventDefault(); // Prevent page reload

  // Gather form data
  const body = {
    destination: document.getElementById('destination').value,
    duration_days: parseInt(document.getElementById('duration').value) || 3,
    budget: document.getElementById('budget').value,
    travel_style: styleInput.value, // use the selected theme
    interests: (document.getElementById('interests').value || '')
                 .split(',').map(s => s.trim()).filter(Boolean),
    eat_out: document.getElementById('eat_out').checked
  };

  // Send data to backend
  const res = await fetch('/api/plan', {
    method: 'POST',
    headers: { 'Content-Type':'application/json' },
    body: JSON.stringify(body)
  });

  // Handle server errors
  if (!res.ok) {
    alert('Server error: ' + (await res.text()));
    return;
  }

  // Get plan from server and render it
  const plan = await res.json();
  renderPlan(plan);
});

// Function to display the trip plan
function renderPlan(plan) {
  // Show the story section
  storySection.style.display = 'block';

  // Set title and summary
  planTitle.textContent = plan.title || `${plan.destination} — Trip`;
  planSummary.textContent = plan.summary || '';
  chaptersDiv.innerHTML = ''; // Clear old itinerary

  // Initialize map if first time
  if (!map) {
    map = L.map('map', { scrollWheelZoom: false }).setView([20, 0], 2);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 }).addTo(map);
    markersLayer = L.layerGroup().addTo(map);
  }
  markersLayer.clearLayers(); // Clear old markers

  // Loop through each day in the itinerary
  plan.itinerary.forEach(day => {
    const chapterDiv = document.createElement('div');
    chapterDiv.classList.add('chapter');
    chapterDiv.innerHTML = `
      <h3>Day ${day.day}: ${day.location.name}</h3>
      <p>${day.location.description}</p>
      <p><strong>Activities:</strong></p>
      <ul>
        ${day.activities.map(a => `<li>${a.name}: ${a.description} ($${a.price})</li>`).join('')}
      </ul>
      <p><strong>Restaurant:</strong> ${day.restaurant.name} - ${day.restaurant.description} (${day.restaurant.price_range})</p>
      <p><strong>Location:</strong> ${day.location.city}</p>
    `;
    chaptersDiv.appendChild(chapterDiv);

    // Add a marker for this location on the map
    const marker = L.marker([day.location.lat, day.location.lng]).addTo(markersLayer);
    marker.bindPopup(`<b>${day.location.name}</b><br>${day.location.description}`);
  });
}
