from todoapp.security.password import hash_password, verify_password


def test_hash_and_verify_password():
    password = "pass123"

    hashed_password = hash_password(password)

    assert hashed_password != password
    assert verify_password(password, hashed_password)
