# ttt_cmd: tictactoe slash command

The app is hosted on heroku at ticslashtoe.herokuapp.com

## Local Installation & Set-Up

Clone the repo:

`git clone`

If not already installed, install virtualenv:

`pip insall virtualenev`

Navigate to application directory:

`cd ttt_cmd`

Create a virtual environment:

`virtualenv venv`

...And activate it:

`source venv/bin/activate`

Download the dependencies:

`pip -r requirements.txt`

If necessary (running locally), configure the integration to point to an ngrok or some other localhost tunnel
Start-up the server

`python app.py`

## Database migration

The database tables have already been created a seeded with an example game; however, please note that this postgres instance uses an add-on that supports JSON fields

## Approach

I first tackled my approach to game-play: basic turn-by-turn moves and what sequence of moves constitutes a win. I next set-up the basics: server and database. I gave a great deal of thought into how the game should be modeled and how commands should be parsed and processed. My biggest concerns when writing this portion of the program were extensibility and maintainability.

I considered using slacker, a python wrapper for the slack-api when I was checking to make sure I wasn't 're-inventing the wheel', but I instead took the opportunity to use the slack API pretty directly.