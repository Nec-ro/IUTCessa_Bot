from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    BigInteger, Integer, SmallInteger, Numeric, Text, Boolean,
    UniqueConstraint, CheckConstraint, ForeignKey, Enum, TIMESTAMP
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import CITEXT  # needs the extension already there

# Map to existing Postgres ENUM "season_enum"
import enum
class SeasonEnum(str, enum.Enum):
    spring = "spring"
    summer = "summer"
    fall   = "fall"

class Base(DeclarativeBase):
    pass

# ---------- Core tables ----------
class User(Base):
    __tablename__ = "users"
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_telegram_id: Mapped[Optional[int]] = mapped_column(BigInteger, unique=True)

    assessments: Mapped[List["InstructorAssessment"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

class Department(Base):
    __tablename__ = "department"
    dept_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    dept_name: Mapped[str] = mapped_column(Text, unique=True)

    instructors: Mapped[List["Instructor"]] = relationship(back_populates="department")

class Instructor(Base):
    __tablename__ = "instructor"
    instructor_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    dept_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("department.dept_id", onupdate="CASCADE", ondelete="RESTRICT"), index=True
    )
    email: Mapped[str] = mapped_column(CITEXT, unique=True)

    department: Mapped[Department] = relationship(back_populates="instructors")
    available_courses: Mapped[List["AvailableCourse"]] = relationship(back_populates="instructor")

class Course(Base):
    __tablename__ = "course"
    course_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    course_name: Mapped[str] = mapped_column(Text, unique=True)

    available_courses: Mapped[List["AvailableCourse"]] = relationship(back_populates="course")

class Semester(Base):
    __tablename__ = "semester"
    semester_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    year: Mapped[int] = mapped_column("year", Integer)
    season: Mapped[SeasonEnum] = mapped_column(
        Enum(SeasonEnum, name="season_enum", native_enum=True)
    )
    __table_args__ = (
        UniqueConstraint("year", "season", name="uq_semester_year_season"),
        CheckConstraint(' "year" BETWEEN 1390 AND EXTRACT(YEAR FROM now())::int ', name="ck_semester_year_range"),
    )

    available_courses: Mapped[List["AvailableCourse"]] = relationship(back_populates="semester")

class AvailableCourse(Base):
    __tablename__ = "available_course"
    ac_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    instructor_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("instructor.instructor_id", onupdate="CASCADE", ondelete="RESTRICT"), index=True
    )
    semester_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("semester.semester_id", onupdate="CASCADE", ondelete="RESTRICT"), index=True
    )
    course_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("course.course_id", onupdate="CASCADE", ondelete="RESTRICT"), index=True
    )
    __table_args__ = (
        UniqueConstraint("instructor_id", "semester_id", "course_id", name="uq_available_course"),
    )

    instructor: Mapped[Instructor] = relationship(back_populates="available_courses")
    semester: Mapped[Semester] = relationship(back_populates="available_courses")
    course: Mapped[Course] = relationship(back_populates="available_courses")
    assessments: Mapped[List["InstructorAssessment"]] = relationship(back_populates="available_course", cascade="all, delete-orphan")

# ---------- Assessments ----------
class InstructorAssessment(Base):
    __tablename__ = "instructor_assessment"
    assessment_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.user_id", onupdate="CASCADE", ondelete="RESTRICT"), index=True
    )
    available_course_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("available_course.ac_id", onupdate="CASCADE", ondelete="CASCADE"), index=True
    )

    instructor_presence_importance: Mapped[Optional[int]] = mapped_column(SmallInteger)
    instructor_course_scoring: Mapped[Optional[int]] = mapped_column(SmallInteger)
    instructor_resource_completeness: Mapped[Optional[int]] = mapped_column(SmallInteger)
    instructor_knowledge: Mapped[Optional[int]] = mapped_column(SmallInteger)
    instructor_teaching_skill: Mapped[Optional[int]] = mapped_column(SmallInteger)
    instructor_class_time_management: Mapped[Optional[int]] = mapped_column(SmallInteger)
    instructor_answering: Mapped[Optional[int]] = mapped_column(SmallInteger)
    instructor_politeness: Mapped[Optional[int]] = mapped_column(SmallInteger)

    instructor_overall: Mapped[Optional[int]] = mapped_column(SmallInteger)
    course_content_worth: Mapped[Optional[int]] = mapped_column(SmallInteger)

    student_final_score: Mapped[Optional[float]] = mapped_column(Numeric(4, 2))
    student_class_presence: Mapped[Optional[int]] = mapped_column(SmallInteger)
    student_assessment: Mapped[Optional[str]] = mapped_column(Text)
    student_allow_show_id: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))

    __table_args__ = (
        UniqueConstraint("user_id", "available_course_id", name="uq_assessment_once_per_course"),
        CheckConstraint("(student_final_score IS NULL) OR (student_final_score >= 0.00 AND student_final_score <= 20.00)", name="ck_student_final_score_range"),
    )

    user: Mapped[User] = relationship(back_populates="assessments")
    available_course: Mapped[AvailableCourse] = relationship(back_populates="assessments")