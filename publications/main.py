"Web application server for a publications database."

import logging
import os

import tornado.web
import tornado.ioloop

from publications import constants
from publications import settings
from publications import uimodules
from publications import utils

import publications.admin
import publications.home
import publications.account
import publications.publication
import publications.blacklist
import publications.journal
import publications.label
import publications.search
import publications.researcher
import publications.subset


def get_handlers():
    url = tornado.web.url
    return [
        url(r"/", publications.home.Home, name="home"),
        url(r"/status", publications.home.Status, name="status"),
        url(
            r"/publication/([^/]{32,32})",
            publications.publication.Publication,
            name="publication",
        ),
        url(
            r"/publication/([^/]{32,32}).json",
            publications.publication.PublicationJson,
            name="publication_json",
        ),
        url(
            r"/publications/(\d{4})",
            publications.publication.Publications,
            name="publications_year",
        ),
        url(
            r"/publications/(\d{4}).json",
            publications.publication.PublicationsJson,
            name="publications_year_json",
        ),
        url(
            r"/publications", publications.publication.Publications, name="publications"
        ),
        url(
            r"/publications.json",
            publications.publication.PublicationsJson,
            name="publications_json",
        ),
        url(
            r"/publications/csv",
            publications.publication.PublicationsCsv,
            name="publications_csv",
        ),
        url(
            r"/publications/xlsx",
            publications.publication.PublicationsXlsx,
            name="publications_xlsx",
        ),
        url(
            r"/publications/txt",
            publications.publication.PublicationsTxt,
            name="publications_txt",
        ),
        url(
            r"/publications/table/(\d{4})",
            publications.publication.PublicationsTable,
            name="publications_table_year",
        ),
        url(
            r"/publications/table",
            publications.publication.PublicationsTable,
            name="publications_table",
        ),
        url(
            r"/publications/recent.json",
            publications.publication.PublicationsRecentJson,
            name="publications_recent_json",
        ),
        url(
            r"/publications/years.json",
            publications.publication.PublicationsYearsJson,
            name="publications_years_json",
        ),
        url(
            r"/publications/no_pmid",
            publications.publication.PublicationsNoPmid,
            name="publications_no_pmid",
        ),
        url(
            r"/publications/no_pmid.json",
            publications.publication.PublicationsNoPmidJson,
            name="publications_no_pmid_json",
        ),
        url(
            r"/publications/no_doi",
            publications.publication.PublicationsNoDoi,
            name="publications_no_doi",
        ),
        url(
            r"/publications/no_doi.json",
            publications.publication.PublicationsNoDoiJson,
            name="publications_no_doi_json",
        ),
        url(
            r"/publications/no_label",
            publications.publication.PublicationsNoLabel,
            name="publications_no_label",
        ),
        url(
            r"/publications/no_label.json",
            publications.publication.PublicationsNoLabelJson,
            name="publications_no_label_json",
        ),
        url(
            r"/publications/duplicates",
            publications.publication.PublicationsDuplicates,
            name="publications_duplicates",
        ),
        url(
            r"/publications/modified",
            publications.publication.PublicationsModified,
            name="publications_modified",
        ),
        url(
            r"/edit/([^/]{32,32})",
            publications.publication.PublicationEdit,
            name="publication_edit",
        ),
        url(
            r"/researchers/([^/]{32,32})",
            publications.publication.PublicationResearchers,
            name="publication_researchers",
        ),
        url(
            r"/xrefs/([^/]{32,32})",
            publications.publication.PublicationXrefs,
            name="publication_xrefs",
        ),
        url(r"/add", publications.publication.PublicationAdd, name="publication_add"),
        url(
            r"/fetch",
            publications.publication.PublicationFetch,
            name="publication_fetch",
        ),
        url(r"/blacklist/([^/]+)", publications.blacklist.Blacklist, name="blacklist"),
        url(r"/blacklisted", publications.blacklist.Blacklisted, name="blacklisted"),
        url(
            r"/update/([^/]{32,32})/pmid",
            publications.publication.PublicationUpdatePmid,
            name="publication_update_pmid",
        ),
        url(
            r"/update/([^/]{32,32})/find_pmid",
            publications.publication.PublicationFindPmid,
            name="publication_find_pmid",
        ),
        url(
            r"/update/([^/]{32,32})/doi",
            publications.publication.PublicationUpdateDoi,
            name="publication_update_doi",
        ),
        url(
            r"/researcher", publications.researcher.ResearcherAdd, name="researcher_add"
        ),
        url(
            r"/researchers_json",
            publications.researcher.ResearchersJson,
            name="researchers_json",
        ),
        url(r"/researchers", publications.researcher.Researchers, name="researchers"),
        url(
            r"/researcher/([^/]+).json",
            publications.researcher.ResearcherJson,
            name="researcher_json",
        ),
        url(
            r"/researcher/([^/]+)",
            publications.researcher.Researcher,
            name="researcher",
        ),
        url(
            r"/researcher/([^/]+)/edit",
            publications.researcher.ResearcherEdit,
            name="researcher_edit",
        ),
        url(
            r"/researcher/([^/]+)/publications.csv",
            publications.researcher.ResearcherPublicationsCsv,
            name="researcher_publications_csv",
        ),
        url(
            r"/researcher/([^/]+)/publications.xlsx",
            publications.researcher.ResearcherPublicationsXlsx,
            name="researcher_publications_xlsx",
        ),
        url(
            r"/researcher/([^/]+)/publications.txt",
            publications.researcher.ResearcherPublicationsTxt,
            name="researcher_publications_txt",
        ),
        url(
            r"/researcher/([^/]+)/publications/edit",
            publications.researcher.ResearcherPublicationsEdit,
            name="researcher_publications_edit",
        ),
        url(r"/journals", publications.journal.Journals, name="journals"),
        url(r"/journals.json", publications.journal.JournalsJson, name="journals_json"),
        url(
            r"/journal/([^/]+).json",
            publications.journal.JournalJson,
            name="journal_json",
        ),
        url(r"/journal/([^/]+)", publications.journal.Journal, name="journal"),
        url(
            r"/journal/([^/]+)/edit",
            publications.journal.JournalEdit,
            name="journal_edit",
        ),
        url(r"/labels", publications.label.LabelsList, name="labels"),
        url(r"/labels.json", publications.label.LabelsJson, name="labels_json"),
        url(r"/labels/table", publications.label.LabelsTable, name="labels_table"),
        # These two label path patterns need to be checked first.
        url(r"/label/([^/]+)/edit", publications.label.LabelEdit, name="label_edit"),
        url(r"/label/([^/]+)/merge", publications.label.LabelMerge, name="label_merge"),
        url(r"/label/([^/]+)/add", publications.label.LabelAdd, name="label_add"),
        url(
            r"/label/([^/]+)/remove",
            publications.label.LabelRemove,
            name="label_remove",
        ),
        url(r"/label/(.+).json", publications.label.LabelJson, name="label_json"),
        url(r"/label/(.+)", publications.label.Label, name="label"),
        url(r"/label", publications.label.LabelCreate, name="label_create"),
        url(r"/account/reset", publications.account.AccountReset, name="account_reset"),
        url(
            r"/account/password",
            publications.account.AccountPassword,
            name="account_password",
        ),
        url(
            r"/account/([^/]+).json",
            publications.account.AccountJson,
            name="account_json",
        ),
        url(r"/account/([^/]+)", publications.account.Account, name="account"),
        url(
            r"/account/([^/]+)/edit",
            publications.account.AccountEdit,
            name="account_edit",
        ),
        url(
            r"/account/([^/]+)/disable",
            publications.account.AccountDisable,
            name="account_disable",
        ),
        url(
            r"/account/([^/]+)/enable",
            publications.account.AccountEnable,
            name="account_enable",
        ),
        url(r"/accounts", publications.account.Accounts, name="accounts"),
        url(r"/accounts.json", publications.account.AccountsJson, name="accounts_json"),
        url(r"/account", publications.account.AccountAdd, name="account_add"),
        url(r"/search", publications.search.Search, name="search"),
        url(r"/search.json", publications.search.SearchJson, name="search_json"),
        url(r"/subset", publications.subset.SubsetDisplay, name="subset"),
        url(r"/logs/([^/]+)", publications.home.Logs, name="logs"),
        url(r"/documentation", publications.home.Documentation, name="documentation"),
        url(r"/contact", publications.home.Contact, name="contact"),
        url(r"/software", publications.home.Software, name="software"),
        url(constants.LOGIN_URL, publications.account.Login, name="login"),
        url(r"/logout", publications.account.Logout, name="logout"),
        url(
            r"/api/publication",
            publications.publication.ApiPublicationFetch,
            name="api_publication_fetch",
        ),
        url(
            r"/api/publication/([^/]{32,32})/labels",
            publications.publication.ApiPublicationLabels,
            name="api_publication_labels",
        ),
        url(r"/site/([^/]+)", publications.admin.Site, name="site"),
        url(
            r"/configuration",
            publications.admin.Configuration,
            name="configuration",
        ),
        url(r"/database", publications.admin.Database, name="database"),
        url(r"/settings", publications.admin.Settings, name="settings"),
        url(r"/(.*)", publications.home.NoSuchEntity),
    ]


def main():
    publications.admin.load_settings_from_file()
    db = publications.database.get_db()
    publications.database.update_design_documents(db)
    publications.admin.load_settings_from_database(db)
    application = tornado.web.Application(
        handlers=get_handlers(),
        debug=settings.get("TORNADO_DEBUG", False),
        cookie_secret=settings["COOKIE_SECRET"],
        xsrf_cookies=True,
        ui_modules=uimodules,
        template_path=constants.TEMPLATE_DIR,
        static_path=constants.STATIC_DIR,
        login_url=constants.LOGIN_URL,
    )
    application.listen(settings["PORT"], xheaders=True)
    logging.getLogger("publications").info(f"Web server at {settings['BASE_URL']}")
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
