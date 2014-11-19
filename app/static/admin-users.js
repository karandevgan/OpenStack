function editField(id){
    var childElements = id.parentNode.parentNode.children
    childElements[6].style.display = 'none';
    childElements[7].style.display = 'none';
    childElements[8].style.display = 'table-cell';
    childElements[9].style.display = 'table-cell';
    childElements[10].style.display = 'none';
    childElements[11].style.display = 'table-cell';
    document.getElementById('updateSubmit').disabled = false;
} 

function cancelField(id){
    var childElements = id.parentNode.parentNode.children
    childElements[6].style.display = 'table-cell';
    childElements[7].style.display = 'table-cell';
    childElements[8].style.display = 'none';
    childElements[9].style.display = 'none';
    childElements[10].style.display = 'table-cell';
    childElements[11].style.display = 'none';
}