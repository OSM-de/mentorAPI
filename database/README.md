# Creating database

1. change current working directory to `database` (this README is located at) (if not done already)
2. Execute `python3 setup.py`. If you execute the script again and the database exists, the script will update the database (if necessary) and rebuild the view used by _mentorAPI_'s search feature.
3. Create a user (e.g. `mentorapi_user`) for _mentorAPI_ and make `service.py` (located in the root dir) start under that user
4. Give the user permission to execute "select" and "insert". Give it also the SQL unrelated permission "Inherit", "Can Login" needed to operate with the database.

Get in [DB Operations](dboperations.md) some queries which mentorAPI uses. But head over to [../database/queries.yml](../database/queries.yml) for a complete and up to data version of all used queries which mentorAPI uses.
