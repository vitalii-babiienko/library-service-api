# Library Service API

The RESTful API is designed to manage borrowing-related information and operations. This service provides a convenient way to interact with different resources such as users, books, and borrowings. Admins receive notifications in telegram chat about new borrowing creation and daily-based notifications about borrowings overdue.

## Run with Docker

**Docker must already be installed!**

```shell
git clone https://github.com/vitalii-babiienko/library-service-api.git
cd library-service-api
```

Create a **.env** file by copying the **.env.sample** file and populate it with the required values.

```shell
docker-compose up --build
```

## Get access

* Create a new user via [api/user/](http://localhost:8000/api/user/).
* Take the access and refresh tokens via [api/user/token/](http://localhost:8000/api/user/token/).
* Refresh the access token via [api/user/token/refresh/](http://localhost:8000/api/user/token/refresh/).

## API Documentation

The API is well-documented with detailed explanations of each endpoint and its functionalities. The documentation provides sample requests and responses to help you understand how to interact with the API. The documentation is available via [api/doc/swagger/](http://localhost:8000/api/doc/swagger/).
