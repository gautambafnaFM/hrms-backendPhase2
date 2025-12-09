# email_service.py
import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from extensions import FROM_ADDRESS, FROM_PASSWORD, TO_ADDRESSES, db
from sqlalchemy import text


def process_leave_email():
    print("Processing leave email...")

    # Handle weekend case
    current_date = datetime.today()
    if current_date.weekday() == 5:      # Saturday
        current_date += timedelta(days=2)
    elif current_date.weekday() == 6:    # Sunday
        current_date += timedelta(days=1)

    current_date_str = current_date.strftime('%Y-%m-%d')

    # ---- FIX: Use thread-safe DB connection ----
    engine = db.engine
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT lt.fromDate, lt.ToDate, e.FirstName, e.LastName,
                       lt.LeaveStatus, ltm.LeaveName
                FROM LeaveTransaction lt
                JOIN Employee e ON lt.AppliedBy = e.EmployeeId
                JOIN LeaveTypeMaster ltm ON lt.LeaveType = ltm.LeaveTypeID
                WHERE :date BETWEEN lt.fromDate AND lt.ToDate
                AND lt.LeaveStatus != 'Cancel'
            """),
            {"date": current_date_str}
        )

        rows = result.fetchall()

    # --------------------------------------------

    leave_table = """
        <table border='1' style='border-collapse: collapse; text-align: left;'>
            <tr>
                <th>From Date</th>
                <th>To Date</th>
                <th>Applied By</th>
                <th>Status</th>
                <th>Leave Type</th>
            </tr>
    """

    for r in rows:
        leave_table += f"""
            <tr>
                <td>{r[0]}</td>
                <td>{r[1]}</td>
                <td>{r[2]} {r[3]}</td>
                <td>{r[4]}</td>
                <td>{r[5]}</td>
            </tr>
        """

    leave_table += "</table>"

    # Email setup
    msg = MIMEMultipart()
    msg['From'] = FROM_ADDRESS
    msg['To'] = ", ".join(TO_ADDRESSES)   # Convert list to string
    msg['Subject'] = f"Leave Report - {current_date_str}"
    msg.attach(MIMEText(f"<html><body>{leave_table}</body></html>", 'html'))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(FROM_ADDRESS, FROM_PASSWORD)
        server.sendmail(FROM_ADDRESS, TO_ADDRESSES, msg.as_string())
        server.quit()

        print("Email sent successfully")
        return True

    except Exception as e:
        print("Email sending failed:", e)
        return False
