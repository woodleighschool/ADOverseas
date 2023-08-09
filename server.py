from flask import Flask, request, jsonify
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from snippies import ad, db, scheduler_config
import os

app = Flask(__name__)
scheduler = BackgroundScheduler(jobstores=scheduler_config.jobstores,
                                executors=scheduler_config.executors,
                                job_defaults=scheduler_config.job_defaults)
scheduler.start()

DATABASE = 'schedules.sqlite'
db.init_db(DATABASE)


def reschedule_jobs():
    rows = db.get_records()

    for row in rows:
        rowID, username, date, action = row
        if action == "leaving":
            if datetime.strptime(date, "%Y-%m-%d %H:%M:%S") > datetime.now():
                scheduler.add_job(ad.edit_ad_user, id=f"{username}_away", trigger='date', run_date=date, args=[
                              username, 'away', rowID], replace_existing=True)
        elif action == "returning":
            if datetime.strptime(date, "%Y-%m-%d %H:%M:%S") > datetime.now():
                scheduler.add_job(ad.edit_ad_user, id=f"{username}_home", trigger='date', run_date=date, args=[
                              username, 'home', rowID], replace_existing=True)


reschedule_jobs()


@app.route('/schedule', methods=['POST'])
def schedule_user():

    api_token = os.getenv("ADAPITOKEN")
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
    row_id = db.add_record(username, start_date, "leaving")
    scheduler.add_job(ad.edit_ad_user, id=f"{username}_away", trigger='date', run_date=start_date, args=[
        username, 'away', row_id], replace_existing=True)
        
    row_id = db.add_record(username, end_date, "returning")
    scheduler.add_job(ad.edit_ad_user, id=f"{username}_home", trigger='date', run_date=end_date, args=[
        username, 'home', row_id], replace_existing=True)


if __name__ == "__main__":
    app.run(debug=True)
