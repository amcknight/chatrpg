var i = 0;

function refresh() {
    

    document.getElementById("content").innerHTML = i;
    i++;
    setTimeout(refresh, 2000);
}

refresh()
