"Home page, and a few other pages."

import certifi
import couchdb2
import pyparsing
import requests
import tornado
import tornado.web
import yaml
import xlsxwriter

from publications import constants
from publications import settings
from publications.subset import Subset
from publications.requesthandler import RequestHandler

import publications.database


class Home(RequestHandler):
    "Home page."

    def get(self):
        limit = settings["SHORT_PUBLICATIONS_LIST_LIMIT"]
        subset = Subset(self.db, recent=limit)
        self.render("home.html", publications=subset, limit=limit)


class Contact(RequestHandler):
    "Contact page."

    def get(self):
        self.render("contact.html", contact=settings["SITE_CONTACT"])


class Software(RequestHandler):
    "Software version information."

    def get(self):
        software = [
            ("Publications", constants.VERSION, constants.URL),
            ("Python", constants.PYTHON_VERSION, constants.PYTHON_URL),
            ("tornado", tornado.version, constants.TORNADO_URL),
            ("certifi", certifi.__version__, constants.CERTIFI_URL),
            ("CouchDB server", self.db.server.version, constants.COUCHDB_URL),
            ("CouchDB2 interface", couchdb2.__version__, constants.COUCHDB2_URL),
            ("XslxWriter", xlsxwriter.__version__, constants.XLSXWRITER_URL),
            ("PyYAML", yaml.__version__, constants.PYYAML_URL),
            ("pyparsing", pyparsing.__version__, constants.PYPARSING_URL),
            ("requests", requests.__version__, constants.REQUESTS_URL),
            ("Bootstrap", constants.BOOTSTRAP_VERSION, constants.BOOTSTRAP_URL),
            ("jQuery", constants.JQUERY_VERSION, constants.JQUERY_URL),
            (
                "jQuery.localtime",
                constants.JQUERY_LOCALTIME_VERSION,
                constants.JQUERY_LOCALTIME_URL,
            ),
            ("DataTables", constants.DATATABLES_VERSION, constants.DATATABLES_URL),
        ]
        self.render("software.html", software=software)


class Status(RequestHandler):
    "Return JSON for the current status and the database entity counts."

    def get(self):
        data = dict(status="OK")
        data.update(publications.database.get_counts(self.db))
        self.write(data)


class Documentation(RequestHandler):
    "Documentation page."

    def get(self):
        self.render("documentation.html")


class Logs(RequestHandler):
    "Logs page."

    @tornado.web.authenticated
    def get(self, iuid):
        try:
            doc = self.db[iuid]
        except couchdb2.NotFoundError:
            raise tornado.web.HTTPError(404, reason="No such entity.")
        if doc[constants.DOCTYPE] == constants.PUBLICATION:
            title = doc["title"]
            href = self.reverse_url("publication", doc["_id"])
        elif doc[constants.DOCTYPE] == constants.ACCOUNT:
            self.check_owner(doc)
            title = doc["email"]
            href = self.reverse_url("account", doc["email"])
        else:
            raise NotImplementedError
        self.render("logs.html", title=title, href=href, logs=self.get_logs(doc["_id"]))


class NoSuchEntity(RequestHandler):
    "Error message on home page."

    def get(self, path=None):
        self.logger.debug(f"Page not found: {path}")
        self.see_other("home", error="Sorry, page not found.")
