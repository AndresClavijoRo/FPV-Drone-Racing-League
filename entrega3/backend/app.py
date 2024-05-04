import click

from build_flask_app import create_flask_app
from models import db
from load_testing import load_test

app = None

flask_app = create_flask_app()

app = create_flask_app()
db.init_app(app)
db.create_all()


@app.cli.command("load-test")
@click.option("--total-tasks", default=50, help="Total tasks to create")
@click.option("--total-minutes", default=10, help="Total tasks to create")
def load_test_tasks(total_tasks, total_minutes):
  load_test(app, total_tasks, total_minutes)
