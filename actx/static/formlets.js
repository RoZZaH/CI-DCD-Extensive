let today = new Date();
let dd = String(today.getDate()).padStart(2, '0');
let mm = String(today.getMonth() + 1).padStart(2, '0');
let yyyy = today.getFullYear();
// datefield parsed as yyyy-mm-dd
today = `${yyyy}-${mm}-${dd}`;

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

/**
 * Remove a form.
 */
function removeForm() {
    let $removedForm = $(this).closest('.subform');
    let removedIndex = parseInt($removedForm.data('index'));
   // console.log(removedIndex)
    $removedForm.remove();

    // Update indices
    //adjustIndices(removedIndex);
}

/**
 * Add a new form.
 */
function addForm() {
    let stuff = this.parentNode.dataset.inx
    console.log(stuff) //.getAttribute("data-inx"))


    // Get Last index
    let $lastForm =  $('.subform').last();

    let newIndex = 0;

    if ($lastForm.length > 0) {
        newIndex = parseInt($lastForm.data('index')) + 1;
    }
    // Maximum of 20 subforms
    if (newIndex > 20) {
        console.log('[WARNING] Reached maximum number of elements');
        return;
    }



    if(stuff == "contact") {

    let $newForm = ` 
    <div id="contact-${newIndex}-form" class="subform" data-index="${newIndex}">
    <label for="contacts-${newIndex}-refname">Ref name</label>
    <input id="contacts-${newIndex}-refname" name="contacts-${newIndex}-refname" type="text" value="">

    <label for="contacts-${newIndex}-contact_1">Contact 1</label>
    <input id="contacts-${newIndex}-contact_1" name="contacts-${newIndex}-contact_1" type="text">
    
    <label for="contacts-${newIndex}-email_1">Email 1</label>
    <input id="contacts-${newIndex}-email_1" name="contacts-${newIndex}-email_1" type="text">

    <label for="contacts-${newIndex}-email_2">Email 1</label>
    <input id="contacts-${newIndex}-email_2" name="contacts-${newIndex}-email_2" type="text">

    <a class="remove" href="#">Remove</a>
    <hr/>
    </div>
    `
    $('#subforms-container-contact').append($newForm);
}

if(stuff == "member") {

    let $newForm = ` 
    <div id="member-${newIndex}-form" class="subform" data-index="${newIndex}">
    <label for="members-${newIndex}-namec">Member key</label>
    <input id="members-${newIndex}-namec" name="members-${newIndex}-namec" type="text" value="">

    <label for="members-${newIndex}-number">Member value</label>
    <input id="members-${newIndex}-number" name="members-${newIndex}-number" type="text">

    <a class="remove" href="#">Remove</a>
    <hr/>
    </div>
    `
    $('#subforms-container-member').append($newForm);
}

if(stuff == "dates") {
    let $newForm = ` 
    <div id="date-${newIndex}-form" class="subform" data-index="${newIndex}">
        <label for="tour_dates-${newIndex}-td_date">Date</label>
        <input id="tour_dates-${newIndex}-td_date" name="tour_dates-${newIndex}-td_datetime" type="date" value="${today}">
        
        <label for="tour_dates-${newIndex}-td_time_hh">Time-Hour</label>
        <select id="tour_dates-${newIndex}-td_time_hh" name="tour_dates-${newIndex}-td_time_hh"><option value="1">1</option><option value="2">2</option><option value="3">3</option><option value="4">4</option><option value="5">5</option><option value="6">6</option><option value="7">7</option><option value="8" selected="selected">8</option><option value="9">9</option><option value="10">10</option><option value="11">11</option><option value="12">12</option></select>
        
        <label for="tour_dates-${newIndex}-td_time_mm">Time-Mins</label>
        <select id="tour_dates-${newIndex}-td_time_mm" name="tour_dates-${newIndex}-td_time_mm"><option selected value="0">00</option><option value="15">15</option><option value="30">30</option><option value="45">45</option></select>
        
        <label for="tour_dates-${newIndex}-td_time_ampm">Date</label>
        <select id="tour_dates-${newIndex}-td_time_ampm" name="tour_dates-${newIndex}-td_time_ampm"><option value="0">AM</option><option selected value="12">PM</option></select>

        <label for="tour_dates-${newIndex}.td_hometown.origin_county">Venue County</label>
        <select id="tour_dates-${newIndex}.td_hometown.origin_county" name="tour_dates-${newIndex}.td_hometown.origin_county">
            <option value="Antrim">Antrim</option><option value="Armagh">Armagh</option><option value="Carlow">Carlow</option><option value="Cavan">Cavan</option><option value="Clare">Clare</option><option value="Cork">Cork</option><option value="Derry">L/Derry</option><option value="Donegal">Donegal</option><option value="Down">Down</option><option value="Dublin">Dublin</option><option value="Fermanagh">Fermanagh</option><option value="Galway">Galway</option><option value="Kerry">Kerry</option><option value="Kildare">Kildare</option><option value="Kilkenny">Kilkenny</option><option value="Laois">Laois</option><option value="Leitrim">Leitrim</option><option value="Limerick">Limerick</option><option value="Longford">Longford</option><option value="Louth">Louth</option><option value="Mayo">Mayo</option><option value="Meath">Meath</option><option value="Monaghan">Monaghan</option><option value="Offaly">Offaly</option><option value="Roscommon">Roscommon</option><option value="Sligo">Sligo</option><option value="Tipperary">Tipperary</option><option value="Tyrone">Tyrone</option><option value="Waterford">Waterford</option><option value="Westmeath">Westmeath</option><option value="Wexford">Wexford</option><option value="Wicklow">Wicklow</option>
        </select>
        <label for="tour_dates-${newIndex}.td_hometown.origin_town">Venue Town</label>
        <select id="tour_dates-${newIndex}.td_hometown.origin_town" name="tour_dates-${newIndex}.td_hometown.origin_town">
            ${ANTRIM_TOWNS}
        </select>
     

        <label for="tour_dates-${newIndex}-venue_name">Venue Name</label>
        <input id="tour_dates-${newIndex}-venue_name" name="tour_dates-${newIndex}-venue_name" type="text">
    
        <a class="remove" href="#">Remove</a>
        <hr/>
    </div>
    `
    $('#subforms-container-date').append($newForm);
}



    [ ...document.querySelectorAll(".remove") ].forEach( el => el.addEventListener("click", removeForm))
}


document.addEventListener("DOMContentLoaded", function(){
    [ ...document.querySelectorAll(".add") ].forEach( el => el.addEventListener("click", addForm));
    [ ...document.querySelectorAll(".remove") ].forEach( el => el.addEventListener("click", removeForm));
    /* find wtforms datefield */
    $('#subforms-container-date').find('input[type=date]').attr("value", today); //attr("value", today);



});