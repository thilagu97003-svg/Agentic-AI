from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True)
    user_name = Column(String(100), default="guest")
    title = Column(String(255))
    category = Column(String(50))      # network / software / access / hardware / other
    priority = Column(String(20))      # low / medium / high / critical
    status = Column(String(20), default="open")  # open / resolved / escalated
    resolution = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = relationship("Message", back_populates="incident")
    actions = relationship("ActionLog", back_populates="incident")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"))
    role = Column(String(20))          # user / assistant
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    incident = relationship("Incident", back_populates="messages")


class ActionLog(Base):
    __tablename__ = "action_logs"

    id = Column(Integer, primary_key=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"))
    tool_name = Column(String(100))
    tool_input = Column(Text)
    tool_output = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    incident = relationship("Incident", back_populates="actions")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)