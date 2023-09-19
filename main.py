from data_adapter.session import engine
from data_adapter.base import Base

def create_tables():
    Base.metadata.create_all(bind=engine)


if __name__ == '__main__':
    create_tables()