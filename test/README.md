# OAuth test

Executing `python3 -m http.server 8080` inside the directory this file is located in and opening http://localhost:8080/login.html let's you log in to OSM and to authorize the application _mentor_. Opening http://localhost:8080/logout.html let's you log out of _mentor_ (it removes just the cookie. _mentor_ revokes the access token immediately after log in and receiving user details so it is already removed before you log out from _mentor_)

**Note:** Going to http://localhost:8080/login.html won't open the OAuthorisation from OpenStreetMap. Instead it provides you with the url you can use to authorize _mentor_

**Note:** Please revoke the authorisation manually by going to the oauth settings resisting in your OSM account profile.

# Region test

Execute `python3 region.py` for a demonstration how the 'region' module works.
