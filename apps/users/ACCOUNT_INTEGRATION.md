# Django User Accounts Management Integration

This directory contains the django-user-accounts-management code integrated into the minija users app.

## Files Overview

### Core Account Management Files (from django-user-accounts-management):
- `account_models.py` - Account, SignupCode, EmailAddress, EmailConfirmation, PasswordHistory, PasswordExpiry, AccountDeletion models
- `account_views.py` - JSON-based views for signup, login, logout, password management, etc.
- `account_forms.py` - Forms for user registration, login, password changes
- `account_utils.py` - Utility functions for redirects, password checking, etc.
- `account_conf.py` - Configuration using django-appconf
- `account_hooks.py` - Hookset system for customization
- `account_managers.py` - Custom managers for EmailAddress and EmailConfirmation
- `account_fields.py` - Custom TimeZoneField
- `account_signals.py` - Django signals for account events
- `account_languages.py` - Language choices for i18n
- `account_timezones.py` - Timezone choices
- `account_admin.py` - Admin configurations for account models

## Integration Steps

### 1. Install Required Dependencies

```bash
pip install pytz django-appconf
```

### 2. Update apps/users/models/__init__.py

Import and expose the account models alongside your existing User model:

```python
from apps.users.models.models import User
from apps.users.account_models import (
    Account,
    SignupCode,
    SignupCodeResult,
    EmailAddress,
    EmailConfirmation,
    AccountDeletion,
    PasswordHistory,
    PasswordExpiry,
)
```

### 3. Fix Import Paths

All `from apps.account.` imports in the copied files need to be changed to `from apps.users.account_`:

Example:
- `from apps.account.conf import settings` → `from apps.users.account_conf import settings`
- `from apps.account.hooks import hookset` → `from apps.users.account_hooks import hookset`

### 4. Update settings.py

Add the following account-related settings:

```python
# Account Management Settings
ACCOUNT_OPEN_SIGNUP = True
ACCOUNT_LOGIN_REDIRECT_URL = "/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/"
ACCOUNT_EMAIL_UNIQUE = True
ACCOUNT_EMAIL_CONFIRMATION_REQUIRED = False
ACCOUNT_EMAIL_CONFIRMATION_EMAIL = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_PASSWORD_USE_HISTORY = False
ACCOUNT_PASSWORD_EXPIRY = 0
ACCOUNT_NOTIFY_ON_PASSWORD_CHANGE = True
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"

# Add sites framework
INSTALLED_APPS = [
    ...
    'django.contrib.sites',
    ...
]

SITE_ID = 1
```

### 5. Create Migrations

```bash
python manage.py makemigrations users
python manage.py migrate
```

### 6. Update URLs

Add account management URLs to `apps/users/api/urls.py`:

```python
from apps.users import account_views

urlpatterns = [
    # Existing URLs...
    
    # Account Management URLs
    path('account/signup/', account_views.SignupView.as_view(), name='account_signup'),
    path('account/login/', account_views.LoginView.as_view(), name='account_login'),
    path('account/logout/', account_views.LogoutView.as_view(), name='account_logout'),
    path('account/password/', account_views.ChangePasswordView.as_view(), name='account_password'),
    path('account/password/reset/', account_views.PasswordResetView.as_view(), name='account_password_reset'),
    path('account/password/reset/<uidb36>/<token>/', account_views.PasswordResetTokenView.as_view(), name='account_password_reset_token'),
    path('account/settings/', account_views.SettingsView.as_view(), name='account_settings'),
    path('account/confirm_email/<key>/', account_views.ConfirmEmailView.as_view(), name='account_confirm_email'),
    path('account/delete/', account_views.DeleteView.as_view(), name='account_delete'),
]
```

### 7. Update Admin

In `apps/users/admin.py`, import and register the account models:

```python
from apps.users.account_models import (
    Account,
    SignupCode,
    EmailAddress,
    AccountDeletion,
    PasswordHistory,
    PasswordExpiry,
)
from apps.users.account_admin import (
    AccountAdmin,
    SignupCodeAdmin,
    EmailAddressAdmin,
    AccountDeletionAdmin,
    PasswordHistoryAdmin,
    PasswordExpiryAdmin,
)

admin.site.register(Account, AccountAdmin)
admin.site.register(SignupCode, SignupCodeAdmin)
admin.site.register(EmailAddress, EmailAddressAdmin)
admin.site.register(AccountDeletion, AccountDeletionAdmin)
admin.site.register(PasswordHistory, PasswordHistoryAdmin)
admin.site.register(PasswordExpiry, PasswordExpiryAdmin)
```

## Features

### User Registration
- Email-based signup with confirmation
- Optional signup codes/invitations
- Username or email-based authentication

### Authentication
- Login with username or email
- Remember me functionality
- Session management

### Password Management
- Password change with current password verification
- Password reset via email
- Password history tracking (optional)
- Password expiration (optional)

### Email Management
- Multiple email addresses per user
- Email verification
- Primary email designation

### Account Settings
- Update email address
- Change timezone
- Change language preference

### Account Deletion
- Soft delete with expunge after specified hours
- Email notification before final deletion

## API Endpoints

All views return JSON responses:

- `POST /account/signup/` - User registration
- `POST /account/login/` - User login
- `POST /account/logout/` - User logout
- `POST /account/password/` - Change password
- `POST /account/password/reset/` - Request password reset
- `POST /account/password/reset/<uidb36>/<token>/` - Reset password with token
- `POST /account/settings/` - Update account settings
- `POST /account/confirm_email/<key>/` - Confirm email address
- `POST /account/delete/` - Delete account

## Customization

### Hooks

Override the default hookset by creating a custom class:

```python
from apps.users.account_hooks import AccountDefaultHookSet

class CustomAccountHookSet(AccountDefaultHookSet):
    def send_confirmation_email(self, to, ctx):
        # Custom email sending logic
        pass
```

Then update settings:

```python
ACCOUNT_HOOKSET = "myproject.hooks.CustomAccountHookSet"
```

### Signals

Connect to account signals for custom behavior:

```python
from apps.users.account_signals import user_signed_up

def handle_user_signup(sender, user, form, **kwargs):
    # Custom logic after user signs up
    pass

user_signed_up.connect(handle_user_signup)
```

## Notes

- The original django-user-accounts-management package was designed as a standalone Django app
- This integration adapts it to work within the minija users app
- All imports have been modified to reference the users app structure
- JSON responses are used instead of HTML templates for API compatibility
