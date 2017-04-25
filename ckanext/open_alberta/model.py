import logging
from ckan.model.domain_object import DomainObject
from ckan.model import meta
from ckan import model
from sqlalchemy import Column, ForeignKey, Table, types
import datetime


log = logging.getLogger(__name__)

pages_table = Table(
    'page',
    meta.metadata,
    Column('content_type', types.Unicode(20), index=True),
    Column('node_id', types.Integer, primary_key=True),
    Column('created_date', types.DateTime, default=datetime.datetime.utcnow),
    Column('modified_date', types.DateTime, default=datetime.datetime.utcnow),
    Column('author_userid', types.Unicode(100), 
           ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'),
           nullable=False),
    Column('updated_by', types.Unicode(100), ForeignKey('user.id', onupdate='CASCADE'),
           nullable=False),
    Column('excerpt', types.Unicode(2000)),
    Column('content', types.UnicodeText)
)

def setup():
    if not pages_table.exists():
        pages_table.create()
        logging.info('ckanext-open_alberta: created page table')


class Pages(DomainObject):
    @classmethod
    def create(cls, session, **kwargs):
        obj = cls(**kwargs)
        session.add(obj)
        session.commit()
        return obj.as_dict()

    @classmethod
    def get(cls, session, **kwargs):
        return session.query(cls).filter_by(**kwargs)


meta.mapper(Pages, pages_table)
