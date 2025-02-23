# FoodTracks Test API
API documentation for the test project.

## Version: v1

### Terms of service
As this is a test project, there are no terms of service.
https://www.example.com/terms/

**Contact information:**  
seantilson@gmail.com  

**License:** MIT License

### Security
**Basic**  
As this is a test project, there is no security.

|basic|*Basic*|
|---|---|

## Endpoints

### /api-token-auth/

#### POST
**Description:**  
Retrieve a token to authenticate the user. Token is provided after successful login or signup.

**Parameters**

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| data | body |  | Yes | [AuthToken](#AuthToken) |

**Responses**

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 201 |  | [AuthToken](#AuthToken) |

### /days-detail/{id}/

#### GET
**Description:**
Retrieve detailed information about the days a specific store is open. This endpoint allows you to view and check off which days the store operates. It provides basic information about the store, including its current days of operation, but does not allow for modifications of other fields through this request.

**Parameters**

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| id | path |  | Yes | string |
| page | query | A page number within the paginated result set. | No | integer |
| page_size | query | Number of results to return per page. | No | integer |

**Responses**

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 |  | object |

#### PATCH
**Description:**  
Update the days of operation for a specific store. This endpoint allows you to modify which days the store is open by providing the updated days in the request body. It enables you to change the store's schedule to reflect its current operational days.

**Parameters**

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| id | path |  | Yes | string |
| data | body |  | Yes | [Days](#Days) |

**Responses**

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 |  | [Days](#Days) |

### /days-list/

#### GET
**Description:**  
Retrieve a list of stores with the ability to filter by the days they are open. This endpoint allows you to view all stores and apply filters to see only those that operate on specific days. It's useful for finding stores based on their operational schedule.

**Parameters**

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| page | query | A page number within the paginated result set. | No | integer |
| page_size | query | Number of results to return per page. | No | integer |

**Responses**

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 |  | object |

### /hours-detail/{id}/

#### GET
**Description:**  

**Parameters**

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| id | path |  | Yes | string |
| page | query | A page number within the paginated result set. | No | integer |
| page_size | query | Number of results to return per page. | No | integer |

**Responses**

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 |  | object |

#### PUT
**Description:**  

**Parameters**

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| id | path |  | Yes | string |
| data | body |  | Yes | [Hours](#Hours) |

**Responses**

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 |  | [Hours](#Hours) |

#### PATCH
**Description:**  

**Parameters**

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| id | path |  | Yes | string |
| data | body |  | Yes | [Hours](#Hours) |

**Responses**

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 |  | [Hours](#Hours) |

### /hours-list/

#### GET
**Description:**  

**Parameters**

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| page | query | A page number within the paginated result set. | No | integer |
| page_size | query | Number of results to return per page. | No | integer |

**Responses**

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 |  | object |

#### PUT
**Description:**  

**Parameters**

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| data | body |  | Yes | [Hours](#Hours) |

**Responses**

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 |  | [Hours](#Hours) |

#### PATCH
**Description:**  

**Parameters**

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| data | body |  | Yes | [Hours](#Hours) |

**Responses**

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 |  | [Hours](#Hours) |

### /login/

#### GET
**Description:**  
Allows for API-GUI form.

**Parameters**

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |

**Responses**

| Code | Description |
| ---- | ----------- |
| 200 |  |

#### POST
**Description:**  

**Parameters**

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |

**Responses**

| Code | Description |
| ---- | ----------- |
| 201 |  |

### /managers-detail/{id}/

#### GET
**Description:**  

**Parameters**

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| id | path |  | Yes | string |
| page | query | A page number within the paginated result set. | No | integer |
| page_size | query | Number of results to return per page. | No | integer |

**Responses**

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 |  | object |

#### PUT
**Description:**  

**Parameters**

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| id | path |  | Yes | string |
| data | body |  | Yes | [Managers](#Managers) |

**Responses**

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 |  | [Managers](#Managers) |

#### PATCH
**Description:**  

**Parameters**

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| id | path |  | Yes | string |
| data | body |  | Yes | [Managers](#Managers) |

**Responses**

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 |  | [Managers](#Managers) |

### /managers-list/

#### GET
**Description:**  

**Parameters**

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| page | query | A page number within the paginated result set. | No | integer |
| page_size | query | Number of results to return per page. | No | integer |

**Responses**

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 |  | object |

#### PUT
**Description:**  

**Parameters**

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| data | body |  | Yes | [Managers](#Managers) |

**Responses**

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 |  | [Managers](#Managers) |

#### PATCH
**Description:**  

**Parameters**

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| data | body |  | Yes | [Managers](#Managers) |

**Responses**

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 |  | [Managers](#Managers) |

### /signup/

#### GET
**Description:**  

**Parameters**

| Name | Located in | Description | Required | Schema |
| ---- | ---------- |