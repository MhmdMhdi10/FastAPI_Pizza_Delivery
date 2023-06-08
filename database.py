from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine('postgresql://mm10:mm12061382@localhost/fastapi_pizza_delivery',
                       echo=True,
                       )
Base = declarative_base()

Session = sessionmaker()
