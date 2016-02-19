# Welcome to Baleen

**Complete documentation coming soon!**

## Quick Start

This quick start is intended to get you setup with Baleen in development mode (since the project is still under development). If you'd like to run Baleen in production, please see the [documentation][rtfd_href].

1. Clone the repository

        $ git clone git@github.com:bbengfort/baleen.git
        $ cd baleen


2. Create a virtualenv and install the dependencies

        $ virtualenv venv
        $ source venv/bin/activate
        $ pip install -r requirements.txt

3. Add the `baleen` module to your `$PYTHONPATH` via the virtualenv.

        $ echo $(pwd) > venv/lib/python2.7/site-packages/baleen.pth

4. Create your local configuration file. Edit it with the connection details to your local MongoDB server.  This is also a good time to check and make sure that you can create a database called Baleen on Mongo.

        $ cp conf/baleen-example.yaml conf/baleen.yaml

    The YAML file should look similar to:

        debug: true
        testing: false
        database:
            host: localhost
            port: 27017
            name: baleen

5. Run the tests to make sure everything is ok.

        $ make test

6. Make sure that the command line utility is ready to go:

        $ bin/baleen --help

7. Import the feeds from the `feedly.opml` file in the fixtures.

        $ bin/baleen import fixtures/feedly.opml
        Ingested 101 feeds from 1 OPML files

8. Perform an ingestion of the feeds that were imported from the `feedly.opml` file.

        $ bin/baleen ingest

Your Mongo database collections should be created as you add new documents to them, and at this point you're ready to develop!
