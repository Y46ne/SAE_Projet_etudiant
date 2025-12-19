function togglePassword(id, button) {
      const field = document.getElementById(id);
      const toggleIcon = button.querySelector('i'); 
      if (field.type === 'password') {
        field.type = 'text';
        toggleIcon.className = 'fas fa-eye-slash';
      } else {
        field.type = 'password';
        toggleIcon.className = 'fas fa-eye';
      }
}