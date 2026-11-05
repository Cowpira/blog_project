/**
 * apply dynamic validation to modals (REPLY ANSWER, EDIT REPLY, EDIT, ANSWER)
 */
function setupDynamicFormValidation(modalId, formId) {
    const modalForm = document.getElementById(modalId);
    if (!modalForm) return;

    const form = modalForm.querySelector(formId);
    if (!form) return;

    const textarea = form.querySelector('#mdl-textarea');
    const msg_alert = form.querySelector('#form_valid');
    let alertTimeoutId = null;

    // CHECK FOR MODAL FORMS BUTTONS SUBMIT EVENTS 
    form.addEventListener('submit', function (event) {
        
        // CHECK IF MODAL FORMS TEXTAREAS ARE EMPTY
        const isInvalid = !form.checkValidity() || (textarea && textarea.value.trim() === '');

        if (isInvalid) {
            event.preventDefault();  // block event 
            event.stopPropagation(); // stop event propagation

            // remove d-none from alert message
            msg_alert.classList.remove('d-none', 'animate__fadeOutDown');
            msg_alert.classList.add('animate__fadeInUp');

            // Cria o cronômetro para ocultar o alerta após 5 segundos (5000ms)
            alertTimeoutId = setTimeout(function () {
                msg_alert.classList.remove('animate_fadeInUp');
                msg_alert.classList.add('animate__fadeOutDown');

                setTimeout(function(){
                    msg_alert.classList.add('d-none');
                }, 1000);
            }, 5000);
            
            // add focus to textarea
            if (textarea) textarea.focus();
        } else {
            // if textarea is filled hide alert message
            if (msg_alert) {
                msg_alert.classList.add('d-none');
                msg_alert.classList.remove('animate__fadeOutDown');
            }
        }

        // add Bootstrap validation style to form inputs
        form.classList.add('was-validated');
    }, false);

    // listen modal to automatically reset forms
    modalForm.addEventListener('show.bs.modal', function () {
        form.classList.remove('was-validated');

        if (msg_alert) msg_alert.classList.add('d-none');
    });
}

// 1. Modal Reply
setupDynamicFormValidation('mdl-reply-answer', '#form-reply-answer');

// 2. Modal Edit Reply
setupDynamicFormValidation('mdl-edit-reply', '#form-edit_reply');

// 3. Modal Edit Answer Principal (mdl-edit-answer)
setupDynamicFormValidation('mdl-edit-answer', '#form-edit_answer');