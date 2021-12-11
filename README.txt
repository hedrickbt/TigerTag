Original article: https://imagga.com/blog/batch-image-processing-from-local-folder-using-imagga-api/
Original source: https://bitbucket.org/snippets/imaggateam/LL6dd

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
ENGINE_IMAGGA_INPUT_LOCATION="data/images/input"
DB_URL="sqlite:///tigertag.db"

Database Lifecycle
create    alembic upgrade head
status    alembic current
history   alembic history --verbose
revise    alembic revision -m "whatever you are going to do"
    This creates a file where you do your work
downgrade alembic downgrade <how many steps. ex: -1>
revision  alembic upgrade <specific revision. ex: ae10>
delete    alembic downgrade base

