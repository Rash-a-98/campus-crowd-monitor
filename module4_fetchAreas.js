// Module 4: Crowd Data Retrieval Module

export function fetchAreas(callback) {
  fetch("/api/areas")
    .then(res => res.json())
    .then(data => callback(data))
    .catch(err => console.error("Fetch error:", err));
}
