
This is the API and data transformation tools for the lobby transparency
project. It combines information from several datasets released by the 
European Union, including the register of interests, EP accreditations, 
expert group memberships.

This package contains a python application with two parts: the ``data`` 
submodule contains the ETL tools used to extract, clean and normalize
the lobbying data. The remainder of the application is a REST API that
can be queried to retrieve information about entities within the
database.


Installing the application
==========================

To install the application, first set up a virtualenv and install the 
dependencies: 

    virtualenv env
    . env/bin/activate
    git clone https://github.com/pudo/lobbyfacts.git
    cd lobbyfacts
    pip install -r requirements.txt
    pip install -e . 

Next, you need to create two databases: ETL and production. Both should 
be on PostgreSQL:

    createdb -E utf-8 lobbyfacts
    createdb -E utf-8 lobbyfacts_etl

Next, you need to create a local settings file by copying the template 
defaults: 

    cp lobbyfacts/default_settings.py settings.py 
    export lobbyfacts_SETTINGS=settings.py
    
Edit the settings file to configure your database connections. To run
the full ETL process, you will also need an account and API key on these
two web services: 

* http://nomenklatura.okfnlabs.org/
* http://pybossa.com/

Finally, you can create the production database, including the full
schema (the ETL schema is created implicitly):
    
    python lobbyfacts/manage.py createdb


Running the application
=======================

To run the application, you'll use the management script. To extract 
and prepare data, this sequence of commands is used: 

    python lobbyfacts/manage.py extract
    python lobbyfacts/manage.py transform
    python lobbyfacts/manage.py load

After having created a production database, the API server can be run
with this command:

    python lobbyfacts/manage.py runserver

It will be bound to http://localhost:5000 by default.


Copying and License
===================

The code in this repository is (C) 2011-2012, Friedrich Lindenberg and 
others. It is open and licensed under the GNU Affero General Public
License (AGPL) v3.0 whose full text may be found at:

http://www.fsf.org/licensing/licenses/agpl-3.0.html


