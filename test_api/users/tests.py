from django.test import TestCase

# Create your tests here.


# Serializer Tests
# These should test each serializer
# testing serialization and deserialization
# see that password is hashed/handled correctly
# test CRUD operations
# Test Signup serializer
## new user can be created
## that a token is created and returned
# Test Login serializer
## user can login
## token is returned
## user can't login with wrong password
## user can't login with wrong email
## bad credentials give a response

# User Views Tests

## Test CustomUserViewSet
### Test that a user can be created
### Test that a user can be updated
### Test that a user can be deleted
### Test that a user can be retrieved
### Test that a user can be listed
## SignupView
### Test that a user can be created
### Test that a token is created and returned
### test edge cases
## LoginView:
### Test login with valid credentials and ensure a token is returned.
### Test login with invalid credentials (e.g., wrong password or non-existent email).
### Test edge cases like empty or malformed requests.
