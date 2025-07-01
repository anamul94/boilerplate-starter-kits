import pytest
from app.core.security import create_access_token, verify_token, get_password_hash, verify_password
from datetime import timedelta

def test_password_hashing():
    password = "testpassword123"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False

def test_jwt_token_creation():
    user_id = 123
    token = create_access_token(user_id)
    
    assert token is not None
    assert isinstance(token, str)
    
    # Verify token
    payload = verify_token(token)
    assert payload["sub"] == str(user_id)

def test_jwt_token_with_expiry():
    user_id = 123
    expires_delta = timedelta(minutes=30)
    token = create_access_token(user_id, expires_delta=expires_delta)
    
    payload = verify_token(token)
    assert payload["sub"] == str(user_id)
    assert "exp" in payload

def test_jwt_token_with_extra_data():
    user_id = 123
    extra_data = {"role": "admin", "permissions": ["read", "write"]}
    token = create_access_token(user_id, extra_data=extra_data)
    
    payload = verify_token(token)
    assert payload["sub"] == str(user_id)
    assert payload["role"] == "admin"
    assert payload["permissions"] == ["read", "write"]

def test_invalid_jwt_token():
    invalid_token = "invalid.jwt.token"
    
    with pytest.raises(Exception):
        verify_token(invalid_token)