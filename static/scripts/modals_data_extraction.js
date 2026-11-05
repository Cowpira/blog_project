// ===============================  SCRIPT TO MAKE GLOBAL MODALS =============================== 
document.addEventListener("DOMContentLoaded", function () {
    //========================  MODAL SEND MESSAGE ========================
    const messageModal = document.getElementById('global-send-msg');
    
    if (messageModal) {
        messageModal.addEventListener('show.bs.modal', function (event) {
            // button that trigger this modal
            const button = event.relatedTarget;
            
            // extract data from data-bs-* from trigger modal button
            const devId = button.getAttribute('data-bs-id');
            const devName = button.getAttribute('data-bs-name');
            
            // get HTML elements from modal that will receive the data
            //const inputDevId = document.getElementById('global-dev-id');
            const spanDevName = document.getElementById('global-dev-name');
            const textareaMessage = document.getElementById('global-msg-text');
            const sendMsgForm= document.getElementById('global-send-msg-frm');

            //adding the placeholder to textarea
            textareaMessage.setAttribute('placeholder', `What's your message to ${devName}...`);
            
            // inject data into HTML elements
            //inputDevId.value = devId;
            spanDevName.innerText = devName;
            
            // clean textarea message
            textareaMessage.value = "";

            // add the action event to the form
            sendMsgForm.setAttribute('action', `/restricted/new_message/${devId}`);
        });
    }


    //========================  MODAL RESUME ========================
    const resumeModal = document.getElementById('global-mdl-resumes');

    if (resumeModal){

    }
});