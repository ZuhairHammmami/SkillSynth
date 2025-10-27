# models.py

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import relationship
from database import Base # نستورد Base من ملف database.py

# جدول المستخدمين
class Profile(Base):
    __tablename__ = "profiles" # اسم الجدول في قاعدة البيانات

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)

    # هذه هي العلاقة: "المستخدم الواحد له عدة مسارات"
    # back_populates يربطها بالعلاقة في جدول Path
    paths = relationship("Path", back_populates="owner")

# جدول المسارات
class Path(Base):
    __tablename__ = "paths"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text, nullable=True)
    profile_id = Column(Integer, ForeignKey("profiles.id")) # مفتاح أجنبي

    # علاقة عكسية مع جدول Profile
    owner = relationship("Profile", back_populates="paths")
    # علاقة مع جدول الخطوات
    steps = relationship("PathStep", back_populates="path", cascade="all, delete-orphan")

# جدول الخطوات
class PathStep(Base):
    __tablename__ = "path_steps"

    id = Column(Integer, primary_key=True, index=True)
    step_number = Column(Integer, nullable=False)
    title = Column(String)
    content = Column(Text)
    path_id = Column(Integer, ForeignKey("paths.id"))

    path = relationship("Path", back_populates="steps")