from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/results", methods=["POST"])
def results():
    # For now this just passes the form input through so the page renders.
    # Will wire the pipeline (geocode -> ticketmaster -> maps + weather -> ranking)
    # in here next

    interest = request.form.get("interest", "")
    location = request.form.get("location", "")

    return render_template("results.html", interest=interest, location=location)


if __name__ == "__main__":
    app.run(debug=True)
