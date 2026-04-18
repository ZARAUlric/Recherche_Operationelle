from flask import Flask, render_template, request
from algorithm import solve_assignment

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/calculate", methods=["POST"])
def calculate():

    matrix = request.form.getlist("matrix")
    size = int(request.form["size"])
    mode = request.form["mode"]

    matrix = list(map(int, matrix))

    matrix2 = []
    k = 0

    for i in range(size):
        row = []
        for j in range(size):
            row.append(matrix[k])
            k += 1
        matrix2.append(row)

    assign, cost = solve_assignment(matrix2, mode)

    return render_template(
        "result.html",
        matrix=matrix2,
        assign=assign,
        cost=cost
    )


if __name__ == "__main__":
    app.run(debug=True)