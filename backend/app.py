"""
Flask Backend for Student Marks Sorting and Ranking System
================================================================
PostgreSQL-backed REST API with Manual Merge Sort

Architecture:
    Frontend → Flask REST API → SQLAlchemy → PostgreSQL
    Frontend → Flask REST API → Manual Merge Sort → Rankings

All sorting is done manually via merge_sort().
No SQL ORDER BY or built-in sorting is used for ranking.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os, sys, json, time, random

# Add the backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import init_db, DATABASE_URL, test_connection
from models import Student, db
from merge_sort import merge_sort, generate_ranks, get_statistics as calc_stats

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Initialize database
init_db(app)


# ==================== HELPER FUNCTIONS ====================

def student_to_dict(student_obj):
    """Convert SQLAlchemy Student object to dictionary."""
    return {
        'id': student_obj.id,
        'roll': student_obj.roll_no,
        'name': student_obj.name,
        'marks': student_obj.marks,
        'created_at': student_obj.created_at.isoformat() if student_obj.created_at else None
    }


def validate_student_data(data):
    """
    Validate student input data.
    Returns (is_valid, error_message) tuple.
    """
    if not isinstance(data, dict):
        return False, 'Student data must be an object'

    roll = data.get('roll')
    name = data.get('name')
    marks = data.get('marks')

    if not roll or not isinstance(roll, (int, float)):
        return False, 'Roll number is required and must be a number'
    if not name or not isinstance(name, str) or name.strip() == '':
        return False, 'Name is required and cannot be empty'
    if marks is None or not isinstance(marks, (int, float)):
        return False, 'Marks is required and must be a number'
    if marks < 0 or marks > 100:
        return False, 'Marks must be between 0 and 100'

    return True, None


# ==================== API ENDPOINTS ====================

@app.route('/', methods=['GET'])
def home():
    """Root endpoint."""
    db_status = 'connected' if test_connection() else 'disconnected'
    return jsonify({
        'message': 'Student Marks Sorting & Ranking System',
        'status': 'Running',
        'algorithm': 'Merge Sort (Manual Implementation)',
        'database': db_status
    }), 200


@app.route('/api/health', methods=['GET'])
def health():
    """Health check - returns database connection status."""
    connected = test_connection()
    return jsonify({
        'status': 'ok' if connected else 'error',
        'database': 'connected' if connected else 'disconnected'
    }), 200 if connected else 503


@app.route('/api/students', methods=['GET'])
def get_students():
    """GET /api/students - Return all students from PostgreSQL."""
    try:
        students = Student.query.all()
        result = [student_to_dict(s) for s in students]
        return jsonify({'students': result}), 200
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500


@app.route('/api/students', methods=['POST'])
def add_student():
    """POST /api/students - Add a new student."""
    data = request.get_json()
    is_valid, error_msg = validate_student_data(data)
    if not is_valid:
        return jsonify({'error': error_msg}), 400

    roll = int(data['roll'])
    name = data['name'].strip()
    marks = float(data['marks'])

    # Check for duplicate roll number
    existing = Student.query.filter_by(roll_no=roll).first()
    if existing:
        return jsonify({'error': 'Roll number already exists'}), 409

    new_student = Student(roll_no=roll, name=name, marks=marks)
    db.session.add(new_student)
    db.session.commit()

    return jsonify({'message': 'Student added successfully', 'student': student_to_dict(new_student)}), 201


@app.route('/api/students/<int:id>', methods=['PUT'])
def update_student(id):
    """PUT /api/students/<id> - Update a student."""
    data = request.get_json()
    is_valid, error_msg = validate_student_data(data)
    if not is_valid:
        return jsonify({'error': error_msg}), 400

    student = Student.query.get(id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    roll = int(data['roll'])
    name = data['name'].strip()
    marks = float(data['marks'])

    # Check for duplicate roll number (excluding current student)
    existing = Student.query.filter(Student.roll_no == roll, Student.id != id).first()
    if existing:
        return jsonify({'error': 'Roll number already exists'}), 409

    student.roll_no = roll
    student.name = name
    student.marks = marks
    student.created_at = datetime.utcnow()
    db.session.commit()

    return jsonify({'message': 'Student updated successfully', 'student': student_to_dict(student)}), 200


@app.route('/api/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    """DELETE /api/students/<id> - Delete a student."""
    student = Student.query.get(id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    db.session.delete(student)
    db.session.commit()

    return jsonify({'message': 'Student deleted successfully'}), 200


@app.route('/api/students', methods=['DELETE'])
def delete_all_students():
    """DELETE /api/students - Delete all students."""
    try:
        Student.query.delete()
        db.session.commit()
        return jsonify({'message': 'All students deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500


@app.route('/api/sample', methods=['GET'])
def load_sample():
    """GET /api/sample - Load sample students into PostgreSQL.
    Does not duplicate existing records."""
    sample_data = [
        {'roll': 101, 'name': 'Rahul', 'marks': 72},
        {'roll': 102, 'name': 'Priya', 'marks': 91},
        {'roll': 103, 'name': 'Aman', 'marks': 85},
        {'roll': 104, 'name': 'Neha', 'marks': 96},
        {'roll': 105, 'name': 'Riya', 'marks': 78}
    ]

    added = []
    skipped = []

    for data in sample_data:
        existing = Student.query.filter_by(roll_no=data['roll']).first()
        if existing:
            skipped.append(data['roll'])
            continue

        student = Student(roll_no=data['roll'], name=data['name'], marks=data['marks'])
        db.session.add(student)
        added.append(data['roll'])

    db.session.commit()

    return jsonify({
        'message': 'Sample data loaded',
        'added': added,
        'skipped': skipped,
        'students': [student_to_dict(s) for s in Student.query.all()]
    }), 200


@app.route('/api/ranking', methods=['GET'])
def get_ranking():
    """GET /api/ranking - Fetch students from PostgreSQL, sort using manual Merge Sort,
    generate ranks, and return the ranking.

    IMPORTANT: Uses manual Merge Sort, NOT SQL ORDER BY.
    """
    try:
        students = Student.query.all()
        if not students:
            return jsonify({'students': [], 'statistics': {'total': 0, 'highest': 0, 'average': 0, 'lowest': 0}}), 200

        # Convert to dictionaries for sorting
        student_list = [student_to_dict(s) for s in students]

        # Run manual Merge Sort (the core algorithm!)
        sorted_students = merge_sort(student_list)

        # Generate competition ranks
        ranked_students = generate_ranks(sorted_students)

        # Calculate statistics
        stats = calc_stats(student_list)

        return jsonify({'students': ranked_students, 'statistics': stats}), 200
    except Exception as e:
        return jsonify({'error': f'Ranking error: {str(e)}'}), 500


@app.route('/api/rank', methods=['POST'])
def rank_students():
    """POST /api/rank - Accept student records, sort using Merge Sort, assign ranks.
    Kept for backward compatibility. Also works with /api/ranking (GET).
    """
    data = request.get_json()

    if not data or 'students' not in data:
        return jsonify({'error': 'Invalid input. Expected {"students": [...]}'}), 400

    students = data['students']
    if not isinstance(students, list) or len(students) == 0:
        return jsonify({'students': [], 'statistics': {'total': 0, 'highest': 0, 'average': 0, 'lowest': 0}}), 200

    # Validate
    for i, s in enumerate(students):
        if not isinstance(s, dict):
            return jsonify({'error': f'Student at index {i} must be an object'}), 400
        if 'roll' not in s or 'name' not in s or 'marks' not in s:
            return jsonify({'error': f'Student at index {i} missing roll, name, or marks'}), 400
        if not isinstance(s['marks'], (int, float)):
            return jsonify({'error': f'Student at index {i} has invalid marks type'}), 400
        if s['marks'] < 0 or s['marks'] > 100:
            return jsonify({'error': f'Student at index {i} has marks outside 0-100'}), 400

    # Run manual Merge Sort
    sorted_students = merge_sort(students)
    ranked_students = generate_ranks(sorted_students)
    stats = calc_stats(students)

    return jsonify({'students': ranked_students, 'statistics': stats}), 200


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """GET /api/statistics - Return database statistics."""
    try:
        students = Student.query.all()
        if not students:
            return jsonify({'total_students': 0, 'highest_marks': 0, 'average_marks': 0, 'lowest_marks': 0}), 200

        marks = [s.marks for s in students]
        return jsonify({
            'total_students': len(students),
            'highest_marks': max(marks),
            'average_marks': round(sum(marks) / len(marks), 2),
            'lowest_marks': min(marks)
        }), 200
    except Exception as e:
        return jsonify({'error': f'Statistics error: {str(e)}'}), 500


@app.route('/api/performance', methods=['POST'])
def performance_test():
    """POST /api/performance - Measure Merge Sort execution time on random datasets.
    
    Input: {"size": 1000}
    Output: {"size": 1000, "execution_time_ms": 1.25}
    
    Generates random records in memory only (not inserted into PostgreSQL).
    Measures only the Merge Sort execution time.
    """
    data = request.get_json()

    if not data or 'size' not in data:
        return jsonify({'error': 'Invalid input. Expected {"size": 1000}'}), 400

    size = data['size']
    if not isinstance(size, int) or size <= 0:
        return jsonify({'error': 'Size must be a positive integer'}), 400

    # Generate random student dataset in memory only
    random.seed(42)
    test_students = []
    for i in range(size):
        test_students.append({
            'roll': 1000 + i,
            'name': f'Student_{i}',
            'marks': random.randint(0, 100)
        })

    # Measure ONLY the Merge Sort execution time
    start_time = time.time()
    sorted_students = merge_sort(test_students)
    end_time = time.time()

    execution_time_ms = round((end_time - start_time) * 1000, 4)

    # Verify sort is correct
    is_sorted = all(sorted_students[i]['marks'] >= sorted_students[i+1]['marks']
                    for i in range(len(sorted_students)-1))

    return jsonify({
        'size': size,
        'execution_time_ms': execution_time_ms,
        'sort_correct': is_sorted
    }), 200


@app.route('/api/sample-data', methods=['POST'])
def generate_sample_data():
    """POST /api/sample-data - Generate sample student data in memory for performance testing."""
    data = request.get_json()
    size = data.get('size', 100) if data else 100

    if not isinstance(size, int) or size <= 0:
        return jsonify({'error': 'Size must be a positive integer'}), 400

    random.seed(42)
    students = []
    for i in range(size):
        students.append({
            'roll': 1000 + i,
            'name': f'Student_{i}',
            'marks': random.randint(0, 100)
        })

    return jsonify({'students': students}), 200


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500


# ==================== RUN ====================

if __name__ == '__main__':
    print("=" * 60)
    print("Student Marks Sorting & Ranking System")
    print("Backend Server Starting...")
    print(f"Database: {DATABASE_URL}")
    print("Algorithm: Merge Sort (Manual Implementation)")
    print("CORS: Enabled")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
