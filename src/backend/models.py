from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    paths = relationship("Path", back_populates="owner")

class Path(Base):
    __tablename__ = "paths"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text, nullable=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    owner = relationship("Profile", back_populates="paths")
    steps = relationship("PathStep", back_populates="path", cascade="all, delete-orphan")

class PathStep(Base):
    __tablename__ = "path_steps"
    id = Column(Integer, primary_key=True, index=True)
    step_number = Column(Integer, nullable=False)
    title = Column(String)
    content = Column(Text, nullable=True)
    path_id = Column(Integer, ForeignKey("paths.id"))
    path = relationship("Path", back_populates="steps")
