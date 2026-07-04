"""
Database configuration.

Responsibilities:
- Create Engine
- Create Session
- Create Base
- Initialize Database
- Provide Database Sessions

"""


from sqlalchemy import create_engine,URL,text
from sqlalchemy.orm import sessionmaker,DeclarativeBase,Session

# create url for the engine 

url_object = URL.create(
    "postgresql+pg8000",
    username="postgres",
    password="postgres",
    host="localhost",
    port=5432,
    database="lead-generation",
)

#  Create SQLite Engine

engine = create_engine(url_object,echo=True)

# Create Session

SessionLocal = sessionmaker(bind=engine,autoflush=True,autocommit=False,expire_on_commit=True)

#  Create Base
class Base(DeclarativeBase):
    pass 


#  Initialize Database

def init_db() -> None:
    """
    Create all database tables.
    """
    from database.models import Lead

    Base.metadata.create_all(bind=engine)



#  Return Database Session


def get_db() -> Session:
    """
    Returns a SQLAlchemy database session.

    Example:
        db = get_db()

        try:
            ...
        finally:
            db.close()
    """
    return SessionLocal()

