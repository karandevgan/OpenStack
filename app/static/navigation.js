function showCheckBoxes()
{
    labelArray = document.getElementsByName("selectLabel")
    for (var i=0; i < labelArray.length; i++)
    {
        labelArray[i].style.display="inline";
    }

    document.getElementById("DeleteButtons").style.display="inline";
}

function hideCheckBoxes()
{
    labelArray = document.getElementsByName("selectLabel")
    for (var i=0; i < labelArray.length; i++)
    {
        labelArray[i].style.display="none";
    }

    document.getElementById("DeleteButtons").style.display="none";   
}