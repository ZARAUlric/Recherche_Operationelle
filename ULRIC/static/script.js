function generateMatrix(){

let size = document.getElementById("size").value;
document.getElementById("sizeInput").value = size;

let html = "<table border='1'>";

for(let i=0;i<size;i++){

html += "<tr>";

for(let j=0;j<size;j++){

html += "<td>";
html += "<input type='number' name='matrix' required>";
html += "</td>";

}

html += "</tr>";

}

html += "</table>";

document.getElementById("matrix").innerHTML = html;

}