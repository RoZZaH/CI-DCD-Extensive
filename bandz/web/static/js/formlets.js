/* based on https://www.rmedgar.com/blog/dynamic-fields-flask-wtf */
/**
 * Remove a form.
 */
function removeForm() {
    let $removedForm = $(this).closest('.subform');
    let removedIndex = parseInt($removedForm.data('index'));
    removedIndex == 0 ? true: $removedForm.remove()
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
    case "member" :
    $newForm = ` 
    <div id="member-${newIndex}-form" class="subform" data-index="${newIndex}">
        <label for="members-${newIndex}-musician" ><span class="label-text">Musician's Name</span>
            <input id="members-${newIndex}-musician" name="members-${newIndex}-musician" type="text"></label>
        <label for="members-${newIndex}-instruments"><span class="label-text">Instrument(s)</span>
            <input id="members-${newIndex}-instruments" name="members-${newIndex}-instruments" type="text" value="" placeholder="use commas, between, instruments" ></label>
        <button type="button" class="remove btn-subform"><span class="btn-text">Remove</span> <i class="fa fa-trash"></i></button>
    </div>
    `
    document.getElementById('subforms-container-member').insertAdjacentHTML("beforeend", $newForm);
    break

    }

    /* refresh 'remove' listeners */
    [ ...document.querySelectorAll(".remove") ].forEach( el => el.addEventListener("click", removeForm, false))
}



document.addEventListener("DOMContentLoaded", function(){
    [ ...document.querySelectorAll(".add") ].forEach( el => el.addEventListener("click", addForm));
    [ ...document.querySelectorAll(".remove") ].forEach( el => el.addEventListener("click", removeForm));    
});
