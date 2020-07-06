/* based on https://www.rmedgar.com/blog/dynamic-fields-flask-wtf */
/**
 * Remove a form.
 */
function removeForm() {
    let $removedForm = $(this).closest('.subform');
    let removedIndex = parseInt($removedForm.data('index'));
    removedIndex == 0 ?  true: $removedForm.remove()
    // error message can't remove first field
    /**  Update indices - Not needed for Mongo
     * adjustIndices(removedIndex); */
}

/**
 * Add a new form. Modified RG
 */
function addForm() {
    let parent = this.parentNode
    console.log(parent.dataset.formlet)
    let $lastForm = parent.querySelector('.subform:last-child')
    let $lastIndex = parseInt($lastForm.dataset.index)
    let newIndex =  $lastIndex+1
    let $newForm = ''
    
    switch(parent.dataset.formlet) {

    case "number" :
    $newForm = ` 
    <div id="number-${newIndex}-form" class="subform numbers" data-index="${newIndex}">
        <div class="numbers-radio-wrapper">
        <label class="number-label" for="contact_details-contact_numbers-${newIndex}-mobile-0">mobile</label> 
            <input checked class="number-radio" id="contact_details-contact_numbers-${newIndex}-mobile-0" name="contact_details-contact_numbers-${newIndex}-mobile" type="radio" value="True">
        <label class="number-label" for="contact_details-contact_numbers-${newIndex}-mobile-1">landline</label> 
            <input class="number-radio" id="contact_details-contact_numbers-${newIndex}-mobile-1" name="contact_details-contact_numbers-${newIndex}-mobile" type="radio" value="False">
        </div>
        <input class="number-field" id="contact_details-contact_numbers-${newIndex}-number" name="contact_details-contact_numbers-${newIndex}-number" placeholder="+353" type="text" value="">
        
        <button type="button" class="remove btn-subform">Remove</button>
    </div>
    `
    $('#subforms-container-number').append($newForm);
    break

    case "member" :
    $newForm = ` 
    <div id="member-${newIndex}-form" class="subform" data-index="${newIndex}">
        <label for="members-${newIndex}-instruments">Instrument(s)</label>
            <input id="members-${newIndex}-instruments" name="members-${newIndex}-instruments" type="text" value="" placeholder="use commas, between, instruments" >
        <label for="members-${newIndex}-musician" >Musician's Name</label>
            <input id="members-${newIndex}-musician" name="members-${newIndex}-musician" type="text">
        
        <button type="button" class="remove btn-subform">Remove</button>
    </div>
    `
    $('#subforms-container-member').append($newForm);
    break

    case "email" :
    $newForm = `
    <div id="email-${newIndex}-form" class="subform" data-index="${newIndex}">
        <label class="instrument-label" for="contact_details-contact_emails-${newIndex}-email_title">Email Title</label>
            <input class="instrument-input" id="contact_details-contact_emails-${newIndex}-email_title" name="contact_details-contact_emails-${newIndex}-email_title" placeholder="Enquiries" required type="text" value="">
        <label class="band-member-label" for="contact_details-contact_emails-${newIndex}-email_address">Email Address</label>
            <input class="band-member-input" id="contact_details-contact_emails-${newIndex}-email_address" name="contact_details-contact_emails-${newIndex}-email_address" placeholder="Enquiries" required type="text" value="">

        <button type="button" class="remove btn-subform">Remove</button>
    </div>
    `
    $('#subforms-container-email').append($newForm);
    break
    }

    /* refresh 'remove' listeners */
    [ ...document.querySelectorAll(".remove") ].forEach( el => el.addEventListener("click", removeForm, false))
}

/**
 * adjustIndices - not needed for Mongo 
 *
function adjustIndices(removedIndex) {
    let $forms = $('.subform')

    $forms.each(i => {
        let $form = $(this)
        let index = parseInt($form.data('index'))
        let newIndex = index - 1

        if (index < removedIndex) {
            // Skip
            return true
        }

        // Change ID in form itself
        $form.attr('id', $form.attr('id').replace(index, newIndex));
        $form.data('index', newIndex);

        // Change IDs in form inputs
        $form.find('input').each(function(j) {
            let $field = $(this)
            $field.attr('id', $field.attr('id').replace(index, newIndex))
            $field.attr('name', $field.attr('name').replace(index, newIndex))
        })
    })
}
*/

/* 
// for datefield for 'tour-date' formlet on Doc loaded
let today = new Date();
let dd = String(today.getDate()).padStart(2, '0');
let mm = String(today.getMonth() + 1).padStart(2, '0');
let yyyy = today.getFullYear();
// datefield parsed as yyyy-mm-dd
today = `${yyyy}-${mm}-${dd}`;
*/


document.addEventListener("DOMContentLoaded", function(){
    [ ...document.querySelectorAll(".add") ].forEach( el => el.addEventListener("click", addForm));
    [ ...document.querySelectorAll(".remove") ].forEach( el => el.addEventListener("click", removeForm));
    /* find wtforms datefield */
  //  $('#subforms-container-date').find('input[type=date]').attr("value", today);

});