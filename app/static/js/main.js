document.addEventListener("DOMContentLoaded", function () {
  // Mobile sidebar toggle
  const sidebar = document.getElementById("sidebar");
  const toggleBtn = document.getElementById("sidebarToggle");

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener("click", function () {
      sidebar.classList.toggle("show");
    });
  }

  // Auto-dismiss alerts after 5 seconds
  const alerts = document.querySelectorAll(".alert-dismissible");
  alerts.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    }, 5000);
  });

  // Archive and critical action confirmation
  const confirmActions = document.querySelectorAll("[data-confirm]");
  confirmActions.forEach(function (elem) {
    elem.addEventListener("click", function (e) {
      const message = elem.getAttribute("data-confirm") || "Are you sure you want to perform this action?";
      if (!confirm(message)) {
        e.preventDefault();
      }
    });
  });
});
