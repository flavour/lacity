
Autocompleter = function(
    field_array, // an array of input fields

    value,
    
    url_function, // 
    set_fields_from_data,
    
    form,
    select_from_registry,
    select_from_registry_row,
    object_autocomplete_row,
    object_autocomplete_label,
    clear_form_link,
    edit_selected_object_link,
    object_load_throbber,
    real_input,
    dummy_input
) {
    var self = this
    var fields = $(field_array)
    function enable_fields() {
        fields.removeAttr('disabled')
    }
    function disable_fields() {
        fields.attr('disabled', true)
    }
    function show(element) {
        element.removeClass('hide')
    }
    function hide(element) {
        element.addClass('hide')
    }
    hide(dummy_input)
    
    
    var object_id = real_input.val()
    if (object_id > 0) {
        // If an ID present then disable input fields
        alert("disabling input fields")
        show(clear_form_link)
        show(edit_selected_object_link)
        disable_fields()
    }
    
    // Set up Listeners
    select_from_registry.click(function () {
        alert("select_from_registry.click")

        hide(select_from_registry_row)

        show(object_autocomplete_row)
        show(object_autocomplete_label)

        show(dummy_input)
        dummy_input.focus();
    });
    dummy_input.focusout(function() {
        alert("dummy_input.focusout")
        object_id = real_input.val()
        
        hide(dummy_input)
        hide(object_autocomplete_label)
        show(select_from_registry_row)
        if (object_id > 0) {
             show(clear_form_link)
        }
    });
    clear_object_form = function() {
        alert("clear_object_form")
        enable_fields()
        real_input.val('')
        fields.val('')
        hide(clear_form_link)
        hide(edit_selected_object_link)
    }
    self.edit_selected_object_form = function() {
        alert("edit_selected_object_form")
        enable_fields()
        hide(edit_selected_object_link)
    }
    
    // Called on post-process by the Autocomplete Widget
    var select_object = self.select_object = function(object_id) {
        alert("select_object "+object_id)
        hide(select_from_registry)
        hide(clear_form_link)
        show(object_load_throbber)
        clear_object_form()
        
        $.getJSONS3(
            url_function(object_id),
            function (data) {
                try {
                    disable_fields()
                    real_input.val(
                        set_fields_from_data(data)
                    )
                }
                catch(e) {
                    alert(e)
                    real_input.val('')
                }
                hide(object_load_throbber)
                show(select_from_registry)
                show(clear_form_link)
                show(edit_selected_object_link)
            }
        );
        hide(object_autocomplete_row)
        show(select_from_registry_row)
    };
    if (value != 'None') {
        real_input.val(value)
        select_object(value)
    }
    form.submit(
        function() {
            alert("form.submit")
            // The form is being submitted

            // Do the normal form-submission tasks
            // @ToDo: Look to have this happen automatically
            // http://forum.jquery.com/topic/multiple-event-handlers-on-form-submit
            // http://api.jquery.com/bind/
            S3ClearNavigateAwayConfirm()

            // Ensure that all fields aren't disabled (to avoid wiping their contents)
            enable_fields()

            // Allow the Form's Save to continue
            return true
        }
    );
}
