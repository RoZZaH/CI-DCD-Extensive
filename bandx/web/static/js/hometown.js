document.querySelector("select.origin-county").addEventListener("change", function(){ 
    oTown_select = document.querySelector("select.origin-town")
    loadTowns(this.value).then(
        data => oTown_select.innerHTML = data
    )
})


async function loadTowns(county="Antrim"){
    let response = await fetch("/towns/"+county)
    let data = await response.json()
    let optionHTML = ""
        for(let town of data.towns){
            optionHTML += `<option values="${town.val}">${town.name}</option>`
        }
    return optionHTML
}

/* selecting town if value known */
function choiceSelect(selector, choiceVar){
    let choices = document.querySelector(selector).options
    for(choice of choices) {
        if(choice.value == choiceVar){
           choice.setAttribute("selected", "selected")
        }
    }        
}



