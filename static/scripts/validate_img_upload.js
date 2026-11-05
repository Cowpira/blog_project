function validate_Image(input) {
    const fileInput = document.getElementById('image');
    const file = fileInput.files[0];
    const errorMessage = document.getElementById('error-message');
    const icon= document.getElementById('alert-icon');
    const allowedTypes = ['image/jpeg', 'image/png', 'application/jpeg'];
    const maxSize = 3 * 1024 * 1024; // 3 MB

    errorMessage.removeAttribute('class');
    icon.removeAttribute('class');

    if (!allowedTypes.includes(file.type)) {
        errorMessage.classList.add('text-warning', 'smaller-texts', 'animate__animated', 'animate__flash', 'animate__repeat-3');
        errorMessage.textContent = 'Invalid image type. Only JPG, JPEG or PNG is allowed';
        icon.classList.add('bi', 'bi-filetype-png', 'animate__animated', 'text-warning', 'animate__flash', 'animate__repeat-3');
        fileInput.value = '';

    } else if (file.size > maxSize) {
        errorMessage.classList.add('text-danger', 'smaller-texts', 'animate__animated', 'animate__flash', 'animate__repeat-3');
        errorMessage.textContent = 'Image is too large. Maximum size allowed 3MB';
        icon.classList.add('bi', 'bi-aspect-ratio', 'animate__animated', 'text-danger', 'animate__flash', 'animate__repeat-3');
        fileInput.value = '';
        
    } else {
        //classList.remove('text-danger', 'animate__flash', 'animate__repeat-3');
        errorMessage.classList.add('text-success', 'small-texts', 'animate__animated', 'animate__fadeInDown', 'animate__delay-1s');
        errorMessage.textContent ='Image successfull validated';
        icon.classList.add('bi', 'bi-check-circle', 'animate__animated', 'text-success', 'animate__fadeInDown', 'animate__delay-1s');
    }
}