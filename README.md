# Blood Connect
An appliction to make it easy to bring the donors closer to the ones in need.

## Starting the application

The required python libraries are present in requirements.txt file
run `pip install -r requirements.txt` to get all dependencies.

### Download a `client_credentials.json` file

1. Open the Credentials page (https://console.developers.google.com/apis/credentials) in the API Console.
2. Click Create credentials > OAuth client ID.
3. Complete the form. Set the application type to Web application. 
4. Add in `Authorized redirect URIs` {address of the server}/auth/callback
5. save and download the `client_credentials.json` to project's root directory

### Start the web-application
1. bloodconnect.db is present in the root directory of the project
2. run `flask run`
3. open {server-host-name}:8080

## Structure

The project contains:
1. application.py that holds the server-side logic of the application
 - This contains routes
   - `/` renders the index of the application
   - `/authroize` redirects to google for authentication
   - `/auth/callback` receives callback from google after authentication
   - `/clear` logs out the user session
   - `/revoke` removes google app permission from users account
   - `/register-donor` saves donor details and renders register donor UI
   - `/notify-donors` saves donation requests and renders UI for donation requests
   - `/archive-request/<message_id>` route for AJAX call to archive donation requests
 2. `static` directory stores applications javascript and css file
 2. `tempalates` directory stores the HTML tempalates of the application,
    - layout.html has the layout for all pages of the application. This links to CSS and JS file. The application uses bootstrap and jquery
   
