from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(String, primary_key=True)
    account_id = Column(String, index=True)
    reference = Column(String)
    amount_cents = Column(Integer)
    due_date = Column(Date)
    status = Column(String, default="open")


class BankLine(Base):
    __tablename__ = "bank_lines"
    id = Column(String, primary_key=True)
    account_id = Column(String, index=True)
    description = Column(String)
    amount_cents = Column(Integer)
    booked_on = Column(Date)
    matched_invoice_id = Column(String, ForeignKey("invoices.id"), nullable=True)
