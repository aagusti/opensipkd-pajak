from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    backref
    )
from zope.sqlalchemy import ZopeTransactionExtension

pbbDBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension(),
                              autocommit=False,
                              autoflush=False,))
pbbBase = declarative_base()
from ...tools import get_settings
settings = get_settings()
pbb_schema = settings and 'schema.pbb' in settings and settings['schema.pbb'] or 'pbb'

PBB_ARGS = {'extend_existing':True,  
        'schema': pbb_schema}  