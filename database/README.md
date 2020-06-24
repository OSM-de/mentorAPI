# Creating database

1. change current working directory to `database` (this README is located at) (if not done already)
2. Execute `sh createdb.sh` as the user you want to handle the database
3. Create a user for _mentorAPI_ and make it start under that user
4. Give the user permission to execute "select" and "insert". Give it also the SQL unrelated permission "Inherit", "Can Login" needed to operate with the database.

Get in [DB Operations](dboperations.md) some queries which mentorAPI uses. But head over to [../lib/database.py](../lib/database.py) for a complete and up to data version of all used queries which mentorAPI uses.
