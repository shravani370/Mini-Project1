import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime

class Database:
    def __init__(self):
        self.connection = None
        self.fallback_data = {
            'students': [
                {"id": 1, "name": "Shravani", "year": 3, "cgpa": 8.5, "total_score": 80, "interview_date": "2026-01-19", "interest": "AI", "email": "shravani@student.edu", "skills": "Python, AI, ML"},
                {"id": 2, "name": "Rahul", "year": 2, "cgpa": 7.8, "total_score": 70, "interview_date": "2026-01-18", "interest": "Web", "email": "rahul@student.edu", "skills": "JavaScript, React, Node"},
                {"id": 3, "name": "Priya", "year": 4, "cgpa": 9.0, "total_score": 95, "interview_date": "2026-01-17", "interest": "AI", "email": "priya@student.edu", "skills": "Python, TensorFlow, Docker"},
                {"id": 4, "name": "Amit", "year": 3, "cgpa": 8.2, "total_score": 75, "interview_date": "2026-01-16", "interest": "Backend", "email": "amit@student.edu", "skills": "Java, Spring, SQL"},
                {"id": 5, "name": "Sneha", "year": 2, "cgpa": 8.8, "total_score": 85, "interview_date": "2026-01-15", "interest": "Cloud", "email": "sneha@student.edu", "skills": "Python, Django, AWS"},
                {"id": 6, "name": "Vikram", "year": 4, "cgpa": 7.5, "total_score": 68, "interview_date": "2026-01-14", "interest": "SDE", "email": "vikram@student.edu", "skills": "C++, Data Structures, Algorithms"},
            ],
            'recruiters': [
                {"id": 1, "company": "Google", "recruiter_name": "Sundar P", "email": "sundar@google.com", "skills": "AI, Python"},
                {"id": 2, "company": "Microsoft", "recruiter_name": "Satya N", "email": "satya@microsoft.com", "skills": "Cloud, .NET"},
                {"id": 3, "company": "Amazon", "recruiter_name": "Andy J", "email": "andy@amazon.com", "skills": "AWS, Java"},
                {"id": 4, "company": "Meta", "recruiter_name": "Mark Z", "email": "mark@meta.com", "skills": "React, Python"},
            ]
        }
        self.connect()

    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', 'Shravani@2006'),
                database=os.getenv('DB_NAME', 'ai_training_platform'),
                port=int(os.getenv('DB_PORT', 3306))
            )
            if self.connection.is_connected():
                print("✅ Connected to MySQL database")
        except Error as e:
            print(f"⚠️ MySQL not available, using fallback data: {e}")
            self.connection = None

    def create_tables(self):
        """Create necessary tables if they don't exist"""
        if not self.connection:
            return False

        cursor = self.connection.cursor()

        # Students table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                year INT NOT NULL,
                cgpa DECIMAL(3,2) NOT NULL,
                skills TEXT,
                interest VARCHAR(100),
                email VARCHAR(150),
                total_score INT DEFAULT 0,
                interview_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Recruiters table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recruiters (
                id INT AUTO_INCREMENT PRIMARY KEY,
                company VARCHAR(100) NOT NULL,
                recruiter_name VARCHAR(100) NOT NULL,
                email VARCHAR(150) UNIQUE NOT NULL,
                skills TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Placement data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS placement_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT,
                company VARCHAR(100),
                role VARCHAR(100),
                salary DECIMAL(10,2),
                placement_date DATE,
                status ENUM('placed', 'pending', 'rejected') DEFAULT 'pending',
                FOREIGN KEY (student_id) REFERENCES students(id)
            )
        """)

        # Interview sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interview_sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT,
                questions TEXT,
                answers TEXT,
                score INT,
                feedback TEXT,
                session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id)
            )
        """)

        self.connection.commit()
        cursor.close()
        print("✅ Database tables created successfully")
        return True

    def get_students(self):
        """Get all students from database"""
        print("🔍 get_students called - fetching from database")
        
        if not self.connection:
            print("❌ Database connection is None, cannot fetch students")
            return []

        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM students ORDER BY created_at DESC")
            students = cursor.fetchall()
            cursor.close()
            
            print(f"✅ Retrieved {len(students)} students from database")
            
            # Debug: Print first student if exists
            if students:
                print(f"   First student: {students[0]['name']} (ID: {students[0]['id']})")
            
            return students
            
        except Error as e:
            print(f"❌ Error fetching students: {e}")
            return []
        except Exception as e:
            print(f"❌ Unexpected error fetching students: {e}")
            return []

    def get_recruiters(self):
        """Get all recruiters from database"""
        print("🔍 get_recruiters called - fetching from database")
        
        if not self.connection:
            print("❌ Database connection is None, cannot fetch recruiters")
            return []

        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM recruiters ORDER BY created_at DESC")
            recruiters = cursor.fetchall()
            cursor.close()
            
            print(f"✅ Retrieved {len(recruiters)} recruiters from database")
            return recruiters
            
        except Error as e:
            print(f"❌ Error fetching recruiters: {e}")
            return []
        except Exception as e:
            print(f"❌ Unexpected error fetching recruiters: {e}")
            return []

    def add_student(self, name, year, cgpa, skills, interest, email=None):
        """Add a new student to the database"""
        print(f"🔍 add_student called: name={name}, year={year}, cgpa={cgpa}, email={email}")
        
        if not self.connection:
            print("❌ ERROR: Database connection is None!")
            print("   Attempting to reconnect...")
            self.connect()  # Try to reconnect
            if not self.connection:
                print("❌ Failed to reconnect to database")
                return False

        try:
            cursor = self.connection.cursor()
            print("   Executing INSERT query...")
            cursor.execute("""
                INSERT INTO students (name, year, cgpa, skills, interest, email)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, year, cgpa, skills, interest, email))
            
            # CRITICAL: Commit the transaction
            self.connection.commit()
            print(f"   ✅ INSERT committed successfully")
            print(f"   📝 Inserted student ID: {cursor.lastrowid}")
            
            # Verify the insertion
            cursor.execute("SELECT * FROM students WHERE id = %s", (cursor.lastrowid,))
            inserted = cursor.fetchone()
            if inserted:
                print(f"   ✅ VERIFIED: Student {cursor.lastrowid} exists in database")
            else:
                print(f"   ⚠️ WARNING: Student {cursor.lastrowid} not found after insert!")
            
            cursor.close()
            return True
            
        except Error as e:
            print(f"❌ MySQL Error saving student: {e}")
            print(f"   Error Code: {e.errno}")
            print(f"   SQL State: {e.sqlstate}")
            # Try to rollback if connection is still active
            if self.connection and self.connection.is_connected():
                try:
                    self.connection.rollback()
                    print("   🔄 Rolled back transaction")
                except:
                    print("   ❌ Could not rollback")
            return False
        except Exception as e:
            print(f"❌ Unexpected error saving student: {e}")
            return False

    def add_recruiter(self, company, recruiter_name, email, skills=None):
        """Add a new recruiter to the database"""
        print(f"🔍 add_recruiter called: company={company}, recruiter_name={recruiter_name}, email={email}")
        
        if not self.connection:
            print("❌ ERROR: Database connection is None!")
            print("   Attempting to reconnect...")
            self.connect()  # Try to reconnect
            if not self.connection:
                print("❌ Failed to reconnect to database")
                return False

        try:
            cursor = self.connection.cursor()
            print("   Executing INSERT query...")
            cursor.execute("""
                INSERT INTO recruiters (company, recruiter_name, email, skills)
                VALUES (%s, %s, %s, %s)
            """, (company, recruiter_name, email, skills))
            
            # CRITICAL: Commit the transaction
            self.connection.commit()
            print(f"   ✅ INSERT committed successfully")
            print(f"   📝 Inserted recruiter ID: {cursor.lastrowid}")
            
            # Verify the insertion
            cursor.execute("SELECT * FROM recruiters WHERE id = %s", (cursor.lastrowid,))
            inserted = cursor.fetchone()
            if inserted:
                print(f"   ✅ VERIFIED: Recruiter {cursor.lastrowid} exists in database")
            else:
                print(f"   ⚠️ WARNING: Recruiter {cursor.lastrowid} not found after insert!")
            
            cursor.close()
            return True
            
        except Error as e:
            print(f"❌ MySQL Error saving recruiter: {e}")
            print(f"   Error Code: {e.errno}")
            print(f"   SQL State: {e.sqlstate}")
            # Try to rollback if connection is still active
            if self.connection and self.connection.is_connected():
                try:
                    self.connection.rollback()
                    print("   🔄 Rolled back transaction")
                except:
                    print("   ❌ Could not rollback")
            return False
        except Exception as e:
            print(f"❌ Unexpected error saving recruiter: {e}")
            return False

    def update_student_score(self, student_id, score):
        """Update student interview score"""
        if not self.connection:
            return False

        cursor = self.connection.cursor()
        cursor.execute("""
            UPDATE students SET total_score = %s WHERE id = %s
        """, (score, student_id))
        self.connection.commit()
        cursor.close()
        return True

    def close(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✅ Database connection closed")

# Global database instance
db = Database()
