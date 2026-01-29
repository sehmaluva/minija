"""Tests for User App"""

from django.test import TestCase, Client
from django.urls import reverse
from django.core.mail import outbox
from rest_framework.test import APITestCase
from rest_framework import status
from apps.users.models.models import User
import uuid


class UserRegistrationTests(APITestCase):
    """Test cases for user registration"""

    def setUp(self):
        self.client = Client()
        self.register_url = reverse("register")

    def test_user_registration_success(self):
        """Test successful user registration"""
        data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "first_name": "New",
            "last_name": "User",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("user", response.json())
        self.assertIn("access", response.json())
        self.assertIn("refresh", response.json())

    def test_user_registration_password_mismatch(self):
        """Test registration with mismatched passwords"""
        data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "first_name": "New",
            "last_name": "User",
            "password": "SecurePass123!",
            "password_confirm": "DifferentPass123!",
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_duplicate_email(self):
        """Test registration with duplicate email"""
        # Create first user
        User.objects.create_user(
            email="duplicate@example.com",
            username="user1",
            password="Pass123!",
            first_name="First",
            last_name="User",
        )

        # Try to register with same email
        data = {
            "email": "duplicate@example.com",
            "username": "user2",
            "first_name": "Second",
            "last_name": "User",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_sends_verification_email(self):
        """Test that verification email is sent on registration"""
        data = {
            "email": "test@example.com",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(outbox), 1)
        self.assertIn("Verify Your Account", outbox[0].subject)

    def test_user_inactive_after_registration(self):
        """Test that user is inactive after registration"""
        data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "first_name": "New",
            "last_name": "User",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
        }
        response = self.client.post(self.register_url, data, format="json")
        user = User.objects.get(email="newuser@example.com")
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_email_verified)


class EmailVerificationTests(APITestCase):
    """Test cases for email verification"""

    def setUp(self):
        self.client = Client()
        self.verify_url = reverse("email_verify")
        self.user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="Pass123!",
            first_name="Test",
            last_name="User",
            is_active=False,
            is_email_verified=False,
            email_verification_token=uuid.uuid4(),
        )

    def test_email_verification_success(self):
        """Test successful email verification"""
        token = str(self.user.email_verification_token)
        response = self.client.get(self.verify_url, {"token": token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Email successfully verified", response.json()["message"])

        # Verify user is now active and email verified
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertTrue(self.user.is_email_verified)
        self.assertIsNone(self.user.email_verification_token)

    def test_email_verification_invalid_token(self):
        """Test email verification with invalid token"""
        response = self.client.get(self.verify_url, {"token": str(uuid.uuid4())})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid token", response.json()["error"])

    def test_email_verification_missing_token(self):
        """Test email verification without token"""
        response = self.client.get(self.verify_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Token is required", response.json()["error"])

    def test_email_already_verified(self):
        """Test verification when email is already verified"""
        self.user.is_email_verified = True
        self.user.save()

        token = str(self.user.email_verification_token)
        response = self.client.get(self.verify_url, {"token": token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Email already verified", response.json()["message"])


class ResendVerificationEmailTests(APITestCase):
    """Test cases for resending verification email"""

    def setUp(self):
        self.client = Client()
        self.resend_url = reverse("resend_verification")
        self.user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="Pass123!",
            first_name="Test",
            last_name="User",
            is_active=False,
            is_email_verified=False,
            email_verification_token=uuid.uuid4(),
        )

    def test_resend_verification_email_success(self):
        """Test successful resending of verification email"""
        outbox.clear()
        data = {"email": "test@example.com"}
        response = self.client.post(self.resend_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(outbox), 1)

    def test_resend_verification_email_missing_email(self):
        """Test resend verification without email"""
        response = self.client.post(self.resend_url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_resend_verification_nonexistent_email(self):
        """Test resend verification with non-existent email"""
        data = {"email": "nonexistent@example.com"}
        response = self.client.post(self.resend_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should not reveal user doesn't exist
        self.assertIn(
            "If an account with this email exists", response.json()["message"]
        )

    def test_resend_verification_already_verified(self):
        """Test resend verification for already verified email"""
        self.user.is_email_verified = True
        self.user.save()

        data = {"email": "test@example.com"}
        response = self.client.post(self.resend_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("already been verified", response.json()["message"])


class UserLoginTests(APITestCase):
    """Test cases for user login"""

    def setUp(self):
        self.client = Client()
        self.login_url = reverse("login")
        self.user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="Pass123!",
            first_name="Test",
            last_name="User",
            is_active=True,
            is_email_verified=True,
        )

    def test_login_success(self):
        """Test successful login"""
        data = {"email": "test@example.com", "password": "Pass123!"}
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.json())
        self.assertIn("refresh", response.json())

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        data = {"email": "test@example.com", "password": "WrongPass123!"}
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_unverified_email(self):
        """Test login with unverified email"""
        unverified_user = User.objects.create_user(
            email="unverified@example.com",
            username="unverified",
            password="Pass123!",
            first_name="Unverified",
            last_name="User",
            is_active=True,
            is_email_verified=False,
        )

        data = {"email": "unverified@example.com", "password": "Pass123!"}
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Email not verified", response.json()["detail"])

    def test_login_inactive_user(self):
        """Test login with inactive user"""
        inactive_user = User.objects.create_user(
            email="inactive@example.com",
            username="inactive",
            password="Pass123!",
            first_name="Inactive",
            last_name="User",
            is_active=False,
            is_email_verified=True,
        )

        data = {"email": "inactive@example.com", "password": "Pass123!"}
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("disabled", response.json()["detail"])


class UserModelTests(TestCase):
    """Test cases for User model"""

    def test_user_creation(self):
        """Test creating a user"""
        user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="Pass123!",
            first_name="Test",
            last_name="User",
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.full_name, "Test User")

    def test_user_full_name_property(self):
        """Test the full_name property"""
        user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="Pass123!",
            first_name="John",
            last_name="Doe",
        )
        self.assertEqual(user.full_name, "John Doe")

    def test_user_str_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="Pass123!",
            first_name="Test",
            last_name="User",
        )
        self.assertEqual(str(user), "Test User (test@example.com)")

    def test_user_email_unique(self):
        """Test that email field is unique"""
        User.objects.create_user(
            email="test@example.com",
            username="user1",
            password="Pass123!",
            first_name="Test",
            last_name="User",
        )

        with self.assertRaises(Exception):
            User.objects.create_user(
                email="test@example.com",
                username="user2",
                password="Pass123!",
                first_name="Another",
                last_name="User",
            )

    def test_user_role_default(self):
        """Test that user role defaults to 'user'"""
        user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="Pass123!",
            first_name="Test",
            last_name="User",
        )
        self.assertEqual(user.role, "user")
