//get value selected to limit total items per page
function allowed_Items_Limit(){
    // return if page does not have a paginario limit dropdown
    const container= document.querySelector('[data-pagination-limit]');
    if (!container) return;

    const storageKey= container.dataset.storageKey;
    const radioName= container.dataset.radioName;
    const urlTemplate= container.dataset.urlTemplate;
    const currentLimit= container.dataset.currentLimit;

    const buildUrl= (limit) => urlTemplate.replace('{limit}', limit);
    const storedValue= localStorage.getItem(storageKey);

    //on page load sunc radiobox checked, if limit is different reload and save new limit
    if(storedValue){
        const radioToSelect= container.querySelector(`input[type="radio"][name="${radioName}"][value="${storedValue}"]`);
        if (radioToSelect){
                radioToSelect.checked= true;
        }

        if(currentLimit && currentLimit !== storedValue && radioToSelect){
            window.location.href= buildUrl(storedValue);
            return;
        }
    }

    //if new limit is selected reload and save it
    const radios= container.querySelectorAll(`input[type="radio"][name="${radioName}"]`);
    radios.forEach((radio) => {
        radio.addEventListener('change', function(){
            if (this.checked){
                localStorage.setItem(storageKey, this.value);
                window.location.href= buildUrl(this.value);
            }
        });
    });
}
document.addEventListener('DOMContentLoaded', allowed_Items_Limit);