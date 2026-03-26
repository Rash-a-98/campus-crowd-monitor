// Module 5: Dashboard Visualization & Colour Logic Module

export function getColor(count) {
  if (count <= 3) return "green";
  if (count <= 7) return "yellow";
  return "red";
}

export function renderDashboard(areas) {
  const dashboard = document.getElementById("dashboard");
  dashboard.innerHTML = "";

  areas.forEach(area => {
    const card = document.createElement("div");
    card.className = `card ${getColor(area.count)}`;
    card.innerHTML = `
      ${area.area_code.toUpperCase()}<br>
      Count: ${area.count}
    `;
    dashboard.appendChild(card);
  });
}
