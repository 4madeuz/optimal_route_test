from sqlalchemy import (Column, Float, ForeignKey, Integer, Table,
                        UniqueConstraint)
from sqlalchemy.orm import relationship

from src.db.postgres import Base

route_point_association = Table(
    'route_point_association',
    Base.metadata,
    Column('route_id', Integer, ForeignKey('routes.id')),
    Column('point_id', Integer, ForeignKey('points.id'))
)


class Point(Base):
    __tablename__ = 'points'

    id = Column(Integer, primary_key=True, index=True)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    routes = relationship('Route', secondary=route_point_association, back_populates='points')

    __table_args__ = (
        UniqueConstraint('lat', 'lng', name='uq_lat_lng'),
    )


class Route(Base):
    __tablename__ = 'routes'

    id = Column(Integer, primary_key=True, index=True)
    points = relationship('Point', secondary=route_point_association, back_populates='routes')
