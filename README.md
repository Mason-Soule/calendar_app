Elevate Me – Smart Event Manager
Elevate Me is a Python-based calendar and event management application built with Flask, HTML/CSS, and SQLite, designed to help users organize daily, weekly, and monthly events. 
The app includes a color-coded calendar, recurring event system, and terminal-based notifications that warn the user when an event is approaching within 30 minutes.

✨ Features

📅 Recurring Events

Supports daily, weekly, and monthly recurring events.
Automatically schedules recurring entries without manual re-adding.

🎨 Color-Coded UI

Events are visually highlighted with color styling in the HTML templates, helping distinguish categories and priority levels.

⏰ Terminal Alerts

While the app is running, it monitors event times.
Prints a warning when an event begins within 30 minutes, keeping you aware without needing to refresh the page.

💾 SQLite Data Storage

Stored inside the instance/ directory for proper Flask handling.
Tracks events, recurrence, timestamps, colors, and modifications.

🌐 Flask Web Interface

Clean and intuitive HTML pages for adding, editing, browsing, and managing events.

📣 Terminal Warning System

When the application is running:
A background task checks upcoming event timestamps.
If an event will occur in the next 30 minutes, a warning is printed to terminal, e.g.:
⚠️ Reminder: "Doctor Appointment" starts in 28 minutes.

🔧 Technologies Used

Backend

Python 3.12.3
Flask Framework

Flask — main web framework
render_template — HTML templating
request — request handling
redirect, url_for — page routing and redirects

Database & Migrations

Flask_SQLAlchemy — ORM layer for interacting with SQLite
Flask_Migrate — database migrations with Alembic
SQLite — underlying database engine (via SQLAlchemy)

Scheduling & Background Tasks

Flask_APScheduler — used for scheduling background checks (e.g., event reminders)
Date & Time Handling
datetime, date, timedelta — time comparisons and scheduling logic
calendar — building monthly calendar views

Frontend

HTML & CSS
Flask/Jinja2 templating

📘 Project Purpose

Elevate Me was created to deliver:
A fast, simple calendar manager,
a visually clean interface,
reliable recurring event automation,
and real-time terminal alerts
Perfect for personal scheduling without overcomplicated features.
