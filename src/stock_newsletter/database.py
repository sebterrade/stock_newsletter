from sqlmodel import create_engine, SQLModel, Session, select
from . import config
from .models import User, Stock, UserPreference

sqlite_url = f"sqlite:///{config.DB_PATH}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

def create_user(session: Session, email: str) -> User:
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        user = User(email=email)
        session.add(user)
        session.commit()
        session.refresh(user)
    return user

def add_user_preference(session: Session, user: User, ticker: str):
    # Ensure stock exists (simple check/add)
    stock = session.exec(select(Stock).where(Stock.ticker == ticker)).first()
    if not stock:
        stock = Stock(ticker=ticker)
        session.add(stock)
        session.commit()
        session.refresh(stock)
        
    # Check if preference already exists
    pref = session.exec(select(UserPreference).where(UserPreference.user_id == user.id, UserPreference.ticker == ticker)).first()
    if not pref:
        pref = UserPreference(user=user, ticker=ticker)
        session.add(pref)
        session.commit()
        session.refresh(pref)
    return pref

def get_user_tickers(session: Session, email: str) -> list[str]:
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        return []
    return [pref.ticker for pref in user.preferences]

