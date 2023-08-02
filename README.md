# TikTok-CMS REST API

The TikTok CMS API allows the user using react or any framework
to upload their content using the Django REST API.

The entire application is contained within the `backend` folder.

`config.ru` is a minimal Rack configuration for unicorn.

`run-tests.sh` runs a simplistic test and generates the API
documentation below.

It uses `run-curl-tests.rb` which runs each command defined in
`commands.yml`.

## Install dependencies 

    python -m pip install requirements.txt 

## Run the app

    python manage.py runserver

## Run the tests

   python manage.py test 
   

# REST API

The Authentication REST API to the example app is described below.

## Login

### Request

`POST /API/login`

    curl -i -H 'Accept: application/json' -d 'email=example@example.com&password=test123'  http://localhost:8000/API/login/

### Response

    HTTP/1.1 200 OK
    Date: Thu, 24 Feb 2023 12:36:30 GMT
    Status: 200 OK
    Content-Type: application/json
    Content-Length: 2

    {"token":2304787d8978979789d,"refresh":"34543534bb3453434c34x345345}

## GoogleOuth

### Request

`POST API/rest-auth/google_login/`

    curl -i -H 'Accept: application/json' -d 'access_token='2304787d8978979789d'&code=''  http://localhost:8000/API/rest-auth/google_login/

### Response

    HTTP/1.1 200 OK
    Date: Thu, 24 Feb 2023 12:36:30 GMT
    Status: 200 OK
    Content-Type: application/json
    Content-Length: 2

    {"token":2304787d8978979789d,"refresh":"34543534bb3453434c34x345345}

## Register

### Request

`POST API/rest-auth/google_login/`

    curl -i -H 'Accept: application/json' -d 'email='person@example.com'&password1='Admin123@'&password2='Admin123@'  http://localhost:8000/API/register/

### Response

    HTTP/1.1 200 OK
    Date: Thu, 24 Feb 2023 12:36:30 GMT
    Status: 200 OK
    Content-Type: application/json
    Content-Length: 2

    {"token":2304787d8978979789d,"refresh":"34543534bb3453434c34x345345}

## Create a new Thing

### Request

`POST /thing/`

    curl -i -H 'Accept: application/json' -d 'name=Foo&status=new' http://localhost:7000/thing

### Response

    HTTP/1.1 201 Created
    Date: Thu, 24 Feb 2011 12:36:30 GMT
    Status: 201 Created
    Connection: close
    Content-Type: application/json
    Location: /thing/1
    Content-Length: 36

    {"id":1,"name":"Foo","status":"new"}


# REST API

The REST API to the example app is described below.

## Get list of Things

### Request

`GET /thing/`

    curl -i -H 'Accept: application/json' http://localhost:7000/thing/

### Response

    HTTP/1.1 200 OK
    Date: Thu, 24 Feb 2011 12:36:30 GMT
    Status: 200 OK
    Connection: close
    Content-Type: application/json
    Content-Length: 2

    []

## Create a new Thing

### Request

`POST /thing/`

    curl -i -H 'Accept: application/json' -d 'name=Foo&status=new' http://localhost:7000/thing

### Response

    HTTP/1.1 201 Created
    Date: Thu, 24 Feb 2011 12:36:30 GMT
    Status: 201 Created
    Connection: close
    Content-Type: application/json
    Location: /thing/1
    Content-Length: 36

    {"id":1,"name":"Foo","status":"new"}

## Get a specific Thing

### Request

`GET /thing/id`

    curl -i -H 'Accept: application/json' http://localhost:7000/thing/1

### Response
