from app.schemas import UserInput


def test_valid_user():
    user = UserInput(
        username="Test User",
        user_id="u-1",
        age=25,
        weight=65,
        goal="general wellness",
        intensity="medium",
    )
    assert user.user_id == "u-1"


def test_invalid_age():
    try:
        UserInput(
            username="Test User",
            user_id="u-1",
            age=10,
            weight=65,
            goal="general wellness",
            intensity="medium",
        )
    except Exception:
        assert True
    else:
        assert False
