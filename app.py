import random

import json

import os

import flask

from flask import Flask, render_template, request

from flask_sqlalchemy import SQLAlchemy

from flask_migrate import Migrate

from flask_wtf import FlaskForm

from wtforms import StringField


app = Flask(__name__)
app.debug = True

app.secret_key = "123"


# FOR SQLite
#
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ## Присваиваем значение переменной окружения параметру настроек
# # # app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
# # app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@127.0.0.1:5432/postgres" FOR PostgreSQL ....
# #
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


with open('teachers.json', 'r', encoding='utf-8') as f:
    teachers = json.load(f)


with open('dayname.json', 'r', encoding='utf-8') as f:
    dayname = json.load(f)
    eng_dayname = list(dayname.keys())  # english dayname version, we can get russian translate from values


with open('goals.json', 'r', encoding='utf-8') as f:
    goals_file = json.load(f)


emoji = ['⛱', '🏫', '🏢', '🚜 🐷', '💻']
# &#128055;
all_random_teachers = random.sample(teachers, len(teachers))


# main page
@app.route('/')
def render_index():
    # deleted with open teachers json file
    random_teachers_list = random.sample(teachers, 6)

    return render_template('index.html',
                           random_teachers_list=random_teachers_list,
                           )


# show us page with all tutors
@app.route('/all/')
def all_page():
    teachers_sorted_by_rating = sorted(teachers, key=lambda teacher: teacher['rating'], reverse=True)
    count_teachers = len(teachers)
    return render_template('all.html',
                           teachers=teachers,
                           count_teachers=count_teachers,
                           all_random_teachers=all_random_teachers,
                           teachers_sorted_by_rating=teachers_sorted_by_rating,
                           )


# show us page with tutors, what depends on var /<goal>
@app.route('/goals/<goal>/')
def goal_page(goal):
    if goal == 'travel':
        emoji_item = emoji[0]
    elif goal == 'work':
        emoji_item = emoji[2]
    elif goal == 'study':
        emoji_item = emoji[1]
    elif goal == 'programming':
        emoji_item = emoji[4]
    else:
        emoji_item = emoji[3]

    teachers_goal_list = [teacher for teacher in teachers if goal in teacher['goals']]
    sorted_by_rating_teachers_goal_list = sorted(teachers_goal_list, key=lambda teachers: teachers['rating'],
                                                 reverse=True)
    return render_template('goal.html',
                           goal=goal,
                           goals_file=goals_file,
                           teachers=teachers,
                           teachers_goal_list=teachers_goal_list,
                           sorted_by_rating_teachers_goal_list=sorted_by_rating_teachers_goal_list,
                           emoji=emoji,
                           emoji_item=emoji_item
                           )


# personal tutor page
@app.route('/profiles/<int:id_tutor>/')
def tutor_page(id_tutor):
    # i deleted with open teachers json file from here
    id_teacher_list = [i for i in teachers if i['id'] == id_tutor][0]
    teacher_goal_list = [goal for goal in id_teacher_list['goals']]
    ru_teacher_goal_list = []

    for goal, ru_goal in goals_file.items():
        if goal in teacher_goal_list:
            ru_teacher_goal_list.append(ru_goal)

    # {% for goal in teacher_goal_list %}{% endfor %} {{ i }}
    return render_template('profile.html',
                           id_tutor=id_tutor,
                           id_teacher_list=id_teacher_list,
                           dayname=dayname,
                           eng_dayname=eng_dayname,
                           goals_file=goals_file,
                           teacher_goal_list=teacher_goal_list,
                           ru_teacher_goal_list=ru_teacher_goal_list
                           )


# tutor selection request page
@app.route('/request/', methods=["GET", "POST"])
def tutor_selection_request():
    with open('goals.json', 'r', encoding='utf-8') as f:
        goals_file = json.load(f)
    return render_template('request.html',
                           goals_file=goals_file,
                           )


# tutor selection DONE
@app.route('/request_done/', methods=["GET", "POST"])
def tutor_selection_done():
    goal = request.form['goal']
    week_time = request.form['time']
    fname = request.form.get('fname')
    fphone = request.form.get('fphone')

    dict_from_request = {"clientName": fname,
                         "clientPhone": fphone,
                         "clientGoal": goal,
                         "clientWeektime": week_time
                         }

    with open('request.json', 'r', encoding='utf-8') as f:
        request_list = json.load(f)
        request_list.append(dict_from_request)

    with open('request.json', 'w', encoding='utf-8') as f:
        json.dump(request_list, f, indent=4, ensure_ascii=False)

    return render_template('request_done.html',
                           goal=goal,
                           week_time=week_time,
                           fname=fname,
                           fphone=fphone,
                           goals_file=goals_file)


# contains and handle form of tutor booking
@app.route('/booking/<int:id_tutor>/<day_name_link>/<booking_time>/', methods=["GET", "POST"])
def booking_form(id_tutor, day_name_link, booking_time):
    teacher_name = [i for i in teachers if i['id'] == id_tutor][0]
    ru_dayname = dayname[day_name_link]

    return render_template('booking.html',
                           id_tutor=id_tutor,
                           day_name_link=day_name_link,
                           ru_dayname=ru_dayname,
                           teacher_name=teacher_name,
                           booking_time=booking_time,
                           )


# shows us booking done status and writes post-data in JSON file
@app.route('/booking_done/', methods=["GET", "POST"])
def booking_done_pg():
    cWeekday = request.form["clientWeekday"]
    cTime = request.form["clientTime"]
    cTeacher = request.form["clientTeacher"]
    clientName = request.form["clientName"]
    clientPhone = request.form["clientPhone"]

    dict_from_booking = {"clientName": clientName,
                         "clientPhone": clientPhone,
                         "cTeacher": cTeacher,
                         "cWeekday": cWeekday,
                         "cTime": cTime}

    with open('booking.json', 'r', encoding='utf-8') as f:
        booking_list = json.load(f)
        booking_list.append(dict_from_booking)

    with open('booking.json', 'w', encoding='utf-8') as f:
        json.dump(booking_list, f, indent=4, ensure_ascii=False)

    return render_template('booking_done.html',
                           dayname=dayname,
                           cWeekday=cWeekday,
                           cTime=cTime,
                           cTeacher=cTeacher,
                           clientName=clientName,
                           clientPhone=clientPhone
                           )


class Teacher(db.Model):
    __tablename__ = "teachers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    schedule = db.Column(db.String, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    picture = db.Column(db.String, nullable=False)
    about = db.Column(db.String, nullable=False)
    goals = db.Column(db.String, nullable=False)
    students = db.relationship("Booking")

class Request(db.Model):
    __tablename__ = "requests"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False)
    goal = db.Column(db.String, nullable=False)
    time_in_week = db.Column(db.String, nullable=False)


class Booking(db.Model):
    __tablename__ = "booking"
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String, nullable=False)
    user_phone = db.Column(db.String, nullable=False)
    weekday = db.Column(db.String, nullable=False)
    time = db.Column(db.String, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id"))
    teacher = db.relationship("Teacher")


# db.create_all()

# with open('teachers.json', 'r', encoding='utf-8') as f:
#         teachers_json = json.load(f)
#         teachers_data_list = []

# for teacher in teachers:
#     db.session.add(Teacher(name=teacher["name"], price=teacher["price"], schedule=str(teacher["free"]),
#                             rating=teacher["rating"], picture=teacher["picture"], about=teacher["about"],
#                             goals=str(teacher["goals"])))


# for teacher in teachers:
#     #print(type(teacher))
#     #print(teacher['free'])
#     for t in teacher['free']['mon']:
#         print(t)

    #a = teacher.values()
    #print(a['friday'])


# db.session.commit()


if __name__ == "__main__":
    app.run()


