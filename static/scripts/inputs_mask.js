$(document).ready(function(){
    function email_expression(param){
        let alphanumericVal = param.replace(/[^a-zA-Z0-9_&#.+$@-]/g, '');
        return alphanumericVal;
    };

    $("#username").on('input', function() {
        username = $(this).val();
        $(this).val(email_expression(username));
    })

    $("#email_address").on('input', function() {
        email = $(this).val();
        $(this).val(email_expression(email));
    });

    function get_expression(param){
        let alphanumericVal = param.replace(/[^\s a-zA-Z çêãéà@._-]/g, '');
        return alphanumericVal;
    };

    $('#search').on('input', function() {
        search = $(this).val();
        $(this).val(get_expression(search));
    });

    $('#first_name').on('input', function() {
        first_name = $(this).val();
        $(this).val(get_expression(first_name));
    });

    $('#last_name').on('input', function() {
        last_name = $(this).val();
        $(this).val(get_expression(last_name));
    });

    $('#company').on('input', function() {
        company = $(this).val();
        $(this).val(get_expression(company));
    });

    $('#position').on('input', function() {
        position = $(this).val();
        $(this).val(get_expression(position));
    });


    function get_alpha_numeric(param){
        let alphanumericVal = param.replace(/[^\s a-zA-Z0-9 )({}]\/´?'"[&çêãéà@._-]/g, '');
        return alphanumericVal;
    };


    $('#search_post').on('input', function() {
        search_post = $(this).val();
        $(this).val(get_alpha_numeric(search_post));
    });

    $('#address').on('input', function() {
        address = $(this).val();
        $(this).val(get_alpha_numeric(address));
    });

    $("#title").on('input', function() {
        title = $(this).val();
        $(this).val(get_alpha_numeric(title));
    });


    function special_chars_expression(param){
        let alphanumericVal = param.replace(/[^\s 0-9a-zA-Z -çêãéà#$*+~^@!?%ºª'"´`/|\\n(){}<>_.,:;*+]/g, '');
        return alphanumericVal;
    };

    $("#contact_topic").on('input', function() {
        contact_topic = $(this).val();
        $(this).val(special_chars_expression(contact_topic));
    });

    $("#text").on('input', function() {
        text = $(this).val();
        $(this).val(special_chars_expression(text));
    });

    $('#contribution').on('input', function() {
        contribution = $(this).val();
        $(this).val(special_chars_expression(contribution));
    });


    // CODE TO VALIDATE PASSWORD
    function get_expression_passwords(param){
        let alphanumericVal = param.replace(/[^0-9a-zA-Z-#$*+@!?%]/g, '');
        return alphanumericVal;
    };

    $('#password').on('input', function() {
        password = $(this).val();
        $(this).val(get_expression_passwords(password));
    });

    $('#cur_password').on('input', function() {
        cur_password = $(this).val();
        $(this).val(get_expression_passwords(cur_password));
    });

    $('#conf_password').on('input', function() {
        conf_password = $(this).val();
        $(this).val(get_expression_passwords(conf_password));
    });

    $('#employee_id').on('input', function() {
        employee_id = $(this).val();
        $(this).val(get_expression_passwords(employee_id));
    });
    

    // MASK EXPERIENCES DATE INPUTS
    $('#cert1_date').mask('99/99/9999');
    $('#cert2_date').mask('99/99/9999');
    $('#cert3_date').mask('99/99/9999');

    // MASK WORK EXPERIENCE DATE INPUTS
    $('#started2').mask('99/99/9999');
    $('#ended2').mask('99/99/9999');
    $('#started3').mask('99/99/9999');
    $('#ended3').mask('99/99/9999');

    // MASK OCUPATION DATES INPUTS
    $('#started').mask('99/99/9999');
    $('#ended').mask('99/99/9999');
        

    // VALIDATE EXPERIENCES INPUTS
    function validade_input_numbers(param){
        let input_number = param.replace(/[^0-9]/g, '');
        return input_number;
    };

    $('#minSalary').on('input', function() {
        min_sal = $(this).val();
        $(this).val(validade_input_numbers(min_sal));
    });
    $('#maxSalary').on('input', function() {
        max_sal = $(this).val();
        $(this).val(validade_input_numbers(max_sal));
    });

    $('#phone').mask('(000) 000-0000');
    $('#minSalary').mask('#,##0', {reverse: true});
    $('#maxSalary').mask('#,##0', {reverse: true});

    $('#phone').mask('(000) 000-0000');

    // VALIDATE EXPERIENCES INPUTS FOR FRONT-END
    $('#exp_frontend1').mask('99');
    $('#exp_frontend2').mask('99');
    $('#exp_frontend3').mask('99');

    $('#exp_frontend1').on('input', function() {
        experience = $(this).val();
        $(this).val(validade_input_numbers(experience));
    });

    $('#exp_frontend2').on('input', function() {
        experience = $(this).val();
        $(this).val(validade_input_numbers(experience));
    });

    $('#exp_frontend3').on('input', function() {
        experience = $(this).val();
        $(this).val(validade_input_numbers(experience));
    });

    $('#experience').on('input', function() {
        experience = $(this).val();
        $(this).val(validade_input_numbers(experience));
    });
    

    // VALIDATE EXPERIENCES INPUTS FOR BACK-END
    $('#exp_backend1').mask('99');
    $('#exp_backend2').mask('99');
    $('#exp_backend3').mask('99');
    
    $('#exp_backend1').on('input', function() {
        experience = $(this).val();
        $(this).val(validade_input_numbers(experience));
    });
    $('#exp_backend2').on('input', function() {
        experience = $(this).val();
        $(this).val(validade_input_numbers(experience));
    });
    $('#exp_backend3').on('input', function() {
        experience = $(this).val();
        $(this).val(validade_input_numbers(experience));
    });

    // VALIDATE EXPERIENCES INPUTS FOR DATABASE
    $('#exp_database1').mask('99');
    $('#exp_database2').mask('99');
    $('#exp_database3').mask('99');

    $('#exp_database1').on('input', function() {
        experience = $(this).val();
        $(this).val(validade_input_numbers(experience));
    });
    $('#exp_database2').on('input', function() {
        experience = $(this).val();
        $(this).val(validade_input_numbers(experience));
    });
    $('#exp_database3').on('input', function() {
        experience = $(this).val();
        $(this).val(validade_input_numbers(experience));
    });

    // VALIDATE EXPERIENCES INPUTS FOR CLOUD COMPUTING
    $('#exp_cloud1').mask('99');
    $('#exp_cloud2').mask('99');
    $('#exp_cloud3').mask('99');

    $('#exp_cloud1').on('input', function() {
        experience = $(this).val();
        $(this).val(validade_input_numbers(experience));
    });
    $('#exp_cloud2').on('input', function() {
        experience = $(this).val();
        $(this).val(validade_input_numbers(experience));
    });
    $('#exp_cloud3').on('input', function() {
        experience = $(this).val();
        $(this).val(validade_input_numbers(experience));
    });
});
