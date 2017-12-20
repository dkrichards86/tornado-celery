import sys
import os
from tornado import autoreload, escape, gen
from tornado.ioloop import IOLoop
from tornado.queues import Queue
from tornado.web import Application, RequestHandler, StaticFileHandler
from tornado.websocket import WebSocketHandler, WebSocketClosedError

from tasks.tasks import slow_add
from tasks.utils import async_task

dirname = os.path.dirname(__file__)
TEMPLATE_PATH = os.path.join(dirname, 'templates')
ASSET_PATH = os.path.join(TEMPLATE_PATH, 'assets')


class IndexHandler(RequestHandler):
    def get(self):
        """
        Handle loading of the index page.
        """
        self.render('index.html')


class SocketHandler(WebSocketHandler):
    @gen.coroutine
    def _add(self, num1, num2):
        """
        Pass two numbers to an asynchronous add task.

        :param num1: First digit to add
        :param num2: Second digit to add
        """
        # Display a message so the user knows the task has started
        self.submit({'type': 'message', 'content': 'Calculating..'})

        # `yield` waits for the task to return, unblocking IOLoop so others can
        # share resources.
        total = yield async_task(slow_add, args=[num1, num2])

        # Return the total to the UI through the websocket
        self.submit({'type': 'message', 'content': f'Sum is {total}'})

    def _close(self):
        """
        Handle client disconnection. Deregister so message aren't broadcast.
        """
        self.registered = False

    def initialize(self):
        """
        Initialize the handler by starting a joinable message queue. This method
        is derived from WebSocketHandler, and ultimately RequestHandler.
        """
        self.messages = Queue()

    def on_close(self):
        """
        On a close event, call the close handler.
        """
        self._close()

    def on_message(self, message):
        """
        Receive a message from the socket.

        :param message: JSON encoded message
        """
        msg = escape.json_decode(message)

        if msg["type"] == "run":
            IOLoop.current().spawn_callback(self._add, int(msg['num1']), int(msg['num2']))

    def open(self):
        """
        Handle a new client connection. Register so message are broadcast. 
        Invoke run(), starting queue monitoring.
        """
        self.registered = True
        self.run()

    @gen.coroutine
    def run(self):
        """
        As long as we're registered, asynchronously poll the messages queue.
        """
        while self.registered:
            # `yield` delays execution of this loop until the generator returns.
            # Only once there is a message does this method start executing again.
            message = yield self.messages.get()
            self.send(message)

    def send(self, message):
        """
        Write a message to the client. If WebSocketClosedError is raised,
        disconnect the client.

        :param message: Message to send forward to client
        """
        try:
            self.write_message(message)
        except WebSocketClosedError:
            if self.registered:
                self._close()

    def submit(self, message):
        """
        Add a message to the queue.

        :param message: Message to send forward to client
        """
        self.messages.put(message)


class Server(Application):
    def __init__(self, args):
        """
        Set up the Tornado server.

        :param args: argparse object containing host and port
        """
        settings = {
            "template_path": TEMPLATE_PATH
        }

        routes = [
            ('/((\w*).js)', StaticFileHandler, {"path": ASSET_PATH}),
            ('/', IndexHandler),
            ('/socket', SocketHandler)
        ]

        self.host = args.host
        self.port = args.port

        super().__init__(routes, **settings)

    def run(self):
        """
        Run the server.
        """
        self.listen('8888', '0.0.0.0')
        try:
            print(f'Starting tornado server on http://{self.host}:{self.port}')
            IOLoop.instance().start()
        except KeyboardInterrupt:
            sys.exit(0)
