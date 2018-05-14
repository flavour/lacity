# -*- coding: utf-8 -*-

"""
    Default Controllers

    @author: Fran Boon
"""

module = "default"

# -----------------------------------------------------------------------------
def call():
    "Call an XMLRPC, JSONRPC or RSS service"
    # If webservices don't use sessions, avoid cluttering up the storage
    #session.forget()
    return service()

# -----------------------------------------------------------------------------
def download():
    """ Download a file """

    # Load the Models
    # @ToDo: Make this just load the relevant models
    s3mgr.model.load_all_models()

    return response.download(request, db)

# -----------------------------------------------------------------------------
def index():
    """ Main Home Page """

    title = deployment_settings.get_system_name()
    response.title = title

    return dict(title = title)

# -----------------------------------------------------------------------------
def site():
    """
        @todo: Avoid redirect
    """
    if len(request.args):
        site_id = request.args[0]
        site_r = db.org_site[site_id]
        tablename = site_r.instance_type
        query = (db[tablename].site_id == site_id)
        id = db(query).select(db[tablename].id,
                              limitby = (0, 1)).first().id
        cf = tablename.split("_", 1)
        redirect(URL(c = cf[0],
                     f = cf[1],
                     args = [id]))
    else:
        raise HTTP(404)

# -----------------------------------------------------------------------------
def message():
    #if "verify_email_sent" in request.args:
    title = T("Account Registered - Please Check Your Email")
    message = T( "%(system_name)s has sent an email to %(email)s to verify your email address.\nPlease check your email to verify this address. If you do not receive this email please check you junk email or spam filters." )\
                 % {"system_name": deployment_settings.get_system_name(),
                    "email": request.vars.email}
    image = "email_icon.png"
    return dict(title = title,
                message = message,
                image_src = "/%s/static/img/%s" % (request.application, image)
                )

# -----------------------------------------------------------------------------
def rapid():
    """ Set/remove rapid data entry flag """

    val = request.vars.get("val", True)
    if val == "0":
        val = False
    else:
        val = True
    session.s3.rapid_data_entry = val

    response.view = "xml.html"
    return dict(item=str(session.s3.rapid_data_entry))

# -----------------------------------------------------------------------------
def user():
    "Auth functions based on arg. See gluon/tools.py"

    auth.settings.on_failed_authorization = URL(f="error")

    _table_user = auth.settings.table_user
    if request.args and request.args(0) == "profile":
        #_table_user.organisation.writable = False
        #_table_user.utc_offset.readable = True
        #_table_user.utc_offset.writable = True
        pass

    login_form = register_form = None
    if request.args and request.args(0) == "login":
        auth.messages.submit_button = T("Sign In")
        form = auth()
        login_form = form
        if s3.crud.submit_style:
            form[0][-1][1][0]["_class"] = s3.crud.submit_style
    elif request.args and request.args(0) == "register":
        if deployment_settings.get_terms_of_service():
            auth.messages.submit_button = T("I accept. Create my account.")
        else:
            auth.messages.submit_button = T("Register")
        # Default the profile language to the one currently active
        _table_user.language.default = T.accepted_language
        form = auth()
        register_form = form
         # Add client-side validation
        s3_register_validation()
    else:
        form = auth()

    if request.args and request.args(0) == "profile" and \
       deployment_settings.get_auth_openid():
        form = DIV(form, openid_login_form.list_user_openids())

    self_registration = deployment_settings.get_security_self_registration()

    # Use Custom Ext views
    # Best to not use an Ext form for login: can't save username/password in browser & can't hit 'Enter' to submit!
    #if request.args(0) == "login":
    #    response.title = T("Login")
    #    response.view = "auth/login.html"

    return dict(form=form,
                login_form=login_form,
                register_form=register_form,
                self_registration=self_registration)

# -----------------------------------------------------------------------------
def source():
    """ RESTful CRUD controller """
    return s3_rest_controller("s3", "source")

# -----------------------------------------------------------------------------
# About Sahana
def apath(path=""):
    """ Application path """
    import os
    from gluon.fileutils import up
    opath = up(request.folder)
    #TODO: This path manipulation is very OS specific.
    while path[:3] == "../": opath, path=up(opath), path[3:]
    return os.path.join(opath,path).replace("\\", "/")

def about():
    """
        The About page provides details on the software dependencies and
        versions available to this instance of Sahana Eden.

        @ToDo: Avoid relying on Command Line tools which may not be in path
               - pull back info from Python modules instead?
    """
    import sys
    import subprocess
    import string
    python_version = sys.version
    web2py_version = open(apath("../VERSION"), "r").read()[8:]
    sahana_version = open(os.path.join(request.folder, "VERSION"), "r").read()
    # Database
    sqlite_version = None
    mysql_version = None
    mysqldb_version = None
    pgsql_version = None
    psycopg_version = None
    if db_string[0].find("sqlite") != -1:
        try:
            import sqlite3
            #sqlite_version = (subprocess.Popen(["sqlite3", "-version"], stdout=subprocess.PIPE).communicate()[0]).rstrip()
            sqlite_version = sqlite3.version
        except:
            sqlite_version = T("Unknown")
    elif db_string[0].find("mysql") != -1:
        try:
            mysql_version = (subprocess.Popen(["mysql", "--version"], stdout=subprocess.PIPE).communicate()[0]).rstrip()[10:]
        except:
            mysql_version = T("Unknown")
        try:
            import MySQLdb
            mysqldb_version = MySQLdb.__revision__
        except:
            mysqldb_version = T("Not installed or incorrectly configured.")
    else:
        # Postgres
        try:
            pgsql_reply = (subprocess.Popen(["psql", "--version"], stdout=subprocess.PIPE).communicate()[0])
            pgsql_version = string.split(pgsql_reply)[2]
        except:
            pgsql_version = T("Unknown")
        try:
            import psycopg2
            psycopg_version = psycopg2.__version__
        except:
            psycopg_version = T("Not installed or incorrectly configured.")
    # Libraries
    try:
        import reportlab
        reportlab_version = reportlab.Version
    except:
        reportlab_version = T("Not installed or incorrectly configured.")
    try:
        import xlwt
        xlwt_version = xlwt.__VERSION__
    except:
        xlwt_version = T("Not installed or incorrectly configured.")
    return dict(
                python_version=python_version,
                sahana_version=sahana_version,
                web2py_version=web2py_version,
                sqlite_version=sqlite_version,
                mysql_version=mysql_version,
                mysqldb_version=mysqldb_version,
                pgsql_version=pgsql_version,
                psycopg_version=psycopg_version,
                reportlab_version=reportlab_version,
                xlwt_version=xlwt_version
                )

# =============================================================================
# LA Custom Views
# =============================================================================
def why():
    """ Custom View """
    response.title = T("Why?")
    return dict()

# -----------------------------------------------------------------------------
def contact():
    """ Custom View """
    response.title = T("Contact us")
    return dict()

# -----------------------------------------------------------------------------
def help():
    """ Custom View """
    response.title = T("Help")
    entries = []
    question = T("How do I register as a volunteer?")
    reply = T("Follow these steps, to register:")
    list = []
    list.append(T("On the Home Page, click the 'Volunteer' link.  Review the 'List of Requests for Volunteers'.  To select a %(request)s (Volunteer Task), click on %(apply)s; OR You can register by clicking the 'Register' link located on the top of the web page.") % dict(request="<i>%s</i>" % T("Request for Volunteers"),
                                                                                                                                                                                                                                                                                apply = "<strong>%s</strong>" % T("'APPLY'")))
    list.append(T("Enter your information into the Required Fields.  After you have entered your information, click %(accept)s to register.") % dict(accept="<strong>%s</strong" % T("'I ACCEPT, CREATE MY ACCOUNT'")))
    entry = (question, reply, list)
    entries.append(entry)
    question = T("How do I update my Profile, Skills and Emergency Details?")
    reply = T("After you are signed-in, please follow these steps to edit your profile: ")
    list = []
    list.append(T("On the top menu, click %(volunteer)s.") % dict(volunteer="<strong>%s</strong>" % T("VOLUNTEER")))
    list.append(T("On the left menu, click %(profile)s .") % dict(profile="<strong>%s</strong>" % T("'My Profile'")))
    list.append(T("On this page, you can update your profile."))
    list.append(T("Additional information like %(notifications)s and other volunteer agency affiliations also can be updated in this page.") % dict(notifications="<strong>%s</strong>" % T("Notifications")))
    list.append(T("Then click %(save)s") % dict(save="<strong>%s</strong>" % T("Save")))
    list.append(T("On the left menu, click %(skills)s.") % dict(skills="<strong>%s</strong>" % T("Skills")))
    list.append(T("Click the %s sign next to the skill(s) that best describes how you can support the City.") % "<strong>'+'</strong>")
    list.append(T("You may also search for a skill by providing the first few characters in the search box.  (Example: When searching for 'Driving' skills, enter the first letters of the word)."))
    list.append(T("If your skill(s) is not listed, you may enter it in the %(extraSkills)s field below.") % dict(extraSkills="<strong>%s</strong>" % T("Skills")))
    list.append(T("Then click %(save)s") % dict(save="<strong>%s</strong>") % T("Save"))
    list.append(T("You may also update your Emergency Contacts information by clicking on 'Emergency Contacts' located on the left menu."))
    list.append(T("Then click %(save)s") % dict(save="<strong>%s</strong>") % T("Save"))
    entry = (question, reply, list)
    entries.append(entry)
    question = T("How do I apply for a Volunteer Request after I have registered with Give2LA?")
    reply = T("You can apply by clicking the %(signin)s link located on the top of the web page.") % dict(signin="<strong>%s</strong>" % T("'Sign-In'"))
    list = []
    list.append(T("Enter your E-Mail and Password information."))
    list.append(T("Review the 'List of Requests for Volunteers'."))
    list.append(T("To select a Volunteer Task, click on %(apply)s.") % dict(apply="<strong>%s</strong>") % T("'APPLY'"))
    list.append(T("Review the 'Volunteer Assignment Details'.  Enter your Emergency Contact information."))
    list.append(T("Download the Give2LA Volunteer Registration Forms, complete the forms, and take them with you to your Volunteer Assignment."))
    list.append(T("Then click %(commit)s.") % dict(commit="<strong>%s</strong>") % T("Commit"))
    list.append(T("Review the Volunteer Application details."))
    list.append(T("Then click %(form)s and take them with you to your Volunteer Assignment.") % dict(form="<strong>%s</strong>" % T("'Print Volunteer Assignment Form'")))
    entry = (question, reply, list)
    entries.append(entry)
    question = T("Can I provide feedback or evaluation for an assignment after volunteering?")
    reply = T("Yes.  After you have signed-in, follow these steps:")
    list = []
    list.append(T("On the top menu, click %(volunteer)s.") % dict(volunteer="<strong>%s</strong>") % T("VOLUNTEER"))
    list.append(T("On the left menu, click  %(assignments)s.") % dict(assignments="<strong>%s</strong>") % T("'My Assignments'"))
    list.append(T("Click on the 'Details' button of the Volunteer Task you have completed."))
    list.append(T("Scroll down to the bottom of the screen to get to 'Evaluation of Event'."))
    list.append(T("Enter the evaluation details; and click %(save)s") % dict(save="<strong>%s</strong>") % T("Save"))
    entry = (question, reply, list)
    entries.append(entry)
    question = T("I would like to register my corporation for donations, what is the process?")
    reply = T("Follow these steps, to register")
    list = []
    list.append(T("Locate the %(register)s for Corporations and Organizations on the Home Page and click on it.") % dict(register="<strong>%s</strong>" % T("'CLICK HERE TO REGISTER'")))
    list.append(T("Enter the Mandatory details and click on the button %(accept)s at the bottom of the screen to register") % dict(accept="<strong>%s</strong" % T("'I ACCEPT, CREATE MY ACCOUNT'")))
    entry = (question, reply, list)
    entries.append(entry)

    return dict(entries=entries)

# -----------------------------------------------------------------------------
def faq():
    """ Custom View """
    donateLink = A(T("Donate Page"), _href=URL(c="don", f="index"))

    response.title = T("Frequently Asked Questions")
    entries = []
    question = T("Is there a minimum age limit to volunteer?")
    reply = T("Yes, you have to be at least 18 years of age to Volunteer.")
    entry = (question, reply)
    entries.append(entry)
    question = T("What is the Privacy policy of Give2LA?")
    reply = T("Please refer to the %(privacy)s") % dict(privacy=A(T("Privacy Policy"),
                                                        _href=URL(c="default", f="disclaimer")))
    entry = (question, reply)
    entries.append(entry)
    question = T("Can I bring a friend to volunteer?")
    reply = T("Yes, but your friend must also %(register)s and apply to the same Volunteer Assignment.") % dict(register=A(T("Register"),
                                                                                                                _href=URL(c="vol", f="register")))
    entry = (question, reply)
    entries.append(entry)
    question = T("Will I get any food or reimbursements for expenses while volunteering?")
    reply = T("No, unless it is otherwise stated on the Volunteer Assignment.")
    entry = (question, reply)
    entries.append(entry)
    question = T("Can I donate cash to support the City of Los Angeles?")
    reply = T("Yes, you can donate cash to the %(laepf)s who support the City of Los Angeles or other partner organizations listed on the %(donate)s. These links will take you directly to the organization's website to complete the cash donation transaction.") % dict(laepf="<a href=http://laemergencypreparednessfoundation.org/>LAEPF</a>", donate=donateLink)
    entry = (question, reply)
    entries.append(entry)
    question = T("What is the process for donating in-kind Items?")
    reply = T("The City of Los Angeles prefers cash donations. In-kind items can be donated directly to the organization(s) listed under Donate Items  or through any Upcoming Donation Drive  on the %(donate)s") % dict(donate=donateLink)
    entry = (question, reply)
    entries.append(entry)
    question = T("Do I have to be a U.S. citizen or legal U.S. resident to volunteer?")
    reply = T("Yes.  You must be a U.S. citizen,  legal U.S. resident, or have gained legal entry into the United States.")
    entry = (question, reply)
    entries.append(entry)
    question = T("Do I have to live in the City of Los Angeles to volunteer?")
    reply = T("No, anyone may register to support the City of Los Angeles' volunteer efforts.")
    entry = (question, reply)
    entries.append(entry)
    question = T("Is my donation tax deductible?")
    reply = T("Yes.  All donations are tax deductible.  The partner organization that receives your donation will provide a receipt for your donation.  Please make sure you obtain your tax receipt from the organization and keep it in a safe place for tax purposes.  The City of Los Angeles will not issue receipts for your donation.")
    entry = (question, reply)
    entries.append(entry)

    return dict(entries=entries)

# -----------------------------------------------------------------------------
def sitemap():
    """ Custom View """
    response.title = T("Site Map")
    return dict()

# -----------------------------------------------------------------------------
def disclaimer():
    """ Custom View """
    response.title = T("Disclaimer")
    return dict()

# -----------------------------------------------------------------------------
def register():
    """
        Registration for Organisations
        - custom form
    """

    s3mgr.load("pr_address")

    # Which type of organisation are we registering?
    don = False
    vol = False
    if "type" in request.vars:
        if request.vars.type == "don":
            don = True
        elif request.vars.type == "vol":
            vol = True
            auth.settings.registration_requires_approval = True

    auth.messages.submit_button = T("I accept. Create my account.")
    request.args = ["register"]
    _table_user.language.default = T.accepted_language
    _table_user.language.readable = False
    _table_user.language.writable = False
    form = auth()
    form.attributes["_id"] = "regform"
    # Custom class for Submit Button
    form[0][-1][0][0]["_class"] = "accept-button"

    # Cancel button
    form[0][-1][0].append(BR())
    #form[0][-1][1].append(INPUT(_type="reset", _value=T("Cancel")))
    form[0][-1][0].append(INPUT(_type="button",
                                _value=T("Cancel"),
                                _class="wide-grey-button",
                                _onClick="javascript: history.go(-1)"))

    formstyle = s3.crud.formstyle

    # Organisation
    if form.errors.organisation:
        organisation_error = DIV(form.errors.organisation,
                                 _id="organisation__error",
                                 _class="error",
                                 _style="display: block;")
    else:
        organisation_error = ""
    if don:
        label = T("Corporation/Organization Name")
    else:
        label = T("Organization Name")
    row = formstyle(id      = "organisation",
                    label   = LABEL("%s:" % label,
                                    SPAN(" *", _class="req")),
                    widget  = DIV(INPUT(_name="organisation",
                                        _id="organisation",
                                        _class="string"),
                                  organisation_error),
                    comment = "")
    form[0].insert(0, row)

    # Industry Sector
    if vol:
        hidden = True
        widget = INPUT(_name="sector_id",
                       _id="sector_id",
                       _class="string")
    else:
        from gluon.sqlhtml import OptionsWidget
        hidden = False
        widget = OptionsWidget.widget(db.org_organisation.sector_id,
                                      value="")
    # dropdown
    row = formstyle(id      = "sector_id",
                    label   = LABEL("%s:" % T("Industry Sector")),
                    widget  = widget,
                    comment = "",
                    hidden = hidden)
    form[0].insert(1, row)
    # freetext box for not listed
    row = formstyle(id      = "sector_other",
                    label   = LABEL("%s:" % T("Other Sector not listed"),
                                    SPAN(" *", _class="req")),
                    widget  = INPUT(_name="sector_other",
                                    _id="org_organisation_sector_other",
                                    _class="string"),
                    comment = "",
                    hidden = True)
    form[0].insert(2, row)
    table = db.org_sector
    query = (table.uuid == "OTHER_UNLISTED")
    other_unlisted = db(query).select(table.id,
                                      limitby=(0, 1)).first()
    if other_unlisted:
        other_unlisted = other_unlisted.id

    # Primary Contact Person section
    row = TR(TD(LABEL(T("Primary Contact")),
                _colspan="3",
                _class="subheading"))
    form[0][2].append(row)
    row = formstyle(id      = "middle_name",
                    label   = LABEL("%s:" % T("Middle Name")),
                    widget  = INPUT(_name="middle_name",
                                    _id="middle_name",
                                    _class="string"),
                    comment = "")
    form[0][4].append(row)

    row = formstyle(id      = "secondary_email",
                    label   = LABEL("%s:" % T("Secondary Email")),
                    widget  = INPUT(_name="secondary_email",
                                    _id="secondary_email",
                                    _class="string"),
                    comment = "")
    form[0][12].append(row)

    # What are you offering?
    if don or vol:
        hidden = True
    else:
        hidden = False
    row = formstyle(id      = "offer",
                    hidden  = hidden,
                    label   = LABEL("%s:" % T("We can offer"),
                                    SPAN(" *", _class="req")),
                    widget  = (T("Items"),
                               INPUT(_type="checkbox",
                                     _value="on",
                                     value="on" if don else "",
                                     _name="has_items",
                                     _id="has_items",
                                     _class="boolean"),
                               T("Volunteers"),
                               INPUT(_type="checkbox",
                                     _value="on",
                                     value="on" if vol else "",
                                     _name="vols",
                                     _id="vols",
                                     _class="boolean"),
                               ),
                    comment = "")
    form[0][12].append(row)

    # Phone
    mobile_phone_widget = INPUT(_name="mobile_phone",
                                _id="",
                                _class="string")
    if form.errors.mobile_phone:
        mobile_phone_error = DIV(form.errors.mobile_phone,
                                 _id="mobile_phone__error",
                                 _class="error",
                                 _style="display: block;")
        # Can't wrap widget in a DIV for client-side validation, so only do so
        # when server-side validation happens
        mobile_phone_widget = DIV(mobile_phone_widget,
                                  mobile_phone_error)

    work_phone_widget = INPUT(_name="work_phone",
                              _id="",
                              _class="string")
    if form.errors.work_phone:
        work_phone_error = DIV(form.errors.work_phone,
                               _id="work_phone__error",
                               _class="error",
                               _style="display: block;")
        # Can't wrap widget in a DIV for client-side validation, so only do so
        # when server-side validation happens
        work_phone_widget = DIV(work_phone_widget,
                                work_phone_error)

    row = formstyle(id      = "phone",
                    label   = LABEL("%s:" % T("Work Phone"),
                                    SPAN(" *", _class="req")),
                    widget  = work_phone_widget,
                    comment = "")
    form[0][12].append(row)
    row = formstyle(id      = "phone",
                    label   = LABEL("%s:" % current.deployment_settings.get_ui_label_mobile_phone(),
                                    #SPAN(" *", _class="req")
                                    ),
                    widget  = mobile_phone_widget,
                    comment = "")
    form[0][12].append(row)

    # Address
    row = TR(TD(LABEL(T("Corporation/Organization Address")),
                _colspan="3",
                _class="subheading"))
    form[0][12].append(row)
    if form.errors.address1:
        address1_error = DIV(form.errors.address1,
                             _id="address1__error",
                             _class="error",
                             _style="display: block;")
    else:
        address1_error = ""
    row = formstyle(id      = "address1",
                    label   = LABEL("%s:" % T("Address 1"),
                                    SPAN(" *", _class="req")
                                    ),
                    widget  = (INPUT(_name="address1",
                                     _id="address1",
                                     _class="string"),
                               address1_error),
                    comment = "")
    form[0][12].append(row)
    row = formstyle(id      = "address2",
                    label   = LABEL("%s:" % T("Address 2")),
                    widget  = INPUT(_name="address2",
                                    _id="address2",
                                    _class="string"),
                    comment = "")
    form[0][12].append(row)
    row = formstyle(id      = "city",
                    label   = LABEL("%s:" % T("City"),
                                    SPAN(" *", _class="req")),
                    widget  = INPUT(_name="city",
                    _id     = "city",
                    _class  = "string"),
                    comment = "")
    form[0][12].append(row)
    states = S3LocationDropdownWidget(level="L1",
                                      default="California",
                                      empty=False)
    widget = states(db.pr_address.location_id, None)
    row = formstyle(id      = "state",
                    label   = LABEL("%s:" % T("State"),
                                    SPAN(" *", _class="req")),
                    widget  = widget,
                    comment = "")
    form[0][12].append(row)
    if form.errors.zip:
        zip_error = DIV(form.errors.zip,
                        _id="zip__error",
                        _class="error",
                        _style="display: block;")
    else:
        zip_error = ""
    row = formstyle(id      = "zip",
                    label   = LABEL("%s:" % T("Zip"),
                                    SPAN(" *", _class="req")
                                   ),
                    widget  = ( INPUT(_name="zip",
                                      _id="zip",
                                      _class="string"),
                                zip_error
                                ),
                    comment = "")
    form[0][12].append(row)


    #form[0][-2].append(TR(TD(LABEL(T("Terms of Service:"),
    #                               _id="terms_of_service__label"),
    #                         _class="w2p_fl"),
    #                      TD(LABEL(TEXTAREA(deployment_settings.get_terms_of_service(),
    #                                        _onfocus="this.rows=10",
    #                                        _readonly="readonly",
    #                                        _style="width:100%;text-align:",
    #                                        _cols="80", _rows="10"),
    #                               _id="terms_of_service"),
    #                         _class="w2p_fw",
    #                         _colspan="2"),
    #                      _id="terms_of_service__row"))

    # Add client-side validation
    # simplified copy of s3_register_validation()
    script = "".join(( """
$('#org_organisation_sector_id').change(function() {
    var sector = $(this).val();
    if (sector == '""", str(other_unlisted), """') {
        $('#sector_other1').show();
        $('#sector_other').show();
    } else {
        $('#sector_other1').hide();
        $('#sector_other').hide();
    }
});
var required = '""", str(T("This field is required.")), """';
$('#regform').validate({
    errorClass: 'req',
    rules: {
        first_name: {
            required: true
            },
        last_name: {
            required: true
            },
        email: {
            required: true,
            email: true
        },
        organisation: {
            required: true
        },
        sector_other: {
            required: true
        },
        //mobile_phone: {
        //    required: true
        //},
        work_phone: {
            required: true
        },
        address1: {
            required: true
        },
        city: {
            required: true
        },
        zip: {
            required: true
        },
        password: {
            required: true
        },
        password_two: {
            required: true,
            equalTo: '.password:first'
        }
    },
    messages: {
        first_name: '""", str(T("Enter your firstname")), """',
        last_name: required,
        email: {
            required: '""", str(T("Please enter a valid email address")), """',
            minlength: '""", str(T("Please enter a valid email address")), """'
        },
        organisation: required,
        sector_other: required,
        //mobile_phone: required,
        work_phone: required,
        address1: required,
        city: required,
        zip: required,
        password: {
            required: '""", str(T("Provide a password")), """'
        },
        password_two: {
            required: '""", str(T("Repeat your password")), """',
            equalTo: '""", str(T("Enter the same password as above")), """'
        }
    },
    errorPlacement: function(error, element) {
        error.appendTo( element.parent().next() );
    },
    submitHandler: function(form) {
        form.submit();
    }
});""" ))
    response.s3.jquery_ready.append( script )

    if session.s3.debug:
        response.s3.scripts.append( "%s/jquery.validate.js" % s3_script_dir )
        response.s3.scripts.append( "%s/jquery.pstrength.1.3.js" % s3_script_dir )
    else:
        response.s3.scripts.append( "%s/jquery.validate.min.js" % s3_script_dir )
        response.s3.scripts.append( "%s/jquery.pstrength.1.3.min.js" % s3_script_dir )

    response.s3.jquery_ready.append("$('.password:first').pstrength();\n")
    response.s3.js_global.append("".join((
        "S3.i18n.password_chars = '%s';\n" % T("The minimum number of characters is "),
        "S3.i18n.very_weak = '%s';\n" % T("Very Weak"),
        "S3.i18n.weak = '%s';\n" % T("Weak"),
        "S3.i18n.medium = '%s';\n" % T("Medium"),
        "S3.i18n.strong = '%s';\n" % T("Strong"),
        "S3.i18n.very_strong = '%s';\n" % T("Very Strong"),
        "S3.i18n.too_short = '%s';\n" % T("Too Short"),
        "S3.i18n.unsafe_password = '%s';\n" % T("Unsafe Password Word!"),
    )))

    response.title = T("Register")
    response.s3.has_required = True

    return dict(form=form)

# -----------------------------------------------------------------------------
def register_validation(form):
    """ Validate the custom fields in registration form """

    # Name
    if "organisation" in request.post_vars and request.post_vars.organisation:
        # Check not in use
        table = db.org_organisation
        query = (table.name == request.post_vars.organisation)
        name = db(query).select(table.id, limitby=(0, 1)).first()
        if name:
            form.errors.organisation = T("Organization Name is already in use")
    else:
        form.errors.organisation = T("Organization Name is required")

    # Sector
    table = db.org_sector
    query = (table.uuid == "OTHER_UNLISTED")
    other_unlisted = db(query).select(table.id,
                                      limitby=(0, 1)).first()
    if other_unlisted:
        if request.post_vars.sector_id == other_unlisted.id:
            # Other is Required
            if "sector_other" in request.post_vars and request.post_vars.sector_other:
                pass
            else:
                form.errors.organisation = T("Other sector details required")

    # Phone
    if "work_phone" in request.post_vars and request.post_vars.work_phone:
        regex = re.compile(single_phone_number_pattern)
        if not regex.match(request.post_vars.work_phone):
            form.errors.work_phone = T("Invalid phone number")
    else:
        form.errors.work_phone = T("Phone number is required")
    if "mobile_phone" in request.post_vars and request.post_vars.mobile_phone:
        regex = re.compile(single_phone_number_pattern)
        if not regex.match(request.post_vars.mobile_phone):
            form.errors.mobile_phone = T("Invalid phone number")
    #else:
    #    form.errors.mobile_phone = T("Phone number is required")

    # Address
    if not request.post_vars.address1:
        form.errors.address1 = T("Address is required")
    if not request.post_vars.city:
        form.errors.city = T("City is required")
    if not request.post_vars.zip:
        form.errors.zip = T("Zip is required")

# -----------------------------------------------------------------------------
def register_onaccept(form):
    # Usual Registration Tasks
    # (PR record, Authenticated Role, Contacts)
    person = auth.s3_register(form)

    # LA-specific
    ptable = db.pr_person
    query = (ptable.id == person)

    if request.post_vars.middle_name:
        db(query).update(middle_name=request.post_vars.middle_name)

    pe = db(query).select(ptable.pe_id,
                          limitby=(0, 1)).first().pe_id

    # Organisation
    organisation = request.post_vars.organisation
    if "vols" in request.post_vars and request.post_vars.vols == "on":
        has_vols = True
    else:
        has_vols = False
    if "has_items" in request.post_vars and request.post_vars.has_items == "on":
        has_items = True
    else:
        has_items = False

    # Phone
    table = db.pr_contact
    work_phone = request.post_vars.work_phone
    mobile_phone = request.post_vars.mobile_phone
    if mobile_phone:
        # Don't auto-subscribe to SMS (priority 10)
        table.insert(pe_id = pe,
                     contact_method = "SMS",
                     value = mobile_phone,
                     priority=10)
    if work_phone:
        table.insert(pe_id = pe,
                     contact_method = "WORK_PHONE",
                     value = work_phone)

    # Address
    address1 = request.post_vars.address1
    address2 = request.post_vars.address2
    #if address2:
    #    address = "%s\n%s" % (address1,
    #                          address2)
    #else:
    #    address = address1
    city = request.post_vars.city
    state = request.post_vars.location_id
    zip = request.post_vars.zip
    if request.post_vars.sector_other:
        sector_other = "Sector: %s" % request.post_vars.sector_other
    else:
        sector_other = ""
    otable = db.org_organisation
    org = otable.insert(name = organisation,
                        has_vols = has_vols,
                        has_items = has_items,
                        phone=work_phone,
                        phone_mobile=mobile_phone,
                        address=address1,
                        address_2=address2,
                        L3=city,
                        L1=state,
                        postcode=zip,
                        sector_id=request.post_vars.sector_id,
                        comments=sector_other)
    record = Storage(id=org)
    s3mgr.model.update_super(otable, record)
    auth.s3_set_record_owner(otable, org)
    if auth.user:
        # For OrgDons which don't require approval
        # Update the session
        auth.user.organisation_id = org
        user_id = auth.user.id
    else:
        user_id = form.vars.id

    # Create HRM
    #table = db.hrm_human_resource
    #hrm = table.insert(person_id = person,
    #                   organisation_id = org,
    #                   focal_point = True,
    #                   owned_by_user = user_id)
    #record = Storage(id=hrm)
    #s3mgr.model.update_super(table, record)
    #auth.s3_set_record_owner(table, hrm)

    # Create Organisation Contacts
    table = db.org_contact
    org_contact = table.insert(organisation_id = org,
                               focal_point = True,
                               first_name = request.post_vars.first_name,
                               middle_name = request.post_vars.middle_name,
                               last_name = request.post_vars.last_name,
                               email = request.post_vars.email,
                               work_phone = request.post_vars.work_phone,
                               mobile_phone = request.post_vars.mobile_phone)
    record = Storage(id=org_contact)
    s3mgr.model.update_super(table, record)
    auth.s3_set_record_owner(table, org_contact)

    # Set the Roles
    person = db(query).select(ptable.uuid,
                              limitby=(0, 1)).first()
    if not person:
        # Error
        return
    utable = db[auth.settings.table_user]
    query = (utable.person_uuid == person.uuid)
    db(query).update(organisation_id = org)
    #user = db(query).select(utable.id,
    #                        limitby=(0, 1)).first()
    #if not user:
    #    # Error
    #    return
    mtable = db[auth.settings.table_membership]
    gtable = db[auth.settings.table_group]
    _org = db(otable.id == org).select(otable.owned_by_organisation,
                                       limitby=(0, 1)).first()
    if _org:
        mtable.insert(user_id = user_id,
                      group_id = _org.owned_by_organisation)

    if has_vols:
        OrgVol = db(gtable.uuid == ORG_VOL).select(gtable.id,
                                                   limitby=(0, 1)).first()
        if OrgVol:
            mtable.insert(user_id = user_id,
                          group_id = OrgVol.id)
        # Go to the Contacts page so that a secondary contact can be added
        # Flag that we've come from registration for subsequent workflow
        #redirect(URL(c="vol", f="organisation", args=[org, "human_resource"],
        #             vars={"register":1}))

    if has_items:
        OrgDon = db(gtable.uuid == ORG_DON).select(gtable.id,
                                                   limitby=(0, 1)).first()
        if OrgDon:
            mtable.insert(user_id = user_id,
                          group_id = OrgDon.id)
        # Go to the Contacts page so that a secondary contact can be added
        # Flag that we've come from registration for subsequent workflow
        redirect(URL(c="don", f="organisation", args=[org, "contact"],
                     vars={"register":1}))

# -----------------------------------------------------------------------------
#auth.settings.registration_requires_approval = True
auth.settings.register_onvalidation = register_validation
auth.settings.register_onaccept = register_onaccept

# END =========================================================================
