import csv
import model
from model import User
from sys import argv

script, filename = argv


def load_users(session):
    with open(filename, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter ='|')
        print reader
        for row in reader:

            print row
            add_object = User(id=row[0], email=row[1], username=row[2], password=row[3])
            session.add(add_object)
        session.commit()

def main(session):

    load_users(session)
    
    

# if __name__ == "__main__":
#     s = model.connect()
#     main(s)