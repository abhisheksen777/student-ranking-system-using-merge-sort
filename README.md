# Student Marks Sorting & Ranking System

## Project Description

This is a college Project-Based Learning (PBL) application for **Design and Analysis of Algorithms (DAA)**. It demonstrates the **Merge Sort** algorithm by sorting student records based on marks in descending order, assigning competition ranks, and providing performance analysis.

**Architecture:**
```
Frontend (HTML/CSS/JS)
      ↓
Flask REST API
      ↓
SQLAlchemy ORM
      ↓
PostgreSQL Database

For Ranking:
PostgreSQL → Student Records → Manual Merge Sort → Descending Marks → Rank Generation → Frontend
```

## Problem Statement

Given a list of student records (Roll Number, Name, Marks), sort them in descending order of marks using the **Merge Sort** algorithm and assign ranks. The system should visualize the sorting process, persist data in PostgreSQL, and analyze its performance.

## Objectives

1. Implement Merge Sort manually (without built-in sorting functions)
2. Sort student records by marks in descending order using Merge Sort
3. Assign competition ranks with tie handling
4. Persist student records in PostgreSQL using SQLAlchemy
5. Visualize the Divide and Conquer process of Merge Sort
6. Measure and compare actual execution times
7. Demonstrate theoretical and practical complexity analysis

## Features

- **Dashboard**: View statistics (total, highest, average, lowest marks) from PostgreSQL
- **Student Records**: Add, edit, delete, and clear students with persistent storage
- **PostgreSQL Database**: Persistent storage using SQLAlchemy ORM
- **Sample Data**: Load predefined student records (prevents duplicates)
- **Merge Sort Ranking**: Fetch from DB, sort using manual Merge Sort, generate ranks
- **Tie-Aware Ranking**: Competition ranking (e.g., 91→Rank 2, 91→Rank 2, 85→Rank 4)
- **Step-by-Step Visualization**: See the Divide → Conquer → Combine process
- **Performance Testing**: Measure execution time for datasets of varying sizes
- **Complexity Analysis**: Theoretical comparison with Bubble, Selection, Insertion Sort
- **API Endpoints**: RESTful Flask backend with CORS support
- **Responsive UI**: Mobile-friendly design

## Architecture

### Data Flow

```
Frontend (Browser)
    ↓  HTTP Requests
Flask REST API (localhost:5000)
    ↓  SQLAlchemy ORM
PostgreSQL Database (student_ranking)
    ↓  Fetch records
Manual Merge Sort (Python)
    ↓  Sort by marks descending
Rank Generation (Competition Ranking)
    ↓  JSON Response
Frontend (Display)
```

**Critical Rule:** The ranking is done by **manual Merge Sort in Python**, NOT by SQL `ORDER BY`. PostgreSQL is only responsible for storing and retrieving records.

### File Structure

```
student-ranking-system/
│
├── backend/
│   ├── app.py              (Flask API with all endpoints)
│   ├── merge_sort.py       (Manual Merge Sort + rank generation)
│   ├── models.py           (SQLAlchemy Student model)
│   ├── database.py         (Database connection and initialization)
│   ├── requirements.txt    (Python dependencies)
│   ├── .env                (Database credentials - NOT committed)
│   ├── .env.example        (Example environment variables)
│   ├── .gitignore          (Git ignore rules)
│   └── data/
│       └── students.json   (Sample data backup)
│
├── frontend/
│   ├── index.html          (Main HTML page)
│   ├── style.css           (CSS stylesheet)宣
│   └── script.js           (JavaScript with API calls)
│
├── README.md
└── screenshots/
```

## Technology Stack

- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Backend**: Python Flask
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **CORS**: Flask-CORS
- **Environment**: python-dotenv
- **Algorithm**: Merge Sort (Manual Implementation)
- **Database Driver**: psycopg2-binary

## Database Design

### students table

| Column      | Type              | Constraints              |
|-------------|-------------------|--------------------------|
| id          | INTEGER (SERIAL)  | PRIMARY KEY, AUTO INCREMENT |
| roll_no     | INTEGER           | UNIQUE, NOT NULL         |
| name        | VARCHAR(100)      | NOT NULL                 |
| marks       | FLOAT             | NOT NULL                 |
| created_at  | TIMESTAMP         | DEFAULT CURRENT_TIMESTAMP |

### Validation Rules
- `marks` must be between 0 and 100
- `roll_no` must be unique
- `name` cannot be empty

## PostgreSQL Setup

### Prerequisites
- PostgreSQL 12+ installed and running
- Access to `psql` command-line tool

### Create Database

```sql
-- Connect to PostgreSQL
psql -U postgres -p 5432

-- Create the database
CREATE DATABASE student_ranking;

-- Verify
\l student_ranking
```

### Configure Environment

Create `backend/.env` file:

```env
DATABASE_URL=postgresql://postgres@localhost:5432/student_ranking
```

**Note:** If you need a password, use:
```env
DATABASE_URL=postgresql://USERNAME:PASSWORD@localhost:5432/student_ranking
```

### Trust Authentication (if needed)

If you encounter password authentication errors, edit `pg_hba.conf`:
1. Find `pg_hba.conf` in your PostgreSQL data directory
2. Change `scram-sha-256` or `md5` to `trust` for local connections
3. Restart PostgreSQL service

### Install Database

The application creates tables automatically on startup. Just ensure the database exists.

## How to Install

### Prerequisites
- Python 3.8+
- PostgreSQL
- Node.js (optional, for local HTTP server)

### Steps

```bash
# 1. Navigate to the project directory
cd student-ranking-system

# 2. Create a virtual environment
python -m venv venv

# 3. Activate the virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install Python dependencies
pip install -r backend/requirements.txt

# 5. Ensure PostgreSQL is running
# Create the student_ranking database (see above)

# 6. Run the Flask backend
python backend/app.py
```

### Start Frontend

You have two options:

**Option 1: Using Python HTTP Server**
```bash
cd frontend
python -m http.server 5500
```
Then open `http://127.0.0.1:5500` in your browser.

**Option 2: Using VS Code Live Server**
Right-click `index.html` → "Open with Live Server"

**Option 3: Using any local HTTP server**
Make sure to serve the `frontend/` directory on port 5500 (or update `API_BASE_URL` in `script.js`).

### URLs
- **Backend API**: http://127.0.0.1:5000
- **Frontend**: http://127.0.0.1:5500
- **Health Check**: http://127.0.0.1:5000/api/health

## How to Run

1. Start the backend server:
   ```bash
   python backend/app.py
   ```

2. Start the frontend server:
   ```bash
   cd frontend
   python -m http.server 5500
   ```

3. Open `http://127.0.0.1:5500` in your browser.

4. Use the navigation to:
   - **Dashboard**: View statistics from PostgreSQL
   - **Students**: Add/edit/delete student records (persists in DB)
   - **Ranking**: Generate and view rankings (uses manual Merge Sort)
   - **Visualization**: See Merge Sort step-by-step
   - **Performance**: Run performance benchmarks
   - **Algorithm**: Read about Merge Sort

## API Endpoints

### GET /api/health
Health check - returns database connection status.

**Response:**
```json
{"status": "ok", "database": "connected"}
```

### GET /api/students
Return all students from PostgreSQL.

**Response:**
```json
{"students": [{"id": 1, "roll": 101, "name": "Rahul", "marks": 72, "created_at": "..."}]}
```

### POST /api/students
Add a new student.

**Input:**
```json
{"roll": 106, "name": "Karan", "marks": 88}
```

**Response:**
```json
{"message": "Student added successfully", "student": {...}}
```

### PUT /api/students/<id>
Update a student.

**Input:**
```json
{"roll": 106, "name": "Karan", "marks": 88}
```

### DELETE /api/students/<id>
Delete a student by ID.

### DELETE /api/students
Delete all students.

### GET /api/sample
Load sample students into PostgreSQL. Does not duplicate existing records.

**Response:**
```json
{"message": "Sample data loaded", "added": [101, 102, 103, 104, 105], "skipped": []}
```

### GET /api/ranking
Fetch students from PostgreSQL, sort using manual Merge Sort, generate ranks.

**Important:** Uses manual Merge Sort, NOT SQL `ORDER BY`.

**Response:**
```json
{
    "students": [
        {"rank": 1, "roll": 104, "name": "Neha", "marks": 96},
        {"rank": 2, "roll": 102, "name": "Priya", "marks": 91}
    ],
    "statistics": {"total": 5, "highest": 96, "average": 84.4, "lowest": 72}
}
```

### POST /api/rank
Same as `/api/ranking` but accepts inline student data. Kept for backward compatibility.

### GET /api/statistics
Return database statistics.

**Response:**
```json
{"total_students": 5, "highest_marks": 96, "average_marks": 84.4, "lowest_marks": 72}
```

### POST /api/performance
Measure Merge Sort execution time on random datasets.

**Input:**
```json
{"size": 1000}
```

**Response:**
```json
{"size": 1000, "execution_time_ms": 1.25, "sort_correct": true}
```

**Note:** Random records are generated in memory only. They are NOT inserted into PostgreSQL. This ensures the benchmark measures only Merge Sort, not database operations.

## Merge Sort Explanation

Merge Sort is a **Divide and Conquer** algorithm with three stages:

### 1. DIVIDE
Split the student records into two halves recursively until each sublist has one element.

### 2. CONQUER
Recursively sort each half. A single element is already sorted by definition.

### 3. COMBINE
Merge the sorted halves back together by comparing marks. Larger marks come first (descending order).

### Pseudocode

```
MERGE_SORT(A, low, high)

IF low < high
    mid = (low + high) / 2
    MERGE_SORT(A, low, mid)
    MERGE_SORT(A, mid + 1, high)
    MERGE(A, low, mid, high)
END IF

MERGE(A, low, mid, high)
    Create left = A[low..mid]
    Create right = A[mid+1..high]
    i = 0, j = 0, k = low
    WHILE i < len(left) AND j < len(right)
        IF left[i].marks >= right[j].marks
            A[k] = left[i]
            i = i + 1
        ELSE
            A[k] = right[j]
            j = j + 1
        k = k + 1
    END WHILE
    Copy remaining elements
```

## Complexity Analysis

| Case | Time Complexity |
|------|----------------|
| Best Case | O(n log n) |
| Average Case | O(n log n) |
| Worst Case | O(n log n) |
| Auxiliary Space | O(n) |

**Explanation**: There are O(log n) levels of recursion. Each level performs O(n) merge work. Therefore: O(n) × O(log n) = O(n log n).

### Comparison with Other Sorting Algorithms

| Algorithm | Best | Average | Worst | Space |
|-----------|------|---------|-------|-------|
| Bubble Sort | O(n²) | O(n²) | O(n²) | O(1) |
| Selection Sort | O(n²) | O(n²) | O(n²) | O(1) |
| Insertion Sort | O(n) | O(n²) | O(n²) | O(1) |
| **Merge Sort** | **O(n log n)** | **O(n log n)** | **O(n log n)** | **O(n)** |

## Sample Input/Output

### Input Students:
| Roll No. | Student | Marks |
|----------|---------|-------|
| 101 | Rahul | 72 |
| 102 | Priya | 91 |
| 103 | Aman | 85 |
| 104 | Neha | 96 |
| 105 | Riya | 78 |

### Expected Ranking (After Manual Merge Sort):
| Rank | Roll No. | Student | Marks |
|------|----------|---------|-------|
| 1 | 104 | Neha | 96 |
| 2 | 102 | Priya | 91 |
| 3 | 103 | Aman | 85 |
| 4 | 105 | Riya | 78 |
| 5 | 101 | Rahul | 72 |

### Tie Example:
If marks are [96, 91, 91, 85]:
| Rank | Marks | Student |
|------|-------|---------|
| 1 | 96 | A |
| 2 | 91 | B |
| 2 | 91 | C |
| 4 | 85 | D |

## Performance Testing Results

Run the Performance section to see actual measured execution times. Results vary by hardware.

**Note:** Performance tests generate random records in memory only. They do NOT insert into PostgreSQL, ensuring the benchmark measures only Merge Sort execution time, not database operations.

## Future Scope

- Add database integration with migrations
- Implement additional sorting algorithms for comparison
- Add user authentication
- Export rankings as PDF/Excel
- Add more visualization algorithms
- Real-time collaborative editing

## PBL Review Topics

1. **Methodology & Implementation**: Merge Sort algorithm, manual implementation, Flask REST API, PostgreSQL
2. **Dataset & Preprocessing**: Student records with validation, normalization in database
3. **Results & Output Analysis**: Before-sorting and after-sorting tables, rank generation
4. **Performance Evaluation**: Theoretical O(n log n) and actual measured times
5. **Project Demonstration**: Complete workflow: Add Students → Validate → Merge Sort → Rank → Display

## Important Notes

### Why Manual Merge Sort?
This project demonstrates the **Merge Sort** algorithm for DAA. Using SQL `ORDER BY` or Python's built-in `sorted()` would defeat the purpose. The ranking is always done by the manually implemented `merge_sort()` function in `backend/merge_sort.py`.

### Why In-Memory for Performance Tests?
Performance tests generate random student records in Python memory. This ensures the measured execution time reflects **only the Merge Sort algorithm**, not database I/O operations. The results are real and accurately measured.

### Database Connection
The application expects PostgreSQL to be running at `localhost:5432` with the `student_ranking` database. The connection status is visible on the Dashboard and Health Check endpoints.

## License

This project is for educational purposes.
