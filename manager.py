import click

from usor import create_app
from usor.models.models import User, Role

app = create_app()


@app.cli.command()
def app_init():
    """Initialize app."""
    for elem in ["admin", "user"]:
        role = Role(elem)
        role.save()

    user = User("admin", "admin@locahost.loc", "admin")
    user.email_verify = True
    user.activate = True
    user.roles.append(Role.objects(name="admin").get())
    user.save()

    click.echo("Initialize {}".format(app.name))


if __name__ == '__main__':
    app.run()
