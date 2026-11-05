document.addEventListener("DOMContentLoaded", function() {
    //script to timer count to display recover account button
    let count = 10;
    const elem = document.getElementById('sec');
    const div_recover = document.getElementById('div-recover-account');

    elem.innerText = count;

    const timer= setInterval(() => {
        count--;
        elem.innerText = count;

        if (count <= 0) {
            clearInterval(timer);
            div_recover.classList.remove('d-none');
        }
        else{ div_recover.classList.add('d-none'); }
    }, 1000)


    //script to manage login alert messages pop-ups
    const params = new URLSearchParams(window.location.search);
    // getting url parameters
    const error_code = params.get('error_code');
    const error_icon = params.get('error_icon');
    const error_msg = params.get('error_msg');
    const email= params.get('email');
    var myModal = new bootstrap.Modal('#loginModal');

    const alert_login= document.querySelector('.global-alerts');
    const icon_login= document.getElementById('icon-login');
    const login_limit= document.getElementById('login_limit');
    const login_form= document.getElementById('login_form');

    if(error_code){
        myModal.show();
        document.getElementById('username').value= email;
        alert_login.classList.remove('d-none');

        if(error_code == 204){
            if(error_msg.includes('exceed')){
                login_form.classList.add('d-none');
                login_limit.classList.remove('d-none');
            }

            alert_login.classList.add('alert-secondary');
            icon_login.classList.add(error_icon);
            document.getElementById('msg-login').innerText= error_msg;
        }
        else if(error_code == 401){
            alert_login.classList.add('alert-info');
            icon_login.classList.add(error_icon);
            document.getElementById('msg-login').innerText= error_msg;
        }
        else if(error_code == 404){
            alert_login.classList.add('alert-dark');
            icon_login.classList.add(error_icon); //('bi-envelope-slash-fill');
            document.getElementById('msg-login').innerText= error_msg; //'E-mail not Found!';
        }
        else if(error_code == 406){
            alert_login.classList.add('alert-warning');
            icon_login.classList.add(error_icon);
            document.getElementById('msg-login').innerText= error_msg;
        }
    }
});