## Please reference the root README for instructions on setting up the project

1. python -m venv venv
2. Change the interpreter to the python.exe file in the scripts folder of the venv
3. .\venv\Scripts\activate
4. pip install -r requirements.txt
5. redis-cli - make sure that it's running
6. psql - make sure this is running too
7. update your env file to match
8. run flask db upgrade to upgrade your db
9. run init_db to populate your db with preset difficulties
