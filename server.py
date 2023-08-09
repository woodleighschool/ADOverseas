from flask import Flask, request, jsonify
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from snippies import ad, scheduler_config, db_config
import sqlite3
import os

app = Flask(__name__)
scheduler = BackgroundScheduler(jobstores=scheduler_config.jobstores,
                                executors=scheduler_config.executors,
                                job_defaults=scheduler_config.job_defaults)
scheduler.start()

DATABASE = 'schedules.sqlite'
db_config.init_db(DATABASE)


def reschedule_jobs():
    with sqlite3.connect(DATABASE) as db:
        rows = db.execute(
            "SELECT username, start_date, end_date FROM schedules").fetchall()

    for row in rows:
        username, start_date, end_date = row
        if datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S") > datetime.now():
            scheduler.add_job(ad.edit_ad_user, id=f"{username}_away", trigger='date', run_date=start_date, args=[
                              username, 'away'], replace_existing=True)
        if datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S") > datetime.now():
            scheduler.add_job(ad.edit_ad_user, id=f"{username}_home", trigger='date', run_date=end_date, args=[
                              username, 'home'], replace_existing=True)


reschedule_jobs()


@app.route('/schedule', methods=['POST'])
def schedule_user():

    api_token = os.getenv('overseas-token')
    api_key = request.headers.get('Authorization')

    # continue if api_key is correct
    if api_key == f'Bearer {api_token}':
        data = request.get_json()

        username = data.get('username')
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')

        # ensure all required fields are sent
        if not (username and start_date_str and end_date_str):
            return jsonify({'status': 'request failed', 'reason': 'Missing Parameter'}), 400

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:  # handle incorrect datetime format
            return jsonify({'status': 'request failed', 'reason': 'invalid date/time format'}), 400

        # check that supplied start_date is in the future
        if start_date <= datetime.now():
            return jsonify({'status': 'request failed', 'reason': 'start_date cannot be in the past!'}), 400

        # make sure that end_date is after start_date
        if end_date <= start_date:
            return jsonify({'status': 'request failed', 'reason': 'end_date cannot be before or same as start_date!'}), 400

        # add to schedule
        schedule(username, start_date_str, end_date_str)
        return jsonify({'status': 'request succesful'})

    return jsonify({'status': 'request failed', 'reason': 'unauthorized'}), 401


def schedule(username, start_date, end_date):
    with sqlite3.connect(DATABASE) as db:
        db.execute("INSERT INTO schedules (username, start_date, end_date) VALUES (?, ?, ?)",
                   (username, start_date, end_date))

    scheduler.add_job(ad.edit_ad_user, id=f"{username}_away", trigger='date', run_date=start_date, args=[
                      username, 'away'], replace_existing=True)
    scheduler.add_job(ad.edit_ad_user, id=f"{username}_home", trigger='date', run_date=end_date, args=[
                      username, 'home'], replace_existing=True)


if __name__ == "__main__":
    app.run(debug=True)
