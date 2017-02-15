from sqlalchemy import Column, Integer, String, func
from app import db

class CnesEquipment(db.Model):
    __tablename__ = 'cnes_equipment'
    year          = Column(Integer, primary_key=True)
    region        = Column(String(1), primary_key=True)
    mesoregion    = Column(String(4), primary_key=True)
    microregion   = Column(String(5), primary_key=True)
    state         = Column(String(2), primary_key=True)
    municipality  = Column(String(7), primary_key=True)
    cnes          = Column(String(7), primary_key=True)

    @classmethod    
    def dimensions(cls):
        return [
            'year',
            'region',
            'mesoregion',
            'microregion',
            'state',
            'municipality',
        ]

    @classmethod
    def aggregate(cls, value):
        return {
            'equipments': func.count(cls.cnes)
        }[value]

    @classmethod
    def values(cls):
        return ['equipments']
