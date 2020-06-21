# mentorAPI

Mentor API server written in python3, using cherrypy as a server framework and PostgreSQL for storing contact (e-mail, social media etc.) and approximately location information about the user who wants to ... and who provides this kind of information to the (non)authorized public by entering it into _mentorAPI_'s database by using _mentorAPI_ or one of the frontends available for it.

## Create database

Click [here](database/README.md) for a how to create the database mentorAPI needs.

## Test OAuth and mentorAPI's log in system

Start mentorAPI by issueing `python3 service.py` and by reading [this README file](test/README.md).

# Thank You

@hauke96 for explaining me the security/cryptographic and oauth stuff :)
