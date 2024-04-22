# Mastermind
This rendition of Mastermind was done as a part of my application to LinkedIn's REACH apprenticeship program. The application includes the core features of Mastermind, configurable difficulties that the user can choose from, and the multiplayer functionality using Socket.io. <br /><br />

## Preview
![image](https://github.com/bobandash/mastermind/assets/74850332/cb2b51b2-29f5-46eb-953e-a2e197ee7f21)
![image](https://github.com/bobandash/mastermind/assets/74850332/cc73e0f0-1b78-4ebf-9a74-53e3bc0aeaba)


## Relevant Technologies Used:
Backend:
- Language: Python
- Web Framework: Flask
- Database: PostgreSQL and Redis

Front-End:
- Language: Typescript
- Important NPM Libraries: TailwindCSS, Axios


## Installation and Running the Project
### Pre-Setup
Please ensure that you have redis, python, PostgreSQL downloaded on your machine.
If you are using windows and cannot find a compatible download link for redis, please use: https://github.com/redis-windows/redis-windows.
1. Start up a local instance of PostgreSQL (open the psql shell and create a local database on your machine, pressing enter in the psql terminal to create a password)
2. After install redis, go to your terminal and type redis-cli to view the url of your redis database
3. Save the URLs of the PostgreSQL and Redis database (will be important in the set-up step with the .env file)

### Set-up
1. Clone the repository (run "git clone https://github.com/bobandash/mastermind.git") in a IDE of your choice
2. Change the working directory to the server (cd server) and follow these steps:
   - Activate your virtual environment - ".\venv\Scripts\activate" - 
   - Download all the dependencies in the virtual environment - "pip install -r requirements.txt"
   - Select your Python interpreter (if you are using VSCode, press control+shift+p and type > python: select interpreter) and select the file at venv/Scripts/python.exe
   - Create a .env file in the server directory and put your PostgreSQL database URL, Redis URL, and secret key (follow the format in the .sample.env)
   - Create the models in your local PostgreSQL database by running "python -m flask db upgrade"
   - Initialize the database with all the difficulty options "python -m init_db"
   - Start the application with "python -m app"
3. Change the working directory to the server (cd server) and follow these steps:
   - Start the client side with "npm run dev"
4. Go to localhost:5173, and your application should be running!

## Thought Process and Code Structure
![image](https://github.com/bobandash/mastermind/assets/74850332/e0feef18-a53c-4400-9862-2de775129da4)

I decided to use a relational database (PostgreSQL) for this application because many of the schemas in the mastermind game have a clear hierarchy (a game has multiple rounds, a round has multiple turns, etc.). Before beginning the project, I was also researching a lot about server-side sessions vs JWT while deciding my implementation, but I chose to use server-side sessions because, if I wanted to make this into an online multiplayer game, it would be better to use a stateful method of tracking whether or not the user is signed in. 

In regards to authentication, I wanted automatic authentication without any username or passwords in my application (similar to games like CodeNames online or Pokemon Showdown) because I needed to use the session token to prevent the user from accessing resources that they were unauthorized to access (such as games or rounds they were not a part of), secret code for ongoing rounds, etc).

In regards to routing, the game logic routes were primarily structured in this format:
- /games - handle everything related to getting game details, creating new games, and creating rounds inside games
- /rounds - handle everything related to getting specific round details and creating new turns within games
- /auth - handle authentication and creating accounts for persistent state
- /user - get current user details and edit username
