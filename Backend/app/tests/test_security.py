from app.utils.security import hash_password, verify_password

def test_hash_verify():
    h = hash_password("pw")
    assert verify_password("pw", h)
    assert not verify_password("wrong", h)
