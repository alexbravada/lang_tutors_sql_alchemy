import random

import json

import os

import flask

from flask import Flask, render_template, request

from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.sql.expression import func

from flask_migrate import Migrate

from flask_wtf import FlaskForm

from wtforms import StringField


app = Flask(__name__)
app.debug = True

app.secret_key = "123"


# FOR SQLite
#
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///data_sql//test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ## Присваиваем значение переменной окружения параметру настроек
# # # app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
# # app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@127.0.0.1:5432/postgres" FOR PostgreSQL ....
# #
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


with open('teachers.json', 'r', encoding='utf-8') as f:
    teachers_json = json.load(f)


with open('dayname.json', 'r', encoding='utf-8') as f:
    dayname = json.load(f)
    eng_dayname = list(dayname.keys())  # english dayname version, we can get russian translate from values


with open('goals.json', 'r', encoding='utf-8') as f:
    goals_file = json.load(f)


emoji = ['⛱', '🏫', '🏢', '🚜 🐷', '💻']
# &#128055;


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
    students = db.relationship("Booking", back_populates="teacher")


class Booking(db.Model):
    __tablename__ = "booking"
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String, nullable=False)
    user_phone = db.Column(db.String, nullable=False)
    weekday = db.Column(db.String, nullable=False)
    time = db.Column(db.String, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id"))
    teacher = db.relationship("Teacher", back_populates="students")


class Request(db.Model):
    __tablename__ = "requests"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False)
    goal = db.Column(db.String, nullable=False)
    time_in_week = db.Column(db.String, nullable=False)


all_teachers_sql = db.session.query(Teacher).all()

# all_random_teachers = random.sample(all_teachers_sql, len(all_teachers_sql))




# main page
@app.route('/')
def render_index():
    random_teachers_list = random.sample(all_teachers_sql, 6)
    return render_template('index.html',
                           random_teachers_list=random_teachers_list,
                           )


# show us page with all tutors
@app.route('/all/', methods=['GET', 'POST'])
def all_page():
    all_random_teachers = db.session.query(Teacher).order_by(func.random()).all()
    #teachers_sorted_by_rating = sorted(all_teachers_sql, key=lambda teacher: teacher.rating, reverse=True)
    count_teachers = len(all_teachers_sql)
    teachers_sorted = all_random_teachers
    selected_r = ''
    selected_rt = ''
    selected_ex = ''
    selected_ch = ''
    if request.method == "POST":
        if request.form["filter"] == "by_random":
            selected_r = 'selected'
            teachers_sorted = all_random_teachers
        if request.form["filter"] == "by_rating":
            selected_rt = 'selected'
            teachers_sorted = db.session.query(Teacher).order_by(Teacher.rating.desc())
        if request.form["filter"] == "f_expensive":
            selected_ex = 'selected'
            teachers_sorted = db.session.query(Teacher).order_by(Teacher.price.desc())
        if request.form["filter"] == "f_cheap":
            selected_ch = 'selected'
            teachers_sorted = db.session.query(Teacher).order_by(Teacher.price)

    return render_template('all.html',
                           count_teachers=count_teachers,
                           teachers_sorted=teachers_sorted,
                           selected_r=selected_r,
                           selected_rt=selected_rt,
                           selected_ex=selected_ex,
                           selected_ch=selected_ch
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

    sorted_by_rating_teachers_goal_list = \
        db.session.query(Teacher).filter(Teacher.goals.contains(goal)).order_by(Teacher.rating.desc())

    # teachers_goal_list = db.session.query(Teacher).filter(Teacher.goals.contains(goal)).all()
    #sorted_by_rating_teachers_goal_list = sorted(teachers_goal_list, key=lambda teachers_json: teachers_json.rating, reverse=True)

    return render_template('goal.html',
                           goal=goal,
                           goals_file=goals_file,
                           sorted_by_rating_teachers_goal_list=sorted_by_rating_teachers_goal_list,
                           emoji=emoji,
                           emoji_item=emoji_item
                           )


# personal tutor page
@app.route('/profiles/<int:id_tutor>/')
def tutor_page(id_tutor):
    ru_teacher_goal_list = []
    teacher_from_id = db.session.query(Teacher).get_or_404(id_tutor)
    for goal, ru_goal in goals_file.items():
        if goal in json.loads(teacher_from_id.goals):
            ru_teacher_goal_list.append(ru_goal)

    return render_template('profile.html',
                           id_tutor=id_tutor,
                           schedule=json.loads(teacher_from_id.schedule),
                           name=teacher_from_id.name,
                           #goals=json.loads(teacher_from_id.goals),
                           rating=teacher_from_id.rating,
                           price=teacher_from_id.price,
                           picture=teacher_from_id.picture,
                           about=teacher_from_id.about,
                           eng_dayname=eng_dayname,
                           ru_teacher_goal_list=ru_teacher_goal_list,
                           )


# tutor selection request page
@app.route('/request/', methods=["GET", "POST"])
def tutor_selection_request():
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

    request_to_db = Request(name=fname, phone=fphone, goal=goal, time_in_week=week_time)
    db.session.add(request_to_db)
    db.session.commit()

    return render_template('request_done.html',
                           goal=goal,
                           week_time=week_time,
                           fname=fname,
                           fphone=fphone,
                           goals_file=goals_file)


# contains and handle form of tutor booking
@app.route('/booking/<int:id_tutor>/<day_name_link>/<booking_time>/', methods=["GET", "POST"])
def booking_form(id_tutor, day_name_link, booking_time):
    teacher_name = db.session.query(Teacher).get_or_404(id_tutor)
    ru_dayname = dayname[day_name_link]

    return render_template('booking.html',
                           id_tutor=id_tutor,
                           booking_time=booking_time,
                           day_name_link=day_name_link,
                           ru_dayname=ru_dayname,
                           teacher_name=teacher_name,

                           )


# shows us booking done status and writes post-data in JSON file
@app.route('/booking_done/', methods=["GET", "POST"])
def booking_done_pg():
    cWeekday = request.form["clientWeekday"]
    cTime = request.form["clientTime"]
    cTeacher = request.form["clientTeacher"]
    clientName = request.form["clientName"]
    clientPhone = request.form["clientPhone"]

    booking_to_database = Booking(user_name=clientName, user_phone=clientPhone, weekday=cWeekday, time=cTime,
                                  teacher_id=cTeacher)

    db.session.add(booking_to_database)
    db.session.commit()

    return render_template('booking_done.html',
                           dayname=dayname,
                           cWeekday=cWeekday,
                           cTime=cTime,
                           cTeacher=cTeacher,
                           clientName=clientName,
                           clientPhone=clientPhone
                           )


def seed_db():
    teachers_list = []
    for teacher in teachers_json:
        teachers_list.append(Teacher(id=teacher["id"], name=teacher["name"],
                                     price=teacher["price"],
                                     schedule=json.dumps(teacher["free"]),
                                     rating=teacher["rating"],
                                     picture=teacher["picture"],
                                     about=teacher["about"],
                                     goals=json.dumps(teacher["goals"])))

    db.session.add_all(teachers_list)
    db.session.commit()



# if __name__ == "__main__":
#     seed_db()

if __name__ == "__main__":
    app.run()
