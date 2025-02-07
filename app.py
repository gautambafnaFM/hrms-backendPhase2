from flask import Flask, jsonify
from extensions import *  # Importing db from extension.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import os
import urllib.parse
from dotenv import load_dotenv
from flask_cors import CORS
from datetime import datetime, timedelta

TO_ADDRESSES = "gautam.bafna@flairminds.com"


@scheduler.task('cron',id='send_leave_email01', hour=10, minute=00)
@scheduler.task('cron', id='send_leave_email_2', hour=12, minute=5)

def send_leave_email01():
    print("IN")
    with scheduler.app.app_context():
        current_date = datetime.today()
        if current_date.weekday() == 5:  
            current_date = current_date + timedelta(days=2)  
        elif current_date.weekday() == 6:  
            current_date = current_date + timedelta(days=1)  

      
        current_date = current_date.strftime('%Y-%m-%d')

        with db.session.begin():
            result = db.session.execute(
                text("""
                     SELECT 
                    lt.fromDate, 
                    e.FirstName, 
                    e.LastName, 
                    lt.LeaveStatus, 
                    ltm.LeaveName  -- LeaveName from LeaveTypeMaster
                FROM LeaveTransaction lt
                JOIN Employee e ON lt.AppliedBy = e.EmployeeId
                JOIN LeaveTypeMaster ltm ON lt.LeaveType = ltm.LeaveTypeID  -- Joining with LeaveTypeMaster to get LeaveName
                WHERE lt.fromDate = :date
                AND lt.LeaveStatus != 'Cancel'  -- Exclude canceled leaves
                     """),
                {"date": current_date}
            )

            rows = result.fetchall()
            leave_data = [
                {
                    'FromDate': row[0].strftime('%Y-%m-%d') if hasattr(row[0], 'strftime') else str(row[0]),
                    'AppliedBy': f"{row[1]} {row[2]}",
                    'LeaveStatus': row[3],
                    'LeaveType': row[4]
                }
                for row in rows
            ]

        # Convert leave data to JSON format
        leave_data_json = json.dumps(leave_data, indent=4)

        # Convert JSON to HTML Table for better readability
        leave_table = "<table border='1' style='border-collapse: collapse;'>"
        leave_table += "<tr><th>From Date</th><th>Applied By</th><th>Leave Status</th><th>Leave Type</th></tr>"

        for leave in leave_data:
            leave_table += f"<tr><td>{leave['FromDate']}</td><td>{leave['AppliedBy']}</td><td>{leave['LeaveStatus']}</td><td>{leave['LeaveType']}</td></tr>"

        leave_table += "</table>"

        # Email Subject & Body
        subject = f"Leave Data Report - {current_date}"
        body = f"""
        <html>
            <body>
                <h3>Leave Data for {current_date}</h3>
                {leave_table}
            </body>
        </html>
        """

        # Set up the email message
        msg = MIMEMultipart()
        msg['From'] = FROM_ADDRESS
        msg['To'] = ", ".join(TO_ADDRESSES)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        try:
            # Send the email using Gmail SMTP
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()  # Upgrade to secure connection
            server.login(FROM_ADDRESS, FROM_PASSWORD)
            server.sendmail(FROM_ADDRESS, TO_ADDRESSES, msg.as_string())
            server.quit()
            print("Email sent successfully!")
        except Exception as e:
            print(f"Error on line {e.__traceback__.tb_lineno} inside {__file__}\n Failed to send email: {str(e)}")



def send_leave_email02():
    print("IN")
    with scheduler.app.app_context():
        current_date = datetime.today()
        if current_date.weekday() == 5:  
            current_date = current_date + timedelta(days=2)  
        elif current_date.weekday() == 6:  
            current_date = current_date + timedelta(days=1)  

      
        current_date = current_date.strftime('%Y-%m-%d')

        with db.session.begin():
            result = db.session.execute(
                text("""
                     SELECT 
                    lt.fromDate, 
                    e.FirstName, 
                    e.LastName, 
                    lt.LeaveStatus, 
                    ltm.LeaveName  -- LeaveName from LeaveTypeMaster
                FROM LeaveTransaction lt
                JOIN Employee e ON lt.AppliedBy = e.EmployeeId
                JOIN LeaveTypeMaster ltm ON lt.LeaveType = ltm.LeaveTypeID  -- Joining with LeaveTypeMaster to get LeaveName
                WHERE lt.fromDate = :date
                AND lt.LeaveStatus != 'Cancel'  -- Exclude canceled leaves
                     """),
                {"date": current_date}
            )

            rows = result.fetchall()
            leave_data = [
                {
                    'FromDate': row[0].strftime('%Y-%m-%d') if hasattr(row[0], 'strftime') else str(row[0]),
                    'AppliedBy': f"{row[1]} {row[2]}",
                    'LeaveStatus': row[3],
                    'LeaveType': row[4]
                }
                for row in rows
            ]

        # Convert leave data to JSON format
        leave_data_json = json.dumps(leave_data, indent=4)

        # Convert JSON to HTML Table for better readability
        leave_table = "<table border='1' style='border-collapse: collapse;'>"
        leave_table += "<tr><th>From Date</th><th>Applied By</th><th>Leave Status</th><th>Leave Type</th></tr>"

        for leave in leave_data:
            leave_table += f"<tr><td>{leave['FromDate']}</td><td>{leave['AppliedBy']}</td><td>{leave['LeaveStatus']}</td><td>{leave['LeaveType']}</td></tr>"

        leave_table += "</table>"

        # Email Subject & Body
        subject = f"Leave Data Report - {current_date}"
        body = f"""
        <html>
            <body>
                <h3>Leave Data for {current_date}</h3>
                {leave_table}
            </body>
        </html>
        """

        # Set up the email message
        msg = MIMEMultipart()
        msg['From'] = FROM_ADDRESS
        msg['To'] = ", ".join(TO_ADDRESSES)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        try:
            # Send the email using Gmail SMTP
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()  # Upgrade to secure connection
            server.login(FROM_ADDRESS, FROM_PASSWORD)
            server.sendmail(FROM_ADDRESS, TO_ADDRESSES, msg.as_string())
            server.quit()
            print("Email sent successfully!")
        except Exception as e:
            print(f"Error on line {e.__traceback__.tb_lineno} inside {__file__}\n Failed to send email: {str(e)}")

# # Scheduler to run the email sending task daily at 10:18 PM
# def schedule_email_task():
#     scheduler.add_job(id='send_leave_email', func=send_leave_email, trigger='cron', hour=00, minute=38)  


# Start the scheduler when the app runs
if __name__ == '__main__':
    app.run("0.0.0.0", port=7000, debug=True)
