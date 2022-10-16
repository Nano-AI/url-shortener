from flask import Flask, render_template, request, redirect
import sqlite3
import uuid
import validators

app = Flask(__name__, template_folder="./app/templates")

connection = sqlite3.connect("urls.db", check_same_thread=False, isolation_level=None)
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS url (href TEXT, id TEXT)")

@app.route("/<string:url_id>")
def shorten(url_id):
    urls_query = cursor.execute("""SELECT * FROM url WHERE href = (SELECT href FROM url WHERE id = \"{}\")""".format(url_id))
    urls = urls_query.fetchone()
    if urls is None:
        return redirect("/")
    href, id = urls
    return redirect(href)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/success/<string:id>")
def success_url(id):
    url = request.base_url.replace(request.path, "") + "/" + id
    return render_template("success.html", url=url)

@app.route("/add/", methods=['POST'])
def add_url():
    data = dict(request.form)

    if "url" not in data:
        return redirect("/")

    if not validators.url(data["url"]):
        return redirect("/")

    url_id = str(uuid.uuid4())[:8]
    urls_query = cursor.execute("""SELECT * FROM url WHERE id = (SELECT id FROM url WHERE href = \"{}\")""".format(data["url"]))
    urls = urls_query.fetchone()

    if urls is not None:
        _, existing_id = urls
        return redirect("/success/" + existing_id)

    cursor.execute("""INSERT INTO url (href, id) VALUES ("{}", "{}")""".format(data["url"], url_id))
    return redirect("/success/" + url_id)

if __name__ == "__main__":
    app.run(debug=True) 
