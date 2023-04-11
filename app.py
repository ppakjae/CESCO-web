import os
import json
import tempfile
from flask import Flask, render_template, request, flash
from werkzeug.utils import secure_filename
import subprocess
import markdown2
import markdown

app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key"

# MYTHRIL_PATH = "/home/ppakjae/Downloads/mythril-0.23.17/myth"
MYTHRIL_PATH = "/home/infosec/Desktop/mythril-develop/myth"


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("file")
        code = request.form.get("code")
        mode = request.form["mode"]

        if file:
            filename = secure_filename(file.filename)
            _, file_ext = os.path.splitext(filename)

            if file_ext != ".sol":
                flash("Please upload a Solidity (.sol) file.")
                return render_template("index.html")

            temp_dir = tempfile.mkdtemp()
            file.save(os.path.join(temp_dir, filename))
            file_path = os.path.join(temp_dir, filename)

        elif code:
            temp_file = tempfile.NamedTemporaryFile(mode="w", dget_flashed_messageselete=False, suffix=".sol")
            temp_file.write(code)
            temp_file.close()
            file_path = temp_file.name

        else:
            flash("Please provide a Solidity file or enter the code.")
            return render_template("index.html")

        use_solv = request.form.get("use_solv")
        solv_version = request.form.get("solv_version")

        use_t = request.form.get("use_t")
        transaction_count = request.form.get("transaction_count")

        mythril_command = [MYTHRIL_PATH, mode, file_path, "-o", "json"]

        if use_solv == "on" and solv_version:
            mythril_command.extend(["--solv", solv_version])

        if use_t == "on" and transaction_count:
            mythril_command.extend(["-t", transaction_count])

        try:
            mythril_output = subprocess.check_output(
                mythril_command, stderr=subprocess.PIPE,
            ).decode("utf-8")

        except subprocess.CalledProcessError as e:
            mythril_output = e.output.decode("utf-8")

        mythril_json = None
        if mythril_output:
            try:
                mythril_json = json.loads(mythril_output)
            except json.JSONDecodeError as json_error:
                print(f"Failed to parse JSON: {json_error}")
                # flash("An error occurred while analyzing the Solidity code. Please try again.")

        return render_template("index.html", mythril_output=mythril_output, mythril_json=mythril_json)

    return render_template("index.html")


@app.route("/opcodes", methods=["GET", "POST"])
def opcodes():
    with open("opcodes.json", 'r') as f:
        data = json.load(f)
    return render_template("opcodes.html", table_data=data)

@app.route("/swc", methods=["GET", "POST"])
def swc():
    with open("swc_simple.json", 'r') as f:
        data = json.load(f)
    return render_template("swc_main.html", swc_data=data)

@app.route("/swc/<swc_id>", methods=["GET"])
def swc_id_description(swc_id):
    with open("swc.json", 'r') as f:
        data = json.load(f)

    md_content = data[swc_id]["markdown"]
    md_parser = markdown2.Markdown(extras=['tables'])
    html_content = md_parser.convert(md_content)
    html_content = html_content.replace('<table>', '<table class="table">')

    md_code = data[swc_id]["code"]
    with open(md_code, 'r') as file:
        code = file.read()
    html_code = markdown.markdown(code)

    return render_template("swc_description.html", swc_description=html_content, code = html_code)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
