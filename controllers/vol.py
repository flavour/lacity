# -*- coding: utf-8 -*-

"""
   Volunteer Module
"""

module = request.controller
resourcename = request.function

# Options Menu (available in all Functions)
shn_menu(module)

# -----------------------------------------------------------------------------
def index():
    """ Module's Home Page """

    if s3_has_role(STAFF):
        response.view = "vol/index.html"
        return dict()
    else:
        redirect(URL(c="vol", f="req_skill"))

# -----------------------------------------------------------------------------
# People
# -----------------------------------------------------------------------------
def person():
    """
        Person Controller
        - List of Volunteers
    """

    module = "pr"
    tablename = "pr_person"
    table = db[tablename]

    s3.filter = (table.volunteer == True)
    table.volunteer.default = True
    
    ADD_VOL = T("Add Volunteer")
    LIST_VOLS = T("List Volunteers")
    s3.crud_strings[tablename] = Storage(
        title_create = T("Add a Volunteer"),
        title_display = T("Volunteer Details"),
        title_list = LIST_VOLS,
        title_update = T("Edit Volunteer Details"),
        title_search = T("Search Volunteers"),
        subtitle_create = ADD_VOL,
        subtitle_list = T("Volunteers"),
        label_list_button = LIST_VOLS,
        label_create_button = ADD_VOL,
        label_delete_button = T("Delete Volunteer"),
        msg_record_created = T("Volunteer added"),
        msg_record_modified = T("Volunteer details updated"),
        msg_record_deleted = T("Volunteer deleted"),
        msg_list_empty = T("No Volunteers currently registered"))
    
    configure(tablename,
              insertable=False,
              orderby = table.last_name,
              list_fields=["id",
                           "last_name",
                           "first_name",
                           (T("Email"), "email"),
                           (T("Phone"), "phone"),
                           (T("Address"), "address"),
                           ],
              )

    # Load Model
    load("pr_address")
    db.pr_address.location_id.readable = False
    db.pr_address.location_id.writable = False
    db.pr_address.comments.readable = False
    db.pr_address.comments.writable = False
    configure("pr_address",
              list_fields = ["id",
                             "type",
                             #"building_name",
                             "address",
                             #"L4",
                             "L3",
                             #"L2",
                             "L1",
                             #"L0"
                             "postcode",
                             ])
    
    load("vol_skill")

    configure("vol_skill",
              deletable = False)

    configure("pr_contact",
              list_fields = ["contact_method",
                             "value"
                             ],
              )

    tabs = [ (T("Basic Details"), None),
             (T("Skills"), "skill"),
             (T("Organizational Affiliations"), "organisation"),
             (T("Address"), "address"),
             (T("Contact Details"), "contact"),
        ]

    rheader = lambda r: vol_pr_rheader(r, tabs=tabs)

    output = s3_rest_controller(module, resourcename,
                                rheader=rheader)

    return output

# -----------------------------------------------------------------------------
def vol_pr_rheader(r, tabs=[]):
    """ Resource headers for component views """

    rheader = None
    rheader_tabs = s3_rheader_tabs(r, tabs)

    if r.representation == "html":

        if r.name == "person":
            # Person Controller
            person = r.record
            if person:
                rheader = DIV(TABLE(

                    TR(TH("%s: " % T("Name")),
                       vita.fullname(person),
                       TH(""),
                       ""),

                    ), rheader_tabs)

    return rheader

# =============================================================================
def organisation():
    """
        Org Controller for OrgAdmins
    """

    table = db.org_organisation

    table.acronym.readable = False
    table.acronym.writable = False
    org_has_vols_field = table.has_vols
    org_has_vols_field.default = True
    s3.filter = (org_has_vols_field == True)

    if "register" in request.vars:
        s3.show_listadd = True
    output = organisation_controller(organisation_rheader = organisation_rheader)

    if isinstance(output, dict):
        output["title"] = T("Edit Organization Profile")
    return output

# -----------------------------------------------------------------------------
def organisation_rheader(r, tabs = []):
    """ Organisation rheader """

    if r.representation == "html":

        if r.record is None:
            # List or Create form: rheader makes no sense here
            return None

        tabs = [(T("Basic Details"), None),
                (T("Contacts"), "human_resource"),
                #(T("Activities"), "activity")
                ]
        rheader_tabs = s3_rheader_tabs(r, tabs)

        organisation = r.record

        rheader = DIV(TABLE(
            TR(
                TH("%s: " % T("Organization")),
                organisation.name,
                ),
            ),
            rheader_tabs
        )
        return rheader
    return None

# =============================================================================
def vol_sidebar():
    """ Sidebar for people who aren't logged-in """

    request.args = ["login"]
    loginform = auth()
    loginform.attributes["_id"] = "loginform"
    request.args = []

    if not response.menu_left:
        response.menu_left = DIV()

    if not auth.is_logged_in():
        response.menu_left.append(
    DIV(
        P(T("Already registered?"),
          BR(),
          "%s:" % T("Sign in here")),
        #loginform,
        FORM(
            LABEL(T("Email"), _for="email"),
            INPUT(_type="text", _name="email", _title=T("Email")),
            LABEL(T("Password"), _for="password"),
            INPUT(_type="password", _name="password", _title=T("Password")),
            A(SPAN(T("Sign In")),
              _href="#",
              _onclick="$('#sign-in-menu form').submit();",
              _class="sign-in-button"),
            loginform.custom.end,
        _action="", _enctype="multipart/form-data", _method="post"),
    _id="sign-in-menu",
    _class="sub-menu"))
    response.menu_left.append(
    DIV(
        P("%s:" % T("Other Volunteering Opportunities"), _class="osm-title"),
        UL(
            LI(
                A(
                    DIV("American Red Cross", _class="link-name"),
                    DIV(
                        H3("redcrossla.org"),
                        IMG(_src="/%s/static/img/la/logo_arc.png" % request.application, _width="87", _height="29", _alt="American Red Cross Logo"),
                        P(T("Rooted in over a century's tradition of service to the community, the American Red Cross is one of the world's most renowned humanitarian organizations.  American Red Cross volunteers assist with community emergency preparedness, services to the armed forces, emergency and disaster response, blood services, health and safety education, international services and other support volunteer services.")),
                    _class="other-popup"),
                _href="http://redcrossla.org", _target="_blank",
                _title="American Red Cross - %s" % T("Link will open to new Window"))
            ),
            LI(
                A(
                    DIV("CERT", _class="link-name"),
                    DIV(
                        H3("www.cert-la.com"),
                        IMG(_src="/%s/static/img/la/logo_cert.png" % request.application, _width="101", _height="100", _alt="CERT Logo"),
                        P(T("The Los Angeles Fire Department Community Emergency Response Training Program (CERT), has been educating the citizens of Los Angeles in Disaster Preparedness since 1987.")),
                    _class="other-popup"),
                _href="http://www.cert-la.com", _target="_blank",
                _title="CERT - %s" % T("Link will open to new Window"))
            ),
            LI(
                A(
                    DIV("LA County Disaster Healthcare Volunteers", _class="link-name"),
                    DIV(
                        H3("www.lacountydhv.org"),
                        IMG(_src="/%s/static/img/la/logo_dhv.png" % request.application, _width="88", _height="30", _alt="Disaster Healthcare Volunteers"),
                        P(T("LA County Disaster Healthcare Volunteers, comprised of 4 volunteer units, is led by the County of LA Departments of Health Services, Emergency Medical Services Agency and Public Health Emergency Preparedness and Response Program.  It is specifically for licensed medical, health, mental health, and other volunteers who want to volunteer their professional skills for public health emergencies or other large scale disasters.  Actively licensed health professionals are encouraged to register with one of the four units (MRC LA, LA County Surge Unit, Long Beach MRC, Beach Cities Health District MRC) on the State of California Disaster Healthcare Volunteers (DHV) site in advance of the next disaster.")),
                    _class="other-popup"),
                _href="http://www.lacountydhv.org", _target="_blank",
                _title="Disaster Healthcare Volunteers - %s" % T("Link will open to new Window"))
            ),
            LI(
                A(
                    DIV("L.A. Works", _class="link-name"),
                    DIV(
                        H3("www.laworks.com"),
                        IMG(_src="/%s/static/img/la/laworks.png" % request.application, _width="47", _height="40", _alt="L.A. Works Logo"),
                        P(T("L.A. Works is a 501(c)3 nonprofit, volunteer action center that creates and implements hands-on community service projects throughout the greater LA area.")),
                    _class="other-popup"),
                _href="http://www.laworks.com", _target="_blank",
                _title="L.A. Works - %s" % T("Link will open to new Window"))
            ),
            LI(
                A(
                    DIV("Public Health Emergency Volunteer Network", _class="link-name"),
                    DIV(
                        H3("publichealth.lacounty.gov"),
                        IMG(_src="/%s/static/img/la/logo_phev.png" % request.application, _width="121", _height="30", _alt="Public Health Emergency Volunteer (PHEV) Network"),
                        P(T("The purpose of the Public Health Emergency Volunteer (PHEV) Network is to increase the coordination and collaboration with established community volunteer units that are willing to assist the Department of Public Health in responding to public health emergencies by creating a system to engage, train, and deploy these groups.")),
                    _class="other-popup"),
                _href="http://publichealth.lacounty.gov/eprp/volview.htm", _target="_blank",
                _title="Public Health Emergency Volunteer (PHEV) Network - %s" % T("Link will open to new Window"))
            ),
            LI(
                A(
                    DIV("Volunteer Los Angeles", _class="link-name"),
                    DIV(
                        H3("www.VolunteerLosAngeles.org"),
                        IMG(_src="/%s/static/img/la/vla.png" % request.application, _alt="Volunteer Los Angeles Logo"),
                        P(T("Volunteer Los Angeles, a service of Assistance League of Southern California, is committed to building a strong, viable network of concerned and compassionate people who believe volunteer action creates needed change and elevates our sense of community. Through two key programs, we partner closely with local government and nonprofits to support both health care workers as well as spontaneous, unaffiliated volunteers who want to serve in times of disaster.")),
                    _class="other-popup"),
                _href="http://www.VolunteerLosAngeles.org", _target="_blank",
                _title="Volunteer Los Angeles - %s" % T("Link will open to new Window"))
            )
        ),
    _class="other-sub-menu")
    )
    if session.s3.debug:
        s3.scripts.append( "%s/jquery.hoverIntent.js" % s3_script_dir )
    else:
        s3.scripts.append( "%s/jquery.hoverIntent.minified.js" % s3_script_dir )

    s3.jquery_ready.append('''
$('.other-popup').css('display','none')
$('.tooltip .message').css('display','none')
$('.other-sub-menu li a').hoverIntent(menuFadeIn,menuFadeOut)
$('.tooltip a').hoverIntent(tooltipFadeIn,tooltipFadeOut)''')
    # For Popup Panels for the Other Menu
    # For Tooltop Panels for the Other Menu
    s3.js_global.append('''
function menuFadeIn(){$(this).children('.other-popup').fadeIn()}
function menuFadeOut(){$(this).children('.other-popup').fadeOut()}
function tooltipFadeIn(){$(this).next('.message').fadeIn()}
function tooltipFadeOut(){$(this).next('.message').fadeOut()}''')

# -----------------------------------------------------------------------------
def register():
    """ Custom Registration Form """

    load("pr_address")

    auth.messages.submit_button = T("I accept. Create my account.")
    request.args = ["register"]
    db[auth.settings.table_user].language.default = T.accepted_language
    form = auth()
    form.attributes["_id"] = "regform"
    # Custom class for Submit Button
    form[0][-1][0][0]["_class"] = "accept-button"

    # Cancel button
    form[0][-1][0].append(BR())
    #form[0][-1][0].append(INPUT(_type="reset", _value=T("Cancel")))
    form[0][-1][0].append(INPUT(_type="button",
                                _value=T("Cancel"),
                                _class="wide-grey-button",
                                _onClick="javascript: history.go(-1)"))

    formstyle = s3.crud.formstyle

    # Medical note
    row = formstyle(id      = "",
                    label   = "",
                    widget  = DIV("%s:" % T("If you are a Medical or Health Professional and wish to volunteer in a professional capacity, please register at"),
                                BR(),
                                A("LA County Disaster Healthcare Volunteers",
                                  _href="http://www.lacountydhv.org",
                                  _target="_blank"),
                                BR(),
                                BR(),
                                "%s:" % T("Individuals or Volunteer Units/Organizations interested in assisting during public health emergencies (i.e. Mass vaccine/medication dispensing sites or PODs) please register at"),
                                BR(),
                                A("LA County Department of Public Health Emergency Preparedness and Response Program",
                                  _href="http://publichealth.lacounty.gov/eprp/volview.htm",
                                  _target="_blank"),
                                _style="width: 400px;",
                                ),
                    comment = "")
    form[0].insert(0, row)

    # Middle Name
    row = formstyle(id      = "middle_name",
                    label   = LABEL("%s:" % T("Middle Name"),
                                    _for="middle_name"),
                    widget  = INPUT(_name="middle_name",
                                    _id="middle_name",
                                    _class="string"),
                    comment = "")
    form[0][2].append(row)

    # Phone
    phone_opts = {
        "SMS": current.deployment_settings.get_ui_label_mobile_phone(),
        "HOME_PHONE":   T("Home phone"),
        "WORK_PHONE":   T("Work phone")
    }
    if form.errors.phone:
        phone_error = DIV(form.errors.phone,
                          _id="phone__error",
                          _class="error",
                          _style="display: block;")
    else:
        phone_error = ""
    phone_widget = (INPUT(_name="phone",
                          _id="",
                          _class="string"),
                    SELECT(OPTION(current.deployment_settings.get_ui_label_mobile_phone(), _value="SMS"),
                           OPTION(T("Home phone"), _value="HOME_PHONE"),
                           OPTION(T("Work phone"), _value="WORK_PHONE"),
                           requires=IS_IN_SET(phone_opts),
                           value="SMS",
                           _name="phone_type",
                           _alt="Phone Type",
                           _id="phone_type"),
                    phone_error
                   )
    phone_help = DIV(_class="tooltip",
                     _title="%s|%s" % (T("Phone"),
                                       T("if you provide your Cell phone then you can choose to subscribe to SMS notifications by selecting 'My Profile' once you have completed registration.")))
    row = formstyle(id      = "phone",
                    label   = LABEL("%s:" % T("Phone"),
                                    SPAN(" *", _class="req"),
                                    _for="phone"),
                    widget  = phone_widget,
                    comment = phone_help)
    form[0][11].append(row)

    # Address
    if form.errors.address1:
        address1_error = DIV(form.errors.address1,
                             _id="address1__error",
                             _class="error",
                             _style="display: block;")
    else:
        address1_error = ""
    row = formstyle(id      = "address1",
                    label   = LABEL("%s:" % T("Address 1"),
                                    SPAN(" *", _class="req"),
                                    _for="address1"),
                    widget  = (INPUT(_name="address1",
                                     _id="address1",
                                     _class="string"),
                               address1_error),
                    comment = "")
    form[0][11].append(row)
    row = formstyle(id      = "address2",
                    label   = LABEL("%s:" % T("Address 2"),
                                    _for="address2"),
                    widget  = INPUT(_name="address2",
                                    _id="address2",
                                    _class="string"),
                    comment = "")
    form[0][11].append(row)
    row = formstyle(id      = "city",
                    label   = LABEL("%s:" % T("City"),
                                    SPAN(" *", _class="req"),
                                    _for="city"),
                    widget  = INPUT(_name="city",
                                    _id     = "city",
                                    _class  = "string"),
                    comment = "")
    form[0][11].append(row)
    states = S3LocationDropdownWidget(level="L1",
                                      default="California",
                                      empty=False)
    widget = states(db.pr_address.location_id, None)
    row = formstyle(id      = "state",
                    label   = LABEL("%s:" % T("State"),
                                    SPAN(" *", _class="req"),
                                    _for="location_id"),
                    widget  = widget,
                    comment = "")
    form[0][11].append(row)
    if form.errors.zip:
        zip_error = DIV(form.errors.zip,
                        _id="zip__error",
                        _class="error",
                        _style="display: block;")
    else:
        zip_error = ""
    row = formstyle(id      = "zip",
                    label   = LABEL("%s:" % T("Zip"),
                                    SPAN(" *", _class="req"),
                                    _for="zip"
                                   ),
                    widget  = ( INPUT(_name="zip",
                                      _id="zip",
                                      _class="string"),
                                zip_error
                                ),
                    comment = "")
    form[0][11].append(row)


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

    # Eighteen
    if form.errors.eighteen:
        eighteen_error = DIV(form.errors.eighteen,
                             _id="eighteen__error",
                             _class="error",
                             _style="display: block;")
    else:
        eighteen_error = ""
    label = LABEL(#"%s:" % T("I am 18 or over"),
                  T("I am 18 or over"),
                  SPAN(" *", _class="req"),
                  _for="eighteen",
                  _style="display: inline;",
                  _id="eighteen__label")
    widget = INPUT(_type="checkbox",
                   _value="on",
                   _name="eighteen",
                   _id="eighteen",
                   _class="boolean")
    row = TR(TD(widget, label, eighteen_error),
             TD(),
             _id="eighteen")
    form[0][-2].append(row)

    # US Citizen
    #if form.errors.citizen:
    #    citizen_error = DIV(form.errors.citizen,
    #                         _id="citizen__error",
    #                         _class="error",
    #                         _style="display: block;")
    #else:
    #    citizen_error = ""
    #label = LABEL(#"%s:" % T("I am a U.S. Citizen"),
    #              T("I am a U.S. Citizen"),
    #              SPAN(" *", _class="req"),
    #              _for="citizen",
    #              _style="display: inline;",
    #              _id="citizen__label")
    #widget = INPUT(_type="checkbox",
    #               _value="on",
    #               _name="citizen",
    #               _id="citizen",
    #               _class="boolean")
    #row = formstyle(id      = "citizen",
    #                label   = label,
    #                widget  = (widget,
    #                           citizen_error),
    #                comment = "")
    #row = TR(TD(widget, label, citizen_error),
    #         TD(),
    #         _id="citizen")
    #form[0][-2].append(row)
    
    # Program Regulations
    label  = LABEL(XML(T("I will comply with all %(program_regulations)s including being registered by an accredited disaster council or its authorized designee.") % \
                          dict(program_regulations = T("program regulations"))
                       ),
                   SPAN(" *", _class="req"),
                   _for="program_regulations",
                   _style="display: inline;",
                   )
    widget  = INPUT(_type="checkbox",
                    _value="on",
                    _name="program_regulations",
                    _id="program_regulations",
                    _class="boolean"
                    )
    if form.errors.program_regulations:
        program_regulations_error = DIV(form.errors.program_regulations,
                                        _id="program_regulations__error",
                                        _class="error",
                                        _style="display: block;")
    else:
        program_regulations_error = ""
    row = TR(TD(widget, label, program_regulations_error),
             TD(),
             _id="program_regulations")
    form[0][-2].append(row)
    
    # Loyalty Oath 
    label  = LABEL(XML(T("I will subscribe to the %(loyalty_oath)s and perform eligible disaster service duties.") % \
                           dict(loyalty_oath = T("loyalty oath"))
                       ),
                   SPAN(" *", _class="req"),
                   _for="loyalty_oath",
                   _style="display: inline;",
                   )
    widget  = INPUT(_type="checkbox",
                    _value="on",
                    _name="loyalty_oath",
                    _id="loyalty_oath",
                    _class="boolean"
                    )
    if form.errors.loyalty_oath:
        loyalty_oath_error = DIV(form.errors.loyalty_oath,
                                 _id="loyalty_oath__error",
                                 _class="error",
                                 _style="display: block;")
    else:
        loyalty_oath_error = ""
    row = TR(TD(widget, label, loyalty_oath_error),
             TD(),
             _id="loyalty_oath")
    form[0][-2].append(row)

    # Privacy Policy
    row = formstyle(id      = "",
                    label   = "",
                    widget  = DIV(XML(T("By clicking on 'I accept' below you are agreeing to the %(privacy_policy)s.") % \
                                    dict(privacy_policy = A(T("Privacy Policy"),
                                                        _href = URL(c="default",
                                                                    f="disclaimer#privacy"),
                                                        _target = "_blank"
                                                        )
                                     )
                                    ),
                                _style="width: 300px;",
                                ),
                    comment = "")
    form[0][-2].append(row)
    


    # Add client-side validation
    # simplified copy of s3_register_validation()
    script = "".join(( """
var required='""", str(T("This field is required.")), """'
$('#regform').validate({
 errorClass:'req',
 rules:{
  first_name:{required:true},
  last_name:{required:true},
  phone:{required:true},
  email:{required:true,email:true},
  address1:{required:true},
  city:{required:true},
  zip:{required:true},
  password:{required:true},
  password_two:{required:true,equalTo:'.password:first'},
  eighteen:{required:true},
  program_regulations:{required:true},
  loyalty_oath:{required:true}
 },
 messages:{
  first_name:'""", str(T("Enter your firstname")), """',
  last_name:required,
  phone:required,
  email:{
   required:'""", str(T("Please enter a valid email address")), """',
   minlength:'""", str(T("Please enter a valid email address")), """'
  },
  address1:required,
  city:required,
  zip:required,
  password:{required:'""", str(T("Provide a password")), """'},
  password_two:{
   required:'""", str(T("Repeat your password")), """',
   equalTo:'""", str(T("Enter the same password as above")), """'
  },
  eighteen:'""", str(T("If you are under the age 18, you may not register to apply to be a volunteer.  Thank you for your interest in our volunteer opportunities.")), """',
  program_regulations:'""", str(T("You must comply with all program regulations")), """',
  loyalty_oath:'""", str(T("You must subscribe to the loyalty oath")), """'
 },
 errorPlacement:function(error,element){
  error.appendTo(element.parent().next())
 },
 submitHandler:function(form){
  form.submit()
 }
})\n"""))
    s3.jquery_ready.append(script)

    if session.s3.debug:
        s3.scripts.append( "%s/jquery.validate.js" % s3_script_dir )
        s3.scripts.append( "%s/jquery.pstrength.1.3.js" % s3_script_dir )
    else:
        s3.scripts.append( "%s/jquery.validate.min.js" % s3_script_dir )
        s3.scripts.append( "%s/jquery.pstrength.1.3.min.js" % s3_script_dir )

    s3.jquery_ready.append("$('.password:first').pstrength()\n")
    s3.js_global.append("".join((
        "S3.i18n.password_chars='%s'\n" % T("The minimum number of characters is "),
        "S3.i18n.very_weak='%s'\n" % T("Very Weak"),
        "S3.i18n.weak='%s'\n" % T("Weak"),
        "S3.i18n.medium='%s'\n" % T("Medium"),
        "S3.i18n.strong='%s'\n" % T("Strong"),
        "S3.i18n.very_strong='%s'\n" % T("Very Strong"),
        "S3.i18n.too_short='%s'\n" % T("Too Short"),
        "S3.i18n.unsafe_password='%s'\n" % T("Unsafe Password Word!"),
    )))

    # Add sidebar for login box & other volunteering opportunities
    vol_sidebar()

    response.title = T("Register")
    s3.has_required = True

    return dict(form=form)

# -----------------------------------------------------------------------------
def register_validation(form):
    """ Validate the custom fields in registration form """
    # Terms of Service
    if "eighteen" not in request.post_vars or request.post_vars.eighteen != "on":
        form.errors.eighteen = T("If you are under the age 18, you may not register to apply to be a volunteer.  Thank you for your interest in our volunteer opportunities.")
    if "program_regulations" not in request.post_vars or request.post_vars.program_regulations != "on":
        form.errors.program_regulations = T("You must comply with all program regulations")
    if "loyalty_oath" not in request.post_vars or request.post_vars.loyalty_oath != "on":
        form.errors.loyalty_oath = T("You must comply with all program regulations")

    #if "citizen" not in request.post_vars or request.post_vars.citizen != "on":
    #    form.errors.citizen = T("If you are not a U.S. citizen, you may not register to apply to be a volunteer.  Thank you for your interest in our volunteer opportunities.")
    # Phone
    if "phone" in request.post_vars and request.post_vars.phone:
        regex = re.compile(single_phone_number_pattern)
        if not regex.match(request.post_vars.phone):
            form.errors.phone = T("Invalid phone number")
    else:
        form.errors.phone = T("Phone number is required")
    # Address
    if not request.post_vars.address1:
        form.errors.address1 = T("Address is required")
    if not request.post_vars.city:
        form.errors.city = T("City is required")
    if not request.post_vars.zip:
        form.errors.zip = T("Zip is required")

    return

# -----------------------------------------------------------------------------
def register_onaccept(form):
    # Usual Registration Tasks
    # (PR record, Authenticated Role, Contacts)
    person = auth.s3_register(form)

    # LA-specific
    table = db.pr_person
    query = (table.id == person)

    db(query).update(volunteer=True,
                     middle_name=request.post_vars.middle_name)

    pe = db(query).select(table.pe_id,
                          limitby=(0, 1)).first().pe_id

    # Phone
    table = db.pr_contact
    phone = request.post_vars.phone
    phone_type = request.post_vars.phone_type
    # Don't auto-subscribe to SMS (priority 10)
    table.insert(pe_id = pe,
                 contact_method = phone_type,
                 value = phone,
                 priority=10)

    # Address
    table = db.gis_location
    address1 = request.post_vars.address1
    address2 = request.post_vars.address2
    if address2:
        address = "%s\n%s" % (address1,
                              address2)
    else:
        address = address1
    city = request.post_vars.city
    location = request.post_vars.location_id
    state = db(table.id == location).select(table.id,
                                            table.name,
                                            cache=gis.cache,
                                            limitby=(0, 1)).first()
    if state:
        statename = state.name
    else:
        # Duff data - not USA
        statename = "unknown"
    zip = request.post_vars.zip
    county = ""
    if city:
        query = (table.name == city) & \
                (table.level == "L3") & \
                (table.path.like("%%/%s/%%" % state))
        _city = db(query).select(table.id,
                                 table.parent,
                                 limitby=(0, 1)).first()
        if _city:
            if _city.parent != state:
                query = (table.id == _city.parent)
                county = db(query).select(table.name,
                                          limitby=(0, 1)).first().name
        elif state:
            _city = table.insert(name=city, level="L3", parent=state.id)
            gis.update_location_tree(_city, state.id)
        else:
            usa = db(table.code == "US").select(table.id,
                                                limitby=(0, 1)).first().id
            _city = table.insert(name=city, level="L3", parent=usa)
            gis.update_location_tree(_city, usa)
    else:
        _city = None
    location = table.insert(addr_street=address, addr_postcode=zip, parent=_city)
    gis.update_location_tree(location, _city)
    load("pr_address")
    table = db.pr_address
    table.insert(pe_id = pe,
                 location_id = location,
                 address=address,
                 postcode=zip,
                 L3=city,
                 L2=county,
                 L1=statename,
                 L0="United States")

# -----------------------------------------------------------------------------
_settings = auth.settings
_settings.register_onvalidation = register_validation
_settings.register_onaccept = register_onaccept
_settings.register_next = URL(c="vol", f="skill", args=["create"])

# Organisation widget for use in Registration Screen
# NB User Profile is only editable by Admin - using User Management
org_widget = IS_ONE_OF(db, "org_organisation.id",
                       organisation_represent,
                       orderby="org_organisation.name",
                       sort=True)
if deployment_settings.get_auth_registration_organisation_mandatory():
    _table_user.organisation_id.requires = org_widget
else:
    _table_user.organisation_id.requires = IS_NULL_OR(org_widget)

# =============================================================================
def profile():
    """ Custom Profile Screen """

    if not auth.is_logged_in():
        redirect(URL(f="user", args="login"))
    elif s3_has_role(ORG_VOL):
        #return organisation_profile()
        redirect(URL(f="organisation", args=[auth.user.organisation_id]))

    # Only show admin-set fields if there is data
    table = db.auth_user
    if not auth.user.organisation_id:
        # Not relevant to Volunteers
        table.organisation_id.readable = False
    if not auth.user.site_id:
        # Only relevant to Field Staff
        table.site_id.readable = False

    # Validate the custom fields
    _settings.profile_onvalidation = profile_validation

    # Process the custom fields
    _settings.profile_onaccept = profile_onaccept

    auth.messages.profile_save_button = "Save"

    request.args = ["profile"]
    form = auth()

    # Custom class for Submit Button
    form[0][-1][1][0]["_class"] = "submit-button"

    # Lookup the Person
    id = auth.s3_logged_in_person()
    table = db.pr_person
    person = db(table.id == id).select(table.pe_id,
                                       table.middle_name,
                                       table.volunteer,
                                       limitby=(0, 1)).first()

    row = TR(TD(LABEL("%s:" % table.middle_name.label, _for="middle_name")),
             TD(INPUT(_name="middle_name",
                      _id="middle_name",
                      _class="string",
                      _value=person.middle_name)))
    form[0][0].append(row)

    # Lookup the Contacts
    table = db.pr_contact
    query = (table.pe_id == person.pe_id) & \
            (table.deleted == False)
    contacts = db(query).select(table.contact_method,
                                table.value,
                                table.priority)
    cell = ""
    home = ""
    work = ""
    sms_enabled = False
    email_enabled = True
    for contact in contacts:
        if contact.contact_method == "SMS":
            cell = contact.value
            if contact.priority == 10:
                sms_enabled = False
            else:
                sms_enabled = True
        elif contact.contact_method == "EMAIL":
            if contact.priority == 10:
                email_enabled = False
            else:
                email_enabled = True
        elif contact.contact_method == "HOME_PHONE":
            home = contact.value
        elif contact.contact_method == "WORK_PHONE":
            work = contact.value

    # Cell phone
    if form.errors.mobile:
        cell_error = DIV(form.errors.mobile,
                         _id="mobile__error",
                         _class="error",
                         _style="display: block;")
    else:
        cell_error = ""
    row = TR(TD(LABEL("%s:" % msg.CONTACT_OPTS["SMS"], _for="mobile")),
             TD(INPUT(_name="mobile",
                      _id="mobile",
                      _class="string",
                      _value=cell),
                cell_error))
    form[0][2].append(row)
    # @ToDo: JS validation

    if person.volunteer:
        # Home phone
        if form.errors.home_phone:
            home_phone_error = DIV(form.errors.home_phone,
                                   _id="home_phone__error",
                                   _class="error",
                                   _style="display: block;")
        else:
            home_phone_error = ""
        row = TR(TD(LABEL("%s:" % msg.CONTACT_OPTS["HOME_PHONE"], _for="home_phone")),
                 TD(INPUT(_name="home_phone",
                          _id="home_phone",
                          _class="string",
                          _value=home),
                    home_phone_error))
        form[0][2].append(row)
        # @ToDo: JS validation

        # Work phone
        if form.errors.work_phone:
            work_phone_error = DIV(form.errors.work_phone,
                                   _id="work_phone__error",
                                   _class="error",
                                   _style="display: block;")
        else:
            work_phone_error = ""
        row = TR(TD(LABEL("%s:" % msg.CONTACT_OPTS["WORK_PHONE"], _for="work_phone")),
                 TD(INPUT(_name="work_phone",
                          _id="work_phone",
                          _class="string",
                          _value=work),
                    work_phone_error))
        form[0][2].append(row)
        # @ToDo: JS validation

        # Lookup the Address
        load("pr_address")
        table = db.pr_address
        query = (table.pe_id == person.pe_id) & \
                (table.deleted == False)
        address = db(query).select(table.location_id,
                                   limitby=(0, 1)).first()
        address1 = ""
        address2 = ""
        city = ""
        state = ""
        zip = ""
        if address:
            table = db.gis_location
            query = (table.id == address.location_id)
            location = db(query).select(table.id,
                                        table.path,
                                        table.parent,
                                        table.addr_street,
                                        table.addr_postcode,
                                        limitby=(0, 1)).first()
            if location:
                try:
                    address1, address2 = location.addr_street.split("\n", 1)
                except ValueError:
                    address1 = location.addr_street
                zip = location.addr_postcode
                # Load model
                load("gis_config")
                results = gis.get_parent_per_level(None, location.id, location)
                try:
                    city = results["L3"].name
                #except KeyError, AttributeError:
                except:
                    pass
                try:
                    state = results["L1"].name
                #except KeyError, AttributeError:
                except:
                    pass

        if form.errors.address1:
            address1_error = DIV(form.errors.address1,
                                 _id="address1__error",
                                 _class="error",
                                 _style="display: block;")
        else:
            address1_error = ""
        row = TR(TD(LABEL("%s: " % T("Address 1"),
                          SPAN("*", _class="req"),
                          _for="address1")),
                 TD(INPUT(_name="address1",
                          _id="address1",
                          _class="string",
                          _value=address1),
                    address1_error))
        form[0][2].append(row)
        row = TR(TD(LABEL("%s:" % T("Address 2"), _for="address2")),
                 TD(INPUT(_name="address2",
                          _id="address2",
                          _class="string",
                          _value=address2)))
        form[0][2].append(row)
        row = TR(TD(LABEL("%s: " % T("City"),
                          SPAN("*", _class="req"),
                          _for="city")),
                 TD(INPUT(_name="city",
                          _id="city",
                          _class="string",
                          _value=city)))
        form[0][2].append(row)
        states = S3LocationDropdownWidget(level="L1",
                                          default=state or "California",
                                          empty=False)
        widget = states(db.pr_address.location_id, None)
        row = TR(TD(LABEL("%s:" % T("State"),
                          SPAN("*", _class="req"),
                          _for="location_id")),
                 TD(widget))
        form[0][2].append(row)
        if form.errors.zip:
            zip_error = DIV(form.errors.zip,
                            _id="zip__error",
                            _class="error",
                            _style="display: block;")
        else:
            zip_error = ""
        row = TR(TD(LABEL("%s:" % T("Zip"),
                          SPAN("*", _class="req"),
                          _for="zip")),
                 TD(INPUT(_name="zip",
                          _id="zip",
                          _class="string",
                          _value=zip),
                    zip_error))
        form[0][2].append(row)

        # Notifications
        div = DIV(TR(TD(LABEL("%s:" % T("Notifications"))),
                     TD()
                    ),
                  TR(TD(T("Receive Notifications via Email?")),
                     TD(INPUT(_type="checkbox",
                        _value="on",
                        value="on" if email_enabled else "",
                        _name="sub_email",
                        _id="sub_email",
                        _alt=T("Receive Notifications via Email?"),
                        _class="boolean"))
                    ),
                  TR(TD(T("Receive Notifications via SMS?")),
                     TD(INPUT(_type="checkbox",
                        _value="on",
                        value="on" if sms_enabled else "",
                        _name="sub_sms",
                        _id="sub_sms",
                        _alt=T("Receive Notifications via SMS?"),
                        _class="boolean")),
                     TD(DIV(_class="tooltip",
                            _title="%s|%s" % (T("Receive Notifications via SMS"),
                                              T("Note that this may incur costs from your carrier."))))
                    )
                )
        form[0][-2].append(div)

        # Affiliated Orgs
        load("vol_organisation")
        table = db.vol_organisation
        orgs = db(table.pe_id == person.pe_id).select(table.organisations_id,
                                                      limitby=(0, 1)).first()
        if orgs:
            orgs = orgs.organisations_id
            table = db.org_organisation
            if orgs:
                _orgs = db(table.id.belongs(orgs)).select(table.name)
            else:
                _orgs = []
            orgs = []
            for org in _orgs:
                orgs.append(org.name)
        else:
            orgs = []

        div = DIV(TR(TD(),
                     TD(B(T("Affiliation with other volunteer organizations")))),
                  TR(TD(T("Are you affiliated with other volunteer organizations?"),
                        " (", DIV(T("Check all that apply"),
                                 _style="display: inline;",
                                 _class="red"),
                        ")",
                        _colspan=2)),
                  TR(TD("American Red Cross"),
                     TD(INPUT(_type="checkbox",
                              _value="on",
                              value="on" if "American Red Cross of Greater Los Angeles" in orgs else "",
                              _name="arc",
                              _id="arc",
                              _alt=T("American Red Cross"),
                              _class="boolean"))),
                  TR(TD("CERT"),
                     TD(INPUT(_type="checkbox",
                              _value="on",
                              value="on" if "CERT Los Angeles" in orgs else "",
                              _name="cert",
                              _id="cert",
                              _alt=T("CERT"),
                              _class="boolean"))),
                  TR(TD("Disaster Healthcare Volunteers"),
                     TD(INPUT(_type="checkbox",
                              _value="on",
                              value="on" if "Disaster Healthcare Volunteers" in orgs else "",
                              _name="dhv",
                              _id="dhv",
                              _alt=T("Disaster Healthcare Volunteers"),
                              _class="boolean"))),
                  TR(TD("L.A. Works"),
                     TD(INPUT(_type="checkbox",
                              _value="on",
                              value="on" if "LA Works" in orgs else "",
                              _name="laworks",
                              _id="laworks",
                              _alt=T("L.A. Works"),
                              _class="boolean"))),
                  TR(TD("Volunteer Center of Los Angeles"),
                     TD(INPUT(_type="checkbox",
                              _value="on",
                              value="on" if "Volunteer Center of Los Angeles" in orgs else "",
                              _name="vcla",
                              _id="vcla",
                              _alt=T("Volunteer Center of Los Angeles"),
                              _class="boolean"))),
                )
        form[0][-2].append(div)

        # Skills
        # - separate screen

    response.title = T("Profile")
    s3.has_required = True

    return dict(form=form)

# -----------------------------------------------------------------------------
def profile_validation(form):
    """ Validate the custom fields in profile form """

    if s3_has_role(STAFF):
        volunteer = False
    else:
        volunteer = True

    # Mobile Phone
    if "mobile" in request.post_vars and request.post_vars.mobile:
        regex = re.compile(single_phone_number_pattern)
        if not regex.match(request.post_vars.mobile):
            form.errors.mobile = T("Invalid phone number")
    elif "sub_sms" in request.post_vars and request.post_vars.sub_sms == "on":
        form.errors.mobile = T("Cell phone number is required for SMS notifications")
    # Home Phone
    if "home_phone" in request.post_vars and request.post_vars.home_phone:
        regex = re.compile(single_phone_number_pattern)
        if not regex.match(request.post_vars.home_phone):
            form.errors.home_phone = T("Invalid phone number")
    # Work Phone
    if "work_phone" in request.post_vars and request.post_vars.work_phone:
        regex = re.compile(single_phone_number_pattern)
        if not regex.match(request.post_vars.work_phone):
            form.errors.work_phone = T("Invalid phone number")
    # Address
    if volunteer and not request.post_vars.address1:
        form.errors.address1 = T("Address is required")
    if volunteer and not request.post_vars.zip:
        form.errors.zip = T("Zip is required")

    return

# -----------------------------------------------------------------------------
def profile_onaccept(form):
    """ Process the custom fields """

    if s3_has_role(STAFF):
        volunteer = False
    else:
        volunteer = True

    post_vars = request.post_vars
    table = db.pr_person
    query = (table.id == auth.s3_logged_in_person())
    db(query).update(middle_name=post_vars.middle_name)
    pe_id = db(query).select(table.pe_id,
                             limitby=(0, 1)).first().pe_id

    if volunteer:
        # Contacts / Notifications
        if post_vars.get("sub_email") == "on":
            email_enabled = True
        else:
            email_enabled = False
        if post_vars.get("sub_sms") == "on":
            sms_enabled = True
        else:
            sms_enabled = False
        home_phone = post_vars.home_phone
        work_phone = post_vars.work_phone
    email = post_vars.email
    cell = post_vars.mobile
    table = db.pr_contact
    if email:
        query = (table.pe_id == pe_id) & \
                (table.contact_method == "EMAIL") & \
                (table.deleted == False)
        _email = db(query).select(table.value,
                                  limitby=(0, 1)).first().value
        if not _email == email:
            # Email has changed
            # Update pr_contact
            query = (table.value == _email)
            if volunteer:
                priority = 1 if email_enabled else 10
                db(query).update(value=email, priority=priority)
            else:
                db(query).update(value=email)
        elif volunteer:
            # Just update the notifications
            priority = 1 if email_enabled else 10
            db(table.value == email).update(priority=priority)

    _cell = ""
    _home_phone = ""
    _work_phone = ""
    query = (table.pe_id == pe_id) & \
            (table.deleted == False)
    contacts = db(query).select(table.contact_method,
                                table.value)
    for contact in contacts:
        if contact.contact_method == "SMS":
            _cell = contact.value
        elif contact.contact_method == "HOME_PHONE":
            _home_phone = contact.value
        elif contact.contact_method == "WORK_PHONE":
            _work_phone = contact.value
    table = db.pr_contact
    base_query = (table.pe_id == pe_id)
    if volunteer:
        priority = 1 if sms_enabled else 10
        if _cell:
            # Update existing record
            query = base_query & (table.value == _cell)
            db(query).update(value=cell, priority=priority)
        elif cell:
            # Insert new record
            table.insert(pe_id=pe_id, contact_method="SMS", value=cell,
                         priority=priority)
        if _home_phone:
            # Update existing record
            query = base_query & (table.value == _home_phone)
            db(query).update(value=home_phone)
        elif home_phone:
            # Insert new record
            table.insert(pe_id=pe_id, contact_method="HOME_PHONE",
                         value=home_phone)

        if _work_phone:
            # Update existing record
            query = base_query & (table.value == _work_phone)
            db(query).update(value=work_phone)
        elif work_phone:
            # Insert new record
            table.insert(pe_id=pe_id, contact_method="WORK_PHONE",
                         value=work_phone)

        # Address
        address1 = post_vars.address1
        address2 = post_vars.address2
        if address2:
            address = "%s\n%s" % (address1, address2)
        else:
            address = address1
        zip = post_vars.zip
        city = post_vars.city
        state = post_vars.location_id
        table = db.gis_location
        statename = db(table.id == state).select(table.name,
                                                 cache=gis.cache,
                                                 limitby=(0, 1)).first().name
        county = ""
        if city:
            query = (table.name == city) & \
                    (table.level == "L3") & \
                    (table.path.like("%%/%s/%%" % state))
            _city = db(query).select(table.id,
                                     table.parent,
                                     limitby=(0, 1)).first()
            if _city:
                if _city.parent != state:
                    query = (table.id == _city.parent)
                    county = db(query).select(table.name,
                                              limitby=(0, 1)).first().name
            else:
                _city = table.insert(name=city, level="L3", parent=state)
                gis.update_location_tree(_city, state)
        else:
            _city = None
        load("pr_address")
        table = db.pr_address
        query = (table.pe_id == pe_id) & \
                (table.deleted == False)
        test = db(query).select(table.location_id,
                                limitby=(0, 1)).first()
        if test:
            db(query).update(address=address,
                             postcode=zip,
                             L3=city,
                             L2=county,
                             L1=statename,
                             L0="United States")
            table = db.gis_location
            location = test.location_id
            query = (table.id == location)
            db(query).update(addr_street=address,
                             addr_postcode=zip,
                             parent=_city)
            gis.update_location_tree(location, _city)

        # Affiliated Organisations
        # Also in models/vol.py
        vol_orgs = ["American Red Cross of Greater Los Angeles",
                    "CERT Los Angeles",
                    "Disaster Healthcare Volunteers",
                    "LA Works",
                    "Volunteer Center of Los Angeles"]
        table = db.org_organisation
        query = (table.name.belongs(vol_orgs))
        orgs = db(query).select(table.id,
                                table.name,
                                cache=(cache.ram, 60))
        for org in orgs:
            if org.name == "American Red Cross of Greater Los Angeles":
                ARC = org.id
            elif org.name == "CERT Los Angeles":
                CERT = org.id
            elif org.name == "Disaster Healthcare Volunteers":
                DHV = org.id
            elif org.name == "LA Works":
                LAW = org.id
            elif org.name == "Volunteer Center of Los Angeles":
                VCLA = org.id
        orgs = []
        if post_vars.get("arc") == "on":
            orgs.append(ARC)
        if post_vars.get("cert") == "on":
            orgs.append(CERT)
        if post_vars.get("dhv") == "on":
            orgs.append(DHV)
        if post_vars.get("laworks") == "on":
            orgs.append(LAW)
        if post_vars.get("vcla") == "on":
            orgs.append(VCLA)
        load("vol_organisation")
        table = db.vol_organisation
        query = (table.pe_id == pe_id)
        test = db(query).select(table.id,
                                limitby=(0, 1)).first()
        if test:
            db(query).update(organisations_id = orgs)
        else:
            table.insert(pe_id = pe_id,
                         organisations_id = orgs,
                         owned_by_user = auth.user.id)

    else:
        # Not a volunteer: EOC staff
        if _cell:
            # Update existing record
            query = base_query & (table.value == _cell)
            db(query).update(value=cell)
        elif cell:
            # Insert new record
            table.insert(pe_id=pe_id, contact_method="SMS", value=cell)

# -----------------------------------------------------------------------------
# Skills
# -----------------------------------------------------------------------------
def skill():
    """
        Collect a Volunteer's Skills
    """

    tablename = "vol_skill"
    load(tablename)
    table = db[tablename]

    person = auth.s3_logged_in_person()
    table.person_id.default = person
    table.person_id.writable = table.person_id.readable = False

    ctable = db.vol_contact
    record = db(ctable.person_id == person).select(table.id,
                                                   limitby=(0, 1),
                                                   cache = gis.cache).first()
    if record:
        create_next = None
    else:
        # Workflow: Prompt for creating Emergency Contacts after adding Skills
        create_next = URL(f="contact", args="my")

    configure(tablename,
              create_next = create_next,
              update_next = URL(f="skill", args="my"),
              deletable = False,
              listadd = False,
              )

    # Parse the request
    if "my" in request.args:
        record = db(table.person_id == person).select(table.id,
                                                      limitby=(0, 1),
                                                      cache = gis.cache).first()
        if record:
            r = s3mgr.parse_request(args=[str(record.id)])
        else:
            r = s3mgr.parse_request(args=["create"])
    else:
        r = s3mgr.parse_request()

    # Execute the request
    output = r()

    response.title = T("My Skills")
    return output

# -----------------------------------------------------------------------------
# Contacts
# -----------------------------------------------------------------------------
def contact():
    """
        Emergency Contacts for the volunteer
    """

    tablename = "vol_contact"
    load(tablename)
    table = db[tablename]

    person = auth.s3_logged_in_person()
    table.person_id.default = person
    table.person_id.writable = table.person_id.readable = False

    configure(tablename,
              # Workflow: During registration, proceed to List of Requests after contacts created
              create_next = URL(f="req_skill"),
              update_next = URL(f="contact", args=["my"]),
              deletable = False,
              listadd = False)

    # Parse the request
    if "my" in request.args:
        record = db(table.person_id == person).select(table.ALL,
                                                      limitby=(0, 1),
                                                      cache = gis.cache).first()
        if record:
            r = s3mgr.parse_request(args=str(record.id))
        else:
            r = s3mgr.parse_request(args="create")
    else:
        r = s3mgr.parse_request()

    # Execute the request
    output = r()

    response.title = T("Emergency Contact")
    return output

# -----------------------------------------------------------------------------
# Assignments
# - My Assignments menu
# -----------------------------------------------------------------------------
def assignment():
    """ Allow a Volunteer/Org to View the details of their own assignments """

    tablename = "vol_assignment"
    load(tablename)
    table = db[tablename]

    if auth.user.organisation_id:
        s3.filter = (table.organisation_id == auth.user.organisation_id)
        # Control List View
        table.person_id.readable = False
        table.number.readable = True
        table.number.label = T("Number of Volunteers Committed")
    else:
        my_person_id = s3_logged_in_person()
        # Control List View
        table.person_id.readable = False

        if not my_person_id:
            session.error = T("No person record found for current user.")
            redirect(URL(f="index"))

        s3.filter = (table.person_id == my_person_id)

    # Filter for current/past assignments
    sel = (table.checkout == None) | \
          (table.checkout >= request.utcnow) | \
          (table.task_evaluation == None)
    crud_strings[tablename].update(
        subtitle_list = T("Current Assignments"))
    if "show" in request.get_vars:
        show = request.get_vars["show"]
        if show == "past":
            sel = (table.checkout < request.utcnow) & \
                  (table.task_evaluation != None)
            crud_strings[tablename].update(
                subtitle_list = T("Past Assignments"),
                msg_no_match = T("No past assignments"))
    s3.filter &= sel

    # Post-process
    def postp(r, output):
        if r.interactive:
            s3.actions = [dict(
                        url = URL(c = "vol",
                                  f = "req",
                                  args = ["assignment", "[id]"]),
                        _class = "action-btn",
                        label = str(T("Details"))
                    )]
            if "show" in request.get_vars and request.get_vars["show"] == "past":
                s3.actions += [dict(
                            url = URL(c=request.controller,
                                      f="req",
                                      args=["assignment",
                                            "[id]",
                                            "print"]),
                            _class = "action-btn",
                            label = str(T("Certificate"))
                        )]

        return output
    s3.postp = postp

    output = s3_rest_controller("vol", "assignment")
    return output

# -----------------------------------------------------------------------------
# Requests
# -----------------------------------------------------------------------------
def vol_req_rheader(r):
    """
        Resource Header for Requests
        - Volunteer view
        - inc Volunteer Roster
    """

    if r.representation == "html":
        if r.name == "req":
            record = r.record
            if record:
                if s3_has_role(STAFF):
                    # Show Tabs on Roster
                    tabs = [(T("Details"), None)]
                    if record.type == 3 and has_module("hrm"):
                        tabs.append((T("Requested Volunteers"), "req_skill"))
                    if has_module("doc"):
                        tabs.append((T("Documents"), "document"))
                    #if deployment_settings.get_req_use_commit():
                    #    tabs.append((T("Commitments"), "commit"))
                    tabs.append((T("Roster"), "assignment"))
                    try:
                        # Remove the default_type from URLs as set within respective controller
                        r.vars.pop("default_type")
                    except KeyError:
                        pass
                    rheader_tabs = s3_rheader_tabs(r, tabs)
                elif not r.component:
                    # Volunteers should only ever access Requests via the Components
                    return

                table = db.req_req_skill
                query = (table.req_id == record.id)
                srecord = db(query).select(table.skill_id,
                                           table.quantity,
                                           table.quantity_commit,
                                           limitby=(0, 1)).first()
                if srecord:
                    skills = s3.hrm_multi_skill_represent(srecord.skill_id)
                    requested = srecord.quantity
                    required = srecord.quantity - (srecord.quantity_commit or 0)
                else:
                    skills = requested = required = ""

                address = shn_site_represent(record.site_id, address=True)

                table = db.hrm_human_resource
                query = (table.id == record.request_for_id)
                person = db(query).select(table.person_id,
                                          limitby=(0, 1)).first()
                phone = email = report_to = ""
                if person:
                    report_to = person_represent(person.person_id)

                    ptable = db.pr_person
                    ctable = db.pr_contact
                    query = (ptable.id == person.person_id) & \
                            (ctable.pe_id == ptable.pe_id)
                    contacts = db(query).select(ctable.contact_method,
                                                ctable.value)
                    for contact in contacts:
                        if contact.contact_method == "SMS":
                            phone = contact.value
                        elif contact.contact_method == "EMAIL":
                            email = contact.value

                if s3_has_role(STAFF):
                    subtitle = T("Request Details")
                    buttons = DIV(A(SPAN(T("PRINT ROSTER"),
                                         _class="wide-grey-button"),
                                    _href = URL(c=request.controller,
                                                f="req",
                                                args=[record.id,
                                                      "assignment",
                                                      "print"])),
                                )
                    if not deployment_settings.get_req_webeoc_is_master():
                        buttons.append(
                                A(SPAN(T("CANCEL REQUEST"),
                                       _class="wide-grey-button"),
                                  _href = URL(c=request.controller,
                                              f="req",
                                              args=[record.id,
                                                    "cancel"]))
                                    )
                    textbox = ""
                else:
                    subtitle = T("Volunteer Assignment Details")
                    buttons = ""
                    if r.component.name == "application":
                        textbox = P(T("When you volunteer with Give2LA, you are an extension of the good will of the City of Los Angeles. For many survivors, volunteers are their first point of contact. Your respect, courtesy, and sensitivity during these difficult times are vital. In addition, following directions, procedures, and processes given to you by your supervisor are essential; failure to do so may exclude you from future volunteer assignments."))
                    else:
                        give2la_forms = A(T("Give2LA Registration Forms"),
                                          _href = URL(c="static",
                                                      f="Give2LA_Registration_Forms.pdf"),
                                          _target="_blank"
                                          )
                        textbox = DIV(P(T("Thank you for Volunteering. Please print out your Volunteer Assignment Form as it contains important information about who, when, and where to report to for your Volunteer Assignment.")),
                                      P(XML(T("As a volunteer working to assist disaster survivors and in disaster recovery efforts, you will be required to fill out and sign the %(give2la_forms)s.") %
                                            dict(give2la_forms = give2la_forms) )),
                                      P(T("Please let us know in advance if you cannot report for your Volunteer Assignment by calling the Point of Contact listed below.")),
                                      )

                if record.date_required:
                    time_req = s3_time_represent(record.date_required,
                                                 utc=True)
                else:
                    time_req = ""
                if record.date_required_until:
                    time_until = s3_time_represent(record.date_required_until,
                                                   utc=True)
                else:
                    time_until = ""

                class DL(DIV):
                    tag = "dl"

                class DT(DIV):
                    tag = "dt"

                class DD(DIV):
                    tag = "dd"

                rheader = DIV(
                                textbox,
                                H2(subtitle, _class="paper-strip"),
                                buttons,
                                DIV(
                                    TABLE(
                                       TR(
                                        TH(T("Request Number")),
                                        TH(T("Task")),
                                        TH(T("Date+Time")),
                                        TH(T("Required Skills")),
                                        TH(T("Request Priority")),
                                        TH(T("Location")),
                                        TH(T("Number of Volunteers"),BR(),DIV("(", T("Still Required"), "/", T("Total Requested"), ")")), # (assigned/required)
                                        _class="odd"
                                        ),
                                       TR(
                                        TD(record.request_number),
                                        TD(record.purpose),
                                        TD(B(s3_date_represent_utc(record.date_required)),
                                           BR(),
                                           "%s - %s" % (time_req,
                                                        time_until),
                                           ),
                                        TD(skills),
                                        TD(s3.req_priority_represent(record.priority) ),
                                        TD(record.location or ""),
                                        TD(B(required),
                                           " / %s" % requested,
                                           _class="red"),
                                        _class="even"
                                        ),
                                    _class="datatable display"
                                    ),
                                _id="table-container"
                                ),
                                DL(
                                   DT(T("Point of Contact")),
                                   DD(report_to,
                                      BR(),
                                      "%s: %s" % (T("Phone"),
                                                  phone),
                                      BR(),
                                      "%s: %s" % (T("Email"),
                                                  email),
                                     ),
                                   DT(T("Volunteering Location")),
                                   DD(address),
                                   DT(T("Comments")),
                                   DD(record.comments),
                                   _class="assignment-details"
                                ),
                            )
                if r.component and r.component.name == "assignment":
                    if s3_has_role(STAFF):
                        # Volunteer Roster
                        s3.rfooter = DIV(
                            A(SPAN(T("CHECK-IN ALL"),
                                   _class="wide-grey-button"),
                              _href = URL(c=request.controller,
                                          f="req",
                                          args=[record.id,
                                                "assignment",
                                                "checkin"])),
                            A(SPAN(T("CHECK-OUT ALL"),
                                   _class="wide-grey-button"),
                              _href = URL(c=request.controller,
                                          f="req",
                                          args=[record.id,
                                                "assignment",
                                                "checkout"]))
                            )
                    else:
                        # Volunteer Assignment
                        assignment = r.component_id
                        table = db.vol_assignment
                        query = table.id == r.component_id
                        record = db(query).select(limitby=(0, 1)).first()
                        if not record:
                            # Probably a Volunteer trying to use a URL for STAFF
                            session.error = auth.permission.INSUFFICIENT_PRIVILEGES
                            redirect(URL(c="vol", f="req_skill"))
                        req_id = record.req_id
                        if record.checkout != None and record.task_evaluation != None:
                            printBtn = T("PRINT CERTIFICATE")
                        else:
                            printBtn = T("PRINT VOLUNTEER ASSIGNMENT FORM")
                        if record.checkin:
                            cancelBtn = ""
                        else:
                            # Only show the Cancel button if Volunteer not yet checked-in
                            cancelBtn = A(SPAN(T("CANCEL ASSIGNMENT"),
                                               _class="wide-grey-button"),
                                          _href = URL(c=request.controller,
                                                      f="req",
                                                      args=[record.req_id,
                                                            "assignment",
                                                            assignment,
                                                            "delete"]))

                        rheader.append(
                          DIV(
                            A(SPAN(printBtn),
                              _class="big-red-arrow",
                              _href = URL(c=request.controller,
                                          f="req",
                                          args=["assignment",
                                                assignment,
                                                "print"])),
                            # Also in controllers/don.py - DRY
                            A(IMG(_src="/%s/static/img/get_adobe_reader.png" % request.application,
                                  _title="%s - %s" % (T("Get Adobe Reader"),
                                                      T("This link will open a new browser window.")),
                                  _alt=T("Get Adobe Reader"),
                                  _width=158,
                                  _height=39,
                                  _style="float:right;"),
                              _href="http://www.adobe.com/products/acrobat/readstep2.html",
                              _target="_blank"),
                            BR(),
                            cancelBtn
                            )
                        )
                if s3_has_role(STAFF):
                    rheader.append(rheader_tabs)

                return rheader
    return None

# -----------------------------------------------------------------------------
def req():
    """ REST Controller """

    load("req_req")
    default_type = 3
    request.vars["default_type"] = 3

    if "skill_id" in request.get_vars:
        # Look up the Request from the Skill component
        # (since that is what is available to us within the dataTables row)
        table = db.req_req_skill
        query = (table.id == request.vars.skill_id)
        req = db(query).select(table.req_id,
                               limitby=(0, 1)).first()
        if not req:
            session.error = T("Invalid Request!")
            redirect(URL(f="req_skill", args=[], vars={}))
        # @ToDo: A nicer way to do this (without a 2nd request)
        # simply amending request.args doesn't work
        # Need to rewrite to not use prep/postp but rather process r() directly
        redirect(URL(args = [req.req_id, "application", "create"],
                     vars={}))

    if "document" in request.args:
        load("doc_document")

    req_table = db.req_req
    configure(req_table,
              orderby=~req_table.date)

    type_field = req_table.type
    type_field.default = int(default_type)
    type_field.writable = False

    if s3_has_role(STAFF):
        db.req_req.comments.label = T("Comments (including details for Parking, Check-in Location, Working conditions, Attire)")
        if "assignment" in request.args or \
           "checkin" in request.args or \
           "checkout" in request.args:
            load("vol_assignment")

    elif s3_has_role(ORG_VOL):
        load("vol_application")
        # Volunteer Orgs can see Public Requests & those published for them
        org = auth.user.organisation_id
        s3.filter = (req_table.public == True) | \
                             (req_table.organisations_id.belongs((org,)))
        configure(req_table,
                  editable=False), # We need the Controller/Table ACL to be editable to be able to add components
        if "application" in request.args:
            s3.crud.submit_button = T("COMMIT")
            table = db.vol_application
            table.organisation_id.default = org
            table.organisation_id.readable = table.organisation_id.writable = False
            table.number.readable = table.number.writable = True
            table.person_id.readable = table.person_id.writable = False
            field = table.team_leader_id
            field.readable = field.writable = True
            field.requires = IS_NOT_EMPTY()
            table.emergency_contact_name.readable = table.emergency_contact_name.writable = False
            table.emergency_contact_name.requires = []
            table.emergency_contact_relationship.readable = table.emergency_contact_relationship.writable = False
            table.emergency_contact_relationship.requires = []
            table.emergency_contact_phone.readable = table.emergency_contact_phone.writable = False
            table.emergency_contact_phone.requires = []
            s3.crud_strings["vol_application"].subtitle_create = ""

        elif "assignment" in request.args:
            table = db.vol_assignment
            table.organisation_id.default = org
            table.organisation_id.readable = table.organisation_id.writable = False
            table.person_id.readable = table.person_id.writable = False
            # Make the component multiple=False
            add_component("vol_assignment",
                          req_req=dict(joinby="req_id",
                                       multiple=False))
    else:
        load("vol_application")
        # Volunteers can only see Public Requests
        s3.filter = (req_table.public == True)
        configure(req_table,
                  editable=False), # We need the Controller/Table ACL to be editable to be able to add components
        person = s3_logged_in_person()
        if "application" in request.args:
            # Check for required Skills
            table = db.req_req_skill
            query = (table.req_id == request.args[0])
            req = db(query).select(table.skill_id,
                                   limitby=(0, 1)).first()
            if req and req.skill_id:
                # Read the applicant's skills
                table = db.vol_skill
                query = (table.person_id == auth.s3_logged_in_person())
                skillset = db(query).select(table.skill_id,
                                            limitby=(0, 1)).first()
                gap = False
                if not skillset:
                    gap = True
                else:
                    for skill in req.skill_id:
                        if not skill in skillset.skill_id:
                            gap = True
                            break
                if gap:
                    response.warning = T("Please check that you have the required skills for this assignment as you've not specified that you have all the required skills.")

            s3.crud.submit_button = T("COMMIT")
            table = db.vol_application
            table.person_id.default = person
            table.person_id.readable = table.person_id.writable = False
            s3.crud_strings["vol_application"].subtitle_create = ""
            # Read in current Emergency Contacts
            ctable = db.vol_contact
            query = (ctable.person_id == person)
            contacts = db(query).select(limitby=(0, 1)).first()
            if contacts:
                table.emergency_contact_name.default = contacts.emergency_contact_name
                table.emergency_contact_relationship.default = contacts.emergency_contact_relationship
                table.emergency_contact_phone.default = contacts.emergency_contact_phone

        elif "assignment" in request.args:
            table = db.vol_assignment
            table.person_id.default = person
            table.person_id.readable = table.person_id.writable = False
            # Make the component multiple=False
            # @ToDo: Currently multiple=False will just return the .first() record even if inaccessible!
            #        That would be fixed by a filter, however then UI would break.
            add_component("vol_assignment",
                          req_req=dict(joinby="req_id",
                                       multiple=False))

    def prep(r):
        db.req_req.status.readable = db.req_req.status.writable = False

        # Remove type from list_fields
        list_fields = s3mgr.model.get_config("req_req",
                                             "list_fields")
        try:
            list_fields.remove("type")
        except:
             # It has already been removed.
             # This can happen if the req controller is called
             # for a second time, such as when printing reports
             # see vol.print_assignment()
            pass
        configure(tablename, list_fields=list_fields)

        # @ToDo: MH - type is always 3
        type = ( r.record and r.record.type ) or \
               ( request.vars and request.vars.default_type )
        if type:
            type = int(type)
            req_table.type.default = int(type)

        # Filter the query based on type
        if s3.filter:
            s3.filter = s3.filter & \
                        (db.req_req.type == type)
        else:
            s3.filter = (db.req_req.type == type)

        configure("req_req",
                  list_fields = ["id",
                                 "priority",
                                 "event_id",
                                 "incident_id",
                                 "purpose",
                                 "site_id",
                                 "date",
                                 "date_required",
                                 ])

        req_table.purpose.label = T("Task Details")

        if r.interactive:
            # Set Fields and Labels depending on type
            # @ToDo: MH - type is always 3
            if type:
                # This prevents the type from being edited AFTER it is set
                req_table.type.readable = False
                req_table.type.writable = False

                # @ToDo: MH - refer to crud strings here - rather than in deployment_settings
                crud_strings = deployment_settings.get_req_req_crud_strings(type)
                if crud_strings:
                    s3.crud_strings["req_req"] = crud_strings

                if "application" in request.args:
                    s3.crud_strings["req_req"].title_display = T("Volunteer Application")
                elif "assignment" in request.args:
                    if s3_has_role(STAFF) and not r.component_id:
                        s3.crud_strings["req_req"].title_display = T("Volunteer Roster")
                    else:
                        s3.crud_strings["req_req"].title_display = T("Volunteer Assignment")
                        atable = db.vol_assignment
                        # @ToDo: Hide if vol hasn't yet checked-out or if time not > time_until
                        #atable.task_evaluation.readable = False


            elif r.component and r.component.name == "req_skill" and \
                deployment_settings.get_req_webeoc_is_master():
                # Is this component being updated (not created)
                req_skill_table = db.req_req_skill
                req_skill_table.skill_id.writable = False
                req_skill_table.quantity.writable = False

            # @ToDo: apply these changes via JS for the create form where type is editable
            #if type == 3: # Person
            req_table.date_required.requires = req_table.date_required.requires.other
            req_table.date_required_until.requires = req_table.date_required_until.requires.other
            req_table.location.readable = True
            req_table.public.readable = True
            req_table.organisations_id.readable = True
            req_table.emailed.readable = True

            if r.method == "create" or \
               not deployment_settings.get_req_webeoc_is_master():
                # Only enable Edit for fields where Sahana (not WebEOC) is Master
                req_table.location.writable = True
                req_table.public.writable = True
                req_table.organisations_id.writable = True

            req_table.purpose.comment = DIV(_class="tooltip",
                                            _title="%s|%s" % \
                                                (T("Task Details"),
                                                 T("Please include information regarding the accessibility & mobility constraints of the volunteer task and location")
                                                ),
                                            ) 
            req_table.site_id.label =  T("Report To Facility")
            req_table.request_for_id.label = T("Point of Contact")

            if r.method != "update" and r.method != "read":
                if not r.component:
                    # Hide fields which don't make sense in a Create form
                    # - includes one embedded in list_create
                    # - list_fields over-rides, so still visible within list itself
                    s3.req_create_form_mods()

                    # Get the default Facility for this user
                    # @ToDo: Use site_id in User Profile (like current organisation_id)
                    if has_module("hrm"):
                        hrtable = db.hrm_human_resource 
                        query = (hrtable.person_id == s3_logged_in_person())
                        site = db(query).select(hrtable.site_id,
                                                limitby=(0, 1)).first()
                        if site:
                            r.table.site_id.default = site.site_id

                elif r.component.name == "req_skill":
                    #req_hide_quantities(r.component.table)
                    table = r.component.table
                    table.quantity_commit.writable = table.quantity_commit.readable = False
                    table.quantity_fulfil.writable = table.quantity_fulfil.readable = False

        if r.component:
            if r.component.name == "req_skill":
                # Limit site_id to facilities the user has permissions for
                # @ToDo: Non-Item requests shouldn't be bound to a Facility?
                auth.permission.permitted_facilities(table=r.table,
                                                     error_msg=T("You do not have permission for any facility to make a request."))

            elif r.component.name == "assignment":
                table = db.vol_assignment
                # Tweak the breadcrumb
                if r.component.count() > 1:
                    label = T("Roster")
                else:
                    label = T("Assignment")
                breadcrumbs[2] = (label, False,
                                  URL(c=request.controller,
                                      f=request.function,
                                      args=request.args))
                if s3_has_role(STAFF):
                    table.report_to_id.default = r.record.request_for_id
                else:
                    # Volunteer can evaluate task if vol has checked-in and (checked-out or time > time_until)
                    query = (table.id == r.component_id)
                    assign = db(query).select(table.checkin,
                                              table.checkout,
                                              limitby=(0, 1)).first()
                    checkin = None
                    if assign:
                        checkin = assign.checkin
                        checkout = assign.checkout
                        query = (req_table.id == r.id)
                        req = db(query).select(req_table.date_required_until,
                                                          limitby=(0, 1)).first()
                        if req:
                            required_until = req.date_required_until
                        else:
                            required_until = datetime.datetime(3000, 1, 1)

                    if checkin and (checkout or \
                                    request.utcnow > required_until):
                        table.task_evaluation.writable = True
                        table.task_eval_comments.writable = True
                    else:
                        table.task_evaluation.readable = False
                        table.task_eval_comments.readable = False
                        if s3_has_role(ORG_VOL):
                            # Allow to edit Who/How Many until Evaluation time
                            s3.crud_strings.vol_assignment.title_update = T("Application Details")
                            table.team_leader_id.readable = table.team_leader_id.writable = True
                            table.number.readable = table.number.writable = True
                            table.number.label = T("Number of Volunteers Committed")
                            # Allow OrgVols to check-in/out themselves
                            table.checkin.readable = table.checkin.writable = True
                            table.checkout.readable = table.checkout.writable = True

            elif r.id and \
                 r.component.name == "application" and \
                 r.method == "create":

                if not auth.user.organisation_id:
                    # Display an error message if the user has already got an
                    # assignment during this time period, this can
                    # alternatively be done onvalidation of the application,
                    # but doing it here is better UX and saves a query:
                    req_id = r.id
                    req = r.record
                    # @todo: make min_lag deployment setting:
                    min_lag = datetime.timedelta(hours=1)
                    # Earliest that another Request can start
                    earliest = req.date_required_until + min_lag
                    # Latest that another Request can end
                    latest = req.date_required - min_lag
                    person_id = s3_logged_in_person()
                    if person_id:
                        rtable = db.req_req
                        atable = db.vol_assignment
                        query = (atable.person_id == person_id) & \
                                (rtable.id == atable.req_id) & \
                                ((rtable.date_required >= earliest) | \
                                 (rtable.date_required_until >= latest))
                        conflict = db(query).select(rtable.id,
                                                    limitby=(0, 1)).first()
                        if conflict:
                            session.error = T("You are assigned to another request during this time period")
                            redirect(URL(c="vol", f="req_skill"))
                            # Could be made less strong:
                            #response.error = T("You are assigned to another request during this time period")
        else:
            # Limit site_id to facilities the user has permissions for
            auth.permission.permitted_facilities(table=r.table,
                                                 error_msg=T("You do not have permission for any facility to make a request."))

        return True
    s3.prep = prep

    # Post-process
    def postp(r, output):

        if r.interactive:
            if r.http == "POST":
                form = output.get("form", None)
                if not form.errors:
                    # Form submitted Succesfully
                    # interactive-only onaccept routines can go here
                    if r.component and \
                       r.component.name == "application":
                        # Check whether Request Full:
                        # Create Assignment, Update Commit status
                        s3.application_onaccept_interactive(form)

            # GET & POST
            if deployment_settings.get_req_webeoc_is_master():
                deletable = False
            else:
                deletable = True
            s3_action_buttons(r, deletable=deletable)
            if not r.component:
                pass
            elif r.component.name == "req_skill":
                pass
            elif r.component.name == "application":
                try:
                    form = output["form"]
                    if form.errors.dsw:
                        dsw_error = DIV(form.errors.dsw,
                                        _id="dsw__error",
                                        _class="error",
                                        _style="display: block;")
                    else:
                        dsw_error = ""
                    give2la_forms = A( T("Give2LA Registration Forms"),
                                       _href = URL(c="static",
                                                   f="Give2LA_Registration_Forms.pdf"),
                                      _target="_blank"
                                      )
                    dsw_program_regulations = A( T("DSW Program regulations"),
                                                 _href = "http://www.calema.ca.gov/planningandpreparedness/pages/disaster-service-worker-volunteer-program.aspx",
                                                 _target="_blank"
                                                 )
                    vol_appl_conditions = SPAN( XML(T("As a volunteer working to assist disaster survivors and in disaster recovery efforts, you will be required to fill out and sign the %(give2la_forms)s. Please print these forms and bring them to the Volunteering Location. The forms are in English only.") % \
                                                      dict(give2la_forms = give2la_forms)
                                                      ),
                                                BR(),
                                                XML(T("As a Disaster Service Worker (DSW) volunteer, I agree to comply with all %(dsw_program_regulations)s including being registered by an accredited disaster council or its authorized designee, subscribing to the loyalty oath, and performing eligible disaster service duties.") %
                                                      dict(dsw_program_regulations = dsw_program_regulations)
                                                     ),
                                                BR(),
                                                T("Check here to agree to these conditions:")
                                                )
                    form[0][-2].append(TR(TD(LABEL(vol_appl_conditions,
                                                   _for="dsw",
                                                   _style="display: inline;",
                                                   _id="dsw__label"),
                                             SPAN("*", _class="req"),
                                             INPUT(_type="checkbox",
                                                   _value="on",
                                                   _name="dsw",
                                                   _id="dsw",
                                                   _class="boolean"),
                                             dsw_error,
                                             _class="w2p_fl"),
                                          _id="dsw__row"))
                    form[0][-1][0][0]["_class"] = "accept-button"
                    form[0][-1][0].append(BR())
                    form[0][-1][0].append(INPUT(_type="button",
                                                _value=T("DECLINE"),
                                                _class="wide-grey-button",
                                                _onClick="javascript: window.location='%s'" % \
                                                        URL(c=request.controller,
                                                            f="req_skill")))
                except KeyError:
                    # update 'form'
                    pass
                if "subtitle" in output and not output["subtitle"]:
                    # Remove null subtitle from Application form to avoid CSS markup
                    output.pop("subtitle")

            elif r.component.name == "assignment":
                ctable = r.component.table
                # This is always appropriate
                s3.actions = [
                    dict(url = URL(f = "req",
                                   args = [r.id,
                                           r.component_name,
                                           "[id]"]),
                         _class = "action-btn",
                         label = str(T("Details"))
                        )]
                # This is only appropriate if vol not yet checked-in
                query = (ctable.checkin == None)
                rows = db(query).select(ctable.id)
                restrict = [str(row.id) for row in rows]
                s3.actions.append(
                    dict(url = URL(f = "req",
                                   args = [r.id,
                                           r.component_name,
                                           "[id]",
                                           "checkin"]),
                         _class = "action-btn",
                         label = str(T("Check-In NOW")),
                         restrict = restrict
                        )
                    )
                # This is only appropriate if vol checked-in but not out
                query = (ctable.checkin != None) & \
                        (ctable.checkout == None)
                rows = db(query).select(ctable.id)
                restrict = [str(row.id) for row in rows]
                s3.actions.append(
                    dict(url = URL(f = "req",
                                   args = [r.id,
                                           r.component_name,
                                           "[id]",
                                           "checkout"]),
                         _class = "action-btn",
                         label = str(T("Check-Out NOW")),
                         restrict = restrict
                        )
                    )
            else:
                # We don't have other components
                pass

        return output
    s3.postp = postp

    output = s3_rest_controller("req", "req",
                                rheader=vol_req_rheader)

    return output

# -----------------------------------------------------------------------------
def req_skill():
    """ REST Controller """

    if s3_has_role(ORG_DON) and not s3_has_role(ORG_VOL):
        session.warning = T("As a Corporation/Organization we suggest you donate staff as Services. If you wish to volunteer personally, then please sign out and then login with another account.")
        redirect(URL(c="don", f="organisation", args=[auth.user.organisation_id, "don_item"], vars={"item":"services"}))

    tablename = "req_req_skill"
    load(tablename)
    table = db[tablename]

    configure(tablename,
              insertable=False)

    if not s3_has_role(STAFF):
        req_table = db.req_req
        load("vol_assignment")
        vtable = db.vol_assignment

        vol_sidebar()

        # Filter out:
        #   Reqs which haven't been published to the public site
        #   Reqs which are complete (status defined in models/req.py)
        #   Reqs which are past their end date
        s3.filter = \
            ((req_table.id == table.req_id) & (req_table.public == True)) & \
            ((req_table.id == table.req_id) & (req_table.commit_status != 2)) & \
            ((req_table.id == table.req_id) & (req_table.date_required_until > request.utcnow))
            
        if s3_has_role(ORG_VOL):
            # Also include Requests for their Org
            s3.filter = s3.filter | \
                ((req_table.id == table.req_id) & (req_table.organisations_id.belongs((auth.user.organisation_id,))))


        #if auth.s3_is_logged_in():
        #    person = auth.s3_logged_in_person()
        #    # Filter Out:
        #    #   Reqs which the Vol has already got an Assignment for
        #    s3.filter = s3.filter & \
        #                         ~((vtable.req_id == table.req_id) & (vtable.person_id == person))

        configure(tablename,
                  # Can't orderby a virtual field
                  #orderby = table.priority,
                  list_fields=["id",
                               (T("Task"), "task"),
                               # Just for training!?
                               (T("Priority"), "priority"),
                               (T("Date + Time"), "date"),
                               "skill_id",
                               # @ToDo: If-needed, VirtualField
                               #"priority",
                               (T("Location"), "location"),
                               #(T("Number of Volunteers Needed (Still Needed/Total Needed)"), "needed"),
                               (T("Number of Volunteers Still Needed"), "needed"),
                               #"quantity",
                               "comments"
                               ])
        actions = [
                dict(url = URL(c = "vol",
                               f = "req",
                               args = ["application", "create"],
                               vars = {"skill_id" : "[id]"}),
                     _class = "apply-button",
                     #label = str(T("Apply"))
                     label = SPAN(T("Apply")).xml()
                    )
                ]
    else:
        # NB No link leads Staff here
        # Tweak the breadcrumbs
        breadcrumbs[2] = (T("Requests for Volunteers"), False,
                          URL(c=request.controller,
                              f=request.function))
        actions = [
                dict(url = URL(c = "vol",
                               f = "req",
                               args = ["req_skill", "[id]"]),
                     _class = "action-btn",
                     label = str(READ)
                    )
                ]

    def prep(r):
        if r.interactive:
            if r.method != "update" and r.method != "read":
                # Hide fields which don't make sense in a Create form
                # - includes one embedded in list_create
                # - list_fields over-rides, so still visible within list itself
                s3.req_hide_quantities(r.table)
        return True
    s3.prep = prep

    # Post-process
    def postp(r, output):
        if r.interactive:
            s3.actions = actions
            if not s3_has_role(STAFF) and r.method == None:
                if auth.is_logged_in():
                    line = XML(T("If you have the required skills, click to %(apply_button)s") %
                                    dict( apply_button = A(SPAN(T("Apply")),
                                                           _class="apply-button",
                                                           _style ="display:inline-block;text-align:center")
                                        )
                                )
                else:
                    line = TAG[""]( XML(T("Please %(register)s to volunteer with %(give2la)s and receive updates of new Requests for Volunteers.") %
                                   dict( register = A( T("register"),
                                                           _href = URL(c = "vol",
                                                                       f = "register")
                                                          ),
                                             give2la = B("Give2", I("LA"))
                                        )
                                   ),
                            )
                output["rheader"] = DIV(P(B(T("The City of Los Angeles has the following Requests for Volunteers.") ),
                                          BR(),
                                          line
                                          ))
        return output
    s3.postp = postp

    output = s3_rest_controller("req", "req_skill")

    return output

# END =========================================================================
