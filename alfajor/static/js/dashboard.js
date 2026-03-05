(function () {
  var toggle = document.getElementById('sidebarToggle');
  var sidebar = document.getElementById('sidebar');
  var body = document.body;

  if (toggle && sidebar) {
    toggle.addEventListener('click', function () {
      body.classList.toggle('sidebar-open');
    });

    document.addEventListener('click', function (e) {
      if (!body.classList.contains('sidebar-open')) return;
      if (sidebar.contains(e.target) || toggle.contains(e.target)) return;
      body.classList.remove('sidebar-open');
    });
  }

  /* Confirmación para acciones destructivas */
  document.addEventListener('submit', function (e) {
    var form = e.target;
    if (form && (form.getAttribute('data-confirm') || form.classList.contains('form-destructive'))) {
      if (!confirm(form.getAttribute('data-confirm') || '¿Estás seguro?')) {
        e.preventDefault();
      }
    }
  });

  /* Feedback visual en botones submit */
  document.addEventListener('submit', function (e) {
    var form = e.target;
    if (!form || !form.tagName || form.tagName !== 'FORM') return;
    var btn = form.querySelector('button[type="submit"]');
    if (btn && !btn.disabled) {
      btn.classList.add('loading');
      btn.disabled = true;
    }
  });
})();
