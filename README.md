# SpoofCheck Self Test
Web application that lets you test if your domain is vulnerable to email spoofing.

## NOTE: This application is still in development.

# Installation:
This application is designed to be used as a service. However, if you want to host this yourself, do the following:
        
        apt-get install python-pip rabbitmq-server sqlite memcached npm
        
        npm install -g bower
        
        git clone https://github.com/bishopfox/spoofcheckselftest.git
        
        cd spoofcheckselftest
        
        pip install -r requirements.txt
        
        /usr/local/bin/bower install
        
RECAPTCHA: put the site key in static/ng-app/base.js. set the RECAPTCHA_SECRET_KEY environment variable with the secret key.
        
# Running:
    ./selftest.py --api
    ./selftest.py --celery
    
Then visit http://localhost:8888 in a web browser
