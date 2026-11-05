// SCRIPT TO DYNAMICALLY OPEN MODALS TO REPLY AN ANSWER, EDIT REPLY, 
document.addEventListener('DOMContentLoaded', function () {
    // === 1. CONTROL MODAL TO CLOSE A POST ===
    const closePostModal = document.getElementById('mdl-close-post');

    if (closePostModal) {
        closePostModal.addEventListener('show.bs.modal', function (event) {
            // button that trigger modal event
            const button = event.relatedTarget; 

            // extract data from button trigger
            const postId = button.getAttribute('data-bs-post-id'); 
            const title = button.getAttribute('data-bs-title');
            const url_endpoint = button.getAttribute('data-bs-action');
            
            // get modal form
            const form = closePostModal.querySelector('#form-close-post');
            
            // formatting URL to close post by ID
            if (form && url_endpoint){ form.action = url_endpoint; }

            closePostModal.querySelector('#post-title').innerHTML = title;
        });
    }
});