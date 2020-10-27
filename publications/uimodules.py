"User web interface modules."

import tornado.web

from . import constants
from . import settings
from . import utils


class Authors(tornado.web.UIModule):
    "HTML for authors list."

    def render(self, publication, complete=False):
        return utils.get_formatted_authors(publication['authors'],
                                           complete=complete)


class Journal(tornado.web.UIModule):
    "HTML for authors list."

    def render(self, publication):
        journal = publication['journal']
        title = journal.get('title')
        if title:
            url = self.handler.reverse_url('journal', title)
            result = ['<a href="%s">%s</a>' % (url, title)]
        else:
            result = ['-']
        result.append("<strong>%s</strong>" % (journal.get('volume') or '-'))
        result.append("(%s)" % (journal.get('issue') or '-'))
        result.append(journal.get('pages') or '-')
        return ' '.join(result)


class Published(tornado.web.UIModule):
    "Published date, and online, if present."

    def render(self, publication):
        result = publication['published']
        epub = publication.get('epublished')
        if epub:
            result += '; online ' + epub
        return "[%s]" % result


class Xref(tornado.web.UIModule):
    "HTML for a general external database entry."

    ICON = '<span class="glyphicon glyphicon-share"></span>'
    ATTRS = 'class="btn btn-link btn-xs" role="button" target="_"'

    def render(self, xref, full=False):
        db = xref["db"].lower()
        key = xref["key"]
        description = xref.get("description") or ""
        try:
            url = settings['XREF_TEMPLATE_URLS'][db]
        except KeyError:
            url = None
        else:
            if "%-s" in url:    # Use lowercase key
                url.replace("%-s", "%s")
                key = key.lower()
            url = url % key
        if db == "url":
            title = description or url
        elif url:
            title = f"{xref['db']} {key}"
            if full and description:
                title += " " + description
        elif description.startswith("http:") or description.startswith("https:"):
            url = description
            title = key
            description = ""
        else:
            title = f"{xref['db']} {description or key}"
        if url:
            result = f'<a {self.ATTRS} href="{url}">{self.ICON} {title}</a>'
        else:
            result = f'<button disabled {self.ATTRS}>{self.ICON} {title}</button>'
        return result


class ExternalButton(tornado.web.UIModule):
    "HTML for a button to an external publication page."

    ICON = '<span class="glyphicon glyphicon-link"></span>'
    ATTRS = 'class="btn btn-default btn-xs" role="button" target="_"'
    NAME = None
    URL = None

    def render(self, key, full=False):
        assert self.NAME
        assert self.URL
        if key:
            url = self.URL % key
            result = '<a %s href="%s">%s %s</a>' % \
                     (self.ATTRS, url, self.ICON, self.NAME)
            if full: result = '<p>' + result + ' ' + key + '</p>'
            return result
        else:
            return ''

class PubmedButton(ExternalButton):
    NAME = 'PubMed'
    URL = constants.PUBMED_URL
    

class DoiButton(ExternalButton):
    NAME = 'DOI'
    URL = constants.DOI_URL


class CrossrefButton(ExternalButton):
    NAME = 'Crossref'
    URL = 'https://search.crossref.org/?q=%s'


class QcFlags(tornado.web.UIModule):
    "Output QC information for the publication."

    def render(self, publication):
        result = []
        qc = publication.get('qc', {})
        for aspect in settings['PUBLICATION_QC_ASPECTS']:
            entry = qc.get(aspect)
            if entry is None:
                result.append('<span class="label label-default">'
                              'QC %s'
                              '</span>' % aspect)
            elif entry['flag']:
                result.append('<span class="label label-success"'
                              ' data-toggle="tooltip" data-placement="top"'
                              ' title="%s %s">'
                              '<span class="glyphicon glyphicon-ok"></span>'
                              ' QC %s'
                              '</span>' % (entry['date'],
                                           entry['account'], 
                                           aspect))
            else:
                result.append('<span class="label label-danger"'
                              ' data-toggle="tooltip" data-placement="top"'
                              ' title="%s %s">'
                              '<span class="glyphicon glyphicon-remove"></span>'
                              ' QC %s'
                              '</span>' % (entry['date'],
                                           entry['account'], 
                                           aspect))
        return ' '.join(result)


class Translate(tornado.web.UIModule):
    "Translate the term, or keep as is."

    def render(self, term):
        istitle = term.istitle()
        try:
            term = settings['DISPLAY_TRANSLATIONS'][term.lower()]
            if istitle:
                term = term.title()
        except KeyError:
            pass
        return term
