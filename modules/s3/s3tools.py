# -*- coding: utf-8 -*-

"""
    Tools

    @requires: U{B{I{gluon}} <http://web2py.com>}

    @author: Fran Boon <francisboon[at]gmail.com>
    @author: Dominic König <dominic[at]aidiq.com>
    @author: sunneach

    @copyright: (c) 2010-2011 Sahana Software Foundation
    @license: MIT

    Permission is hereby granted, free of charge, to any person
    obtaining a copy of this software and associated documentation
    files (the "Software"), to deal in the Software without
    restriction, including without limitation the rights to use,
    copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the
    Software is furnished to do so, subject to the following
    conditions:

    The above copyright notice and this permission notice shall be
    included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
    OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
    HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
    WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
    OTHER DEALINGS IN THE SOFTWARE.
"""

__all__ = ["SQLTABLES3",
           "CrudS3",
           "S3BulkImporter",
           "S3Menu",
           "S3DateTime",
           "S3Comment"]

import sys
import os
import datetime
import re
import urllib
import uuid
import warnings
from cgi import escape

from gluon import *
from gluon.html import xmlescape
from gluon.storage import Storage, Messages
from gluon.sql import Field, Row, Query
from gluon.sqlhtml import SQLFORM, SQLTABLE
from gluon.tools import Crud
from gluon import current

from s3validators import IS_UTC_OFFSET

DEBUG = False
if DEBUG:
    print >> sys.stderr, "S3Tools: DEBUG MODE"
    def _debug(m):
        print >> sys.stderr, m
else:
    _debug = lambda m: None

DEFAULT = lambda: None
table_field = re.compile("[\w_]+\.[\w_]+")

# *****************************************************************************

class SQLTABLES3(SQLTABLE):

    """
    S3 custom version of gluon.sqlhtml.SQLTABLE

    Given a SQLRows object, as returned by a db().select(), generates
    an html table with the rows.

        - we need a different linkto construction for our CRUD controller
        - we need to specify a different ID field to direct to for the M2M controller
        - used by S3XRC

    Optional arguments:

    @keyword linkto: URL (or lambda to generate a URL) to edit individual records
    @keyword upload: URL to download uploaded files
    @keyword orderby: Add an orderby link to column headers.
    @keyword headers: dictionary of headers to headers redefinions
    @keyword truncate: length at which to truncate text in table cells.
        Defaults to 16 characters.

    Optional names attributes for passed to the <table> tag

    Simple linkto example::

        rows = db.select(db.sometable.ALL)
        table = SQLTABLES3(rows, linkto="someurl")

    This will link rows[id] to .../sometable/value_of_id

    More advanced linkto example::

        def mylink(field):
            return URL(args=[field])

        rows = db.select(db.sometable.ALL)
        table = SQLTABLES3(rows, linkto=mylink)

    This will link rows[id] to::

        current_app/current_controller/current_function/value_of_id

    """

    def __init__(self, sqlrows,
                 linkto=None,
                 upload=None,
                 orderby=None,
                 headers={},
                 truncate=16,
                 columns=None,
                 th_link="",
                 **attributes):

        # reverted since it causes errors (admin/user & manual importing of req/req/import.xml)
        # super(SQLTABLES3, self).__init__(**attributes)
        TABLE.__init__(self, **attributes)
        self.components = []
        self.attributes = attributes
        self.sqlrows = sqlrows
        (components, row) = (self.components, [])
        if not columns:
            columns = sqlrows.colnames
        if headers=="fieldname:capitalize":
            headers = {}
            for c in columns:
                headers[c] = " ".join([w.capitalize() for w in c.split(".")[-1].split("_")])
        elif headers=="labels":
            headers = {}
            for c in columns:
                (t, f) = c.split(".")
                field = sqlrows.db[t][f]
                headers[c] = field.label

        if headers!=None:
            for c in columns:
                if orderby:
                    row.append(TH(A(headers.get(c, c),
                                    _href=th_link+"?orderby=" + c)))
                else:
                    row.append(TH(headers.get(c, c)))
            components.append(THEAD(TR(*row)))

        tbody = []
        for (rc, record) in enumerate(sqlrows):
            row = []
            if rc % 2 == 0:
                _class = "even"
            else:
                _class = "odd"
            for colname in columns:
                if not table_field.match(colname):
                    if "_extra" in record and colname in record._extra:
                        r = record._extra[colname]
                        row.append(TD(r))
                        continue
                    else:
                        raise KeyError("Column %s not found (SQLTABLE)" % colname)
                (tablename, fieldname) = colname.split(".")
                try:
                    field = sqlrows.db[tablename][fieldname]
                except KeyError:
                    field = None
                if tablename in record \
                        and isinstance(record, Row) \
                        and isinstance(record[tablename], Row):
                    r = record[tablename][fieldname]
                elif fieldname in record:
                    r = record[fieldname]
                else:
                    raise SyntaxError("something wrong in Rows object")
                r_old = r
                if not field:
                    pass
                elif linkto and field.type == "id":
                    #try:
                        #href = linkto(r, "table", tablename)
                    #except TypeError:
                        #href = "%s/%s/%s" % (linkto, tablename, r_old)
                    #r = A(r, _href=href)
                    try:
                        href = linkto(r)
                    except TypeError:
                        href = "%s/%s" % (linkto, r)
                    r = A(r, _href=href)
                #elif linkto and field.type.startswith("reference"):
                    #ref = field.type[10:]
                    #try:
                        #href = linkto(r, "reference", ref)
                    #except TypeError:
                        #href = "%s/%s/%s" % (linkto, ref, r_old)
                        #if ref.find(".") >= 0:
                            #tref,fref = ref.split(".")
                            #if hasattr(sqlrows.db[tref],"_primarykey"):
                                #href = "%s/%s?%s" % (linkto, tref, urllib.urlencode({fref:r}))
                    #r = A(str(r), _href=str(href))
                elif linkto \
                     and hasattr(field._table, "_primarykey") \
                     and fieldname in field._table._primarykey:
                    # have to test this with multi-key tables
                    key = urllib.urlencode(dict([ \
                                ((tablename in record \
                                      and isinstance(record, Row) \
                                      and isinstance(record[tablename], Row)) \
                                      and (k, record[tablename][k])) \
                                      or (k, record[k]) \
                                    for k in field._table._primarykey]))
                    r = A(r, _href="%s/%s?%s" % (linkto, tablename, key))
                elif field.type.startswith("list:"):
                    r = field.represent(r or [])
                elif field.represent:
                    r = field.represent(r)
                elif field.type.startswith("reference"):
                    pass
                elif field.type == "blob" and r:
                    r = "DATA"
                elif field.type == "upload":
                    if upload and r:
                        r = A("file", _href="%s/%s" % (upload, r))
                    elif r:
                        r = "file"
                    else:
                        r = ""
                elif field.type in ["string", "text"]:
                    r = str(field.formatter(r))
                    ur = unicode(r, "utf8")
                    if truncate!=None and len(ur) > truncate:
                        r = ur[:truncate - 3].encode("utf8") + "..."
                row.append(TD(r))
            tbody.append(TR(_class=_class, *row))
        components.append(TBODY(*tbody))

# =============================================================================
class S3Menu(DIV):
    """
        MENUS3 reimplementation - 
            * breadcrumbs support
            * greater control / flexibility
            * future - side menu

        @author Abhishek Mishra
    """

    def __init__(self, data, **args):
        self.data = data
        self.attributes = args
        
    def serialize(self, data, level=0):
        """
            NOTE on right :
                personal-menu is the one on top right besides login,
                a presence of right in module level menu indicates a personal-menu
                
                nav is the big menu below the logo,
                an absence of right in module level menu indicates nav items
                
                main-sub-menu is the left side menu (blue ones)
                a right = True indicates a highlight here (set by 01_menu)
                
                extension are submenus under main-sub-menu
                a right = True indicates highlight here (set by 01_menu)
        """
        _type = self.attributes["_type"]
        if _type == "personal-menu":
            items = []
            data = [x for x in data if x[1]]
            for item in data:
                (name, right, link) = item[:3]
                items.append(LI(A(name,
                                  _href=link)
                                )
                            )

            deployment_settings = current.deployment_settings
            if deployment_settings.get_L10n_display_toolbar():
                menu_langs = self.attributes["_menu_langs"]
                current_lang = current.T.accepted_language
                langopts = [ OPTION(x[0], _value=x[2]) for x in menu_langs[3] ]
                langselect = SELECT(langopts, 
                                    _name="_language", 
                                    _title="Language Selection", 
                                    value=current_lang, 
                                    _onchange="$('#personal-menu div form').submit();"
                                )
                langform = FORM(langselect,
                                _name="_language",
                                _action="",
                                _method="get")
                return DIV([UL(items), langform], _class="pmenu-wrapper")
            else:
                return DIV(UL(items), _class="pmenu-wrapper")
        elif _type == "nav":
            _highlight = "" or self.attributes["_highlight"]
            items = []
            for item in data:
                (name, right, link) = item[:3]
                if not right:
                    import re
                    _link = link
                    if "default" not in _highlight:
                        _highlight = re.match("(.*/).*$", _highlight).group(1)
                        _link = re.match("(.*/).*$", link).group(1)
                    _class = "highlight" if str(_link) in _highlight else " "
                    items.append(LI(
                        A(name, _href=link, _class=_class)
                    ))
            return UL(items, **self.attributes)
        elif _type == "main-sub-menu":
            items = []
            for item in data:
                (name, right, link) = item[:3]
                items.append(LI(A(name,
                                  _href=link,
                                  _class="highlight" if right==True else " ")
                                )
                            )
                if len(item) > 3:
                    sub = item[3]
                    append = S3Menu(sub,
                                    _type="extension",
                                    _class="menu-extention").serialize(sub)
                    items.append(append)
            return UL(items, **self.attributes)
        elif _type == "extension":
            items = []
            for item in data:
                (name, right, link) = item[:3]
                items.append(LI(A(name,
                                  _href=link,
                                  _class="highlight" if right==True else " ")
                                )
                            )
            return UL(items, **self.attributes)
        else:
            return UL()
            
    def xml(self):
        return self.serialize(self.data, 0).xml()


# =============================================================================

class CrudS3(Crud):

    """
        S3 extension of the gluon.tools.Crud class
        - select() uses SQLTABLES3 (to allow different linkto construction)
    """

    def __init__(self):
        """ Initialise parent class & make any necessary modifications """
        Crud.__init__(self, current.db)

    def select(
        self,
        table,
        query=None,
        fields=None,
        orderby=None,
        limitby=None,
        headers={},
        **attr):

        db = current.db
        request = current.request
        if not (isinstance(table, db.Table) or table in db.tables):
            raise HTTP(404)
        if not self.has_permission("select", table):
            redirect(self.settings.auth.settings.on_failed_authorization)
        #if record_id and not self.has_permission("select", table):
        #    redirect(self.settings.auth.settings.on_failed_authorization)
        if not isinstance(table, db.Table):
            table = db[table]
        if not query:
            query = table.id > 0
        if not fields:
            fields = [table.ALL]
        rows = db(query).select(*fields, **dict(orderby=orderby,
            limitby=limitby))
        if not rows:
            return None # Nicer than an empty table.
        if not "linkto" in attr:
            attr["linkto"] = self.url(args="read")
        if not "upload" in attr:
            attr["upload"] = self.url("download")
        if request.extension != "html":
            return rows.as_list()
        return SQLTABLES3(rows, headers=headers, **attr)


# =============================================================================

class S3BulkImporter(object):
    """
        Import CSV files of data to pre-populate the database.
        Suitable for use in Testing, Demos & Simulations

        @author: Graeme Foster
    """

    def __init__(self, manager, s3base):
        """
            Constructor

            @param manager: the S3ResourceController
        """

        self.manager = manager
        response = current.response
        self.s3base = s3base
        self.importTasks = []
        self.specialTasks = []
        self.tasks = []
        self.alternateTables = {"hrm_person":  {"tablename":"hrm_human_resource",
                                                "loader":response.s3.hrm_person_loader,
                                                "prefix":"pr",
                                                "name":"person"},
                                "req_req":     {"loader":response.s3.req_loader},
                                "req_req_item":{"loader":response.s3.req_item_loader},
                               }
        self.errorList = []
        self.resultList = []

    def load_descriptor(self, path):
        """ Method that will load the descriptor file and then all the
            import tasks in that file into the importTasks property.
            The descriptor file is the file called tasks.txt in path.
            The file consists of a comma separated list of:
            application, resource name, csv filename, xsl filename.
        """
        source = open(os.path.join(path, "tasks.cfg"), "r")
        values = source.readlines()
        source.close()
        for tasks in values:
            # strip out the new line
            task = tasks.strip()
            if task == "":
                continue
            if task[0] == "#": # comment
                continue
            # split at the comma
            details = task.split(",")
            prefix = details[0].strip('" ')
            if prefix == "*": # specialist function
                self.extractSpecialistLine(path, details)
            else: # standard importer
                self.extractImporterLine(path, details)

    def extractImporterLine(self, path, details):
        """
            Method that extract the details for an import Task
        """
        if len(details) == 4:
             # remove any spaces and enclosing double quote
            app = details[0].strip('" ')
            res = details[1].strip('" ')
            request = current.request
            csvFileName = details[2].strip('" ')
            (csvPath, csvFile) = os.path.split(csvFileName)
            if csvPath != "":
                path = os.path.join(request.folder,
                                    "private",
                                    "prepopulate",
                                    csvPath)
            csv = os.path.join(path, csvFile)
            xslFileName = details[3].strip('" ')
            templateDir = os.path.join(request.folder,
                                       "static",
                                       "formats",
                                       "s3csv",
                                      )
            # try the app directory in the templates directory first
            xsl = os.path.join(templateDir, app, xslFileName)
            _debug("%s %s" % (xslFileName, xsl))
            if os.path.exists(xsl) == False:
                # now try the templates directory
                xsl = os.path.join(templateDir, xslFileName)
                _debug ("%s %s" % (xslFileName, xsl))
                if os.path.exists(xsl) == False:
                    # use the same directory as the csv file
                    xsl = os.path.join(path, xslFileName)
                    _debug ("%s %s" % (xslFileName, xsl))
                    if os.path.exists(xsl) == False:
                        self.errorList.append(
                        "Failed to find a transform file, Giving up.")
                        return
            self.tasks.append([1, app, res, csv, xsl])
            self.importTasks.append([app, res, csv, xsl])
        else:
            self.errorList.append(
            "prepopulate error: job not of length 4. %s job ignored" % task)

    def extractSpecialistLine(self, path, details):
        """ Method that will store a single import job into
            the importTasks property.
        """
        function = details[1].strip('" ')
        csv = None
        if len(details) == 3:
            csv = os.path.join(path, details[2].strip('" '))
        extraArgs = None
        if len(details) == 4:
            extraArgs = details[3].strip('" ')
        self.tasks.append([2, function, csv, extraArgs])
        self.specialTasks.append([function, csv, extraArgs])

    def load_import(self, controller, csv, xsl):
        """ Method that will store a single import job into
            the importTasks property.
        """
        self.importTasks.append([controller, csv, xsl])

    def execute_import_task(self, task):
        """ Method that will execute each import job, in order """

        if task[0] == 1:
            manager = self.manager
            db = current.db
            request = current.request
            response = current.response
            errorString = "prepopulate error: file %s missing"
            # Store the view
            view = response.view
    
            auth = current.auth
            deployment_settings = auth.deployment_settings

            _debug ("Running job %s %s (filename=%s transform=%s)" % (task[1], task[2], task[3], task[4]))
            prefix = task[1]
            name = task[2]
            tablename = "%s_%s" % (prefix, name)
            if tablename in self.alternateTables:
                details = self.alternateTables[tablename]
                if "tablename" in details:
                    tablename = details["tablename"]
                manager.load(tablename)
                if "loader" in details:
                    loader = details["loader"]
                    if loader is not None:
                        loader()
                if "prefix" in details:
                    prefix = details["prefix"]
                if "name" in details:
                    name = details["name"]
            else:
                manager.load(tablename)
            # Skip the job if the target table doesn't exist
            if tablename not in db:
                self.errorList.append("WARNING: Unable to find table %s import job skipped" % tablename)
                return
            # Check if the source file is accessible
            try:
                csv = open(task[3], "r")
            except IOError:
                self.errorList.append(errorString % task[3])
                return
            # Check if the stylesheet is accessible
            try:
                open(task[4], "r")
            except IOError:
                self.errorList.append(errorString % task[4])
                return
            # Create a request
            vars = dict(filename=task[3], transform=task[4])
            # Old back-end
            r = manager.parse_request(prefix=prefix,
                                      name=name,
                                      args=["create.s3csv"],
                                      vars=vars)
#            # New back-end
#            r = manager.parse_request(prefix=prefix,
#                                      name=name,
#                                      args=["import"],
#                                      vars=vars)
#            from s3import import S3Importer
#            r.set_handler("import", S3Importer(), transform=True)
            # Execute the request
            output = r()
            db.commit()
            _debug ("%s import job completed" % tablename)
    
            # Restore the view
            response.view = view
            self.clear_import_tasks()

    def execute_special_task(self, task):
        if task[0] == 2:
            fun = task[1]
            #fun_g, fun_a = fun.split(".", 1)
            csv = task[2]
            extraArgs = task[3]
            if csv is None:
                if extraArgs is None:
                    current.response.s3[fun]()
                else:
                    current.response.s3[fun](extraArgs)
            elif extraArgs is None:
                current.response.s3[fun](csv)
            else:
                current.response.s3[fun](csv, extraArgs)

    def clear_import_tasks(self):
        """ Clear the importTask list """
        self.importTasks = []

    def perform_tasks(self, path):
        """ convenience method that will load and then execute the import jobs
            that are listed in the descriptor file
        """
        self.load_descriptor(path)
        for task in self.tasks:
            if task[0] == 1:
                self.execute_import_task(task)
            elif task[0] == 2:
                self.execute_special_task(task)

    def perform_task(self, controller, csv, xsl):
        """ convenience method that will load and execute the import job """
        self.load_import(controller, csv, xsl)
        self.execute_import_tasks()


# =============================================================================

class S3DateTime(object):
    """
        Toolkit for date+time parsing/representation
    """

    NONE = "-"

    # -----------------------------------------------------------------------------
    @staticmethod
    def date_represent(date):
        """
            Represent the date according to deployment settings &/or T()

            @param date: the date
        """

        settings = current.deployment_settings
        format = settings.get_L10n_date_format()

        if date:
            return date.strftime(str(format))
        else:
            return S3DateTime.NONE

    # -----------------------------------------------------------------------------
    @staticmethod
    def time_represent(time, utc=False):
        """
            Represent the date according to deployment settings &/or T()

            @param time: the time
        """

        session = current.session
        settings = current.deployment_settings
        format = settings.get_L10n_time_format()

        if time and utc:
            offset = IS_UTC_OFFSET.get_offset_value(session.s3.utc_offset)
            if offset:
                time = time + datetime.timedelta(seconds=offset)

        if time:
            return time.strftime(str(format))
        else:
            return S3DateTime.NONE

    # -----------------------------------------------------------------------------
    @staticmethod
    def datetime_represent(dt, utc=False):
        """
            Represent the datetime according to deployment settings &/or T()
        """

        session = current.session
        xml = current.manager.xml

        if dt and utc:
            offset = IS_UTC_OFFSET.get_offset_value(session.s3.utc_offset)
            if offset:
                dt = dt + datetime.timedelta(seconds=offset)

        if dt:
            return xml.encode_local_datetime(dt)
        else:
            return S3DateTime.NONE

# =============================================================================

class S3Comment(object):
    """
    Stores resource table field comment, so that it can later be
    represented in different formats

    @author: Shiv Deepak
    """

    def __init__(self, desc=None, title=None,
                 anchor_title=None, anchor_link=None):
        """
            Initialise the object

            @param desc: the actual comment which will be displayed as tooltip

            @param title: the title of the comment, mostly it will the
                          name of the field to which the comment belongs to

            @param anchor_title: hiperlink title for HTML forms, added just
                                 just before the tooltip

            @param anchor_link: hiperlink url, anchor_title and anchor_link
                                should be specified together
        """

        self.desc = unicode(desc).decode("utf-8") if desc else None
        self.title = unicode(title).decode("utf-8") if title else None

        self.anchor_title =\
            unicode(anchor_title).decode("utf-8") if anchor_title else None
        self.anchor_link =\
            unicode(anchor_link).decode("utf-8") if anchor_link else None

    def markup(self):
        """
            General HTML output for webpages with tooltip

            @return: field's comment in HTML markup,
                     return object will be of type
                     U{XmlComponent
                     <http://web2py.com/examples/static/epydoc/web2py.gluon.html-module.html>}
        """

        xmlescape = lambda m: escape(m)

        if self.anchor_title and self.anchor_link:

            if self.desc:
                need_tooltip=True
                desc = xmlescape(self.desc)
                if self.title == None:
                    title = ""
                    tooltip_text = desc
                else:
                    title = xmlescape(self.title)
                    tooltip_text = "%s|%s" % (title, desc)
            else:
                need_tooltip=False

            anchor_title = xmlescape(self.anchor_title)
            anchor_link = xmlescape(self.anchor_link)

            if need_tooltip:
                output = DIV(A(anchor_title,
                               _href=anchor_link,
                               _class="colorbox",
                               _target='top',
                               _title=anchor_title),
                             DIV(_class="tooltip",
                                 _title=tooltip_text
                                 )
                             )
            else:
                output = DIV(A(anchor_title,
                               _href=anchor_link,
                               _class="colorbox",
                               _target='top',
                               _title=anchor_title),
                             )

        elif self.title and self.desc:

            desc = xmlescape(self.desc)
            title = xmlescape(self.title)

            output = DIV(_class="tooltip",
                         _title="%s|%s" % (title,
                                           desc),
                         )

        elif self.desc:

            desc = xmlescape(self.desc)

            output = DIV(_class="tooltip",
                         _title=desc,
                         )

        else:
            output = DIV("")

        return output

    def plaintext(self):
        """
            Comment in plain text, suitable on PDF

            @return: field's comment in plain text
        """

        output = self.desc if self.desc else ""
        return output

    def xml(self):
        """
            to impart U{XmlComponent
            <http://web2py.com/examples/static/epydoc/web2py.gluon.html-module.html>}
            behaviour to the class
        """
        return str(self)

    # Magic Methods for string like behaviour
    def __str__(self):
        output = self.markup()
        return output.xml()

    def __repr__(self):
        return str(self)

    def __len__(self):
        return len(str(self))

    def __add__(self,other):
        return '%s%s' % (self,other)

    def __radd__(self,other):
        return '%s%s' % (other,self)

    def __cmp__(self,other):
        return cmp(str(self),str(other))

    def __hash__(self):
        return hash(str(self))

    def __getattr__(self,name):
        return getattr(str(self),name)

    def __getitem__(self,i):
        return str(self)[i]

    def __getslice__(self,i,j):
        return str(self)[i:j]

    def __iter__(self):
        for c in str(self): yield c

# END =========================================================================