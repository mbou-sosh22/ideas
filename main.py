import sqlite3

from flask import Flask, render_template, request, redirect

app = Flask(__name__)
us = None


class User:
    def __init__(self, username, password, new_user=False):
        self.con = sqlite3.connect("all_tables.sqlite")
        self.error = ""
        if not new_user:
            cur = self.con.cursor()
            up = cur.execute(f"""SELECT user_id, password FROM users WHERE username='{username}'""").fetchone()
            if up:
                if password == up[1]:
                    self.user_id = up[0]
                    self.username = username
                    self.password = up[1]
                else:
                    self.error = "Неверный пароль"
            else:
                self.error = f"Нет пользователя '{username}'"
        else:
            cur = self.con.cursor()
            cur.execute(f"""INSERT INTO users(username, password) VALUES ('{username}', '{password}')""")
            cur.close()
            self.con.commit()
            v = self.con.execute(f"""SELECT user_id FROM users WHERE username='{username}'""").fetchone()
            self.user_id = v[0]
            self.username = username
            self.password = password


class Idea:
    def __init__(self, idea_, user):
        self.con = sqlite3.connect("all_tables.sqlite")
        cur = self.con.cursor()
        cur.execute(f"""INSERT INTO ideas(idea_text, username) VALUES ('{idea_}', '{user}')""")
        self.con.commit()


@app.route('/', methods=["POST", "GET"])
def login():
    global us
    error = ""
    if request.method == "POST":
        user_login = request.form["user_login"]
        password = request.form["password"]
        if request.form["btn-log-reg"] == "Вход":
            us = User(user_login, password)
            if us.error == "":
                return redirect("/idea/")
            else:
                return render_template("login_form.html", error=us.error)
        else:
            us = User(user_login, password, new_user=True)
            return redirect("/idea/")
    else:

        return render_template("login_form.html", error="")


@app.route('/idea/', methods=["POST", "GET"])
def idea():
    global us
    if request.method == "POST":
        name = request.form["name"]
        email_address = request.form["email_address"]
        idea_text = request.form["idea_text"]
        ideaa = Idea(idea_text, us.username)
        return redirect("/all_ideas/")
    else:
        return render_template("change.html", us=us)


@app.route("/all_ideas/")
def my():
    ideas = sqlite3.connect("all_tables.sqlite").cursor().execute(f"""SELECT idea_text, username FROM ideas""").fetchall()[::-1]
    return render_template("all_ideas.html", ideas=ideas, us=us)


if __name__ == '__main__':
    app.run(debug=True)
