from typing import List
from sqlalchemy import create_engine, String, Integer, Float, ForeignKey, Boolean, Select, delete, DateTime, Index, event
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from datetime import datetime
import json
import os

class Base(DeclarativeBase):
    pass


if os.path.isfile("posTable.db"):
    existsAlready = True
else:
    existsAlready = False


# Enable WAL mode for better concurrent read/write performance
engine = create_engine(
    "sqlite:///posTable.db",
    connect_args={"check_same_thread": False},
    pool_pre_ping=True
)

# Enable WAL mode on connection
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()

class Table(Base):
    __tablename__ = "tables"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    status: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False) # Status of false is when there is no one at the table, True is when there are people are the table (occupied)
    orders: Mapped[List["Order"]] = relationship(back_populates="table")
    numberOfGuests: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    table_id: Mapped[int] = mapped_column(ForeignKey("tables.id"), nullable=False, index=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("menu.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[int] = mapped_column(Integer, nullable=False, default=0, index=True) # This is 0 is ordered (dont make yet), 1 is main away (make it), 2 is completed (finished). This will be for all items of food, so if a drink is ordered, it will go straight to 1
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    seat_number: Mapped[int] = mapped_column(Integer, nullable=True)  # For seat assignment feature
    voided: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)  # For voiding orders

    item: Mapped["MenuItems"] = relationship(back_populates="orders") 
    table: Mapped["Table"] = relationship(back_populates="orders")
    
    __table_args__ = (
        Index('idx_table_status', 'table_id', 'status'),
        Index('idx_created_status', 'created_at', 'status'),
    )


class MenuItems(Base):
    __tablename__ = "menu"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    subcategory: Mapped[str] = mapped_column(String, nullable=True)
    needToBeMainAway: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False) # This is for the items that should and shouldnt be main awayed
    place_to_go: Mapped[str] = mapped_column(String, nullable=False) # this is to tell logic where to place items (ie kitchen or bar)

    orders: Mapped[List["Order"]] = relationship(back_populates="item")


class Settings(Base):
    __tablename__ = "settings"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    value: Mapped[str] = mapped_column(String, nullable=False)


class Receipt(Base):
    __tablename__ = "receipts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    table_id: Mapped[int] = mapped_column(Integer, nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    receipt_data: Mapped[str] = mapped_column(String, nullable=False)  # JSON string of order details
    

if not existsAlready:
    Base.metadata.create_all(engine)