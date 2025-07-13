from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

CustomUser = get_user_model()


class UserAuthTests(APITestCase):
    """
    Test suite for the user authentication API (registration, login, logout, me).
    """

    def setUp(self):
        """
        Set up the necessary data for the tests.
        This method is run before each test function.
        """
        # URLs for the auth endpoints
        self.register_url = reverse("auth_register")
        self.login_url = reverse("auth_login")
        self.logout_url = reverse("auth_logout")
        self.me_url = reverse("auth_me")
        self.token_refresh_url = reverse("token_refresh")

        # Common user data for tests
        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "a-very-strong-password123",
        }

        # Create a pre-existing user for login and other tests
        self.user = CustomUser.objects.create_user(
            username="existinguser",
            email="existing@example.com",
            password="a-strong-password-too",
        )

    # == REGISTRATION TESTS ==

    def test_user_registration_success(self):
        """
        Ensure a new user can be registered successfully.
        """
        data = {
            "username": self.user_data["username"],
            "email": self.user_data["email"],
            "password": self.user_data["password"],
            "password2": self.user_data["password"],
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            CustomUser.objects.filter(email=self.user_data["email"]).exists()
        )

    def test_registration_with_existing_email_fails(self):
        """
        Ensure registration fails if the email already exists.
        """
        data = {
            "username": "anotheruser",
            "email": self.user.email,  # Using the email from the user created in setUp
            "password": self.user_data["password"],
            "password2": self.user_data["password"],
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_with_mismatched_passwords_fails(self):
        """
        Ensure registration fails if passwords do not match.
        """
        data = {
            "username": self.user_data["username"],
            "email": self.user_data["email"],
            "password": self.user_data["password"],
            "password2": "a-different-password",
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    # == LOGIN TESTS ==

    def test_user_login_success(self):
        """
        Ensure a registered user can log in and receive JWT tokens.
        """
        data = {
            "username": self.user.username,
            "password": "a-strong-password-too",
        }
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_user_login_with_wrong_password_fails(self):
        """
        Ensure login fails with an incorrect password.
        """
        data = {
            "username": self.user.username,
            "password": "wrong-password",
        }
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # == 'ME' ENDPOINT TESTS (/api/auth/me/) ==

    def test_get_user_profile_unauthenticated_fails(self):
        """
        Ensure accessing the 'me' endpoint without authentication fails.
        """
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_profile_authenticated_success(self):
        """
        Ensure an authenticated user can retrieve their profile.
        """
        # log in to get the token
        login_response = self.client.post(
            self.login_url,
            {"username": self.user.username, "password": "a-strong-password-too"},
        )
        access_token = login_response.data["access"]

        # Set the authentication header
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        # Make the request to the 'me' endpoint
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(response.data["username"], self.user.username)

    def test_update_user_profile_success(self):
        """
        Ensure an authenticated user can update their profile (e.g., their bio).
        """
        login_response = self.client.post(
            self.login_url,
            {"username": self.user.username, "password": "a-strong-password-too"},
        )
        access_token = login_response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        updated_data = {"bio": "This is my new bio."}
        response = self.client.patch(self.me_url, updated_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["bio"], "This is my new bio.")

        # Verify the change in the database
        self.user.refresh_from_db()
        self.assertEqual(self.user.bio, "This is my new bio.")

    # == LOGOUT (TOKEN BLACKLISTING) TESTS ==

    def test_logout_success(self):
        """
        Ensure a user can log out by blacklisting their refresh token.
        """
        # Step 1: Log in to get both access and refresh tokens
        login_response = self.client.post(
            self.login_url,
            {"username": self.user.username, "password": "a-strong-password-too"},
            format="json",
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        access_token = login_response.data["access"]
        refresh_token = login_response.data["refresh"]

        # Step 2: Authenticate the client for the logout request using the access token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        # Step 3: Send the refresh token to the logout endpoint to be blacklisted
        logout_data = {"refresh": refresh_token}
        response = self.client.post(self.logout_url, logout_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

        # Step 4: Verify the blacklisted token can no longer be used for refresh
        refresh_attempt_response = self.client.post(
            self.token_refresh_url, {"refresh": refresh_token}, format="json"
        )
        self.assertEqual(
            refresh_attempt_response.status_code, status.HTTP_401_UNAUTHORIZED
        )
