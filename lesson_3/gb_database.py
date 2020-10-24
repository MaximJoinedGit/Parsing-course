from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from . import gb_models, gb_parse


engine = create_engine('sqlite:///gb_blog.db')

gb_models.Base.metadata.create_all(bind=engine)

SessionMaker = sessionmaker(bind=engine)

if __name__ == '__main__':
    db = SessionMaker()
    print(1)