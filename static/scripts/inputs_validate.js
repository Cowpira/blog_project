// script to validate contact form
function validate_contact() {
    let form = document.getElementById("form_valid");
    var name = document.getElementById("first_name").value;
    var topic = document.getElementById("contact_topic").value;
    var email = document.getElementById("email_address").value;
    var message = document.getElementById("text-1").value;

    if (name === "" || topic === "" || email === "" || message === "") {
        form.classList.remove('d-none');
    }
}


// script to validate contact form
function validate_post_job() {
    let form = document.getElementById("form_valid");
    var req_lang = document.getElementById("lag_req");
    var title = document.getElementById("title").value;
    var selc_langs = document.getElementById("selected_boxes").value;
    var max_sal = document.getElementById("maxSalary").value;
    var description = document.getElementById("role_desc").value;
    var benefits = document.getElementById("benefits").value;

    if (selc_langs === "" || title === "" || max_sal === "" || 
        description === "" || benefits === "") {
        form.classList.remove('d-none');
        req_lang.classList.remove('d-none');
    }
}


// script to validate form to create employee account
function validate_employee_account(){
    let form = document.getElementById("form_valid");
    var employee_id = document.getElementById("employee_id").value;
    var f_name = document.getElementById("first_name").value;
    var l_name = document.getElementById("last_name").value;
    var phone = document.getElementById("phone").value;
    var position = document.getElementById("position").value;
    var email = document.getElementById("email_address").value;
    var password = document.getElementById("password").value;
    var conf_pass = document.getElementById("conf_password").value;


    if (employee_id === "" || f_name === "" || l_name === "" || phone === "" || 
        position === "" || email === "" || password === "" || conf_pass === "") {
        form.classList.remove('d-none');
    }
}


// script to validate form to send message for developer
function validate_mdl_send_msg() {
    let form = document.getElementById("form_valid");
    var reply_msg = document.getElementById("global-msg-text").value;

    if (reply_msg === "") {
        form.classList.remove('d-none');
    }
};


// script to validate form to create user account
function validate_dev_account(){
    let form = document.getElementById("form_valid");
    var f_name = document.getElementById("first_name").value;
    var l_name = document.getElementById("last_name").value;
    var company = document.getElementById("company").value;
    var position = document.getElementById("position").value;
    var email = document.getElementById("email_address").value;
    var password = document.getElementById("password").value;
    var conf_pass = document.getElementById("conf_password").value;

    if (f_name === "" || l_name === "" || company === "" || position === "" || 
        email === "" || password === "" || conf_pass === "") {
        form.classList.remove('d-none');
    }
}


// script to validate form to update coding level
function validate_update_ocupation(){
    let form = document.getElementById("validate_ocupation");
    var company = document.getElementById("update_company").value;
    var position = document.getElementById("update_position").value;

    if (company === "" || position === "") {
        form.classList.remove('d-none');
    }
}


function validate_update_coding(){
    let form = document.getElementById("validate_coding");
    var title = document.getElementById("update_title").value;
    var language = document.getElementById("update_language").value;
    var input_title = document.getElementById("update_input_title").value;
    var input_language = document.getElementById("update_input_lang").value;

    if (title === "Select a title" || language === "Select a language" || input_title === "" || input_language === "") {
        form.classList.remove('d-none');
    }
}


// script to validate empty login form
function validate_login() {
    let form = document.getElementById("login_valid");
    var email = document.getElementById("username").value;
    var password = document.getElementById("password").value;

    if (email === "" || password === "") {
        form.classList.remove('d-none');
    }
}


// script to validate update password form
function update_password_validation() {
    let form = document.getElementById("form_update_pass");
    var cur_pass = document.getElementById("cur_password").value;
    var new_pass = document.getElementById("password").value;
    var conf_pass = document.getElementById("conf_password").value;

    if (cur_pass === "" || new_pass === "" || conf_pass === "") {
        form.classList.remove('d-none');
    }
}


// script to validate recover password form
function validate_reset_password() {
    let form = document.getElementById("form_valid");
    var new_pass = document.getElementById("password").value;
    var conf_pass = document.getElementById("conf_password").value;

    if (new_pass === "" || conf_pass === "") {
        form.classList.remove('d-none');
    }
}


// script to validate post question form
function question_validate(){
    let form = document.getElementById("form_valid");
    var title = document.getElementById("new_title").value;
    var question = document.getElementById("question").value;

    if (title === "" || question === "") {
        form.classList.remove('d-none');
    }
}


// script to valudate updates post question form
function edit_question_validate(){
    let form = document.getElementById("edit_form_valid");
    var title = document.getElementById("edit_title").value;
    var question = document.getElementById("edit_question").value;

    if (title === "" || question === "") {
        form.classList.remove('d-none');
    }
}


// script to validate portfolio form
function validate_portfolio(){
    let form = document.getElementById("validate_resume");
    var school = document.getElementById("school").value;
    var education = document.getElementById("education_type").value;
    var graduation = document.getElementById("graduated_at").value;
    var in_progress = document.getElementById("in_progress").checked;
    var concluded = document.getElementById("concluded").checked;
    var stoped = document.getElementById("stoped").checked;

    if (school === "" || education === "" || graduation === "" || in_progress === "" || 
        concluded === "" || stoped === "") {
        education_tab();
        form.classList.remove('d-none');
    }
}


//  ============  VALIDATING FORMS FOR MODALS ===================
function validate_answer_post(){
    var form = document.getElementById("form_valid");
    var text = document.getElementById("mdl-textarea").value;
    
    if (text === "") {
        form.classList.remove('d-none');
    }
}


// script to manipulate alerts to dismiss smoothly
$(document).ready(function() {
    setTimeout(() => {
        // trigger all alerts that has  class global-alerts
        $(".global-alerts").each(function() {
            const $this = $(this);
            
            // 1. remove the animated css class
            $this.removeClass('animate__animated animate__fadeInDown');
            
            // 2. fade out the alert message 
            $this.fadeOut(2000, function() {
                $this.slideUp(700, function() {
                    $this.remove();
                });
            });
        });
    }, 7000);
});


//check if passwords match
function checkPasswordMatch() {
    var passwordInput = document.getElementById("user_reg_password");
    var confPassInput = document.getElementById("user_reg_conf_password");
    var messageElement = document.getElementById("message");
    var icon = document.getElementById("pass-icon");

    if (!passwordInput || !confPassInput || !messageElement) return;

    var password = passwordInput.value.trim();
    var confirmPassword = confPassInput.value.trim();
    icon.removeAttribute("class");
    messageElement.removeAttribute("class");
    
    if (password === "" && confirmPassword === "") {
        messageElement.innerHTML = "";
        return;
    }

    if (password.length < 8){
        icon.classList.add("text-warning", "bi", "bi-exclamation-triangle-fill", "animate__animated", "animate__flash", "animate__delay-1s");
        messageElement.innerHTML = 'Password must be at least 8 characters long!';
        messageElement.classList.add("text-warning", "smaller-texts", "fw-bold", "animate__animated", "animate__flash", "animate__delay-1s");
        return;
    }
    
    if(confirmPassword === ""){
        messageElement.innerHTML= "";
        return;
    }
    
    if (password !== confirmPassword){
        icon.classList.add("text-danger", "bi", "bi-x-circle-fill", "animate__animated", "animate__flash", "animate__delay-1s");
        messageElement.innerHTML = "Passwords does not match!";
        messageElement.classList.add("text-danger", "smaller-texts", "fw-bold", "animate__animated", "animate__flash", 'animate__delay-1s');
        return;
    }
    
    icon.classList.add("text-success", "bi", "bi-check-circle-fill", "animate__animated", "animate__flash", "animate__delay-1s");
    messageElement.innerHTML = "Passwords match!";
    messageElement.classList.add("text-success", "smaller-texts", "fw-bold", "animate__animated", "animate__flash", 'animate__delay-1s');
    
    console.log("Senha:", document.getElementById("password").value.length);
    console.log("ConfSenha:", document.getElementById("conf_password").value.length);
}

window.checkPasswordMatch= checkPasswordMatch;



// script for fade out alerts and form msg erros
setTimeout(() => {
    $("#form_valid").fadeTo(3000, 800).slideUp(800, function() {
        $("form_valid").slideUp(800);
    });

    $("#login_valid").fadeTo(3000, 800).slideUp(800, function() {
        $("login_valid").slideUp(800);
    });

    $("#validate_ocupation").fadeTo(3000, 800).slideUp(800, function() {
        $("validate_ocupation").slideUp(800);
    });

    $("#validate_coding").fadeTo(3000, 800).slideUp(800, function() {
        $("validate_coding").slideUp(800);
    });

    $("#validate_resume").fadeTo(3000, 600).slideUp(600, function() {
        $("validate_resume").slideUp(900);
    });

    $("#form_update_pass").fadeTo(3000, 800).slideUp(800, function() {
        $("form_update_pass").slideUp(800);
    });
}, 6000);


// Example starter JavaScript for disabling form submissions if there are invalid fields
(function () {
  'use strict'

  // Fetch all the forms we want to apply custom Bootstrap validation styles to
  var forms = document.querySelectorAll('.needs-validation')

  // Loop over them and prevent submission
  Array.prototype.slice.call(forms)
    .forEach(function (form) {
      form.addEventListener('submit', function (event) {
        if (!form.checkValidity()) {
          event.preventDefault()
          event.stopPropagation()
        }

        form.classList.add('was-validated')
      }, false)
    })
})();