# Test Exercise
The goal of this project is to construct a basic API for creation of users and stores. The API has CRUD functionality for users as well as stores. It uses token authentication to perform stateless communication with the server.

Users are only, currently, shown stores they either own or manage (various design choices are discussed later). Owners and Managers are able to adjust hours and days of operation for their stores. Owners are able to promote users to managers. Any user can create a store, and they are assigned as the owner.

I used standard design practices from the Django REST framework. This means serializers to control validation and serialization, views to control the logic of the API, and routers to control the URLs. I used standard Django Class based views.

## Uding the API

### Deployment
This API is not yet deployed to Heroku. It can be forked from [this](https://github.com/smtilson/test-aufgabe-ft/) repository and run locally.

### Requirements
The main packages used are Django 5.1.6, Django REST Framework 3.15.2, and Django Filter 25.1.

### Login and Signup
A new user can signup at the endpoint /users/signup/. The user will receive a token. This token should be passed in the header of all requests to the API:
HTTP_AUTHORIZATION: Token token.key

After initial signup, the user will also receive the same token upon login at the endpoint /users/login/.

### Users
The user endpoint is /users/. This endpoint can be used to create a new user, retrieve a list of all users, retrieve a single user, update a user, and delete a user. This page is intended for use 
## Design Decisions
### User Types
I decided to have one basic user type. Any user can be an owner and any user can be a manager. This can be easily modified to prevent owners from being managers and managers from being owners, but this didn't seem like a priority.

Whether or not a user is an owner or a manager is determined dynamically. It would also be possible to add a One-to-Many relationship between owners and other users, to signify employment. This also did not seem like a priority. It seemed a bit annoying to implement because of how it would be used in practice (do employers register their employees? at what point in the signup process is this relationship determine?). It did not seem like there was a good business case for it, or at least not a good enough one for it to be a priority. Given that each company uses a separate database, it also seemed unnecessary.

### Permisssions
Permissions are used only to make sure that users are authenticated. Currently, users are only shown stores that they manage or own. This is done by checking if the user is in the managers or owners fields of the store. This means that further permissions are redundant. The query set enforces these restrictions. Additionally, users can only edit the managers of stores that they own.

### Store Views
It seemed most relevant to have ways of controlling hours, days, and managers of a store. Given that this is an API and there is no frontend, I added endpoints to accommodate this more directly than through the use of the Store view set. Filtering is enabled for all of these. However, I have not yet implemented filtering stores by sets of manager ids.

### Filtering
Filtering is enabled for all of the Store views. Filtering is extensively tested in the Days, Hours, and Managers views. The filter for the Stores view set inherits from these, so testing of those specific filters for that view is not necessary.

Note, I realized late that I could use the serializers to handle a lot of the validation for the filters. Ideally, this would make the implementation a lot cleaner and would be the first thing I do if I were to continue working on this.

### Serializers
Serializers are used extensively. They are used to validate, serialize, and deserialize data. Specific serializers have business logic built into them for less common validation (ensuring a stores opening hours being before its closing hours). We followed the practice of having a separate serializer for each view.

### Testing
I used Djangos testing framework. I think I covered a lot of cases, but I would like to reorganize it and use a stronger BaseTestCase class. The testing was extremely helpful in improving the functionality of the API and ensuring it behaved as I intended.

In order to test the filters with enough cases, I wrote utility scripts which load the database with essentially random valid data. In order to view all of the records I enabled the superuser to see all of the records. This is not a good practice, but it was helpful for testing. It can be easily disabled.

### Security
Minimal security is implemented. I used the basic TokenAuthentication package that comes with Django REST framework. If this were something intended for production, I would consider JWT authentication. I don't know too much about it, but have implemented it in a practice tutorial.

Note: I did enable sessions so that I could remain logged in while manually testing the API. I understood this was the only way to keep the token during manual testing. This is not RESTful though, as I understand it.


## Future directions
There are many things I would like to do to improve.

- I would like to go back through and refactor the code to be more readable and more DRY.
- Implementing an Employer-Employee relationship.
- Implementing permissions so that employees would have read but not right access.
- - I would like to use the Django Rest Framework permissions package, but this could also be done easily with manual checks.
- Implementing filtering by sets of manager ids.
- Implementing JWT authentication.
- Improving the testing.
- - This could be done by organizing the tests better. Either dividing tests into more separate test classes, or by having standard types of tests that can be reused across model, serializer, view, and filter tests. I would also like to organize the edge cases for each field better.
- - Testing for the Filters on the User ViewSet. (this was not prioritized as the store views are used primarily and filtering the managers and owners there is possible).
- More extensive documentation.
- - Type hinting.
- - Extensive and consistent docstrings.
- There was an issue with the parser I would like to try to address. This is discussed more in the Challenges section.


## Challenges
This project was a lot of fun and I ran into some interesting challenges. I learned a lot in this project. I learned a lot about the Django REST Framework and about designing APIs. I also learned about ways I can improve my design process. Here are some specific challenges I ran into.

- There is an issue with the JSON parser. Specifically, I was trying to pass inappropriate types to the views and get a 400 error. However, I could not figure out how to get to the input before it was already parsed into a string. I tried making a custom parser but as it seemed it would take a lot of time to implement, I decided to leave it as is. I assume that this is something that there is either an obvious/standard solution to for more experienced developers or that it is not a concern at all.

- There was an issue with routing the list and detail views. I spent a lot of time trying to debug it, but ultimately using one view but routing it to two different urls worked best. I don't think this is the best way to do it, but it seemed reasonable as the urls were descriptive.

- Getting the logic to work properly for adding ids to many-to-many relationships was difficult at first. The default behavior was not what I wanted. It would replace the whole list with what was submitted in the request instead of simply adding a relationship.

### Minor issues
There were some bugs. Here are the ones that stood out.
- At one point, the ordering keyword was being passed to the serializer. This took a bit of time to figure out.
- The fields in the model are required by default. This caused an error to be thrown before validation by the serializer caught it. This was annoying.
- I tried to name a model field _state. Django did not like this (a "youthful" error on my part). I changed it to state_abbrv.
- A delete request was not returning a 204 status code. Perhaps there is some middleware that is intercepting the response. This is likely note hard to fix, but I found it late and didnt consider it a priority.

## Documentation
The primary documentation uses the tool Swagger and DRF-yasg. It can be accessed at http://localhost:8000/swagger/. There is a markdown version of the [Swagger Yaml](/documentation/swagger_yaml.md).
We give a brief summary here nonetheless.

## Endpoints
Brief descriptions of endpoints are given with relevant HTTP methods. More extensive documentation was generated by Swagger and can be found (here)[documentation\swagger_yaml.md].

### Generic

#### /api-token-auth/
Used for retrieving tokens. Accepts POST requests.

### Users-/users/
This can be used to access the viewset for all of the users. It is accessible to all authenticated users.

router = DefaultRouter()
router.register(r"users", CustomUserViewSet)
urlpatterns = [
    path("", include(router.urls)),
    path("login/", LoginView.as_view(), name="login"),
    path("signup/", SignupView.as_view(), name="signup"),
]

### /stores/
outer.register("stores", StoreViewSet, basename="stores")

urlpatterns = [
    path("", include(router.urls)),
    path("days-list/", StoreDaysView.as_view(), name="store-days-list"),
    path("days-detail/<int:pk>/", StoreDaysView.as_view(), name="store-days-detail"),
    path("hours-list/", StoreHoursView.as_view(), name="store-hours-list"),
    path("hours-detail/<int:pk>/", StoreHoursView.as_view(), name="store-hours-detail"),
    path("managers-list/", StoreManagersView.as_view(), name="store-managers-list"),
    path(
        "managers-detail/<int:pk>/",
        StoreManagersView.as_view(),
        name="store-managers-detail",
    ),
]
 
#### Create a new user

### Store Endpoints
#### /store/
##### Create a new store
##### Retrieve a single store by ID
##### Retrieve a list of all stores
##### Update an existing store (with all fields)
##### Update an existing store (with some fields)
##### Delete an existing store
####



## Bugs
- When trying to make migrations, I got error: fields.E304. This was due to the similar field names in the AbstractBaseUser model I am inheriting from.
 - Fix: Override the field and change the related name attribute.
- Error with field named _state. Led to error regarding string not having a certain attribute. I guess _state is a reserved term in Django ro Django Rest Framework.
 - Fix: Rename the field to state_abbrv.
- Browsable API: when adding a day to the many to many days_of_operation field, it replaces the day completely instead of adding it.
- Passowrd not being hashed wia the CustomUserViewSet
 - Fix: Use the set_password and create_user methods in the relevant serializer.
- Not adding managers properly via rest form.
 - Fix: Overwrite update method of relevant serializer.
- Test for delete user is failing to get the right status code.
 - Fix: Add field HTTP_ACCEPT: application/json to the client in setUp method.
- Django can't find tests.
 - Fix: add __init__.py to the tests folder.
## References
### AI support
- [ChatGPT](https://chat.openai.com/)
- [GitHub Copilot](https://github.com/features/copilot)
- [Cody](https://www.sourcegraph.com/)

### Documentation
- [Django Rest Framework](https://www.django-rest-framework.org/)
- [Django](https://www.djangoproject.com/)

### Other
- [Swagger Markdown UI](https://swagger-markdown-ui.netlify.app/)
- StackOverflow (I did not document the questions that thoroughly)