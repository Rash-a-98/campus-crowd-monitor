// ---------------- LOAD LOGS ----------------
function loadLogs() {

    const selectedDate = document.getElementById("dateFilter")?.value;
    const selectedRole = document.getElementById("roleFilter")?.value;

    let url = "/api/logs?";
    let params = [];

    if (selectedDate) params.push("date=" + selectedDate);
    if (selectedRole) params.push("role=" + selectedRole);

    url += params.join("&");

    fetch(url)
        .then(res => res.json())
        .then(data => {

            const tbody = document.getElementById("logTableBody");
            tbody.innerHTML = "";

            if (!data || data.length === 0) {
                tbody.innerHTML = "<tr><td colspan='6'>No logs found</td></tr>";
                return;
            }

            data.forEach(log => {

                const row = document.createElement("tr");

                row.innerHTML = `
                    <td>${log.name || "Unknown"}</td>
                    <td>${log.dept || "-"}</td>
                    <td>${log.role || "-"}</td>
                    <td>${log.area_code || "-"}</td>
                    <td>${log.entry_time || "-"}</td>
                    <td>${log.exit_time ? log.exit_time : "Active"}</td>
                `;

                tbody.appendChild(row);
            });

        })
        .catch(error => {
            console.error("Error loading logs:", error);
        });
}


// ---------------- DOWNLOAD PDF ----------------
// ---------------- DOWNLOAD FILTERED PDF ----------------
function downloadPDF() {

    const selectedDate = document.getElementById("dateFilter")?.value;
    const selectedRole = document.getElementById("roleFilter")?.value;

    let params = [];

    if (selectedDate && selectedDate !== "")
        params.push("date=" + encodeURIComponent(selectedDate));

    if (selectedRole && selectedRole !== "all")
        params.push("role=" + encodeURIComponent(selectedRole));

    let url = "/download_logs";

    if (params.length > 0)
        url += "?" + params.join("&");

    window.location.href = url;
}

// ---------------- AUTO LOAD WHEN PAGE OPENS ----------------
document.addEventListener("DOMContentLoaded", function () {
    loadLogs();
});