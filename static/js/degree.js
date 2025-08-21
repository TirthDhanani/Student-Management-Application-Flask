document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("degreeForm");
  if (!form) return;

  form.addEventListener("submit", e => {
    e.preventDefault();
    const name = document.getElementById("degreeName").value.trim();
    if (!name) {
      alert("Degree name required!");
      return;
    }
    fetch("/api/degrees", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name })
    })
      .then(res => res.json())
      .then(data => {
        if (data.error) alert(data.error);
        else {
          alert("Degree added!");
          form.reset();
        }
      })
      .catch(() => alert("Error adding degree"));
  });
});