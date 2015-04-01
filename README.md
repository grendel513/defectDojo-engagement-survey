       ___      ___        __  ___         _         
      / _ \___ / _/__ ____/ /_/ _ \___    (_)__      
     / // / -_) _/ -_) __/ __/ // / _ \  / / _ \     
    /____/\__/_/ \__/\__/\__/____/\___/_/ /\___/  __ 
      / __/__  ___ ____ ____ ____ __ |___/_ ___  / /_
     / _// _ \/ _ `/ _ `/ _ `/ -_)  ' \/ -_) _ \/ __/
    /___/_//_/\_, /\_,_/\_, /\__/_/_/_/\__/_//_/\__/ 
      / __/_ /___/__  _/___/__ __                    
     _\ \/ // / __/ |/ / -_) // /                    
    /___/\_,_/_/  |___/\__/\_, /                     
                          /___/                                      

defectDojo_engagement_survey
===========================

DefectDojo Engagement Survey extends django-DefectDojo
(https://github.com/rackerlabs/django-DefectDojo) by incorporating survey(s)
associated with each engagement to help develop a test strategy.  The
questions within these surveys have been created by the Rackspace Security
Engineering team to help identify the attack vectors and risks associated
with the product being assessed.

Installation
------------

If you are using virtual environments, make sure you activate the appropriate one
before installation.

clone the repository:

    git clone https://github.rackspace.com/jay7958/defectDojo-engagement-survey.git

run the install script:
    
    cd defectDojo-engagement-survey
    pip install .
    
synchronize your database (Django < 1.7 with south):

    python manage.py schemamigration defectDojo-engagement-survey  --initial
    python manage.py migrate defectDojo-engagement-survey
    
synchronize your database (Django >= 1.7):

    python manage.py makemigrations defectDojo-engagement-survey
    python manage.py migrate
    
## Load initial fixtures

The Rackspace Security Engineering team has created an initial set of surveys, if you want to import them run:

    python manage.py loaddata /path_to/initial_surveys.json
    
**NOTE:** Before installing the fixtures, add a Question via the Django Admin.  Then use mysql to
`select * from defectDojo_engagement_survey_question;`, this will give you the `polymorphic_ctype_id` for your system.

Update the `initial_surveys.json` to reflect your ID number, this can be accomplised with `vim` with `:%s/70/NEW/g` where
`NEW` is your `polymorphic_ctype_id`

## Configuration

### `settings.py`

Add the following to the `INSTALLED_APPS` setting: 

    INSTALLED_APPS = (
        ...
        'defectDojo_engagement_survey',
        'dojo',
        'polymorphic',   # provides admin templates
        "overextends",
        ...
    ) 

Notice that `defectDojo_engagement_survey` is before `dojo`, this is because
it extends and overrides features.

### `urls.py`

Add the following:

`from defectDojo_engagement_survey.urls import urlpatterns as survey_urls` 

`urlpatterns += survey_urls`

Usage
=====

The Engagement Survey functionality will now be available under each engagement.  
The creation of surveys is done via Django's Admin Interface
        
Questions or Comments?
======================

Let me know if you have any questions or comments.  Send me an email to jay.paz@gmail.com

Contributing
============

I love getting patches! Send me a pull request.  


