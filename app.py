from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta
from flask_migrate import Migrate
from flask_apscheduler import APScheduler
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import calendar

#Create the flask app object
app = Flask(__name__)

#Tell Flask where the database lives
#(events.db is the name of the folder and it will be created automatically)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#Creates the data base object
db = SQLAlchemy(app)

migrate = Migrate(app, db)

#Creates event class that descirbes what an event looks like in the database
class Event(db.Model):
    """  Each Event has 6 columns id, title, date, time, description, and created at """
    """  This class represents what the database will look like """
    id = db.Column(db.Integer, primary_key=True) #sets id as unique identifier
    title = db.Column(db.String(100), nullable=False) #nullable = false makes it required
    date = db.Column(db.String(10), nullable=False)
    time= db.Column(db.String(5))
    description = db.Column(db.String(200))
    category = db.Column(db.String(50))

    def to_dict(self):
        category_colors = {
            "None": "#FFFFFF",   # white
            "School": "#ffdc97",   # orange
            "Work": "#bbdefb",     # blue
            "Health": "#fefb98",   # yellow
            "Personal": "#ffcdd2", # pink
            "Other": "#eeeeee"     # gray
        }

        return {
            "id": self.id,
            "title": self.title,
            "date": self.date,
            "time": self.time,
            "description": self.description,
            "color": category_colors.get(self.category, "#3788d8"),
            "textColor": "black"
        }

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

def check_upcoming_events():
    with app.app_context():
        now = datetime.now()
        soon = now + timedelta(minutes=30)
        events = Event.query.all()

        for e in events:
            if not e.time:
                continue

            event_datetime = datetime.strptime(f"{e.date} {e.time}", "%Y-%m-%d %H:%M")

            if now <= event_datetime <= soon:
                print(f"🔔 Reminder: '{e.title}' at {event_datetime.strftime('%I:%M %p')}")

scheduler.add_job(
    id='check_events',
    func=check_upcoming_events,
    trigger='interval',
    minutes=1
)

#Creates all defined tables in teh database
with app.app_context(): #app.app_context() makes sure the code runs within Flask
    #Actually creates table when first ran
    db.create_all()

#Tell flask what url this function should handle (in this case homepage)
@app.route('/')

#The home function decides what to send back to the user
def home():
    """  orders all events in the database and loads them into html file """
    events = Event.query.order_by(Event.date, Event.time).all()
    return render_template("home.html", events=events)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        title = request.form['title']
        date = request.form['date']
        time = request.form['time']
        desc = request.form['desc']
        group = request.form['category']

        new_event = Event(
            title=title,
            date=date,
            time=time,
            description=desc,
            category=group
        )
        db.session.add(new_event)
        db.session.commit()
        return redirect(url_for('add'))

    events = Event.query.order_by(Event.date, Event.time).all()
    return render_template('add.html', events=events)

@app.route('/delete/<int:id>', methods=["GET","POST"])

def delete_event(id):
    event_to_delete = Event.query.get_or_404(id)
    db.session.delete(event_to_delete)
    db.session.commit()
    return redirect(url_for('day_view', date=event_to_delete.date))

@app.route('/edit/<int:id>', methods=["GET","POST"])

def edit_event(id):
    event = Event.query.get_or_404(id)
    return render_template('edit.html', event=event)

@app.route('/save/<int:id>', methods=["POST"])

def save_changes(id):
    event = Event.query.get_or_404(id)
    event.title = request.form['title']
    event.date = request.form['date']
    event.time = request.form['time']
    event.description = request.form['description']
    event.category = request.form['category']
    db.session.commit()
    return redirect(url_for('day_view', date=event.date))

@app.route('/calendar')
def calendar_view():
    return render_template('calendar.html')

@app.route('/day/<date>')
def day_view(date):
    events = Event.query.order_by(Event.date, Event.time).all()
    dayEvents = []
    DT_date = datetime.strptime(date, '%Y-%m-%d')
    fullDate = DT_date.strftime("%A, %B %d")
    for e in events:
        if e.date == date:
            if (e.time == ""):
                e.time = "23:59"
            dayEvents.append(e)
    return render_template('day.html', events=dayEvents, full_date=fullDate)


@app.route('/events')
def events():
    allEvents = []
    events = Event.query.order_by(Event.date, Event.time).all()
    for e in events:
        allEvents.append(e.to_dict())
    return jsonify(allEvents)

@app.route('/task')
def task_flow():
    current_events = currentEvents()
    return render_template('task_flow.html',events=current_events)

def get_iterator(pattern, start_date, end_date):
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    if pattern == "daily":
        # Total days between dates (inclusive)
        delta = (end_dt - start_dt).days + 1
        return delta
        
    elif pattern == "weekly":
        # Weeks between dates
        delta = (end_dt - start_dt).days // 7 + 1
        return delta
        
    elif pattern == "monthly":
        # Months between dates
        months = (end_dt.year - start_dt.year) * 12 + (end_dt.month - start_dt.month) + 1
        return months

@app.route('/add_recurring', methods=['POST'])
def add_recurring():
    title = request.form['title']
    pattern = request.form['recurrence']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    time = request.form['time']
    desc = request.form['desc']
    group = request.form['category']

    # Convert to datetime objects
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    current_date = start_dt
    
    exclude_days = request.form.getlist("exclude_days")
    exclude_days = list(map(int, exclude_days))

    for i in range(len(exclude_days)):
        exclude_days[i] -= 1
    
    if pattern == "daily":
        while current_date <= end_dt:
            if(current_date.weekday() in exclude_days):
                current_date += timedelta(days=1)
                continue       
            date_str = current_date.strftime('%Y-%m-%d')
            new_event = Event(title=title, date=date_str, time=time, description=desc, category=group)
            db.session.add(new_event)
            current_date += timedelta(days=1)

    elif pattern == "weekly":
        while current_date <= end_dt:
            date_str = current_date.strftime('%Y-%m-%d')
            new_event = Event(title=title, date=date_str, time=time, description=desc, category=group)
            db.session.add(new_event)
            current_date += timedelta(weeks=1)

    elif pattern == "monthly":
        while current_date <= end_dt:
            date_str = current_date.strftime('%Y-%m-%d')
            new_event = Event(title=title, date=date_str, time=time, description=desc, category=group)
            db.session.add(new_event)
            
            # Move to same day next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
    
    db.session.commit()
    return redirect(url_for('add'))

def currentEvents():
    events = Event.query.order_by(Event.date, Event.time).all()
    current_events = []
    day = request.args.get('day', date.today().day, type=int)
    month = request.args.get('month',date.today().month, type=int)
    year = request.args.get('year', date.today().year, type=int)
    
    #Only gets the events for that day
    for event in events:
        if day == int(event.date[8:]) and year == int(event.date[:4]) and month == int(event.date[5:7]):
            current_events.append(event)
    
    return current_events


if __name__ == '__main__':
    #This function starts Flask's development web server (With debugging)
    app.run(debug=True)

 