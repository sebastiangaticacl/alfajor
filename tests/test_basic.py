def test_request_main_page(client):
    """Test that the main page redirects to login when not authenticated."""
    response = client.get("/")
    assert response.status_code == 302
    assert "/auth/login" in response.location

def test_login_page_loads(client):
    """Test that the login page loads successfully."""
    response = client.get("/auth/login")
    assert response.status_code == 200
    assert b"ALFAJOR" in response.data
