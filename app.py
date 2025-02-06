from flask import Flask, render_template, request, jsonify
from extensions import app, db
from sqlalchemy import text
import os

# No need to create another Flask app here, since `app` is already created in `extensions.py`


@app.route('/api/leaves', methods=['GET'])
def get_leaves():
    date = '2025-02-06'  # This should be dynamically set or passed

    with db.session.begin():
        # Use the correct formatted date in your SQL query
        result = db.session.execute(
            text(f"SELECT * FROM LeaveTransaction WHERE fromDate = :date")
            .params(date=date)  # Pass the date as a parameter
        )
        rows = result.fetchall()
        leave_data = []
        for row in rows:
            leave_data.append({
                'fromDate': row[4],  # Assuming 'fromDate' is at index 4
                'AppliedBy': row[1],  # Assuming 'AppliedBy' is at index 10
                'LeaveStatus': row[13],  # Assuming 'leaveStatus' is at index 14
                "LaeveType":row[3]
            })
    
    return leave_data

if __name__ == '__main__':
    app.run("0.0.0.0", port=7000, debug=True)
