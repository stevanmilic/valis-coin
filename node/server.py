from apistar import App, Include

from node.client import config
from node import api

routes = [
    Include('/node', name='node', routes=api.routes),
]

app = App(routes=routes)


def start_server():
    app.serve(
        config['SERVER']['Host'],
        int(config['SERVER']['Port']),
        debug=True,
        use_reloader=False,
    )
