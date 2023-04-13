from typing import List
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
        pass


class Gare(Base):
    __tablename__ = "Gare"
    nom_gare: Mapped[str] = mapped_column(String(30),  primary_key=True)
    longitude: Mapped[float] = mapped_column(nullable=True)
    latitude: Mapped[float] = mapped_column( nullable=True)
    lostitems: Mapped[List["LostItem"]] = relationship(back_populates="gare")
    freq_2019 : Mapped[int] = mapped_column(nullable=True)
    freq_2020 : Mapped[int] = mapped_column(nullable=True)
    freq_2021 : Mapped[int] = mapped_column(nullable=True)

class Temperature(Base):
    __tablename__ = "Temperature"
    
    date: Mapped[str] = mapped_column(String(30),  primary_key=True)
    temperature: Mapped[float] = mapped_column(nullable=True)
    lostitems: Mapped[List["LostItem"]] = relationship(back_populates="date_join")


class LostItem(Base):
    __tablename__ = "LostItem"

    id : Mapped[int] = mapped_column(primary_key=True)
    date : Mapped[str] = mapped_column(ForeignKey(Temperature.date),  nullable=False)
    type_objet : Mapped[str] = mapped_column(String(30),  nullable=False)
    nom_gare : Mapped[str] = mapped_column(ForeignKey(Gare.nom_gare),  nullable=False)
    date_restitution: Mapped[str] = mapped_column(String(30),  nullable=True)
    gare: Mapped["Gare"] = relationship(back_populates="lostitems")
    date_join: Mapped["Temperature"] = relationship(back_populates="lostitems")


def create_tables(engine):

    Base.metadata.create_all(engine)
    

if __name__ == "__main__":
    engine = create_engine('sqlite:///db.sqlite')
    create_tables(engine)