from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, Response
from flask_sqlalchemy import SQLAlchemy
from io import StringIO
import csv

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200))
    start_date = db.Column(db.Date)
    due_date = db.Column(db.Date)
    priority = db.Column(db.String(10))
    status = db.Column(db.String(20), default='Incomplete')

@app.route('/')
def index():
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)

@app.route('/add_task', methods=['POST'])
def add_task():
    title = request.form['title']
    description = request.form['description']
    start_date_str = request.form['start_date']
    due_date_str = request.form['due_date']
    priority = request.form['priority']
    status = request.form['status']

    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()

    new_task = Task(
        title=title,
        description=description,
        start_date=start_date,
        due_date=due_date,
        priority=priority,
        status=status
    )
    db.session.add(new_task)
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/download')
def download():
    tasks = Task.query.all()

    # Create a CSV file in memory
    output = StringIO()
    csv_writer = csv.writer(output)

    # Write CSV header
    csv_writer.writerow(['Title', 'Description', 'Start Date', 'Due Date', 'Priority', 'Duration', 'Status'])

    # Write task data to CSV
    for task in tasks:
        csv_writer.writerow([task.title, task.description, task.start_date, task.due_date, task.priority, task.status])

    # Prepare CSV data for download
    output.seek(0)
    csv_data = output.getvalue()

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=task_details.csv"}
    )
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)