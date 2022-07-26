from node import Node
import socket
import Retica
import Retica.Render
import Retica.Sockets

node = Node("0x0", (socket.gethostname(),880), "test-one")

def runtime(first_run):
    if first_run:
        retica = Retica.Server(__name__)

        templator = Retica.Render.TemplateRender(retica,template_dir="Templates")

        @retica.create_endpoint("/")
        def index(request: Retica.Request.request, response: Retica.Response.response, **data):
            response.body = templator.render("index.html", data)

        http_socket = Retica.Sockets.HTTP_Socket(Retica.Sockets.gethostname(), 80)

        if __name__ == "__main__":
            retica.run([http_socket])
        

if __name__ == "__main__":
    node.runtime = runtime
    node.run()