from apistar import App, Include

from blockchain.client import config
from blockchain import api

routes = [
    Include('/node', name='node', routes=api.routes),
]

app = App(routes=routes)


def start_server():
    app.serve(config['SERVER']['Host'], int(config['SERVER']['Port']), debug=False)
