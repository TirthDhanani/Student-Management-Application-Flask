document.addEventListener("DOMContentLoaded", () => {
  const id = new URLSearchParams(location.search).get("id");
  const formTitle = document.getElementById("formTitle");

  // Toggle family section
  document.getElementById("toggleFamily").onclick = function() {
    const sec = document.getElementById("familySection");
    sec.style.display = sec.style.display === "none" ? "block" : "none";
  };

  // Load degrees
  fetch("/api/degrees")
    .then(res => res.json())
    .then(degrees => {
      const select = document.getElementById("degreeSelect");
      degrees.forEach(d => {
        const opt = document.createElement("option");
        opt.value = d.id;
        opt.textContent = d.name;
        select.appendChild(opt);
      });

      // If editing, load student data
      if (id) {
        formTitle.innerText = "Edit Student";
        fetch(`/api/students/${id}`)
          .then(res => res.json())
          .then(data => {
            for (let key in data) {
              document.querySelectorAll(`[name="${key}"]`).forEach(el => {
                if (el.type === "radio") {
                  el.checked = (el.value === data[key]);
                } else {
                  el.value = data[key] ?? "";
                }
              });
            }
            document.getElementById("studentId").value = id;
            if (data.mother_name || data.father_name || data.sibling_name) {
              document.getElementById("familySection").style.display = "block";
            }
            // Show attachment download link if a file exists
            if (data.attachment_filename) {
              document.getElementById("attachmentInfo").innerHTML =
                `<span>Current file: <a href="/api/students/${id}/attachment" target="_blank">${data.attachment_filename}</a></span>`;
            } else {
              document.getElementById("attachmentInfo").innerHTML = "";
            }
          });
      }
    })
    .catch(err => {
      console.error("Error loading degrees:", err);
      alert("Failed to load degree list.");
    });

  // Handle form submit (add or edit)
  const form = document.getElementById("studentForm");
  if (!form) return;
  form.addEventListener("submit", e => {
    e.preventDefault();
    const id = document.getElementById("studentId").value;
    const formData = new FormData(e.target);

    fetch(id ? `/api/students/${id}` : "/api/students", {
      method: id ? "PUT" : "POST",
      body: formData // No Content-Type! Let browser set boundary
    })
      .then(res => {
        if (!res.ok) return res.json().then(err => { throw err });
        return res.json();
      })
      .then(() => location.href = "/")
      .catch(err => {
        console.error("Save error:", err);
        alert(err.error || JSON.stringify(err) || "Error saving student");
      });
  });
});

