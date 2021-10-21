:: ASE Flask skeleton script
::
:: set -e

:: export the variables for flask
$Env:FLASK_ENV="development"
$Env:FLASK_DEBUG="0"
$Env:FLASK_APP="monolith"

:: execute the flask run command
flask run

