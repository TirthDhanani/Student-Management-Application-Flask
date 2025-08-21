document.addEventListener("DOMContentLoaded", () => {
  const tbody = document.querySelector("#studentTable tbody");
  if (!tbody) return;

  fetch("/api/students")
    .then(res => res.json())
    .then(data => {
      tbody.innerHTML = "";
      data.forEach(s => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${s.id}</td>
          <td>${s.fname}</td>
          <td>${s.lname}</td>
          <td>${s.gender}</td>
          <td>${s.degree || ""}</td>
          <td>${s.address || ""}</td>
          <td>${s.zipcode || ""}</td>
          <td>${s.city || ""}</td>
          <td>${
            s.attachment_filename
              ? `<a href="/api/students/${s.id}/attachment" target="_blank">Download</a>`
              : ""
          }</td>
          <td>
            <a href="/upsert?id=${s.id}" class="btn btn-sm btn-warning">Edit</a>
            <button class="btn btn-sm btn-danger ms-1" onclick="deleteStudent(${s.id})">Delete</button>
          </td>
        `;
        tbody.appendChild(tr);
      });
    })
    .catch(err => {
      console.error("Error loading students:", err);
    });
});

function deleteStudent(id) {
  if (!confirm("Delete this student?")) return;
  fetch(`/api/students/${id}`, { method: "DELETE" })
    .then(res => res.json())
    .then(() => location.reload())
    .catch(() => alert("Error deleting student"));
}
