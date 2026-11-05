(function(){
    // prevent multipes clicks
    window.isResumeLoading= window.isResumeLoading || false;

    document.addEventListener('click', async function(e){
        const button= e.target.closest('.open-resume');
        if (!button) return;

        e.preventDefault();
        e.stopPropagation();

        if (window.isResumeLoading || document.querySelector('.modal.show')) return;
        window.isResumeLoading= true;
        const dev_id= button.getAttribute('data-id');
        
        try{
            const response= await fetch(`/restricted/dev_resume_modal/${dev_id}`);
            if (!response.ok) throw new Error("Error trying to load developer resume!!");

            const modalHTL= await response.text();

            const container= document.getElementById('dislay_modal_resume');
            container.innerHTML= modalHTL;

            const modalEl= container.querySelector('.modal');
            const bsModal= new bootstrap.Modal(modalEl, {
                backdrop: 'static',
                keyboard: true
            });

            modalEl.addEventListener('hidden.bs.modal', function(){
                bsModal.dispose();
                container.innerHTML= '';

                document.querySelectorAll('.modal-backdrop').forEach(backdrop => backdrop.remove());
                document.body.classList.remove('modal-open');
                document.body.style.overflow= '';
                document.body.style.paddingRight= '';
            });

            bsModal.show();

        }catch (error){
            console.error(error);
        } finally{
            window.isResumeLoading= false;
        }
    });
})();