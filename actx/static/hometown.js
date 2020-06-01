[ ...document.getElementsByClassName("origin-county") ].forEach(
    el => el.addEventListener("change", function() {
    oTown_select = this.nextElementSibling.nextElementSibling;
    loadTowns(this.value).then(
        data => oTown_select.innerHTML = data
    )
    
    /*
    fetch("/town/" + this.value).then(function(response){
        response.json().then( function(data) {
            //console.table(data)
            let optionHTML = ""
            for(let town of data.towns) {
                optionHTML += `<option value='${town.val}'>${town.name}</option>`
            }
            oTown_select.innerHTML = optionHTML

        })
    }) */
}))

async function loadTowns(county){
    let response = await fetch(`/town/${county}`)
    let data = await response.json()
    let optHTML = ""
            for(let town of data.towns){
                optHTML += `<option values="${town.val}">${town.name}</option>`
            }
    return optHTML
}




