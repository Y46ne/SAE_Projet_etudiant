from monApp.database import User


def test_user_repr(db_session):
    user = User(Login="test", Password="test")
    db_session.add(user)
    db_session.commit()

    assert repr(user) == f"<User {user.Login}>"