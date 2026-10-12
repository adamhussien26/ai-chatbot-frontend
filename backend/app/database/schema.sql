-- ============================================================================
-- schema.sql — مخطط قاعدة بيانات MySQL الكامل (utf8mb4)
-- جامعة العلوم والتقانة — نظام المساعد الذكي
-- الاستخدام: mysql -u root -p < schema.sql
-- ============================================================================

CREATE DATABASE IF NOT EXISTS ust_chatbot
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ust_chatbot;

-- ---------------------------------------------------------------------------
-- 1) users — حسابات الدخول (طالب / أدمن)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  email         VARCHAR(190) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  full_name     VARCHAR(190) NOT NULL,
  role          ENUM('student','admin') NOT NULL DEFAULT 'student',
  is_active     BOOLEAN NOT NULL DEFAULT TRUE,
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 2) faculties — الكليات
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS faculties (
  id   INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(190) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 3) departments — الأقسام (تابعة لكلية)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS departments (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  name       VARCHAR(190) NOT NULL,
  faculty_id INT NOT NULL,
  CONSTRAINT fk_dept_faculty FOREIGN KEY (faculty_id) REFERENCES faculties(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 4) students — بيانات الطلاب (مرتبطة 1:1 بـ users)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS students (
  id             INT AUTO_INCREMENT PRIMARY KEY,
  user_id        INT NOT NULL UNIQUE,
  university_id  VARCHAR(20) NOT NULL UNIQUE,
  faculty_id     INT NULL,
  department_id  INT NULL,
  level          INT NULL,
  phone          VARCHAR(30) NULL,
  avatar_url     VARCHAR(500) NULL,
  enrollment_year INT NULL,
  CONSTRAINT fk_stu_user      FOREIGN KEY (user_id)      REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_stu_faculty   FOREIGN KEY (faculty_id)   REFERENCES faculties(id) ON DELETE SET NULL,
  CONSTRAINT fk_stu_dept      FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 5) courses — المقررات
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS courses (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  code         VARCHAR(20) NOT NULL UNIQUE,
  name         VARCHAR(190) NOT NULL,
  credit_hours INT NOT NULL DEFAULT 3,
  description  TEXT NULL,
  department_id INT NULL,
  CONSTRAINT fk_course_dept FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 6) enrollments — تسجيل الطالب في مقرر بفصل معين
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS enrollments (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  course_id  INT NOT NULL,
  semester   VARCHAR(30) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_enrollment (student_id, course_id, semester),
  CONSTRAINT fk_enr_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
  CONSTRAINT fk_enr_course  FOREIGN KEY (course_id)  REFERENCES courses(id)  ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 7) results — النتائج والدرجات
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS results (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  course_id  INT NOT NULL,
  semester   VARCHAR(30) NOT NULL,
  midterm    DECIMAL(5,2) NULL,
  final_exam DECIMAL(5,2) NULL,
  practical  DECIMAL(5,2) NULL,
  total      DECIMAL(5,2) NOT NULL,
  grade      VARCHAR(5) NOT NULL,
  gpa_points DECIMAL(3,2) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_result (student_id, course_id, semester),
  CONSTRAINT fk_res_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
  CONSTRAINT fk_res_course  FOREIGN KEY (course_id)  REFERENCES courses(id)  ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 8) schedules — جدول المحاضرات (student_id NULL = يخص جميع مسجلي المقرر)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS schedules (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  student_id  INT NULL,
  course_id   INT NOT NULL,
  day_of_week TINYINT NOT NULL,           -- 0=الأحد .. 6=السبت
  start_time  TIME NOT NULL,
  end_time    TIME NOT NULL,
  room        VARCHAR(60) NULL,
  lecturer    VARCHAR(190) NULL,
  semester    VARCHAR(30) NOT NULL,
  CONSTRAINT fk_sch_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
  CONSTRAINT fk_sch_course  FOREIGN KEY (course_id)  REFERENCES courses(id)  ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 9) exams — الامتحانات
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS exams (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  course_id  INT NOT NULL,
  title      VARCHAR(190) NOT NULL,
  exam_date  DATE NOT NULL,
  start_time TIME NOT NULL,
  end_time   TIME NOT NULL,
  room       VARCHAR(60) NULL,
  semester   VARCHAR(30) NOT NULL,
  CONSTRAINT fk_exam_course FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 10) notifications — الإشعارات (user_id NULL = إشعار عام للجميع)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS notifications (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  user_id    INT NULL,
  title      VARCHAR(190) NOT NULL,
  body       TEXT NOT NULL,
  is_read    BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_notif_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 11) chat_history — سجل المحادثات (user_id, question, answer, timestamp, source)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS chat_history (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  user_id    INT NOT NULL,
  question   TEXT NOT NULL,
  answer     TEXT NOT NULL,
  source     VARCHAR(20) NOT NULL DEFAULT 'llm',   -- database / rag / llm
  source_ref VARCHAR(255) NULL,                    -- اسم المستند أو اسم الجدول/المقرر
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_chat_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;
CREATE INDEX IF NOT EXISTS idx_chat_user ON chat_history (user_id, created_at);

-- ---------------------------------------------------------------------------
-- 12) knowledge_documents — مستندات قاعدة المعرفة
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS knowledge_documents (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  title       VARCHAR(255) NOT NULL,
  filename    VARCHAR(255) NOT NULL,
  doc_type    VARCHAR(10) NOT NULL,               -- pdf / docx / txt
  size_bytes  INT NOT NULL DEFAULT 0,
  chunk_count INT NOT NULL DEFAULT 0,
  is_active   BOOLEAN NOT NULL DEFAULT TRUE,
  uploaded_by INT NULL,
  created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT kb_doc_user FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 13) knowledge_chunks — مقاطع المستندات + Embeddings (JSON)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS knowledge_chunks (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  document_id INT NOT NULL,
  chunk_index INT NOT NULL,
  content     TEXT NOT NULL,
  embedding   TEXT NOT NULL,                      -- JSON array
  created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_chunk_doc FOREIGN KEY (document_id) REFERENCES knowledge_documents(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 14) otp_codes — رموز التحقق OTP (مجزأة hash وليست نصًا صريحًا)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS otp_codes (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  user_id    INT NOT NULL,
  code_hash  VARCHAR(255) NOT NULL,
  purpose    VARCHAR(30) NOT NULL DEFAULT 'password_reset',
  is_used    BOOLEAN NOT NULL DEFAULT FALSE,
  expires_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_otp_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;
