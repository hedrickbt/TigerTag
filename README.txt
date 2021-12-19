TigerTag

The goal of this project is to provide tags to Plex for image libraries.  The automatic Plex tagging
support is very poor, even with a paid account.  It will only index up to 1000 images per month.

TigerTag will go through all images in a Library Section and apply engines based on how TigerTag has been
configured.  This avoid writing any Plex plugins which have fallen out of favor with Plex and while can
still be written the support is no longer being developed.

Currently supported tagging engines

1. Imagga - the same one that Plex uses, BUT you can purchase an API key and tag as many images per month as your
license allows.  This is an object recognition engine.  This online service (SAAS) will allow you to scan
1000 images for free, per month.
Original article: https://imagga.com/blog/batch-image-processing-from-local-folder-using-imagga-api/
Original source: https://bitbucket.org/snippets/imaggateam/LL6dd

2. Compreface - a free facial recognition engine that you can self-host with Docker.  Very easy to set up a local
server.  Tiger tag will use a faces.yaml configuration file you supply as well as a faces images folder,
you supply, to check each of the images in your Plex Library Section.


Making flask into container
https://runnable.com/docker/python/dockerize-your-flask-application

Example DB URLs
https://docs.sqlalchemy.org/en/14/core/engines.html

Configuration - Environment Variables
ENGINE_<ENGINE_NAME>_NAME=<EngineClassName>
ENGINE_<ENGINE_NAME>_ENABLED=<True|False>
ENGINE_<ENGINE_NAME>_<OTHER_ATTRIBUTES>=<VALUE>
DB_URL=<VALUE>

Ex: for tigertag.imagga
ENGINE_IMAGGA_NAME=tigertag.imagga
ENGINE_IMAGGA_ENABLED=True
ENGINE_IMAGGA_API_KEY=<VALUE>
ENGINE_IMAGGA_API_SECRET=<VALUE>
ENGINE_IMAGGA_API_URL="https://api.imagga.com/v2"
DB_URL="sqlite:///tigertag.db"

Look in main.py for an in-depth example of environment variables

Database Lifecycle
create    alembic upgrade head
status    alembic current
history   alembic history --verbose
revise    alembic revision -m "whatever you are going to do"
    This creates a file where you do your work
downgrade alembic downgrade <how many steps. ex: -1>
revision  alembic upgrade <specific revision. ex: ae10>
delete    alembic downgrade base
upgrade   alembic upgrade <specific revision, ex: head>

To clean up/recreate db you can:
1. use alembic
alembic downgrade -1  (until all changes are gone)
alembic upgrade head



Other things to look at
MachineBox / Objectbox (facebox?) - COST?
Compreface - face
Luminoth - object
OpenCV - object
  https://www.youtube.com/watch?v=HXDD7-EnGBY&ab_channel=Murtaza%27sWorkshop-RoboticsandAI
