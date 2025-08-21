from flask import Flask, render_template, request, jsonify, send_file
import mysql.connector
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key'

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='studentdb'
)

# ----- ROUTES -----

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upsert')
def upsert_page():
    return render_template('upsert.html')

@app.route('/add-degree')
def add_degree_page():
    return render_template('add_degree.html')

# --- API ROUTES ---

@app.route('/api/students', methods=['GET'])
def get_students():
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT students.id, fname, lname, gender, address, zipcode, city, degrees.name AS degree, attachment_filename
        FROM students
        LEFT JOIN degrees ON students.degree_id = degrees.id
    """)
    rows = cur.fetchall()
    cur.close()
    return jsonify(rows)

@app.route('/api/students', methods=['POST'])
def add_student():
    data = request.form
    file = request.files.get('attachment')
    file_data = file.read() if file and file.filename else None
    file_name = file.filename if file and file.filename else None
    required = ['fname', 'lname', 'gender']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        INSERT INTO students (fname, lname, gender, address, zipcode, city, degree_id, attachment, attachment_filename)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        data['fname'],
        data['lname'],
        data['gender'],
        data.get('address', ''),
        data.get('zipcode', ''),
        data.get('city', ''),
        int(data['degree_id']) if data.get('degree_id') not in [None, '', 'null'] else None,
        file_data,
        file_name
    ))
    student_id = cur.lastrowid
    fam = {k: data.get(k) for k in [
        'mother_name', 'mother_contact', 'father_name', 'father_contact', 'sibling_name', 'sibling_contact'
    ]}
    if any(fam.values()):
        cur.execute("""
            INSERT INTO student_family (student_id, mother_name, mother_contact, father_name, father_contact, sibling_name, sibling_contact)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (student_id, fam['mother_name'], fam['mother_contact'], fam['father_name'], fam['father_contact'], fam['sibling_name'], fam['sibling_contact']))
    conn.commit()
    cur.close()
    return jsonify({'message': 'Student added successfully'})

@app.route('/api/students/<int:id>', methods=['GET'])
def get_student(id):
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT id, fname, lname, gender, address, zipcode, city, degree_id, attachment_filename
        FROM students WHERE id = %s
    """, (id,))
    row = cur.fetchone() or {}

    cur.execute("""
        SELECT mother_name, mother_contact, father_name, father_contact, sibling_name, sibling_contact
        FROM student_family WHERE student_id = %s
    """, (id,))
    fam = cur.fetchone() or {}
    cur.close()
    if not row:
        return jsonify({'error': 'Student not found'}), 404
    row.update(fam)
    return jsonify(row)

@app.route('/api/students/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.form
    file = request.files.get('attachment')
    file_data = None
    file_name = None
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT attachment, attachment_filename FROM students WHERE id = %s", (id,))
    current = cur.fetchone()
    if file and file.filename:
        file_data = file.read()
        file_name = file.filename
    else:
        file_data = current['attachment'] if current else None
        file_name = current['attachment_filename'] if current else None
    cur.execute("""
        UPDATE students SET fname=%s, lname=%s, gender=%s, address=%s, zipcode=%s, city=%s, degree_id=%s, attachment=%s, attachment_filename=%s
        WHERE id=%s
    """, (
        data['fname'],
        data['lname'],
        data['gender'],
        data.get('address', ''),
        data.get('zipcode', ''),
        data.get('city', ''),
        int(data['degree_id']) if data.get('degree_id') not in [None, '', 'null'] else None,
        file_data,
        file_name,
        id
    ))
    fam = {k: data.get(k) for k in [
        'mother_name','mother_contact','father_name','father_contact','sibling_name','sibling_contact'
    ]}
    cur.execute("SELECT id FROM student_family WHERE student_id = %s", (id,))
    famrow = cur.fetchone()
    if any(fam.values()):
        if famrow:
            cur.execute("""
                UPDATE student_family SET mother_name=%s, mother_contact=%s, father_name=%s, father_contact=%s, sibling_name=%s, sibling_contact=%s
                WHERE student_id=%s
            """, (fam['mother_name'], fam['mother_contact'], fam['father_name'], fam['father_contact'], fam['sibling_name'], fam['sibling_contact'], id))
        else:
            cur.execute("""
                INSERT INTO student_family (student_id, mother_name, mother_contact, father_name, father_contact, sibling_name, sibling_contact)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (id, fam['mother_name'], fam['mother_contact'], fam['father_name'], fam['father_contact'], fam['sibling_name'], fam['sibling_contact']))
    conn.commit()
    cur.close()
    return jsonify({'message': 'Student updated successfully'})

@app.route('/api/students/<int:id>/attachment', methods=['GET'])
def download_attachment(id):
    cur = conn.cursor()
    cur.execute("SELECT attachment, attachment_filename FROM students WHERE id = %s", (id,))
    row = cur.fetchone()
    cur.close()
    if not row or not row[0]:
        return "No file found", 404
    return send_file(io.BytesIO(row[0]), download_name=row[1], as_attachment=True)


@app.route('/api/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    cur = conn.cursor()
    cur.execute("DELETE FROM student_family WHERE student_id = %s", (id,))
    cur.execute("DELETE FROM students WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    return jsonify({'message': 'Student deleted'})

# Degrees API
@app.route('/api/degrees', methods=['GET'])
def get_degrees():
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM degrees ORDER BY name")
    result = cur.fetchall()
    cur.close()
    return jsonify(result)

@app.route('/api/degrees', methods=['POST'])
def add_degree():
    data = request.json
    if not data.get('name'):
        return jsonify({'error': 'Degree name required'}), 400
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO degrees (name) VALUES (%s)", (data['name'],))
        conn.commit()
        return jsonify({'message': 'Degree added'})
    except mysql.connector.errors.IntegrityError:
        return jsonify({'error': 'Degree already exists'}), 400
    finally:
        cur.close()

if __name__ == '__main__':
    app.run(debug=True)

