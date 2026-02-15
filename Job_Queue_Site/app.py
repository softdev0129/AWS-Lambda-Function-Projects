import json
import os
import pg8000
import traceback
from datetime import datetime

# Database connection details
db_host = 'database-1.c05cmttqad2g.eu-west-1.rds.amazonaws.com'
db_port = int(os.environ.get('DB_PORT', 5432))  # Default PostgreSQL port
db_database = 'scraper_db'
db_user = 'postgres'
db_password = 'GWtxSGM4swxxhN3fMHRH'

def lambda_handler(event, context):
    try:
        action = event.get('action')
        if action == 'start_job':
            return start_job(event)
        elif action == 'complete_job':
            return complete_job(event, 'COMPLETE')
        elif action == 'fail_job':
            return complete_job(event, 'FAILED')
        else:
            return view_jobs(event)
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        print(traceback.format_exc())
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }

def get_db_connection():
    try:
        conn = pg8000.connect(
            host=db_host,
            port=db_port,
            database=db_database,
            user=db_user,
            password=db_password
        )
        create_table_if_not_exists(conn)
        return conn
    except Exception as e:
        print(f"Error in get_db_connection: {str(e)}")
        print(traceback.format_exc())
        raise

def create_table_if_not_exists(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_events (
            id SERIAL PRIMARY KEY,
            event_name VARCHAR(255),
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            status VARCHAR(50) CHECK (status IN ('COMPLETE', 'FAILED', 'IN_PROGRESS'))
        );
        """)
        conn.commit()
        cursor.close()
    except Exception as e:
        print(f"Error in create_table_if_not_exists: {str(e)}")
        print(traceback.format_exc())
        raise

def start_job(event):
    try:
        event_name = event.get('event_name')
        start_time = datetime.now()

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO job_events (event_name, start_time, status) VALUES (%s, %s, %s) RETURNING id",
            (event_name, start_time, 'IN_PROGRESS')
        )
        
        job_id = cursor.fetchone()[0]

        conn.commit()
        cursor.close()
        conn.close()

        # Ensure the ID is correctly generated and returned
        print(f"Job started with ID: {job_id}")

        return {
            'statusCode': 200,
            'body': json.dumps({'id': job_id})
        }
    except Exception as e:
        print(f"Error starting job: {str(e)}")
        print(traceback.format_exc())
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }

def complete_job(event, status):
    try:
        job_id = event.get('id')
        end_time = datetime.now()

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE job_events SET end_time = %s, status = %s WHERE id = %s",
            (end_time, status, job_id)
        )

        conn.commit()
        cursor.close()
        conn.close()

        # Ensure the ID is correctly returned
        print(f"Job completed with ID: {job_id}")

        return {
            'statusCode': 200,
            'body': json.dumps({'id': job_id})
        }
    except Exception as e:
        print(f"Error completing job: {str(e)}")
        print(traceback.format_exc())
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }

def view_jobs(event):
    try:
        # Extract pagination parameters
        page = int(event.get('queryStringParameters', {}).get('page', 1))
        limit = int(event.get('queryStringParameters', {}).get('limit', 10))
        job_name_filter = event.get('queryStringParameters', {}).get('job_name', '')
        offset = (page - 1) * limit

        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch distinct job names for dropdown
        cursor.execute("SELECT DISTINCT event_name FROM job_events ORDER BY event_name")
        job_names = cursor.fetchall()

        # Get total count of jobs for pagination
        if job_name_filter:
            cursor.execute("SELECT COUNT(*) FROM job_events WHERE event_name ILIKE %s", (f'%{job_name_filter}%',))
        else:
            cursor.execute("SELECT COUNT(*) FROM job_events")
        total_jobs = cursor.fetchone()[0]
        
        # Fetch jobs with pagination, filtering, and sorting
        if job_name_filter:
            cursor.execute("""
                SELECT id, event_name, start_time, end_time, status
                FROM job_events
                WHERE event_name ILIKE %s
                ORDER BY id DESC
                LIMIT %s OFFSET %s
            """, (f'%{job_name_filter}%', limit, offset))
        else:
            cursor.execute("""
                SELECT id, event_name, start_time, end_time, status
                FROM job_events
                ORDER BY id DESC
                LIMIT %s OFFSET %s
            """, (limit, offset))
        rows = cursor.fetchall()

        # Generate HTML content
        html_content = """
        <html>
        <head>
            <title>Job Events</title>
            <style>
                table {
                    width: 100%;
                    border-collapse: collapse;
                }
                table, th, td {
                    border: 1px solid black;
                }
                th, td {
                    padding: 15px;
                    text-align: left;
                }
                th {
                    background-color: #f2f2f2;
                }
                .pagination {
                    margin: 10px 0;
                    display: flex;
                    justify-content: center;
                }
                .pagination a {
                    margin: 0 5px;
                    padding: 8px 16px;
                    text-decoration: none;
                    color: black;
                    border: 1px solid #ddd;
                }
                .pagination a.active {
                    background-color: #4CAF50;
                    color: white;
                    border: 1px solid #4CAF50;
                }
                .pagination a:hover:not(.active) {
                    background-color: #ddd;
                }
            </style>
        </head>
        <body>
            <h1>Job Events</h1>
            <form method="GET" action="">
                <label for="job_name">Filter by Job Name:</label>
                <select id="job_name" name="job_name">
                    <option value="">Select a job name</option>
        """
        
        for job_name in job_names:
            selected = "selected" if job_name[0] == job_name_filter else ""
            html_content += f'<option value="{job_name[0]}" {selected}>{job_name[0]}</option>'
        
        html_content += """
                </select>
                <input type="submit" value="Filter">
            </form>
            <table>
                <tr>
                    <th>ID</th>
                    <th>Event Name</th>
                    <th>Start Time</th>
                    <th>End Time</th>
                    <th>Status</th>
                    <th>Duration (seconds)</th>
                </tr>
        """

        for row in rows:
            start_time = row[2]
            end_time = row[3]
            duration = (end_time - start_time).total_seconds() if end_time else 'N/A'
            html_content += f"""
                <tr>
                    <td>{row[0]}</td>
                    <td>{row[1]}</td>
                    <td>{row[2]}</td>
                    <td>{row[3]}</td>
                    <td>{row[4]}</td>
                    <td>{duration}</td>
                </tr>
            """

        html_content += """
            </table>
        """

        # Add pagination controls
        total_pages = (total_jobs + limit - 1) // limit  # Calculate total number of pages
        html_content += '<div class="pagination">'
        for i in range(1, total_pages + 1):
            if i == page:
                html_content += f'<a class="active" href="?page={i}&limit={limit}&job_name={job_name_filter}">{i}</a>'
            else:
                html_content += f'<a href="?page={i}&limit={limit}&job_name={job_name_filter}">{i}</a>'
        html_content += '</div>'

        html_content += """
        </body>
        </html>
        """

        cursor.close()
        conn.close()

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html'
            },
            'body': html_content
        }
    except Exception as e:
        print(f"Error viewing jobs: {str(e)}")
        print(traceback.format_exc())
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }
