$(function() {
    let el = document.getElementById("datab")
    let genrelist = el.dataset.genrelist.split(",")
    //console.log(genrelist)
    $("#testInput").tags({
        requireData: false,
        unique: true,
        maxTags: 8,
    }).autofill({
        color: "green",
        top: "0",
        left: "2em",
        data: genrelist
    }); 
});