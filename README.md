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

The database tables have already been created a seeded with an example game; however, please note that this Postgres instance utilizes the JSON type.

## Approach

I first tackled my approach to game-play: basic turn-by-turn moves and what sequence of moves constitutes a win. I next set-up the basics: server and database. I gave a great deal of thought into how the game should be modeled and how commands should be parsed and processed. My biggest concerns when writing this portion of the program were extensibility and maintainability.

### Technology Choices

Given the prompt, I wanted to set up a dead-simple server, and my go-to for this is Flask. My favorite aspect of Flask is adding technologies 'drop-wise' as needed by the problem at hand, rather than having everything pre-rolled in. For example, when I read the prompt, I considered how I would model the game, game-state (board), and users in a database, or if I would even use a database at all (instead opting for an in-memory solution). When I settled on creating a Postgres instance for extensibility, I chose an ORM to model the aforementioned concepts. With the wonderful simplicity of tic-tac-toe and the specifications of the challenge, I again opted for a simple technology and chose PeeWee instead of one with a lot of meat and overhead, such as SQLAlchemy. Both PeeWee and Postgres allowed me to store JSON as a type, which helped settle my decision as this is how I wanted to store game-state rather than column-wise position tracking.  In the vein of simplicity, I might have chosen SQLite as a database, but unfortunately this technology is not supported by Heroku where my app is currently hosted.

When making technology decisions, I always hope to avoid 're-inventing the wheel'.  I saw that slacker was available as an api wrapper, but I instead took the opportunity to use the slack API pretty directly.

--

Thank you so much for this opportunity to create something fun and interesting for Slack. I cannot stress enough how much I enjoyed working with the Slack API.
