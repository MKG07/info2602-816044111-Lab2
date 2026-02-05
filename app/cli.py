from re import search
import typer
from app.database import create_db_and_tables, get_session, drop_all
from app.models import User
from fastapi import Depends
from sqlmodel import select
from sqlalchemy.exc import IntegrityError

cli = typer.Typer()

@cli.command()
def initialize():
    with get_session() as db: # Get a connection to the database
        drop_all() # delete all tables
        create_db_and_tables() #recreate all tables
        bob = User('bob', 'bob@mail.com', 'bobpass') # Create a new user (in memory)
        db.add(bob) # Tell the database about this new data
        db.commit() # Tell the database persist the data
        db.refresh(bob) # Update the user (we use this to get the ID from the db)
        print("Database Initialized")

@cli.command()
def get_user(username:str = typer.Argument(..., help="The exact username to search for")):
    """Get a user by exact username. 
    Example: 
        python app/cli.py get-user bob
    """ 
    with get_session() as db: # Get a connection to the database
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found!')
            return
        print(user) 

#Exercise 1 
@cli.command()
def find_user(search: str = typer.Argument(..., help="A partial search term to look for in usernames or emails")):
    """Find users by partial match in username or email.
    Example: 
        python app/cli.py find-user thom
    """
    with get_session() as db: 
        users = db.exec(select(User).where(User.username.contains(search) | User.email.contains(search))).all()
        if not users:
            print(f"No users found with search term '{search}'.")
        else:
            print(f"Users matching '{search}':")
            for user in users:
                print(user)  

@cli.command()
def get_all_users(): 
    """Get all users in the database.
    Example:
        python app/cli.py get-all-users
    """
    with get_session() as db: 
        all_users = db.exec(select(User)).all()
        if not all_users:
            print("No users found.")
        else:
            for user in all_users:
                print(user) 

#Exercise 2
@cli.command()
def list_users(limit: int = 10, help: str = "The number of users to show", offset: int = 0, help2: str = "The number of users to skip before starting to collect the result set"): 
    """List users with pagination.""" 

    with get_session() as db: 
        total_users = len(db.exec(select(User)).all())
        users = db.exec(select(User).limit(limit).offset(offset)).all()
        print(f"Showing {len(users)} of {total_users} users") 
        for user in users:
            print(user) 



@cli.command()
def change_email(username: str = typer.Argument(..., help="The username of the user whose email is to be changed"), new_email:str = typer.Argument(..., help="The new email address")):
    """Change a user's email address.""" 

    with get_session() as db: 
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found! Unable to update email.')
            return
        user.email = new_email
        db.add(user)
        db.commit()
        print(f"Update {user.username}'s email to {user.email}") 

@cli.command()
def create_user(username: str = typer.Argument(..., help="The username of the new user"), email:str = typer.Argument(..., help="The email of the new user"), password: str = typer.Argument(..., help="The password of the new user")):
    """Create a new user.
    Example:
        python app/cli.py create-user alice alice@example.com password123

    """

    with get_session() as db:
        newuser = User(username, email, password)
        try:
            db.add(newuser)
            db.commit()
        except IntegrityError as e:
            db.rollback()
            print(f"Username or email already exists") 
        else: 
            print(newuser) 

@cli.command()
def delete_user(username: str = typer.Argument(..., help="The username of the user to delete")):
    """Delete a user by username.
    Example:
        python app/cli.py delete-user bob 
    """
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found! Unable to delete.')
            return
        db.delete(user)
        db.commit()
        print(f"User '{username}' deleted successfully.") 



if __name__ == "__main__":
    cli() 