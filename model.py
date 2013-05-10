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
    project_master = Column(Integer, ForeignKey('users.id'))
    project_name = Column(String(80), nullable=True)
    project_password = Column(String, nullable=True)
    base_text = Column(String, nullable=True)
    keywords = Column(String, nullable=True)

    master = relationship("User", backref=backref("projects", order_by=id))

class Membership(Base):
    __tablename__ = "memberships"
    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey('users.id'))
    project_id = Column(Integer, ForeignKey('projects.id'))

  
    user = relationship("User", backref=backref("memberships", order_by=id))

    
    project = relationship("Project", backref=backref("memberships", order_by=id))

class Idea(Base):
    __tablename__ = "ideas"
    id = Column(Integer, primary_key = True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    creator_id = Column(Integer, ForeignKey('users.id'))
    idea = Column(String, nullable = True)
    average_rating = Column(Integer, nullable = True)
    total_ratings = Column(Integer, nullable = True)
    ratings_sum = Column(Integer, nullable = True)


    idea_project = relationship("Project", backref=backref("ideas", order_by=id))
    creator = relationship("User", backref=backref("ideas", order_by=id))


class Rating(Base):
    __tablename__ = "ratings"
    id = Column(Integer, primary_key = True)
    idea_id = Column(Integer, ForeignKey('ideas.id'))
    rater_id = Column(Integer, ForeignKey('users.id'))
    rating = Column(Integer, nullable=True)
    rating_notes= Column(String, nullable = True)

    idea = relationship("Idea", backref=backref("ideas", order_by=id))
    rater = relationship("User", backref=backref("ratings", order_by=id))

def main():
    """In case we need this for something"""
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    main()


