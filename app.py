from flask import Flask, request,jsonify
from extensions import *  # Importing db from extension.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import BytesIO
import os
import urllib.parse
from dotenv import load_dotenv
from flask_cors import CORS, cross_origin
from datetime import datetime, timedelta
from flask import send_file
from werkzeug.utils import secure_filename



TO_ADDRESSES =[ "hr@flairminds.com","hasmukh@flairminds.com"]
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

@app.route("/api/add-update-skills", methods=["POST"])
def add_or_update_skills():
    """API endpoint to add or update multiple skills for an employee, including isReady and isReadyDate."""
    try:
        data = request.json
        employee_id = data.get('EmployeeId')
        skills = data.get('skills', [])  # Expecting a list of skills
        qualification_year_month = data.get('QualificationYearMonth')  # New field
        full_stack_ready = data.get('FullStackReady', 0)  

        # Validate input
        if not employee_id or not skills:
            return jsonify({'error': 'EmployeeId and skills are required'}), 400

        if qualification_year_month:
            try:
                datetime.strptime(qualification_year_month, "%Y-%m-%d")  # Validate format
            except ValueError:
                return jsonify({'error': 'Invalid QualificationYearMonth format. Expected YYYY-MM.'}), 400

        with db.session.begin():
            if qualification_year_month:
                db.session.execute(
                    text("""
                        UPDATE Employee 
                        SET QualificationYearMonth = :qualification_year_month
                        WHERE EmployeeId = :employee_id
                    """),
                    {'qualification_year_month': qualification_year_month, 'employee_id': employee_id}
                )

        with db.session.begin():
            db.session.execute(
                text("""
                    UPDATE Employee 
                    SET FullStackReady = :full_stack_ready
                    WHERE EmployeeId = :employee_id
                """),
                {'full_stack_ready': full_stack_ready, 'employee_id': employee_id}
            )
       

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
    """API endpoint to fetch all skills for a specific employee, including QualificationYearMonth."""
    try:
        with db.session.begin():
            result = db.session.execute(
                text("""
                    SELECT e.EmployeeId, e.QualificationYearMonth, e.FullStackReady, 
                           es.SkillId, es.SkillLevel, 
                           s.SkillName, es.isReady, es.isReadyDate
                    FROM Employee e
                    LEFT JOIN EmployeeSkill es ON e.EmployeeId = es.EmployeeId
                    LEFT JOIN Skill s ON es.SkillId = s.SkillId
                    WHERE e.EmployeeId = :employee_id
                """),
                {'employee_id': employee_id}
            )

            skills = []
            qualification_year_month = None
            full_stack_ready = None

            for row in result.fetchall():
                row_dict = dict(zip(result.keys(), row))
                
                # Extract QualificationYearMonth once
                if qualification_year_month is None:
                    qualification_year_month = row_dict.pop("QualificationYearMonth", None)

                if full_stack_ready is None:
                    full_stack_ready = row_dict.pop("FullStackReady", None)

                # Append only skill-related fields
                if row_dict["SkillId"]:  # Avoid appending empty skills if no skill exists
                    skills.append({
                        "SkillId": row_dict["SkillId"],
                        "SkillLevel": row_dict["SkillLevel"],
                        "SkillName": row_dict["SkillName"],
                        "isReady": int(row_dict["isReady"]),
                        "isReadyDate": row_dict["isReadyDate"]
                    })

        return jsonify({
            "EmployeeId": employee_id,
            "QualificationYearMonth": qualification_year_month,
            "skills": skills,
             "FullStackReady": full_stack_ready,
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/employees', methods=['GET'])
def get_employees():
    with db.session.begin():
        result = db.session.execute(
            text("""
                SELECT 
                    e.EmployeeId, e.FirstName, e.LastName, e.DateOfJoining,
                    e.TeamLeadId, e.SubRole, e.LobLead, e.IsLead, e.FullStackReady, 
                    es.SkillId, s.SkillName, es.SkillLevel, es.isReady, es.isReadyDate
                FROM HRMS.dbo.Employee e
                LEFT JOIN HRMS.dbo.EmployeeSkill es ON e.EmployeeId = es.EmployeeId
                LEFT JOIN HRMS.dbo.Skill s ON es.SkillId = s.SkillId
            """)
        )
        
        employees_dict = {}

        for row in result.mappings():
            emp_id = row['EmployeeId']
            if emp_id not in employees_dict:
                employees_dict[emp_id] = {
                    "EmployeeId": emp_id,
                    "FirstName": row["FirstName"],
                    "LastName": row["LastName"],
                    "DateOfJoining": row["DateOfJoining"].strftime("%a, %d %b %Y %H:%M:%S GMT") if row["DateOfJoining"] else None,
                    "TeamLeadId": row["TeamLeadId"],
                    "SubRole": row["SubRole"],
                    "LobLead": row["LobLead"],
                    "IsLead": row["IsLead"],
                     "FullStackReady": bool(row["FullStackReady"]), 
                    "Skills": {
                        "Primary": [],
                        "Secondary": [],
                        "CrossTechSkill":[]
                    }
                }

            skill_data = {
                "SkillId": row["SkillId"],
                "SkillName": row["SkillName"],
                "isReady": row["isReady"],
                "isReadyDate": row["isReadyDate"].strftime("%a, %d %b %Y %H:%M:%S GMT") if row["isReadyDate"] else None
            }

            if row["SkillLevel"] == "Primary":
                employees_dict[emp_id]["Skills"]["Primary"].append(skill_data)
            elif row["SkillLevel"] == "Secondary":
                employees_dict[emp_id]["Skills"]["Secondary"].append(skill_data)
            elif row["SkillLevel"] == "Cross Tech Skill":
                employees_dict[emp_id]["Skills"]["CrossTechSkill"].append(skill_data)
            

    return jsonify(list(employees_dict.values()))


# @app.route('/api/send-leave-approval-email', methods=['POST'])
def send_leave_approval_email():
    """Fetch lead emails and send an approval request email."""
    try:
        # Fetching lead emails from the database
        result =()
        # db.session.execute(text("""
        #     SELECT Email
        #     FROM [HRMS].[dbo].[Employee]
        #     WHERE IsLead = 1
        # """))

        lead_emails = [row.Email for row in result if row.Email]  # Extract emails
        lead_emails.append("gautam.bafna@flairminds.com")  # Manually added email

        if not lead_emails:
            return jsonify({"error": "No lead emails found"}), 404

        # Email Configuration
        FROM_ADDRESS = "flairmindshr@gmail.com" # Securely fetch email
        FROM_PASSWORD = "zvhj wpau jqor whkp" # Securely fetch password
        SUBJECT = "Pending Leave Approvals"
        BODY = """
        <p>Hello,</p>
        <p>You have pending leave requests for approval in the HRMS system. Please review and take the necessary action for all associates under your approval.</p>
        <p>Kindly log in to the HRMS portal to process the requests: <a href='https://hrms.flairminds.com'>HRMS Portal</a></p>
        """

        # Prepare Email
        msg = MIMEMultipart()
        msg["From"] = FROM_ADDRESS
        msg["To"] = ", ".join(lead_emails)
        msg["Subject"] = SUBJECT
        msg.attach(MIMEText(BODY, "html"))

        try:
            # Sending Email via Gmail SMTP
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(FROM_ADDRESS, FROM_PASSWORD)
            server.sendmail(FROM_ADDRESS, lead_emails, msg.as_string())
            server.quit()
            return jsonify({"message": "Email sent successfully!"}), 200
        except Exception as e:
            return jsonify({"error": f"Failed to send email: {str(e)}"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500





UPLOAD_FOLDER = "uploads"  # Folder to store files temporarily
ALLOWED_EXTENSIONS = {"pdf"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    """Check if the file has a valid extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/api/upload-document", methods=["POST"])
def upload_document():
    try:
        emp_id = request.form.get("emp_id")
        doc_type = request.form.get("doc_type")  # tenth, twelve, pan, adhar, grad

        if not emp_id or not doc_type:
            return jsonify({"error": "Employee ID and document type are required"}), 400

        if doc_type not in ["tenth", "twelve", "pan", "adhar", "grad"]:
            return jsonify({"error": "Invalid document type"}), 400

        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "Only PDF files are allowed"}), 400

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # Read file as binary
        with open(filepath, "rb") as f:
            file_blob = f.read()

        # Save to database
        with db.session.begin():
            db.session.execute(
                text(f"""
                    UPDATE emp_documents
                    SET {doc_type} = :file_blob
                    WHERE emp_id = :emp_id
                """),
                {"file_blob": file_blob, "emp_id": emp_id},
            )

        # Delete temp file
        os.remove(filepath)

        return jsonify({"message": f"{doc_type} document uploaded successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500




DOCUMENT_COLUMNS = {'tenth', 'twelve', 'pan', 'adhar', 'grad'}

@app.route('/api/get-document/<emp_id>/<doc_type>', methods=['GET'])
def get_document(emp_id, doc_type):
    try:
        # Check if the requested document type is valid
        if doc_type not in DOCUMENT_COLUMNS:
            return jsonify({'error': 'Invalid document type'}), 400

        # Query to fetch the requested document
        query = text(f"SELECT {doc_type} FROM emp_documents WHERE emp_id = :emp_id")
        result = db.session.execute(query, {'emp_id': emp_id}).fetchone()

        if not result or not result[0]:
            return jsonify({'error': 'Document not found'}), 404

        file_blob = result[0]  # Binary data of the document

        return send_file(
            BytesIO(file_blob),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'{emp_id}_{doc_type}.pdf'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/delete-document", methods=["DELETE"])
def delete_document():
    try:
        emp_id = request.args.get("employeeId")  # Get from query params
        doc_type = request.args.get("docType")  # Get from query params

        if not emp_id or not doc_type:
            return jsonify({"error": "Employee ID and document type are required"}), 400

        if doc_type not in ["tenth", "twelve", "pan", "adhar", "grad"]:
            return jsonify({"error": "Invalid document type"}), 400

        # Set the specified document column to NULL in the database
        with db.session.begin():
            db.session.execute(
                text(f"""
                    UPDATE emp_documents
                    SET {doc_type} = NULL
                    WHERE emp_id = :emp_id
                """),
                {"emp_id": emp_id},
            )

        return jsonify({"message": f"{doc_type} document deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/document-status/<emp_id>", methods=["GET"])
def document_status(emp_id):
    try:
        # Fetch document details from the database
        result = db.session.execute(
            text("""
                SELECT tenth, twelve, pan, adhar, grad
                FROM emp_documents
                WHERE emp_id = :emp_id
            """),
            {"emp_id": emp_id}
        ).fetchone()

        if not result:
            return jsonify({"error": "Employee not found"}), 404

        # Convert the database result into a dictionary
        doc_status = {
            "documents": [
                {"doc_type": "tenth", "uploaded": bool(result.tenth)},
                {"doc_type": "twelve", "uploaded": bool(result.twelve)},
                {"doc_type": "adhar", "uploaded": bool(result.adhar)},
                {"doc_type": "pan", "uploaded": bool(result.pan)},
                {"doc_type": "grad", "uploaded": bool(result.grad)}
            ]
        }

        return jsonify(doc_status), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Start the scheduler when the app runs

@app.route("/api/all-employees", methods=["GET"])
def get_all_employees():
    try:
        query = text("""
            SELECT 
                ed.emp_id, 
                e.FirstName, 
                e.MiddleName, 
                e.LastName, 
                ed.tenth, 
                ed.twelve, 
                ed.pan, 
                ed.adhar, 
                ed.grad 
            FROM emp_documents ed
            JOIN Employee e ON ed.emp_id = e.EmployeeId
        """)
        
        result = db.session.execute(query)
        
        employees = []
        for row in result:
            full_name = " ".join(filter(None, [row.FirstName, row.MiddleName, row.LastName]))  # Handling None values
            employees.append({
                "emp_id": row.emp_id,
                "name": full_name,
                "tenth": bool(row.tenth),  # Convert to boolean (True if uploaded, False otherwise)
                "twelve": bool(row.twelve),
                "pan": bool(row.pan),
                "adhar": bool(row.adhar),
                "grad": bool(row.grad),
            })

        return jsonify(employees), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/add-project", methods=["POST"])
def add_project():
    try:
        data = request.json
        project_name = data.get("project_name")
        end_date = data.get("end_date")
        required = data.get("required", 0)  # Default to 0 if not provided

        if not project_name:
            return jsonify({"error": "Project name is required"}), 400

        # Convert `required` to integer (0 or 1)
        required = 1 if required else 0

        with db.session.begin() as session:
            db.session.execute(
                text("""
                    INSERT INTO ProjectList (ProjectName, EndDate, Required)
                    VALUES (:project_name, :end_date, :required)
                """),
                {"project_name": project_name, "end_date": end_date, "required": required},
            )
            session.commit()

        return jsonify({"message": "Project added successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/delete-project/<int:project_id>", methods=["DELETE"])
def delete_project(project_id):
    try:
        with db.session.begin():
            result = db.session.execute(
                text("DELETE FROM ProjectList WHERE ProjectID = :project_id"),
                {"project_id": project_id}
            )
            
            if result.rowcount == 0:  # No matching project found
                return jsonify({"error": "Project not found"}), 404

        return jsonify({"message": "Project deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/delete-project-EmployeeAllocations/<int:project_id>", methods=["DELETE"])
def delete_projectEmployeeAllocations(project_id):
    try:
        with db.session.begin():
            result = db.session.execute(
                text("DELETE FROM ProjectList WHERE ProjectID = :project_id"),
                {"project_id": project_id}
            )
            
            if result.rowcount == 0:  # No matching project found
                return jsonify({"error": "Project not found"}), 404

        return jsonify({"message": "Project deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/projects", methods=["GET"])
def get_projects():
    try:
        result = db.session.execute(text("SELECT ProjectID, ProjectName, EndDate, Required FROM ProjectList"))
        projects = [dict(row) for row in result.mappings()]  

        return jsonify({"projects": projects}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/assign-employee", methods=["POST"])
def assign_employee():
    try:
        data = request.json
        employee_id = data.get("employee_id")
        project_id = data.get("project_id")
        work_category_id = data.get("work_category_id")
        allocation = data.get("allocation", 1.0)  # Default to 1.0 if not provided

        if not employee_id or not project_id or not work_category_id:
            return jsonify({"error": "Employee ID, Project ID, and Work Category ID are required"}), 400

        with db.session.begin():
            db.session.execute(
                text("""
                    INSERT INTO EmployeeAllocations (EmployeeID, ProjectID, WorkCategoryID, Allocation)
                    VALUES (:employee_id, :project_id, :work_category_id, :allocation)
                """),
                {
                    "employee_id": employee_id.strip(),
                    "project_id": project_id,
                    "work_category_id": work_category_id,
                    "allocation": allocation,
                }
            )

        return jsonify({"message": f"Employee {employee_id.strip()} assigned to project successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/policy-acknowledgment/<employee_id>', methods=['GET'])
def get_policy_acknowledgment(employee_id):
    try:
        with db.session.begin():
            result = db.session.execute(
                text("""
                    SELECT 
                        EmployeeId,
                        LeavePolicyAcknowledged,
                        WorkFromHomePolicyAcknowledged,
                        ExitPolicyAndProcessAcknowledged,
                        SalaryAdvanceRecoveryPolicyAcknowledged,
                        ProbationToConfirmationPolicyAcknowledged,
                        SalaryAndAppraisalPolicyAcknowledged
                    FROM EmployeePolicyAcknowledgementStatus
                    WHERE EmployeeId = :employee_id
                """),
                {'employee_id': employee_id}
            )
            
            row = result.fetchone()
            
            if not row:
                return jsonify({'error': 'Employee not found'}), 404
                
            acknowledgment_status = {
                'EmployeeId': row.EmployeeId,
                'LeavePolicyAcknowledged': bool(row.LeavePolicyAcknowledged),
                'WorkFromHomePolicyAcknowledged': bool(row.WorkFromHomePolicyAcknowledged),
                'ExitPolicyAndProcessAcknowledged': bool(row.ExitPolicyAndProcessAcknowledged),
                'SalaryAdvanceRecoveryPolicyAcknowledged': bool(row.SalaryAdvanceRecoveryPolicyAcknowledged),
                'ProbationToConfirmationPolicyAcknowledged': bool(row.ProbationToConfirmationPolicyAcknowledged),
                'SalaryAndAppraisalPolicyAcknowledged': bool(row.SalaryAndAppraisalPolicyAcknowledged)
            }
            
            return jsonify(acknowledgment_status), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/policy-acknowledgment', methods=['POST'])
# @cross_origin(origins=['http://localhost:5173'], supports_credentials=True)
def update_policy_acknowledgment():
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 415

        data = request.get_json()
        employee_id = data.get('employeeId')
        policy_name = data.get('policyName')
        acknowledged = data.get('acknowledged', True)
        
        if not employee_id or not policy_name:
            return jsonify({'error': 'employeeId and policyName are required'}), 400
            
        # Map frontend policy name to database column name
        policy_column_map = {
            'Leave Policy': 'LeavePolicyAcknowledged',
            'Work From Home Policy': 'WorkFromHomePolicyAcknowledged',
            'Exit Policy & Process': 'ExitPolicyAndProcessAcknowledged',
            'Salary Advance & Recovery Policy': 'SalaryAdvanceRecoveryPolicyAcknowledged',
            'Probation To Confirmation Policy': 'ProbationToConfirmationPolicyAcknowledged',
            'Salary and appraisal process Policy': 'SalaryAndAppraisalPolicyAcknowledged'
        }
        
        if policy_name not in policy_column_map:
            return jsonify({'error': 'Invalid policy name'}), 400
            
        column_name = policy_column_map[policy_name]
        
        with db.session.begin():
            # First check if record exists
            result = db.session.execute(
                text(f"""
                    SELECT COUNT(*) 
                    FROM EmployeePolicyAcknowledgementStatus 
                    WHERE EmployeeId = :employee_id
                """),
                {'employee_id': employee_id}
            ).scalar()
            
            if result == 0:
                # Insert new record
                db.session.execute(
                    text(f"""
                        INSERT INTO EmployeePolicyAcknowledgementStatus 
                        (EmployeeId, {column_name})
                        VALUES (:employee_id, :acknowledged)
                    """),
                    {
                        'employee_id': employee_id,
                        'acknowledged': acknowledged
                    }
                )
            else:
                # Update existing record
                db.session.execute(
                    text(f"""
                        UPDATE EmployeePolicyAcknowledgementStatus 
                        SET {column_name} = :acknowledged
                        WHERE EmployeeId = :employee_id
                    """),
                    {
                        'employee_id': employee_id,
                        'acknowledged': acknowledged
                    }
                )
                
        return jsonify({
            'message': 'Policy acknowledgment updated successfully',
            'employeeId': employee_id,
            'policyName': policy_name,
            'acknowledged': acknowledged
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/send-policy-email', methods=['POST'])
def send_policy_email():
    try:
        data = request.json
        employee_id = data.get('employeeId')
        
        if not employee_id:
            return jsonify({'error': 'Employee ID is required'}), 400

        # Get employee details
        with db.session.begin():
            employee_result = db.session.execute(
                text("""
                    SELECT FirstName, LastName, Email
                    FROM Employee
                    WHERE EmployeeId = :employee_id
                """),
                {'employee_id': employee_id}
            ).fetchone()

            if not employee_result:
                return jsonify({'error': 'Employee not found'}), 404

            # Get policy acknowledgment status
            policy_result = db.session.execute(
                text("""
                    SELECT 
                        LeavePolicyAcknowledged,
                        WorkFromHomePolicyAcknowledged,
                        ExitPolicyAndProcessAcknowledged,
                        SalaryAdvanceRecoveryPolicyAcknowledged,
                        ProbationToConfirmationPolicyAcknowledged,
                        SalaryAndAppraisalPolicyAcknowledged
                    FROM EmployeePolicyAcknowledgementStatus
                    WHERE EmployeeId = :employee_id
                """),
                {'employee_id': employee_id}
            ).fetchone()

            if not policy_result:
                return jsonify({'error': 'Policy acknowledgment status not found'}), 404

            # Check if all policies are acknowledged
            all_acknowledged = all([
                policy_result.LeavePolicyAcknowledged,
                policy_result.WorkFromHomePolicyAcknowledged,
                policy_result.ExitPolicyAndProcessAcknowledged,
                policy_result.SalaryAdvanceRecoveryPolicyAcknowledged,
                policy_result.ProbationToConfirmationPolicyAcknowledged,
                policy_result.SalaryAndAppraisalPolicyAcknowledged
            ])

            if not all_acknowledged:
                return jsonify({'error': 'Not all policies are acknowledged'}), 400

            # Prepare email
            employee_name = f"{employee_result.FirstName} {employee_result.LastName}"
            subject = f"Policy Acknowledgment - {employee_name}"
            body = f"""
            <html>
                <body>
                    <h3>Policy Acknowledgment Notification</h3>
                    <p>Employee {employee_name} (ID: {employee_id}) has acknowledged all company policies.</p>
                    <p>All policies have been read and acknowledged:</p>
                    <ul>
                        <li>Leave Policy</li>
                        <li>Work From Home Policy</li>
                        <li>Exit Policy & Process</li>
                        <li>Salary Advance & Recovery Policy</li>
                        <li>Probation To Confirmation Policy</li>
                        <li>Salary and Appraisal Process Policy</li>
                    </ul>
                </body>
            </html>
            """

            # Set up the email message
            msg = MIMEMultipart()
            msg['From'] = FROM_ADDRESS
            msg['To'] = "hr@flairminds.com"
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))

            # Send email
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(FROM_ADDRESS, FROM_PASSWORD)
            server.sendmail(FROM_ADDRESS, ["hr@flairminds.com"], msg.as_string())
            server.quit()

            return jsonify({
                'message': 'Email sent successfully',
                'employeeId': employee_id,
                'employeeName': employee_name
            }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/update-warning-count', methods=['POST'])
def update_warning_count():
    try:
        data = request.json
        employee_id = data.get('employeeId')

        if not employee_id:
            return jsonify({'error': 'Employee ID is required'}), 400

        with db.session.begin():
            # First check if record exists and get current count
            result = db.session.execute(
                text("""
                    SELECT COALESCE(WarningCount, 0) as WarningCount 
                    FROM EmployeePolicyAcknowledgementStatus 
                    WHERE EmployeeId = :employee_id
                """),
                {'employee_id': employee_id}
            ).fetchone()
            
            current_count = result.WarningCount if result else 0
            new_count = current_count + 1
            
            if not result:
                # Insert new record with warning count
                db.session.execute(
                    text("""
                        INSERT INTO EmployeePolicyAcknowledgementStatus 
                        (EmployeeId, WarningCount)
                        VALUES (:employee_id, :warning_count)
                    """),
                    {
                        'employee_id': employee_id,
                        'warning_count': new_count
                    }
                )
            else:
                # Update existing record
                db.session.execute(
                    text("""
                        UPDATE EmployeePolicyAcknowledgementStatus 
                        SET WarningCount = :warning_count
                        WHERE EmployeeId = :employee_id
                    """),
                    {
                        'employee_id': employee_id,
                        'warning_count': new_count
                    }
                )
                
        return jsonify({
            'message': 'Warning count updated successfully',
            'employeeId': employee_id,
            'warningCount': new_count
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/warning-count/<employee_id>', methods=['GET'])
def get_warning_count(employee_id):
    try:
        with db.session.begin():
            result = db.session.execute(
                text("""
                    SELECT COALESCE(WarningCount, 0) as WarningCount 
                    FROM EmployeePolicyAcknowledgementStatus 
                    WHERE EmployeeId = :employee_id
                """),
                {'employee_id': employee_id}
            ).fetchone()
            
            if not result:
                return jsonify({'warningCount': 0}), 200
                
            return jsonify({'warningCount': result.WarningCount}), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/complete-employee-details/<employee_id>', methods=['GET'])
def get_complete_employee_details(employee_id):
    try:
        with db.session.begin():
            # Get employee details
            employee_result = db.session.execute(
                text("""
                    SELECT 
                        ContactNumber,
                        EmergencyContactPerson,
                        EmergencyContactRelation,
                        EmergencyContactNumber,
                        QualificationYearMonth,
                        FullStackReady
                    FROM Employee
                    WHERE EmployeeId = :employee_id
                """),
                {'employee_id': employee_id}
            ).fetchone()
            
            if not employee_result:
                return jsonify({'error': 'Employee not found'}), 404

            # Get address details
            address_result = db.session.execute(
                text("""
                    SELECT 
                        AddressType,
                        State,
                        City,
                        Address1,
                        Address2,
                        IsSamePermanant,
                        ZipCode
                    FROM EmployeeAddress
                    WHERE EmployeeId = :employee_id
                """),
                {'employee_id': employee_id}
            ).fetchall()
            
            # Get document details
            document_result = db.session.execute(
                text("""
                    SELECT 
                        doc_id,
                        tenth,
                        twelve,
                        pan,
                        adhar,
                        grad,
                        resume
                    FROM emp_documents
                    WHERE emp_id = :employee_id
                """),
                {'employee_id': employee_id}
            ).fetchone()

            # Get skills details
            skills_result = db.session.execute(
                text("""
                    SELECT 
                        es.SkillId,
                        es.SkillLevel,
                        es.isReady,
                        es.isReadyDate,
                        es.FullStackReady,
                        s.SkillName
                    FROM EmployeeSkill es
                    LEFT JOIN Skill s ON es.SkillId = s.SkillId
                    WHERE es.EmployeeId = :employee_id
                """),
                {'employee_id': employee_id}
            ).fetchall()
            
            # Convert address results to list of dictionaries
            addresses = []
            for addr in address_result:
                addresses.append({
                    'AddressType': addr.AddressType,
                    'State': addr.State,
                    'City': addr.City,
                    'Address1': addr.Address1,
                    'Address2': addr.Address2,
                    'IsSamePermanant': bool(addr.IsSamePermanant),
                    'ZipCode': addr.ZipCode
                })
            
            # Create document details dictionary and check for missing documents
            documents = {
                'doc_id': document_result.doc_id if document_result else None,
                'tenth': bool(document_result.tenth) if document_result else False,
                'twelve': bool(document_result.twelve) if document_result else False,
                'pan': bool(document_result.pan) if document_result else False,
                'adhar': bool(document_result.adhar) if document_result else False,
                'grad': bool(document_result.grad) if document_result else False,
                'resume': bool(document_result.resume) if document_result else False
            }

            # Convert skills results to list of dictionaries
            skills = []
            for skill in skills_result:
                skills.append({
                    'SkillId': skill.SkillId,
                    'SkillName': skill.SkillName,
                    'SkillLevel': skill.SkillLevel,
                    'isReady': bool(skill.isReady),
                    'isReadyDate': skill.isReadyDate.strftime('%Y-%m-%d') if skill.isReadyDate else None,
                    'FullStackReady': bool(skill.FullStackReady)
                })

            # Check for missing information
            missing_fields = []
            
            if not employee_result.ContactNumber:
                missing_fields.append("Contact Number")
            if not employee_result.EmergencyContactPerson:
                missing_fields.append("Emergency Contact Person")
            if not employee_result.EmergencyContactRelation:
                missing_fields.append("Emergency Contact Relation")
            if not employee_result.EmergencyContactNumber:
                missing_fields.append("Emergency Contact Number")
            if not employee_result.QualificationYearMonth:
                missing_fields.append("Qualification Year Month")
            if employee_result.FullStackReady is None:
                missing_fields.append("Full Stack Ready Status")
            if not addresses:
                missing_fields.append("Address Information")
            if not skills:
                missing_fields.append("Skills Information")

            # Check for missing documents
            if not document_result:
                missing_fields.append("All Documents")
            else:
                if not document_result.tenth:
                    missing_fields.append("10th Certificate")
                if not document_result.twelve:
                    missing_fields.append("12th Certificate")
                if not document_result.pan:
                    missing_fields.append("PAN Card")
                if not document_result.adhar:
                    missing_fields.append("Aadhar Card")
                if not document_result.grad:
                    missing_fields.append("Graduation Certificate")
                if not document_result.resume:
                    missing_fields.append("Resume")

            # Prepare response
            is_complete = len(missing_fields) == 0
            response = {
                'status': is_complete,
                'message': 'All information is complete' if is_complete else f'Missing information: {", ".join(missing_fields)}',
                'data': {
                    'ContactNumber': employee_result.ContactNumber if employee_result.ContactNumber else False,
                    'EmergencyContactPerson': employee_result.EmergencyContactPerson if employee_result.EmergencyContactPerson else False,
                    'EmergencyContactRelation': employee_result.EmergencyContactRelation if employee_result.EmergencyContactRelation else False,
                    'EmergencyContactNumber': employee_result.EmergencyContactNumber if employee_result.EmergencyContactNumber else False,
                    'QualificationYearMonth': employee_result.QualificationYearMonth if employee_result.QualificationYearMonth else False,
                    'FullStackReady': bool(employee_result.FullStackReady) if employee_result.FullStackReady is not None else False,
                    'Addresses': addresses if addresses else False,
                    'Documents': documents,
                    'Skills': skills if skills else False
                }
            }
            
            return jsonify(response), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/increment-address-counter/<employee_id>', methods=['POST'])
def increment_address_counter(employee_id):
    try:
        with db.session.begin():
            # First get the current counter value
            current_counter = db.session.execute(
                text("""
                    SELECT MAX(counter) as current_count
                    FROM EmployeeAddress 
                    WHERE EmployeeId = :employee_id
                """),
                {'employee_id': employee_id}
            ).scalar() or 0

            # Check if counter has reached limit
            if current_counter >= 3:
                return jsonify({
                    'message': 'Counter limit reached',
                    'employeeId': employee_id,
                    'limitReached': True
                }), 200

            # Update the counter for all addresses of the employee
            result = db.session.execute(
                text("""
                    UPDATE EmployeeAddress 
                    SET counter = ISNULL(counter, 0) + 1
                    WHERE EmployeeId = :employee_id
                """),
                {'employee_id': employee_id}
            )
            
            if result.rowcount == 0:
                return jsonify({'error': 'No address found for employee'}), 404
                
            return jsonify({
                'message': 'Counter incremented successfully',
                'employeeId': employee_id,
                'limitReached': False,
                'currentCount': current_counter + 1
            }), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run("0.0.0.0", port=7000, debug=True)
