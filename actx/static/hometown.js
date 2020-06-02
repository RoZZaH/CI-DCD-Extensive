[ ...document.getElementsByClassName("origin-county") ].forEach(
    el => el.addEventListener("change", () => {
    oTown_select = el.nextElementSibling.nextElementSibling;
    loadTowns(el.value).then(
        data => oTown_select.innerHTML = data
    )
}))


async function loadTowns(county){
    let response = await fetch(`/town/${county}`)
    let data = await response.json()
    let optionHTML = ""
            for(let town of data.towns){
                optionHTML += `<option values="${town.val}">${town.name}</option>`
            }
    return optionHTML
}

function choiceSelect(selector, choiceVar){
    let choices = document.querySelector(selector).options
    for(choice of choices) {
        if(choice.value == choiceVar){
           choice.setAttribute("selected", "selected")
        }
    }        
}



