# Test Exercise
The goal of this project is to construct a basic API for creation of users and stores. The API has CRUD functionality for users as well as stores.

## Instructions
### Initial Email
The parameters for the test exercise are as follows:
We got stores with a store ID, store name, address and opening hours.

The task is to build a simple REST API using Django, which should allow users to perform the following actions:

- Create a new store
- Retrieve a single store by ID
- Retrieve a list of all stores
- Update an existing store (with all fields)
- Delete an existing store

Requirements:

The store should be a simple model with the required fields.
The API should use proper HTTP verbs (POST, GET, PUT, DELETE) and status codes (201, 200, 204, 400, 404, etc.).
The API should be secured with token-based authentication (e.g., using Django Rest Framework's TokenAuthentication).
The API should handle validation errors and return appropriate error responses.
The API should include proper pagination and filtering for the list view.

Please add documentation and also a simple readme how to execute the code. 
### Clarification Questions and Answers
Questions:
1. I should not be using the features of  the Django rest framework
other than for authentication, correct?
2. Should stores be tied to a particular user? That is, in order to
modify a store, is it sufficient for the user to just be
authenticated, or should they only be able to modify stores that they
have created/own?
3. After a quick look, HTML forms do not natively support PUT
requests. I have found two workarounds, one using JS and fetch to
interact with the database. Is that the preferred method or is there
something I am missing?
4. I assume a minimal frontend is part of the project as well, or is
more expected?

Answers:
1. You can use how much you want :)

2. Okay, so put yourself in the shoes of our customer who is the manager of 10-15 stores. Each store has a unique address, but some stores may have the same or the similar opening hours. The question now is how easy do we want to make it for our customer to maintain this data? 
Perhaps he also had store area managers who can each manage their 5 stores.
At Foodtracks each of our customers has their own DB.

3. / 4. No, no JS / Html frontend is necessary per se. Django already has its own possibilities to show the DB information over the requested APIs.

## Bugs
- When trying to make migrations, I got error: fields.E304. This was due to the similar field names in the AbstractBaseUser model I am inheriting from.
 - Fix: Override the field and change the related name attribute.
- Error with field named _state. Led to error regarding string not having a certain attribute. I guess _state is a reserved term in Django ro Django Rest Framework.
 - Fix: Rename the field to state_abbrv.
- Browsable API: when adding a day to the many to many open_days field, it replaces the day completely instead of adding it.
- Passowrd not being hashed wia the CustomUserViewSet
 - Fix: Use the set_password and create_user methods in the relevant serializer.
- Not adding managers properly via rest form.
 - Fix: Overwrite update method of relevant serializer.
- Test for delete user is failing to get the right status code.
 - Fix: Add field HTTP_ACCEPT: application/json to the client in setUp method.
## References
### AI support
- [ChatGPT](https://chat.openai.com/)
- [GitHub Copilot](https://github.com/features/copilot)
- [Cody](https://www.sourcegraph.com/)

### Documentation
- [Django Rest Framework](https://www.django-rest-framework.org/)
- [Django](https://www.djangoproject.com/)
