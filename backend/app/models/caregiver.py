# SwasthyaAI Caregiver Database Model

from sqlalchemy import Column, String, Boolean, Float, JSON, Integer
from app.db import Base


class CaregiverModel(Base):
    __tablename__ = "caregivers"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    qualification_verified = Column(Boolean, default=False, nullable=False)
    skills = Column(JSON, default=list, nullable=False)  # list of skill strings
    service_areas = Column(JSON, default=list, nullable=False)  # list of area strings
    languages = Column(JSON, default=list, nullable=False)  # list of language codes
    rating = Column(Float, default=0.0, nullable=False)
    availability = Column(JSON, default=list, nullable=False)  # list of availability windows
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)