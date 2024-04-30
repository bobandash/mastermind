# Mastermind
This rendition of Mastermind was done as a part of my application to LinkedIn's REACH apprenticeship program. The application includes the core features of Mastermind, configurable difficulties that the user can choose from, and the multiplayer functionality using Socket.io. I also implemented points for each completed round; however, I did not have the opportunity to display the final score of games in the frontend.<br /><br />

## Preview
![image](https://github.com/bobandash/mastermind/assets/74850332/cb2b51b2-29f5-46eb-953e-a2e197ee7f21)
![image](https://github.com/bobandash/mastermind/assets/74850332/cc73e0f0-1b78-4ebf-9a74-53e3bc0aeaba)


## Relevant Technologies Used:
Backend:
- Language: Python
- Web Framework: Flask
- Database: PostgreSQL and Redis
- Important Libraries: Socket.io

Front-End:
- Language: Typescript
- Important Libraries: TailwindCSS, Axios, Socket.io


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
   - Create your virtual environment - "python -m venv venv" 
   - Activate your virtual environment - ".\venv\Scripts\activate" 
   - Download all the dependencies in the virtual environment - "pip install -r requirements.txt"
   - Select your Python interpreter (if you are using VSCode, press control+shift+p and type > python: select interpreter) and select the file at venv/Scripts/python.exe
   - Create a .env file in the server directory and put your PostgreSQL database URL, Redis URL, and secret key (follow the format in the .sample.env)
   - Create the models in your local PostgreSQL database by running "python -m flask db upgrade"
   - Initialize the database with all the difficulty options "python -m init_db"
   - Start the application with "python -m app"
3. Change the working directory to the client (cd client) and follow these steps:
   - Install all the necessary dependencies with "npm install"
   - Start the client side with "npm run dev"
5. Go to localhost:5173, and your application should be running!

## Thought Process and Code Structure
![image](https://github.com/bobandash/mastermind/assets/74850332/d0704038-5eb8-44a8-bb51-452b6614e468)

I decided to use a relational database (PostgreSQL) for this application because many of the schemas in the mastermind game have a clear hierarchy (a game has multiple rounds, a round has multiple turns, etc.).

In regards to multiplayer and singleplayer mode, by default, a singleplayer game will have one round, and multiplayer games have 2, 4, 6, or 8 rounds maximum. This is why in my database, games and rounds have a one-many relationship.

Before beginning the project, I was also researching a lot about server-side sessions vs JWT while deciding my implementation, but I chose to use server-side sessions because, if I wanted to make this into an online multiplayer game, it would be better to use a stateful method of tracking whether or not the user is signed in. In regards to authentication, I wanted automatic authentication without any username or passwords in my application (similar to games like CodeNames online or Pokemon Showdown), with the option to register a persistent login in the future, similar to how games like Pokemon Showdown allow you to view and save your stats if you sign in. I also decided to use server-side sessions to prevent the user from accessing resources that they were unauthorized to access (such as games or rounds they were not a part of, the secret code for ongoing rounds, etc).

In regards to routing and the backend structure, the backend routes were structured in this format:
- /games - handle logic related to getting game details, creating new games, and creating rounds inside games
- /rounds - handle logic related to getting specific round details, getting the secret code, and creating new turns within the rounds
- /auth - handle authentication and creating accounts for persistent state
- /users - get current user details and allow users to edit their username
- /rooms - allow users to create, join rooms, and edit rooms if they are the host of the room

## Potential Backend Improvements
- Keeping and displaying score of the multiplayer games
- Tracking the stats of the user
- Fetching the match history against a certain player
