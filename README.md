# Warbler
A Twitter Clone - built using Python, Flask, and PostgreSQL

## Live Demo
[Live Demo](https:https://warbler-r22-loni.herokuapp.com/)

## Setup
1. Clone or fork this repository
2. Setup a virtual environment (inside the repo directory)
* ```python3 -m venv venv```
* ```source venv/bin/activate```
* ```pip3 install -r requirements.txt```
3. Create the database
* ```createdb warbler```
* ```python3 seed.py```
4. Start the Server
* ```flask run```

## Tests: 
1. Create the test database
* ```createdb warbler-test```
2. Run tests:
* Run all tests: ```python3 -m unittest```
* Run specific file: ```python3 -m unittest test_file_to_run.py```

## Technologies
* Flask
