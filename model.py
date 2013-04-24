from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref


engine = create_engine("sqlite:///database.db", echo=True)
session = scoped_session(sessionmaker(bind=engine, autocommit = False, autoflush = False))

Base = declarative_base()
Base.query = session.query_property()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key = True)
    email = Column(String(80), nullable=False)
    username = Column(String(80), nullable=False)
    password = Column(String(80), nullable=False)
    
class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key = True)
    project_name = Column(String(80), nullable=True)
    project_password = Column(String, nullable=True)
    base_text = Column(String, nullable=True)
    keywords = Column(String, nullable=True)


# ASSOCIATION TABLE
# We need this b/c of the many-many relationship
# However, if it were 1-many, we would not need it
class Membership(Base):
    __tablename__ = "memberships"
    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey('users.id'))
    project_id = Column(Integer, ForeignKey('projects.id'))

    # from here we can query for memberships -- 

    # The purpose of this is based on a query
    # whenever we load a project, then corresponding users will also be loaded
    # load corresponding users 
    user = relationship("User", backref=backref("memberships", order_by=id))

    # The purpose of this is based on a query
    # whenever we load a users, then corresponding projects will also be loaded
    # load corresponding projects
    project = relationship("Project", backref=backref("memberships", order_by=id))

class Idea(Base):
    __tablename__ = "ideas"
    id = Column(Integer, primary_key = True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    creator_id = Column(Integer, ForeignKey('users.id'))
    inspiration = Column(String, nullable = True)
    idea = Column(String, nullable = True)

    # load corresponding project object
    idea_project = relationship("Project", backref=backref("ideas", order_by=id))
    creator = relationship("User", backref=backref("ideas", order_by=id))


class Rating(Base):
    __tablename__ = "ratings"
    id = Column(Integer, primary_key = True)
    idea_id = Column(Integer, ForeignKey('ideas.id'))
    rater_id = Column(Integer, ForeignKey('users.id'))
    rating = Column(Integer, nullable=True)
    rating_notes= Column(String, nullable = True)

    # one idea has many ratings - ONE TO MANY
    idea = relationship("Idea", backref=backref("ideas", order_by=id))
    # # one rater has many ratings - ONE TO MANY
    rater = relationship("User", backref=backref("ratings", order_by=id))

def main():
    """In case we need this for something"""
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    main()


