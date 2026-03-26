// Module 3: Location Transmission Module

export function sendLocationToBackend(clientId, lat, lon) {
  fetch("/api/presence", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      client_id: clientId,
      lat: lat,
      lon: lon
    })
  });
}
