:: ASE Flask skeleton script
::
:: set -e

:: export the variables for flask
set FLASK_ENV=development
set FLASK_DEBUG=0
set FLASK_APP=monolith
set FLASK_REDIS2_URL=0.0.0.0
:: execute the flask run command
flask run
