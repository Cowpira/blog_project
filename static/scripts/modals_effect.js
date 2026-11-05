document.addEventListener("DOMContentLoaded", function() {
    const modal_login= document.getElementById('loginModal');
    const open_login= document.querySelector('.open_login');
    const close_login= document.querySelector('.btn-close-modal');
    
    const modal_recover= document.getElementById('findEmailModal');
    const close_recover= document.querySelector('.close_recover');
    const recover_link= document.getElementById('recover-account');
    const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));


    // =========================================================================
    // FUNCTION 1: SCRIPT TO SWITCH LOGN AND RECOVER ACCOUNT MODALS (Login <-> Recover Account)
    // =========================================================================
    if (open_login){
        open_login.onclick= () =>{
            modal_login.classList.remove('animate__bounceOutDown');
            modal_login.classList.add('animate__bounceInDown');

            modal_recover.classList.remove('animate__bounceOutDown');
            modal_recover.classList.add('animate__bounceInDown');

            $(modal_login).modal('show');
        };
    }

    if(recover_link){
        recover_link.onclick= async (e) =>{
            e.preventDefault();

            modal_login.classList.remove('animate__bounceInDown');
            modal_login.classList.add('animate__bounceOutDown');

            await sleep(2000);
            $(modal_login).modal('hide');

            modal_recover.classList.add('animate__bounceInDown');
            $(modal_recover).modal('show');
        };
    }

    if (close_login) {
        close_login.onclick= () =>{
            modal_login.classList.remove('animate__bounceInDown');
            modal_login.classList.add('animate__bounceOutDown');
            close_modal();
        };
    }

    if (close_recover) {
        close_recover.onclick= () =>{
            modal_recover.classList.remove('animate__bounceInDown');
            modal_recover.classList.add('animate__bounceOutDown');
            close_modal();
        };
    }

    // functions to close modals
    async function close_modal(){
        await sleep(1500);
        $(modal_login).modal('hide');
        $(modal_recover).modal('hide');
    }



    // =========================================================================
    // FUNCTION 2: UNIVERSAL MODAL BOUNCE-IN/ BOUND-OUT
    // =========================================================================
    document.addEventListener('show.bs.modal', function(e){
        const modal= e.target;

        if(modal.classList.contains('gen-mdl')){
            modal.classList.remove('animate__bounceOutDown');
            modal.classList.add('animate__bounceInDown', 'animate__animated', 'animate__slow');
        }
    });

    document.addEventListener('click', async function (e) {
        const closeBtn= e.target.closest('.gen-mdl-close');
        
        if(closeBtn){
            e.preventDefault();

            const cur_mdl_window= closeBtn.closest('.gen-mdl');
            const targetUrl= closeBtn.getAttribute('href');

            if(cur_mdl_window){
                if(cur_mdl_window.classList.contains('is-leaving')) return;
                cur_mdl_window.classList.add('is-leaving');

                // add and remove bounce effects
                cur_mdl_window.classList.remove('animate__bounceInDown');
                cur_mdl_window.classList.add('animate__bounceOutDown', 'animate__animated', 'animate__slow');

                const backDrop= document.querySelector('.modal-backdrop');
                if(backDrop){
                    backDrop.style.transition= 'opacity 1500ms ease';
                    backDrop.classList.remove('show');
                }

                await new Promise(resolve => setTimeout(resolve, 1500));

                const instance= bootstrap.Modal.getInstance(cur_mdl_window) || bootstrap.Modal.getOrCreateInstance(cur_mdl_window);
                if(instance) instance.hide();
                cur_mdl_window.classList.remove('animate__bounceInDown', 'animate__bounceOutDown', 'is-leaving');

                if(targetUrl && targetUrl !== '#') window.location.href= targetUrl;
            }
        }
    });

    document.addEventListener('hidden.bs.modal', function(e){
        const modal= e.target;

        if(modal.classList.contains('gen-mdl')){
            if(!document.querySelector('.modal.show')){
                document.querySelectorAll('modal-backdrop').forEach(el => el.remove());
                document.body.classList.remove('modal-open');
                document.body.style.overflow= '';
                document.body.style.paddingRight= '';
            }
        }
    });
});