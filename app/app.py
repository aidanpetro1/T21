"""
app.py
------
Entry point for the Clinical Timeline web application.

Uses only Python's standard library — no external packages needed.

How it works
------------
  1. Python's built-in HTTPServer handles incoming browser requests.
  2. GET /        — reads templates/timeline.html, injects JSON data into
                    the two template placeholders, and sends the page.
  3. GET /api/events   — returns all clinical events as raw JSON.
  4. GET /api/problems — returns the problem list as raw JSON.

The template placeholders look like:  {{ events_json }}
app.py does a simple string replacement to inject the data.
(A production app would use a real template engine like Jinja2.)

To run:
    cd C:\\T21_project\\app
    python app.py

Then open http://localhost:5000 in your browser.
Press Ctrl+C to stop the server.

Key Python concepts used in this file
=====================================

HTTP Servers and the Request/Response Cycle:
  When you visit a website in your browser, it sends an HTTP request to a web
  server. The server reads the request (what page do you want?), then sends back
  an HTTP response (here's the page, or an error, or JSON data). This file uses
  Python's built-in HTTPServer to create a simple web server that listens for
  incoming requests and sends responses.

Class Inheritance:
  We create a class called TimelineHandler that "inherits from" (or "extends")
  SimpleHTTPRequestHandler. This means TimelineHandler gets all the built-in
  functionality of SimpleHTTPRequestHandler (like knowing how to speak HTTP),
  but we can override or add our own methods to customize the behavior. Think of
  it like: "I want everything the parent class does, but with some tweaks."

Method Overriding:
  When a class inherits from a parent, it can override (replace) parent methods
  with its own custom version. For example, SimpleHTTPRequestHandler has a
  log_message() method; we override it with our own version that prints
  messages differently.

String Replacement as a Template Engine:
  A "template" is HTML with placeholders like {{ events_json }}. We load the
  HTML file, then use Python's str.replace() to swap out the placeholders
  with actual data. This is simple but not as powerful as real template engines
  like Jinja2, which support loops, conditionals, and more.

JSON Serialization:
  JSON (JavaScript Object Notation) is a text format for sending data over the
  internet. It's lightweight and widely understood by every programming language.
  json.dumps() converts a Python object (list, dict, etc.) into a JSON string
  that can be sent to the browser or saved to a file. json.loads() does the
  reverse: converts JSON text back into Python objects.

The if __name__ == "__main__" Pattern:
  When Python runs a .py file directly, it sets __name__ to "__main__". If
  another file imports this file, __name__ is set to the module name instead.
  So this pattern means: "only run main() if this file is executed directly,
  not if it's being imported by another file." This lets you write files that
  can be both run standalone or imported as modules.
"""

# ============================================================================
# IMPORTS — What does each one do and why we need it
# ============================================================================

# json: Converts Python objects (lists, dicts, etc.) to/from JSON strings.
#   We use json.dumps() to convert our clinical data to JSON format so the
#   browser's JavaScript can parse it and display it.
import json

# os: Provides utilities for working with the operating system, especially
#   file paths. os.path.join() builds paths that work on Windows, macOS, and
#   Linux. os.path.dirname() and os.path.abspath() help us locate files
#   relative to where this script is running from.
import os

# http.server: Python's built-in module for creating web servers.
#   HTTPServer: A class that listens for incoming HTTP requests and calls
#               our custom handler for each one.
#   SimpleHTTPRequestHandler: A base class that knows how to speak HTTP and
#                            handle requests. We inherit from it and override
#                            methods to customize our behavior.
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Local modules we wrote:
#   models: Contains the ClinicalEvent and Problem classes that structure
#           our clinical data and provide to_dict() methods.
#   sample_data: Contains functions that load pre-made test data.
#               This lets us test the web app without needing a database.
from models import ClinicalEvent, Problem
from sample_data import load_sample_events, load_problem_list


# ============================================================================
# CONFIGURATION
# ============================================================================

# PORT: A port is a numbered "channel" on a computer for network communication.
#   Different services run on different ports (e.g., email on 25, HTTPS on 443).
#   Port 5000 is commonly used for local web development — it's usually not
#   reserved by the OS and it's above 1024, so no admin privileges needed.
#   To use a different port, change this number (e.g., PORT = 8000).
PORT = 5000

# TEMPLATE_DIR: The absolute path to the templates folder.
#   We build it piece by piece for clarity:
#   - __file__ is the path to this very file (app.py).
#   - os.path.abspath(__file__) converts it to an absolute path (no relative ../)
#     so it works no matter what directory we run the program from.
#   - os.path.dirname() extracts just the folder part (removes filename).
#   - os.path.join(..., "templates") adds "templates" to the path, using the
#     correct separator for the OS (\ on Windows, / on Unix).
#   Example: if this file is C:\T21_project\app\app.py, TEMPLATE_DIR becomes
#           C:\T21_project\app\templates
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")


# ============================================================================
# REQUEST HANDLER
# ============================================================================

class TimelineHandler(SimpleHTTPRequestHandler):
    """
    Handles all incoming HTTP GET requests.

    A request handler is a class that receives incoming HTTP requests and sends
    back HTTP responses. It's like a waiter in a restaurant: it takes the
    customer's order (the request), tells the kitchen (our code), and brings
    back the dish (the response).

    We inherit from SimpleHTTPRequestHandler, which gives us the foundation for
    speaking HTTP. We then add our own methods (do_GET, _serve_timeline, etc.)
    to customize what the server does.

    Routes (URL paths the server recognizes):
        /              -> serve the main timeline HTML page
        /index.html    -> same as /
        /api/events    -> return all clinical events as JSON
        /api/problems  -> return the problem list as JSON
        anything else  -> send a 404 "not found" error
    """

    def do_GET(self):
        """
        Called automatically by HTTPServer for every GET request.

        HTTP has different "methods" (GET, POST, PUT, DELETE, etc.) that tell
        the server what action to perform. GET means "please send me this
        resource" — it's what the browser uses when you type a URL or click a
        link. (POST is used for submitting forms, etc.)

        self.path is the URL path the browser requested, e.g., "/" or
        "/api/events". We check it to decide which method to call.
        """
        # If the user requested / or /index.html, serve the HTML page
        if self.path in ("/", "/index.html"):
            self._serve_timeline()
        # If they requested the events API endpoint, return JSON events
        elif self.path == "/api/events":
            self._serve_json(load_sample_events())
        # If they requested the problems API endpoint, return JSON problems
        elif self.path == "/api/problems":
            self._serve_json(load_problem_list())
        # If they requested something we don't recognize, send a 404 error
        else:
            self.send_error(404)

    def _serve_timeline(self):
        """
        Load the HTML template, inject clinical data, and send to the browser.

        An "HTML template" is a skeleton HTML file with placeholders for
        dynamic content. For example, the template might contain:
          {{ events_json }}
        We read the template, find these placeholders, and swap them out with
        actual data (the JSON representation of clinical events).

        This approach is simple but limited. In production, you'd use a
        template engine like Jinja2 that supports loops, conditionals, etc.
        But for a small app, string replacement is quick and understandable.

        The template contains two placeholders that are replaced here:
          {{ events_json }}   -> JSON array of all ClinicalEvent dicts
          {{ problems_json }} -> JSON array of all Problem dicts
        """
        # Step 1: Convert the clinical data to JSON strings.
        #
        # load_sample_events() returns a list of ClinicalEvent objects.
        # [e.to_dict() for e in ...] is a "list comprehension" — a compact way
        # to transform each item in a list. It's equivalent to:
        #   events_list = []
        #   for e in load_sample_events():
        #       events_list.append(e.to_dict())
        # Each to_dict() method converts a ClinicalEvent object to a dict (a
        # Python key-value map, like JSON).
        #
        # json.dumps() converts the list of dicts into a JSON string, which is
        # a text representation that browsers and other programs can parse.
        # default=str tells json.dumps what to do when it encounters a type it
        # doesn't know how to serialize (like a date object). We tell it to
        # convert those to strings automatically.
        events_json   = json.dumps([e.to_dict() for e in load_sample_events()], default=str)
        problems_json = json.dumps([p.to_dict() for p in load_problem_list()],  default=str)

        # Step 2: Read the HTML template from disk. LEFT OFF HERE!!!!!
        #
        # os.path.join(TEMPLATE_DIR, "timeline.html") builds the full path to
        # the template file, e.g., C:\T21_project\app\templates\timeline.html
        #
        # The "with open(...) as f:" syntax is a context manager. It opens the
        # file, runs the code inside the with block, then automatically closes
        # the file — even if an error occurs. Much safer than open() and close().
        # encoding="utf-8" ensures we read text files correctly (UTF-8 is the
        # modern standard for text, supporting all languages).
        template_path = os.path.join(TEMPLATE_DIR, "timeline.html")
        with open(template_path, "r", encoding="utf-8") as f:
            html = f.read()

        # Step 3: Inject the JSON data by replacing the placeholder strings.
        #
        # The template has text like {{ events_json }} and {{ problems_json }}.
        # We use Python's str.replace(old, new) method to swap these placeholders
        # for the actual JSON data.
        #   html.replace("{{ events_json }}", events_json)
        # This finds every occurrence of "{{ events_json }}" and replaces it with
        # the JSON string we created above.
        html = html.replace("{{ events_json }}",   events_json)
        html = html.replace("{{ problems_json }}", problems_json)

        # Step 4: Send the fully-rendered HTML to the browser.
        #
        # The HTTP response has three parts:
        #   1. Status line: "200 OK" (200 means success)
        #   2. Headers: metadata about the response (e.g., what type of data it is)
        #   3. Body: the actual content (the HTML text)
        #
        # self.send_response(200) sends the status code 200 (success).
        #
        # self.send_header(...) sends a header. We send "Content-Type: text/html"
        # to tell the browser "this is HTML, please render it as a web page."
        # charset=utf-8 tells the browser what character encoding we used.
        #
        # self.end_headers() signals the end of the header section.
        #
        # self.wfile.write(...) writes the body — the actual HTML content.
        # html.encode("utf-8") converts the HTML text to bytes (the binary
        # format needed to send over the network).
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def _serve_json(self, items):
        """
        Serialise a list of model objects and send as a JSON response.

        This is an "API endpoint" — a URL that returns data (usually JSON)
        rather than a web page. APIs are useful for:
          - Debugging: you can visit /api/events in your browser and see raw
            data to verify the server is working.
          - Future JavaScript calls: JavaScript code in the browser can call
            these endpoints to fetch fresh data without reloading the page
            (a technique called AJAX).
          - Mobile apps: if you ever build a mobile app, it can talk to the
            same API.

        The "Content-Type: application/json" header tells the browser (or any
        API client) that the response is JSON, not HTML. The browser won't try
        to render it as a web page; instead, it might download it or display
        it as raw text.
        """
        # Convert the model objects to dicts, then to a JSON string.
        # [item.to_dict() for item in items] is a list comprehension (see above).
        # json.dumps(..., default=str) converts to JSON (see above).
        payload = json.dumps([item.to_dict() for item in items], default=str)

        # Send the JSON response.
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(payload.encode("utf-8"))

    def log_message(self, format, *args):
        """
        Override the default logger to keep console output tidy.

        SimpleHTTPRequestHandler normally prints verbose logs like:
          127.0.0.1 - - [07/Apr/2026 10:30:45] "GET / HTTP/1.1" 200 -
        This is useful for debugging, but it's noisy during normal use.

        By overriding log_message(), we replace that behavior with our own
        quieter version. Instead of the full format, we just print the
        first argument (args[0]), which is usually the HTTP status message.

        This is an example of method overriding: the parent class defines
        log_message(), and we provide our own version with different behavior.
        """
        print(f"  {args[0]}")


# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """
    Start the server and block until Ctrl+C is pressed.

    This function sets up and runs the web server. Here's what happens:

    1. HTTPServer(("0.0.0.0", PORT), TimelineHandler)
       Creates a server that:
         - Listens on address "0.0.0.0" (all network interfaces on this computer)
           and port 5000 (the value of our PORT constant).
         - "0.0.0.0" means it accepts requests from the same machine
           (127.0.0.1 or localhost) and from other machines on your network.
         - The second argument (TimelineHandler) tells it which class to use
           for handling requests. Every incoming request creates a new
           TimelineHandler instance and calls its do_GET method.

    2. server.serve_forever()
       Starts the server and blocks — it runs in a loop forever, listening for
       requests and handling them. The program doesn't continue past this line
       until the server stops (e.g., Ctrl+C).

    3. try/except KeyboardInterrupt
       The try block contains code that might raise an exception (error).
       KeyboardInterrupt is the special exception that Python raises when you
       press Ctrl+C. The except block catches it and runs cleanup code instead
       of crashing.

    4. server.server_close()
       Cleanly shuts down the server, closing its listening socket and freeing
       up the port so a new server can use it immediately. Without this, you
       might get "Address already in use" if you restart the server quickly.
    """
    server = HTTPServer(("0.0.0.0", PORT), TimelineHandler)
    print(f"\n  Clinical Timeline running at http://localhost:{PORT}\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Shutting down.")
        server.server_close()


# ============================================================================
# MAIN GUARD
# ============================================================================

# This pattern is Python's way of saying: "Only run this code if this file
# is being executed directly, not if it's being imported by another file."
#
# When Python runs a file directly (e.g., python app.py), it sets the variable
# __name__ to the string "__main__".
#
# But when another file imports this file (e.g., import app in another script),
# __name__ is set to the module name (e.g., "app").
#
# So this pattern lets you write files that can be:
#   - Run as standalone programs: python app.py triggers main()
#   - Imported as modules: import app gives you access to functions/classes
#     without running main()
#
# It's considered a Python best practice — it makes your code reusable.
if __name__ == "__main__":
    main()
