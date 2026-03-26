const id = localStorage.getItem("user_phone");
const role = localStorage.getItem("user_role");

// Hide logs button if not staff
if (role !== "staff") {
    document.getElementById("adminLink").style.display = "none";
}


// ================= SEND LOCATION =================
function sendLocation() {
    navigator.geolocation.getCurrentPosition(pos => {

        fetch("/api/presence", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                client_id: id,
                lat: pos.coords.latitude,
                lon: pos.coords.longitude
            })
        });

    });
}


// ================= LOAD DASHBOARD =================
function loadDashboard() {

    fetch('/api/areas')
        .then(res => res.json())
        .then(data => {

            const container = document.getElementById('cards');
            container.innerHTML = "";

            data.forEach(area => {

                const card = document.createElement('div');

                // 🎯 Crowd level color logic
                let levelClass = "";

                if (area.count <= 5) {
                    levelClass = "card-low";
                } else if (area.count <= 15) {
                    levelClass = "card-medium";
                } else {
                    levelClass = "card-high";
                }

                card.className = "area-card " + levelClass;

                card.innerHTML = `
                    <h2>${area.area_code}</h2>
                    <p><b>People Present:</b> ${area.count}</p>
                `;

                container.appendChild(card);
            });
        });
}


// ================= AUTO RUN =================
sendLocation();
loadDashboard();

// Refresh location every 1 min
setInterval(sendLocation, 60000);

// Refresh dashboard every 5 sec (faster visual update)
setInterval(loadDashboard, 5000);