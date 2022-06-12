# Dermanalyze API

=======

### API for Dermanalyze app.

Language used : **Python**.

Framework used : **FastAPI**.

Database used : **PostgreSQL**.

Latest update : **v.1.5**.

To run the API locally, you need to :
- Make a virtual environment and activate it.
- Run uvicorn.
- Make a .env file with the required variables and values.
- Install and configure PostgreSQL in your machine.
- Monitor the database from pgAdmin.

Virtual Machine Specs :
- Machine Type : n1-standard-1
- OS : Ubuntu 20.04.4 LTS
- Boot Disk Size : 10GB

To run the API on Google Cloud Platform, you need to:
- Create a virtual machine, preferably with static IP.
- Create firewall rules, such as for HTTP, HTTPS, SSH, etc.
- SSH into the machine, and update the packages inside.
- Check for Python and pip, if not installed, install it first.
- Install virtualenv and PostgreSQL.
- Setup the configuration for PostgreSQL and pgAdmin.
- Create a new user with root access for security purposes, then login with that user.
- Create and setup the virtual environment (cloning the code from github, installing the requirements from requirements.txt, etc).
- Setup the environment variables. After setting up the env. variables, you can try to run the API via uvicorn.
- Install Gunicorn in virtualenv.
- Create a service file for the API.
- Install and setup nginx.

