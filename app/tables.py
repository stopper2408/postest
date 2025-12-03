from typing import List
from sqlalchemy import create_engine, String, Integer, Float, ForeignKey, Boolean, Select, delete
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
import json
import os

class Base(DeclarativeBase):
    pass


if os.path.isfile("posTable.db"):
    existsAlready = True
else:
    existsAlready = False


engine = create_engine("sqlite:///posTable.db")

class Table(Base):
    __tablename__ = "tables"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    status: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False) # Status of false is when there is no one at the table, True is when there are people are the table (occupied)
    orders: Mapped[List["Order"]] = relationship(back_populates="table")
    numberOfGuests: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    table_id: Mapped[int] = mapped_column(ForeignKey("tables.id"), nullable=False)
    item_id: Mapped[int] = mapped_column(ForeignKey("menu.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[int] = mapped_column(Integer, nullable=False, default=0) # This is 0 is ordered (dont make yet), 1 is main away (make it), 2 is completed (finished). This will be for all items of food, so if a drink is ordered, it will go straight to 1

    item: Mapped["MenuItems"] = relationship(back_populates="orders") 
    table: Mapped["Table"] = relationship(back_populates="orders")


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
    

if not existsAlready:
    Base.metadata.create_all(engine)