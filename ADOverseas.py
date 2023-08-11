from flask import Flask, request, jsonify
from datetime import datetime, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from snippies import ad, app_log, db, scheduler_config
import os

app = Flask(__name__)
scheduler = BackgroundScheduler(jobstores=scheduler_config.jobstores,
								executors=scheduler_config.executors,
								job_defaults=scheduler_config.job_defaults)
scheduler.start()

app_log.configure_logging()

DATABASE = 'schedules.sqlite'
db.init_db(DATABASE)


def reschedule_jobs():
	app_log.message("debug", "Checking for previously uncompleted jobs")
	app_log.message("debug", "Getting all records from schedules.sqlite")
	rows = db.get_records()

	for row in rows:
		rowID, username, date, action = row
		if action == "leaving":
			if datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.000Z") > datetime.utcnow():
				app_log.message("debug", f"Scheduling leaving job for {username} at {date}")
				scheduler.add_job(ad.edit_ad_user, id=f"{username}_away", trigger='date', run_date=date, args=[
							  username, 'away', rowID], replace_existing=True)
		elif action == "returning":
			if datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.000Z") > datetime.utcnow():
				app_log.message("debug", f"Scheduling leaving job for {username} at {date}")
				scheduler.add_job(ad.edit_ad_user, id=f"{username}_home", trigger='date', run_date=date, args=[
							  username, 'home', rowID], replace_existing=True)


reschedule_jobs()


@app.route('/schedule', methods=['POST'])
def schedule_user():
	api_token = os.getenv("ADAPITOKEN")
	api_key = request.headers.get('Authorization')

	# continue if api_key is correct
	app_log.message("debug", "Checking if authorized")
	if api_key == f'Bearer {api_token}':
		app_log.message("debug", "Getting request as JSON")
		data = request.get_json()

		app_log.message("debug", "Parsing JSON fields")
		email = data.get('username')
		app_log.message("debug", f"Formatting email {email} into samAccountName")
		username = ad.format_username(email)
		start_date_str = data.get('start_date')
		end_date_str = data.get('end_date')

		# ensure all required fields are sent
		app_log.message("debug", "Checking if all fields have been met")
		if not (username and start_date_str and end_date_str):
			app_log.message("error", f"Missing a parameter: {request.data}")
			return jsonify({'status': 'request failed', 'reason': 'Missing Parameter'}), 400

		app_log.message("debug", "Attempting to parse dates to datetime object")
		try:
			start_date = datetime.strptime(start_date_str, "%Y-%m-%dT%H:%M:%S.000Z")
			end_date = datetime.strptime(end_date_str, "%Y-%m-%dT%H:%M:%S.000Z")
		except ValueError:  # handle incorrect datetime format
			app_log.message("error", f"Unable to parse dates {start_date_str} and {end_date_str}")
			return jsonify({'status': 'request failed', 'reason': 'invalid date/time format'}), 400

		# check that supplied start_date is in the future
		app_log.message("debug", "Checking if start_date is in the past")
		if start_date <= datetime.utcnow():
			app_log.message("error", f"Start date {start_date} is in the past")
			return jsonify({'status': 'request failed', 'reason': 'start_date cannot be in the past!'}), 400

		# make sure that end_date is after start_date
		app_log.message("debug", "Checking if end_date is before start_date")
		if end_date <= start_date:
			app_log.message("error", f"end_date {end_date} is before start_date {start_date}")
			return jsonify({'status': 'request failed', 'reason': 'end_date cannot be before or same as start_date!'}), 400

		# add to schedule
		app_log.message("debug", "Adding job to scheduler")
		schedule(username, start_date, end_date)
		return jsonify({'status': 'request succesful'})
	app_log.message("error", "API Token does not match")
	return jsonify({'status': 'request failed', 'reason': 'unauthorized'}), 401


def schedule(username, start_date, end_date):
	app_log.message("debug", f"Adding data for job {username}_away to schedules database in case of system shutdown")
	row_id = db.add_record(username, start_date, "leaving")
	app_log.message("debug", f"Scheduling job {username}_away")
	scheduler.add_job(ad.edit_ad_user, id=f"{username}_away", trigger='date', run_date=start_date, timezone=timezone.utc, args=[
		username, 'away', row_id], replace_existing=True)
		
	app_log.message("debug", f"Adding data for job {username}_home to schedules database in case of system shutdown")
	row_id = db.add_record(username, end_date, "returning")
	app_log.message("debug", f"Scheduling job {username}_home")
	scheduler.add_job(ad.edit_ad_user, id=f"{username}_home", trigger='date', run_date=end_date, timezone=timezone.utc, args=[
		username, 'home', row_id], replace_existing=True)


if __name__ == "__main__":
	app.run()
