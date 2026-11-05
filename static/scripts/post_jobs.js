// fucnton to add values from job inputs and add to tab job review
function review_job(){
    // getting values from inputs and checkboxes
    var job_status= document.getElementById('job_status');
    var title= document.getElementById('title');
    var selected_boxes= document.getElementById('selected_boxes');
    
    var maxSalary= document.getElementById('maxSalary');
    var other_req_text= document.getElementById('other_req');
    var role_desc_text= document.getElementById('role_desc');
    var benefits_text= document.getElementById('benefits');

    var work_local= [...document.querySelectorAll('input[name="work_location"]:checked')].map(cb => cb.value);
    var contracts= [...document.querySelectorAll('input[name="contract"]:checked')].map(cb => cb.value);
    var payments= [...document.querySelectorAll('input[name="payment"]:checked')].map(cb => cb.value);

    // getting SPAN tags to display the inputs and checkboxes values
    var review_status= document.getElementById('review_job_status');
    var review_title= document.getElementById('review_job_title');
    var review_prog_lang= document.getElementById('review_prog_lang');
    var review_location= document.getElementById('review_location');
    var review_contract_type= document.getElementById('review_contract_type');
    var review_pay_type= document.getElementById('review_pay_type');
    
    var review_max_sal= document.getElementById('review_max_sal');
    var review_other_req= document.getElementById('review_other_requir');
    var review_description= document.getElementById('review_description');
    var review_benefits= document.getElementById('review_benefits');
    
    if (review_location) review_location.innerHTML= work_local;
    if (review_contract_type) review_contract_type.innerHTML= contracts;
    if (review_pay_type) review_pay_type.innerHTML= payments;

    if (review_status && job_status) review_status.innerHTML= job_status.value;
    if (review_title && title) review_title.innerHTML= title.value;
    if (review_prog_lang && selected_boxes) review_prog_lang.innerHTML= selected_boxes.value;
    if (review_max_sal && maxSalary) review_max_sal.innerHTML= maxSalary.value;

    if (review_other_req && other_req_text) review_other_req.innerHTML= other_req_text.value;
    if (review_description && role_desc_text) review_description.innerHTML= role_desc_text.value;
    if (review_benefits && benefits_text) review_benefits.innerHTML= benefits_text.value;
}

// script to get all checkboxes selected and add into input box
var checkedOrder = [];
var checkboxes = document.querySelectorAll('input[type="checkbox"]');
var question_checked= document.getElementById('selected_boxes');

// geeting previus checkboxes selected and add into the list
if(question_checked.value){
    // add previous tags into tag_list
    const tags= question_checked.value.split(" ");

    tags.forEach(tag => {
        checkedOrder.push(tag);
    });
}

checkboxes.forEach(checkbox => {
    checkbox.addEventListener('change', () => {
        var value = checkbox.value;

        if (checkbox.checked) {
            checkedOrder.push(value);
        } else {
            var index = checkedOrder.indexOf(value);
            if (index > -1) {
                checkedOrder.splice(index, 1);
            }
        }
        // setting input with tags values to add new question
        question_checked.value= checkedOrder.join(' ');
    });
});

// count number of chars for other requirements textarea
for (let i = 1; i < 0; i++) {
    document.addEventListener("DOMContentLoaded", () => {
        var text_class = document.getElementById(`text-${i}`);
        var bar_class = document.getElementById(`bar-${i}`);
        var chars_class = document.getElementById(`chars-${i}`);

        function charCounter(inputField) {
            var maxLength = inputField.getAttribute("maxlength");
            var currentLength = inputField.value.length;
            var progressWidth = (currentLength / maxLength) * 100;

            bar_class.style.width = `${progressWidth}%`;
            chars_class.style.display = "none";

            if (progressWidth <= 60) {
                bar_class.style.backgroundColor = "rgb(19, 160, 19)";
            } else if (progressWidth > 60 && progressWidth < 85) {
                bar_class.style.backgroundColor = "rgb(236, 157, 8)";
            } else {
                bar_class.style.backgroundColor = "rgb(241, 9, 9)";

                chars_class.innerHTML = `${maxLength - currentLength} characters left`;
                chars_class.style.display = "block";
            }
        }

        if (text_class != null){
            text_class.oninput = () => charCounter(text_class);
        }
    });
}