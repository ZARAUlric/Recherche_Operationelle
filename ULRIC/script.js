function generateMatrix(){

let agents = document.getElementById("agents").value;
let tasks = document.getElementById("tasks").value;

let html = "<table border='1'>";

for(let i=0;i<agents;i++){

html += "<tr>";

for(let j=0;j<tasks;j++){

html += "<td>";
html += "<input type='number' name='matrix["+i+"]["+j+"]' required>";
html += "</td>";

}

html += "</tr>";

}

html += "</table>";

document.getElementById("matrix").innerHTML = html;

}