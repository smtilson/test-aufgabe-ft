# FoodTracks Test API
API documentation for the test project.

## Version: v1

### Terms of service
https://www.example.com/terms/

**Contact information:**  
seantilson@gmail.com  

**License:** MIT License

### Security
**Basic**  

|basic|*Basic*|
|---|---|

### /api-token-auth/

#### POST
##### Description:



##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| data | body |  | Yes | [AuthToken](#AuthToken) |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 201 |  | [AuthToken](#AuthToken) |

### /days-detail/{id}/

#### GET
##### Description:



##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| id | path |  | Yes | string |
| page | query | A page number within the paginated result set. | No | integer |
| page_size | query | Number of results to return per page. | No | integer |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 |  | object |

#### PATCH
##### Description:



##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| id | path |  | Yes | string |
| data | body |  | Yes | [Days](#Days) |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 |  | [Days](#Days) |

### /days-list/

#### GET
##### Description:



##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| page | query | A page number within the paginated result set. | No | integer |
| page_size | query | Number of results to return per page. | No | integer |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 |  | object |

#### PATCH
##### Description:



##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| data | body |  | Yes | [Days](#Days) |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 |  | [Days](#Days) |

### /hours-detail/{id}/

#### GET
##### Description:



##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| id | path |  | Yes | string |
| page | query | A page number within the paginated result set. | No | integer |
| page_size | query | Number of results to return per page. | No | integer |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 |  | object |

#### PUT
##### Description:



##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| id | path |  | Yes | string |
| data | body |  | Yes | [Hours](#Hours) |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 |  | [Hours](#Hours) |

#### PATCH
##### Description:



##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| id | path |  | Yes | string |
| data | body |  | Yes | [Hours](#Hours) |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 |  | [Hours](#Hours) |

### /hours-list/

#### GET
##### Description:



##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| page | query | A page number within the paginated result set. | No | integer |
| page_size | query | Number of results to return per page. | No | integer |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 |  | object |

#### PUT
##### Description:



##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| data | body |  | Yes | [Hours](#Hours) |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 |  | [Hours](#Hours) |

#### PATCH
##### Description:



##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| data | body |  | Yes | [Hours](#Hours) |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 |  | [Hours](#Hours) |

### /login/

#### GET
##### Description:

Allows for API-GUI form.

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 |  |

#### POST
##### Description:



##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |

##### Responses

| Code | Description |
| ---- | ----------- |
| 201 |  |

### /managers-detail/{id}/

#### GET
##### Description:



##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| id | path |  | Yes | string |
| page | query | A page number within the paginated result set. | No | integer |
| page_size | query | Number of results to return per page. | No | integer |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 |  | object |

#### PUT
##### Description:



##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| id | path |  | Yes | string |
| data | body |  | Yes | [Managers](#Managers) |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 |  | [Managers](#Managers) |

#### PATCH
##### Description:



##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| id | path |  | Yes | string |
| data | body |  | Yes | [Managers](#Managers) |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 |  | [Managers](#Managers) |

### /managers-list/

#### GET
##### Description:



##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| page | query | A page number within the paginated result set. | No | integer |
| page_size | query | Number of results to return per page. | No | integer |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 |  | object |

#### PUT
##### Description:



##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| data | body |  | Yes | [Managers](#Managers) |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 |  | [Managers](#Managers) |

#### PATCH
##### Description:



##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| data | body |  | Yes | [Managers](#Managers) |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 |  | [Managers](#Managers) |

### /signup/

#### GET
##### Description:



##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| page | query | A page number within the paginated result set. | No | integer |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 |  | object |

#### POST
##### Description:



##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| data | body |  | Yes | [SignUp](#SignUp) |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 201 |  | [SignUp](#SignUp) |

### /stores/

#### GET
##### Description:



##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| page | query | A page number within the paginated result set. | No | integer |
| page_size | query | Number of results to return per page. | No | integer |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 |  | object |

#### POST
##### Description:



##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| data | body |  | Yes | [Store](#Store) |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 201 |  | [Store](#Store) |

### /stores/{id}/

#### GET
##### Description:



##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| id | path |  | Yes | string |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 |  | [Store](#Store) |

#### PUT
##### Description:



##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| id | path |  | Yes | string |
| data | body |  | Yes | [Store](#Store) |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 |  | [Store](#Store) |

#### PATCH
##### Description:



##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| id | path |  | Yes | string |
| data | body |  | Yes | [Store](#Store) |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 |  | [Store](#Store) |

#### DELETE
##### Description:



##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| id | path |  | Yes | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 204 |  |

### /users/

#### GET
##### Description:



##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| page | query | A page number within the paginated result set. | No | integer |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 |  | object |

#### POST
##### Description:



##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| data | body |  | Yes | [CustomUser](#CustomUser) |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 201 |  | [CustomUser](#CustomUser) |

### /users/{id}/

#### GET
##### Description:



##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| id | path | A unique integer value identifying this custom user. | Yes | integer |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 |  | [CustomUser](#CustomUser) |

#### PUT
##### Description:



##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| id | path | A unique integer value identifying this custom user. | Yes | integer |
| data | body |  | Yes | [CustomUser](#CustomUser) |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 |  | [CustomUser](#CustomUser) |

#### PATCH
##### Description:



##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| id | path | A unique integer value identifying this custom user. | Yes | integer |
| data | body |  | Yes | [CustomUser](#CustomUser) |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 |  | [CustomUser](#CustomUser) |

#### DELETE
##### Description:



##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| id | path | A unique integer value identifying this custom user. | Yes | integer |

##### Responses

| Code | Description |
| ---- | ----------- |
| 204 |  |

### Models


#### AuthToken

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| username | string |  | Yes |
| password | string |  | Yes |
| token | string |  | No |

#### Days

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| id | integer |  | No |
| name | string |  | No |
| owner | string |  | No |
| managers | string |  | No |
| days_of_operation | string |  | No |
| montag | boolean |  | No |
| dienstag | boolean |  | No |
| mittwoch | boolean |  | No |
| donnerstag | boolean |  | No |
| freitag | boolean |  | No |
| samstag | boolean |  | No |
| sonntag | boolean |  | No |

#### Hours

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| id | integer |  | No |
| name | string |  | No |
| owner | string |  | No |
| managers | string |  | No |
| days_of_operation | string |  | No |
| opening_time | string |  | No |
| closing_time | string |  | No |

#### Managers

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| id | integer |  | No |
| name | string |  | No |
| owner | string |  | No |
| managers | string |  | No |
| manager_ids | [ integer ] |  | No |
| days_of_operation | string |  | No |

#### SignUp

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| first_name | string |  | Yes |
| last_name | string |  | Yes |
| email | string (email) |  | Yes |
| password | string |  | Yes |

#### Store

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| id | integer |  | No |
| days_of_operation | string |  | No |
| owner | string |  | No |
| owner_id | integer |  | No |
| managers | string |  | No |
| name | string |  | No |
| address | string |  | No |
| city | string |  | No |
| state_abbrv | string |  | No |
| plz | string |  | No |
| opening_time | string |  | No |
| closing_time | string |  | No |
| montag | boolean |  | No |
| dienstag | boolean |  | No |
| mittwoch | boolean |  | No |
| donnerstag | boolean |  | No |
| freitag | boolean |  | No |
| samstag | boolean |  | No |
| sonntag | boolean |  | No |
| manager_ids | [ integer ] |  | No |
| created_at | dateTime |  | No |
| updated_at | dateTime |  | No |

#### CustomUser

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| id | integer |  | No |
| first_name | string |  | Yes |
| last_name | string |  | Yes |
| email | string (email) |  | Yes |
| password | string |  | Yes |
| date_joined | dateTime |  | No |
| last_login | dateTime |  | No |
| is_superuser | boolean | Designates that this user has all permissions without explicitly assigning them. | No |
| is_staff | boolean |  | No |
| is_manager | string |  | No |
| is_owner | string |  | No |
| token | string |  | No |