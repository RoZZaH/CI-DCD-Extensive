
const $genres = document.getElementById("genres");
const $counties = document.getElementById("counties");
$genres.addEventListener("change", checkCheckboxes, false);
$counties.addEventListener("change", checkCheckboxes, false);


function checkCheckboxes(e){
  if(e.target !== e.currentTarget){
    const clickedArea = e.target.closest("#genres") || e.target.closest(".province")
    const eid = clickedArea.id
    const allCheckboxes = [...document.getElementById(eid).querySelectorAll("input[type=checkbox]")]
    const ALLcheckbox = allCheckboxes[0]
    const checkboxes = allCheckboxes.slice(1)
    const clicked = e.target.closest("input[type=checkbox]")
    if(clicked.value != "all"){
      const numberChecked = checkboxes.filter(input => input.checked).length
      switch(numberChecked){
        case 0:
          unCheckAll()
          break
        case checkboxes.length:
          checkAll()
          break
        default:
          someCheck()
      }
    } else {
      clicked.checked == true ? checkAll() : unCheckAll()
    }
    
    function someCheck(){
      ALLcheckbox["indeterminate"] = true
      clicked.checked
    }
      
    function checkAll(){
      ALLcheckbox["indeterminate"] = false
      for(checkbox of allCheckboxes){
          checkbox.checked = true
      }
    }  

    function unCheckAll(){
      ALLcheckbox["indeterminate"] = false
      for(checkbox of allCheckboxes){
          checkbox.checked = false
      }
    }    
  }

  e.stopPropagation()
}


