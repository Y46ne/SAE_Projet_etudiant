function togglePassword(id) {
    const field = document.getElementById(id);
    const eyeButton = field.nextElementSibling;

    if (field.type === 'password') {
        field.type = 'text';
    } else {
        field.type = 'password';
    }
}