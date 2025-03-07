from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey, Text, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# Users Table
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    email_id = Column(String(255), unique=True, nullable=False)
    phone_no = Column(String(255), nullable=True)
    role = Column(String(255), nullable=False)

    # Relationships
    garages = relationship("Garage", back_populates="owner")

# Garages Table
class Garage(Base):
    __tablename__ = "garages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    garage_name = Column(String(255), nullable=False)
    garage_address = Column(String(255), nullable=False)
    garage_city = Column(String(255), nullable=False)
    garage_state = Column(String(255), nullable=False)
    country = Column(String(255), nullable=False)
    zip_code = Column(Integer, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    owner = relationship("User", back_populates="garages")
    services = relationship("GarageService", back_populates="garage")

# Services Table
class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, autoincrement=True)
    service_name = Column(String(255), nullable=False)
    service_charges = Column(DECIMAL(10, 2), nullable=False)
    service_description = Column(Text, nullable=True)

    # Relationships
    garages = relationship("GarageService", back_populates="service")

# Customer Vehicle Info Table
class CustomerVehicleInfo(Base):
    __tablename__ = "customer_vehicle_info"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vehicle_id = Column(String(255), unique=True, nullable=False)  # ✅ Ensuring UNIQUE vehicle ID

    # Relationships
    user = relationship("User", back_populates="vehicles")
    service_summaries = relationship("VehicleServiceSummary", back_populates="vehicle")

User.vehicles = relationship("CustomerVehicleInfo", back_populates="user")

# Vehicle Service Summary Table
class VehicleServiceSummary(Base):
    __tablename__ = "vehicle_service_summary"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(String(255), ForeignKey("customer_vehicle_info.vehicle_id"), nullable=False)  # ✅ References UNIQUE vehicle ID
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    garage_id = Column(Integer, ForeignKey("garages.id"), nullable=False)
    total_amount = Column(DECIMAL(10, 2), nullable=True)
    total_tax = Column(DECIMAL(10, 2), nullable=True)
    service_date = Column(Date, nullable=True)
    service_details = Column(Text, nullable=True)

    # Relationships
    vehicle = relationship("CustomerVehicleInfo", back_populates="service_summaries")
    service = relationship("Service")
    garage = relationship("Garage")

# Garage Services (Many-to-Many Relationship)
class GarageService(Base):
    __tablename__ = "garage_services"

    garage_id = Column(Integer, ForeignKey("garages.id"), primary_key=True, nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), primary_key=True, nullable=False)

    # Relationships
    garage = relationship("Garage", back_populates="services")
    service = relationship("Service", back_populates="garages")
