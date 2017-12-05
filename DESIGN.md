This application allows users to signs up using their google account and then allows to collaborate and check donation requests.

# Authorization and authentication

The application makes use of the Google API for authentication and authorization https://developers.google.com/api-client-library/python/auth/web-app.

This enabled me to have secure login, signup flows without re-engineering the authentication design and have this working with minimum effort
The API documentation for the use of the API is also extensive and made it easy to implement

# Databse

- The application makes use of sqlite3 for database needs.
- The databse name is bloodconnect.db
- There are two tables in this databse
    - user_profile table stores the profile details for all users that signup with the application
    - donation_requests table stores messages for donors, along with the information on who created the message, blood groups needed for donation and archival flag

# Application Server

The application uses flask for the application server and is hugely inspired by the application server design in pset7.
The server defines application routes and by the use of decorator function specific application routes impose a logged in session to be in place for a successful response.

The use of flask_session enables maintaining secure logged in session

# Django templates

The HTML makes use of Django templates and is again hugely inspired by pset7.
- All pages derive from a layout and individual pages define only the responsible functionalities.

# Bootstrap

The styles in this application makes use of bootstrap and helps bring in trendy look and feel with minimum effort.

# jQuery

The application does not use a lot of javascript, but makes use of jQuery for an AJAX call
