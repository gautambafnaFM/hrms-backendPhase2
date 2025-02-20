from flask import Flask, request,jsonify
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
from flask_cors import CORS, cross_origin
from datetime import datetime, timedelta

TO_ADDRESSES =[ "hr@flairminds.com","hashmukh@flairminds.com"]
# TO_ADDRESSES="gautam.bafna@flairminds.com"
# @scheduler.task('cron', id='send_leave_email01', hour=12, minute=12)
@scheduler.task('cron',id='send_leave_email01', hour=5, minute=00)
@scheduler.task('cron', id='send_leave_email02', hour=7, minute=00)

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
                        lt.ToDate, 
                        e.FirstName, 
                        e.LastName, 
                        lt.LeaveStatus, 
                        ltm.LeaveName  -- LeaveName from LeaveTypeMaster
                    FROM LeaveTransaction lt
                    JOIN Employee e ON lt.AppliedBy = e.EmployeeId
                    JOIN LeaveTypeMaster ltm ON lt.LeaveType = ltm.LeaveTypeID  -- Joining with LeaveTypeMaster to get LeaveName
                    WHERE :date BETWEEN lt.fromDate AND lt.ToDate  -- Ensures date falls within leave duration
                    AND lt.LeaveStatus != 'Cancel'  -- Exclude canceled leaves
                """),
                {"date": current_date}
            )

            rows = result.fetchall()
            leave_data = [
                {
                'FromDate': row[0].strftime('%Y-%m-%d') if row[0] else '',
                'ToDate': row[1].strftime('%Y-%m-%d') if row[1] else '',
                'AppliedBy': f"{row[2]} {row[3]}",
                'LeaveStatus': row[4],
                'LeaveType': row[5]
                }
                for row in rows
            ]

        # Convert leave data to JSON format
        leave_data_json = json.dumps(leave_data, indent=4)

        # Convert JSON to HTML Table for better readability
        leave_table = """
            <table border='1' style='border-collapse: collapse; text-align: left;'>
                <tr>
                    <th>From Date</th>
                    <th>To Date</th>
                    <th>Applied By</th>
                    <th>Leave Status</th>
                    <th>Leave Type</th>
                </tr>
        """

        for leave in leave_data:
            leave_table += f"""
            <tr>
                <td>{leave['FromDate']}</td>
                <td>{leave['ToDate']}</td>
                <td>{leave['AppliedBy']}</td>
                <td>{leave['LeaveStatus']}</td>
                <td>{leave['LeaveType']}</td>
            </tr>
            """
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
    print("email02")
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
                        lt.ToDate, 
                        e.FirstName, 
                        e.LastName, 
                        lt.LeaveStatus, 
                        ltm.LeaveName  -- LeaveName from LeaveTypeMaster
                    FROM LeaveTransaction lt
                    JOIN Employee e ON lt.AppliedBy = e.EmployeeId
                    JOIN LeaveTypeMaster ltm ON lt.LeaveType = ltm.LeaveTypeID  -- Joining with LeaveTypeMaster to get LeaveName
                    WHERE :date BETWEEN lt.fromDate AND lt.ToDate  -- Ensures date falls within leave duration
                    AND lt.LeaveStatus != 'Cancel'  -- Exclude canceled leaves
                """),
                {"date": current_date}
            )

            rows = result.fetchall()
            leave_data = [
                {
                'FromDate': row[0].strftime('%Y-%m-%d') if row[0] else '',
                'ToDate': row[1].strftime('%Y-%m-%d') if row[1] else '',
                'AppliedBy': f"{row[2]} {row[3]}",
                'LeaveStatus': row[4],
                'LeaveType': row[5]
                }
                for row in rows
            ]

        # Convert leave data to JSON format
        leave_data_json = json.dumps(leave_data, indent=4)

        # Convert JSON to HTML Table for better readability
        leave_table = """
            <table border='1' style='border-collapse: collapse; text-align: left;'>
                <tr>
                    <th>From Date</th>
                    <th>To Date</th>
                    <th>Applied By</th>
                    <th>Leave Status</th>
                    <th>Leave Type</th>
                </tr>
        """

        for leave in leave_data:
            leave_table += f"""
            <tr>
                <td>{leave['FromDate']}</td>
                <td>{leave['ToDate']}</td>
                <td>{leave['AppliedBy']}</td>
                <td>{leave['LeaveStatus']}</td>
                <td>{leave['LeaveType']}</td>
            </tr>
            """
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


def get_employee_skills():
    with db.session.begin():
        result = db.session.execute(
            text("""
                SELECT TOP (1000) 
                    EmployeeId, FirstName, MiddleName, LastName, 
                    DateOfBirth, ContactNumber, EmergencyContactNumber, 
                    EmergencyContactPerson, EmergencyContactRelation, 
                    Email, Gender, BloodGroup, DateOfJoining, CTC, 
                    TeamLeadId, HighestQualification, EmploymentStatus, 
                    PersonalEmail, SubRole, LobLead, IsLead
                FROM HRMS.dbo.Employee
            """)
        )
        employees = [dict(row) for row in result.mappings()]
    return jsonify(employees)

@app.route('/api/employee-skills', methods=['GET'])
def employee_skills():
    data = get_employee_skills()
    return jsonify(data)



# @app.route('/api/add-update-skills', methods=['POST'])
# def add_or_update_skills():
#     """API endpoint to add or update multiple skills for an employee, including isReady and isReadyDate."""
#     try:
#         data = request.json
#         employee_id = data.get('EmployeeId')
#         skills = data.get('skills', [])  # Expecting a list of skills

#         # Validate input
#         if not employee_id or not skills:
#             return jsonify({'error': 'EmployeeId and skills are required'}), 400

#         with db.session.begin():
#             for skill in skills:
#                 skill_id = skill.get('SkillId')
#                 skill_level = skill.get('SkillLevel')
#                 is_ready = skill.get('isReady', 'No')  # Default to 'No'
#                 is_ready_date = skill.get('isReadyDate')
#                 # is_ready_date = skill.get('isReadyDate', datetime.utcnow().strftime('%Y-%m-%d'))  # Default to today's date
#                 if is_ready_date:
#                     try:
#                         is_ready_date = datetime.strptime(is_ready_date, "%a, %d %b %Y %H:%M:%S GMT").strftime("%Y-%m-%d")
#                     except ValueError:
#                         return jsonify({'error': 'Invalid date format. Expected format: Mon, 17 Feb 2025 00:00:00 GMT'}), 400
                
#                 if not skill_id or not skill_level:
#                     return jsonify({'error': 'Each skill must have skillId and skillLevel'}), 400

#                 # Check if the skill already exists for this employee
#                 result = db.session.execute(
#                     text("""
#                         SELECT COUNT(*) FROM EmployeeSkill 
#                         WHERE EmployeeId = :employee_id AND SkillId = :skill_id
#                     """),
#                     {'employee_id': employee_id, 'skill_id': skill_id}
#                 ).scalar()

#                 if result > 0:
#                     # Update the existing skill
#                     db.session.execute(
#                         text("""
#                             UPDATE EmployeeSkill 
#                             SET SkillLevel = :skill_level, isReady = :is_ready, isReadyDate = :is_ready_date
#                             WHERE EmployeeId = :employee_id AND SkillId = :skill_id
#                         """),
#                         {
#                             'employee_id': employee_id,
#                             'skill_id': skill_id,
#                             'skill_level': skill_level,
#                             'is_ready': is_ready,
#                             'is_ready_date': is_ready_date
#                         }
#                     )
#                 else:
#                     # Insert new skill
#                     db.session.execute(
#                         text("""
#                             INSERT INTO EmployeeSkill (EmployeeId, SkillId, SkillLevel, isReady, isReadyDate)
#                             VALUES (:employee_id, :skill_id, :skill_level, :is_ready, :is_ready_date)
#                         """),
#                         {
#                             'employee_id': employee_id,
#                             'skill_id': skill_id,
#                             'skill_level': skill_level,
#                             'is_ready': is_ready,
#                             'is_ready_date': is_ready_date
#                         }
#                     )

#         return jsonify({'message': 'Skills added/updated successfully'}), 201

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


@app.route('/api/add-update-skills', methods=['POST'])
def add_or_update_skills():
    """API endpoint to add or update multiple skills for an employee, including isReady and isReadyDate."""
    try:
        data = request.json
        employee_id = data.get('EmployeeId')
        skills = data.get('skills', [])  # Expecting a list of skills

        # Validate input
        if not employee_id or not skills:
            return jsonify({'error': 'EmployeeId and skills are required'}), 400

        with db.session.begin():
            for skill in skills:
                skill_id = skill.get('SkillId')
                skill_level = skill.get('SkillLevel')
                is_ready = skill.get('isReady', 0)  # Ensure it's an integer (0 or 1)
                is_ready_date = skill.get('isReadyDate')

                if not skill_id or not skill_level:
                    return jsonify({'error': 'Each skill must have SkillId and SkillLevel'}), 400

                # ✅ Handle multiple date formats
                if is_ready_date:
                    try:
                        if len(is_ready_date) == 10 and is_ready_date.count('-') == 2:
                            # Already in YYYY-MM-DD format
                            datetime.strptime(is_ready_date, "%Y-%m-%d")  # Validate
                        else:
                            # Convert from "Mon, 17 Feb 2025 00:00:00 GMT" → "YYYY-MM-DD"
                            is_ready_date = datetime.strptime(is_ready_date, "%a, %d %b %Y %H:%M:%S GMT").strftime("%Y-%m-%d")
                    except ValueError:
                        return jsonify({'error': f'Invalid date format: {is_ready_date}. Expected "YYYY-MM-DD" or "Mon, 17 Feb 2025 00:00:00 GMT".'}), 400
                else:
                    is_ready_date = datetime.utcnow().strftime('%Y-%m-%d')  # Default to today's date

                # Check if the skill already exists for this employee
                result = db.session.execute(
                    text("""
                        SELECT COUNT(*) FROM EmployeeSkill 
                        WHERE EmployeeId = :employee_id AND SkillId = :skill_id
                    """),
                    {'employee_id': employee_id, 'skill_id': skill_id}
                ).scalar()

                if result > 0:
                    # Update the existing skill
                    db.session.execute(
                        text("""
                            UPDATE EmployeeSkill 
                            SET SkillLevel = :skill_level, isReady = :is_ready, isReadyDate = :is_ready_date
                            WHERE EmployeeId = :employee_id AND SkillId = :skill_id
                        """),
                        {
                            'employee_id': employee_id,
                            'skill_id': skill_id,
                            'skill_level': skill_level,
                            'is_ready': is_ready,
                            'is_ready_date': is_ready_date
                        }
                    )
                else:
                    # Insert new skill
                    db.session.execute(
                        text("""
                            INSERT INTO EmployeeSkill (EmployeeId, SkillId, SkillLevel, isReady, isReadyDate)
                            VALUES (:employee_id, :skill_id, :skill_level, :is_ready, :is_ready_date)
                        """),
                        {
                            'employee_id': employee_id,
                            'skill_id': skill_id,
                            'skill_level': skill_level,
                            'is_ready': is_ready,
                            'is_ready_date': is_ready_date
                        }
                    )

        return jsonify({'message': 'Skills added/updated successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

        
@app.route('/api/employee-skills/<employee_id>', methods=['GET'])
def get_employee_skills(employee_id):
    """API endpoint to fetch all skills for a specific employee."""
    try:
        with db.session.begin():
            result = db.session.execute(
                text("""
                    SELECT es.EmployeeId, es.SkillId, es.SkillLevel, 
                           s.SkillName, es.isReady, es.isReadyDate
                    FROM EmployeeSkill es
                    LEFT JOIN Skill s ON es.SkillId = s.SkillId
                    WHERE es.EmployeeId = :employee_id
                """),
                {'employee_id': employee_id}
            )
           

            # skills = [dict(row) for row in result.fetchall()]
            # skills = [dict(zip(result.keys(), row)) for row in result.fetchall()]
            skills = []
            for row in result.fetchall():
                skill_dict = dict(zip(result.keys(), row))
                skill_dict["isReady"] = int(skill_dict["isReady"])  # Convert boolean to integer
                skills.append(skill_dict)




        return jsonify({'employee_id': employee_id, 'skills': skills}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500





@app.route('/api/employees', methods=['GET'])
def get_employees():
    with db.session.begin():
        result = db.session.execute(
            text("""
                SELECT TOP (1000) 
                    e.EmployeeId, e.FirstName, e.LastName, e.DateOfJoining,
                    e.TeamLeadId, e.SubRole, e.LobLead, e.IsLead,
                    es.SkillId, s.SkillName, es.SkillLevel, es.isReady, es.isReadyDate
                FROM HRMS.dbo.Employee e
                LEFT JOIN HRMS.dbo.EmployeeSkill es ON e.EmployeeId = es.EmployeeId
                LEFT JOIN HRMS.dbo.Skill s ON es.SkillId = s.SkillId
            """)
        )
        employees = [dict(row) for row in result.mappings()]
    return jsonify(employees)

# Start the scheduler when the app runs
if __name__ == '__main__':
    app.run("0.0.0.0", port=7000, debug=True)
