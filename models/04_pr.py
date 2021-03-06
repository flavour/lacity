# -*- coding: utf-8 -*-

"""
    Person Registry
"""

module = "pr"

# =============================================================================
# Person
#
pr_gender_opts = {
    1:"",
    2:T("female"),
    3:T("male")
}
pr_gender = S3ReusableField("gender", "integer",
                            requires = IS_IN_SET(pr_gender_opts, zero=None),
                            default = 1,
                            label = T("Gender"),
                            represent = lambda opt: \
                                        pr_gender_opts.get(opt, UNKNOWN_OPT))

pr_age_group_opts = {
    1:T("unknown"),
    2:T("Infant (0-1)"),
    3:T("Child (2-11)"),
    4:T("Adolescent (12-20)"),
    5:T("Adult (21-50)"),
    6:T("Senior (50+)")
}
pr_age_group = S3ReusableField("age_group", "integer",
                               requires = IS_IN_SET(pr_age_group_opts,
                                                    zero=None),
                               default = 1,
                               label = T("Age Group"),
                               represent = lambda opt: \
                                           pr_age_group_opts.get(opt,
                                                                 UNKNOWN_OPT))

pr_marital_status_opts = {
    1:T("unknown"),
    2:T("single"),
    3:T("married"),
    4:T("separated"),
    5:T("divorced"),
    6:T("widowed"),
    9:T("other")
}

pr_religion_opts = deployment_settings.get_L10n_religions()

pr_impact_tags = {
    1: T("injured"),
    4: T("diseased"),
    2: T("displaced"),
    5: T("separated from family"),
    3: T("suffered financial losses")
}

if deployment_settings.get_L10n_mandatory_lastname():
    last_name_validate = IS_NOT_EMPTY(error_message = T("Please enter a last name"))
else:
    last_name_validate = None

tablename = "pr_person"
table = define_table(tablename,
                     super_link(db.pr_pentity),    # pe_id
                     super_link(db.sit_trackable), # track_id
                     location_id(readable=False,
                                 writable=False),  # base location
                     pe_label(readable=False,
                              writable=False,
                              comment = DIV(DIV(_class="tooltip",
                                                _title="%s|%s" % (T("ID Tag Number"),
                                                                  T("Number or Label on the identification tag this person is wearing (if any)."))))),
                     Field("missing", "boolean",
                           readable=False,
                           writable=False,
                           default=False,
                           represent = lambda missing: \
                             (missing and ["missing"] or [""])[0]),
                     Field("volunteer", "boolean",
                           readable=False,
                           writable=False,
                           default=False),
                     Field("first_name", notnull=True,
                           length=64, # Mayon Compatibility
                           # NB Not possible to have an IS_NAME() validator here
                           # http://eden.sahanafoundation.org/ticket/834
                           requires = IS_NOT_EMPTY(error_message = T("Please enter a first name")),
                           comment =  DIV(_class="tooltip",
                                          _title="%s|%s" % (T("First name"),
                                                            T("The first or only name of the person (mandatory)."))),
                           label = T("First Name")),
                     Field("middle_name",
                           length=64, # Mayon Compatibility
                           label = T("Middle Name")),
                     Field("last_name",
                           length=64, # Mayon Compatibility
                           label = T("Last Name"),
                           requires = last_name_validate),
                     Field("preferred_name",
                           readable=False,
                           writable=False,
                           comment = DIV(DIV(_class="tooltip",
                                             _title="%s|%s" % (T("Preferred Name"),
                                                                T("The name to be used when calling for or directly addressing the person (optional).")))),
                           length=64), # Mayon Compatibility
                     Field("local_name", label = T("Local Name"),
                           readable = False,
                           writable = False,
                           comment = DIV(DIV(_class="tooltip",
                                             _title="%s|%s" % (T("Local Name"),
                                                               T("Name of the person in local language and script (optional)."))))),
                     pr_gender(readable=False,
                               writable=False,
                               label = T("Gender")),
                     Field("date_of_birth", "date",
                           readable=False,
                           writable=False,
                           label = T("Date of Birth"),
                           requires = [IS_EMPTY_OR(IS_DATE_IN_RANGE(
                                         format = s3_date_format,
                                         maximum=request.utcnow.date(),
                                         error_message="%s %%(max)s!" %
                                             T("Enter a valid date before")))],
                           widget = S3DateWidget(past=1320,  # Months, so 110 years
                                                 future=0)),
                     pr_age_group(readable=False,
                                  writable=False,
                                  label = T("Age group")),
                     Field("nationality",
                           readable = False,
                           writable = False,
                           #default = "US",
                           requires = IS_NULL_OR(IS_IN_SET_LAZY(
                            lambda: gis.get_countries(key_type="code"),
                            zero = SELECT_LOCATION)),
                           label = T("Nationality"),
                           comment = DIV(DIV(_class="tooltip",
                                             _title="%s|%s" % (T("Nationality"),
                                                               T("Nationality of the person.")))),
                           represent = lambda code: \
                               gis.get_country(code, key_type="code") or UNKNOWN_OPT),
                     Field("occupation",
                           readable=False,
                           writable=False,
                           length=128),          # Mayon Compatibility
                     Field("picture", "upload",
                           autodelete=True,
                           requires = IS_EMPTY_OR(IS_IMAGE(maxsize=(800, 800),
                                                  error_message=T("Upload an image file (bmp, gif, jpeg or png), max. 300x300 pixels!"))),
                           represent = lambda image: image and \
                                         DIV(A(IMG(_src=URL(c="default", f="download",
                                                            args=image),
                                                   _height=60,
                                                   _alt=T("View Picture")),
                                                   _href=URL(c="default", f="download",
                                                             args=image))) or
                                         T("No Picture"),
                           comment =  DIV(_class="tooltip",
                                          _title="%s|%s" % (T("Picture"),
                                                            T("Upload an image file here.")))),
 
                     comments(),
                     *s3_meta_fields())

def person_represent(id):

    def _represent(id):
        if isinstance(id, Row):
            person = id
            id = person.id
        else:
            table = db.pr_person
            person = db(table.id == id).select(table.first_name,
                                               table.middle_name,
                                               table.last_name,
                                               limitby=(0, 1)).first()
        if person:
            return vita.fullname(person)
        else:
            return None

    name = cache.ram("pr_person_%s" % id, lambda: _represent(id),
                     time_expire=10)
    return name

def pr_person_onvalidation(form):
    """ Ovalidation callback """

    try:
        age = int(form.vars.get("age_group", None))
    except (ValueError, TypeError):
        age = None
    dob = form.vars.get("date_of_birth", None)

    if age and age != 1 and dob:
        now = request.utcnow
        dy = int((now.date() - dob).days / 365.25)
        if dy < 0:
            ag = 1
        elif dy < 2:
            ag = 2
        elif dy < 12:
            ag = 3
        elif dy < 21:
            ag = 4
        elif dy < 51:
            ag = 5
        else:
            ag = 6

        if age != ag:
            form.errors.age_group = T("Age group does not match actual age.")
            return False

    return True

def pr_person_duplicate(item):
    """
        This callback will be called when importing person records it will look
        to see if the record being imported is a duplicate.

        @param item: An S3ImportItem object which includes all the details
                    of the record being imported

        If the record is a duplicate then it will set the item method to update

        Rules for finding a duplicate:
         - Look for a record with the same name (first name and last name), ignoring case
         - and the same email address (if provided)
    """

    # Ignore this processing if the id is set
    if item.id:
        return

    if item.tablename == "pr_person":
        ptable = db.pr_person
        ctable = db.pr_contact

       # Get the details from the item record
        fname = "first_name" in item.data and item.data.first_name
        lname = "last_name" in item.data and item.data.last_name
        if not fname or not lname:
            return
        query = (ptable.first_name.lower().like('%%%s%%' % fname.lower())) & \
                (ptable.last_name.lower().like('%%%s%%' % lname.lower()))
        email = False
        for citem in item.components:
            if citem.tablename == "pr_contact":
                if citem.data and "contact_method" in citem.data and \
                   citem.data.contact_method == "EMAIL":
                    email = citem.data.value
        if email != False:
            query = query & \
                    (ptable.pe_id == ctable.pe_id) & \
                    (ctable.value.lower() == email.lower())
        # Look for details on the database
        _duplicate = db(query).select(ptable.id,
                                      limitby=(0, 1)).first()
        if _duplicate:
            item.id = _duplicate.id
            item.data.id = _duplicate.id
            item.method = item.METHOD.UPDATE
            for citem in item.components:
                citem.method = citem.METHOD.UPDATE

pr_person_search = s3base.S3PersonSearch(
            name="person_search_simple",
            label=T("Name and/or ID"),
            comment=T("To search for a person, enter any of the first, middle or last names and/or an ID number of a person, separated by spaces. You may use % as wildcard. Press 'Search' without input to list all persons."),
            field=["pe_label",
                   "first_name",
                   "middle_name",
                   "last_name",
                   "local_name",
                   "identity.value"
                ])

configure(tablename,
          super_entity=(db.pr_pentity, db.sit_trackable),
          list_fields = ["id",
                         "first_name",
                         "middle_name",
                         "last_name",
                         "picture",
                         "gender",
                         "age_group"
                         ],
          onvalidation=pr_person_onvalidation,
          search_method=pr_person_search,
          resolve=pr_person_duplicate,
          main="first_name",
          extra="last_name")

ADD_PERSON = T("Add Person")
LIST_PERSONS = T("List Persons")
crud_strings[tablename] = Storage(
    title_create = T("Add a Person"),
    title_display = T("Person Details"),
    title_list = LIST_PERSONS,
    title_update = T("Edit Person Details"),
    title_search = T("Search Persons"),
    subtitle_create = ADD_PERSON,
    subtitle_list = T("Persons"),
    label_list_button = LIST_PERSONS,
    label_create_button = ADD_PERSON,
    label_delete_button = T("Delete Person"),
    msg_record_created = T("Person added"),
    msg_record_modified = T("Person details updated"),
    msg_record_deleted = T("Person deleted"),
    msg_list_empty = T("No Persons currently registered"))

shn_person_comment = lambda title, comment: \
    DIV(A(ADD_PERSON,
        _class="colorbox",
        _href=URL(c="pr", f="person", args="create",
                  vars=dict(format="popup")),
        _target="top",
        _title=ADD_PERSON),
    DIV(DIV(_class="tooltip",
        _title="%s|%s" % (title, comment))))

shn_person_id_comment = shn_person_comment(
    T("Person"),
    T("Type the first few characters of one of the Person's names."))

person_id = S3ReusableField("person_id", db.pr_person,
                            sortby = ["first_name", "middle_name", "last_name"],
                            requires = IS_NULL_OR(IS_ONE_OF(db, "pr_person.id",
                                        person_represent,
                                        orderby="pr_person.first_name",
                                        sort=True,
                                        error_message=T("Person must be specified!"))),
                            represent = lambda id: (id and \
                                        [person_represent(id)] or [NONE])[0],
                            label = T("Person"),
                            comment = shn_person_id_comment,
                            ondelete = "RESTRICT",
                            widget = S3PersonAutocompleteWidget())


def person_contact(pe_id, contact_method):
    ptable = db.pr_person
    ctable = db.pr_contact
    query = ( ( ptable.id == pe_id ) & \
              ( ctable.pe_id == ptable.pe_id ) & \
              ( ctable.contact_method == contact_method)
            )
    contact = db(query).select(ctable.value,
                               limitby=(0, 1)).first()
    if contact:
        return contact.value
    else:
        return NONE

class person_virtualfields(dict, object):
    def phone(self):
        return person_contact(self.pr_person.id,"SMS")
    def email(self):
        return person_contact(self.pr_person.id,"EMAIL")
    def address(self):
        ptable = db.pr_person
        atable = db.pr_address
        
        query = ( ( ptable.id == self.pr_person.id ) & \
                  ( atable.pe_id == ptable.pe_id ) & \
                  ( atable.type == 1) & \
                  ( atable.deleted != True)
                )
        record = db(query).select(atable.address,
                                  atable.L3,
                                  atable.L1,
                                  atable.postcode,
                                  limitby=(0, 1)).first()
        if record:
            return ", ".join( [record.address,
                               record.L3,
                               record.L1,
                               record.postcode,
                               ])
        else:
            return NONE

table.virtualfields.append(person_virtualfields())

# =============================================================================
# Contact
#
# @ToDo: Provide widgets which can be dropped into the main person form to have
#        the relevant ones for that deployment/context collected on that same
#        form
#
pr_contact_method_opts = msg.CONTACT_OPTS

tablename = "pr_contact"
table = define_table(tablename,
                     super_link(db.pr_pentity), # pe_id
                     Field("contact_method",
                           length=32,
                           requires = IS_IN_SET(pr_contact_method_opts,
                                                zero=None),
                           default = "SMS",
                           label = T("Contact Method"),
                           represent = lambda opt: \
                             pr_contact_method_opts.get(opt,
                                                        UNKNOWN_OPT)),
                     Field("value", notnull=True, label= T("Value"),
                           requires = IS_NOT_EMPTY()),
                     Field("priority", "integer", label= T("Priority"),
                           comment = DIV( _class="tooltip",
                                         _title="%s|%s" % (T("Priority"),
                                                           T("What order to be contacted in."))),
                           requires = IS_IN_SET(range(1, 11), zero=None),
                           ),
                     #Field("contact_person", label= T("Contact Person")),
                     comments(),
                     *s3_meta_fields())

tablename = "pr_contact"
table = db[tablename]
table.pe_id.requires = IS_ONE_OF(db, "pr_pentity.pe_id",
                                 shn_pentity_represent,
                                 orderby="instance_type",
                                 filterby="instance_type",
                                 filter_opts=("pr_person", "pr_group"))

def contact_onvalidation(form):
    """ Contact form validation """

    if form.vars.contact_method == "EMAIL":
        email, error = IS_EMAIL()(form.vars.value)
        if error:
            form.errors.value = T("Enter a valid email")

    return False

def contact_deduplicate(item):

    if item.id:
        return
    if item.tablename == "pr_contact":

        table = item.table
        pe_id = item.data.get("pe_id", None)
        contact_method = item.data.get("contact_method", None)
        value = item.data.get("value", None)

        if pe_id is None:
            return

        query = (table.pe_id == pe_id) & \
                (table.contact_method == contact_method) & \
                (table.value == value) & \
                (table.deleted != True)

        _duplicate = db(query).select(table.id,
                                      limitby=(0, 1)).first()
        if _duplicate:
            item.id = _duplicate.id
            item.method = item.METHOD.UPDATE
    return

configure(tablename,
          onvalidation=contact_onvalidation,
          resolve=contact_deduplicate,
          list_fields=["id",
                       #"pe_id",
                       "contact_method",
                       "value",
                       "priority",
                       #"contact_person",
                       #"name",
                       ])

add_component(table, pr_pentity=super_key(db.pr_pentity))

crud_strings[tablename] = Storage(
    title_create = T("Add Contact Information"),
    title_display = T("Contact Details"),
    title_list = T("Contact Information"),
    title_update = T("Edit Contact Information"),
    title_search = T("Search Contact Information"),
    subtitle_create = T("Add Contact Information"),
    subtitle_list = T("Contact Information"),
    label_list_button = T("List Contact Information"),
    label_create_button = T("Add Contact Information"),
    label_delete_button = T("Delete Contact Information"),
    msg_record_created = T("Contact Information Added"),
    msg_record_modified = T("Contact Information Updated"),
    msg_record_deleted = T("Contact Information Deleted"),
    msg_list_empty = T("No contact information available"))

# =============================================================================
def pr_component_tables():
    """ Load Person Component Tables when required """

    # =========================================================================
    # Address (address)
    #
    pr_address_type_opts = {
        1:T("Home Address"),
        2:T("Office Address"),
        #3:T("Holiday Address"),
        9:T("other")
    }

    resourcename = "address"
    tablename = "pr_address"
    table = define_table(tablename,
                         super_link(db.pr_pentity), # pe_id
                         Field("type", "integer",
                               requires = IS_IN_SET(pr_address_type_opts, zero=None),
                               widget = RadioWidget.widget,
                               default = 1,
                               label = T("Address Type"),
                               represent = lambda opt: \
                                           pr_address_type_opts.get(opt, UNKNOWN_OPT)),
                         #Field("co_name", label=T("c/o Name")),
                         location_id(),
                         comments(),
                         *(address_fields()  + s3_meta_fields()))

    table.pe_id.requires = IS_ONE_OF(db, "pr_pentity.pe_id", shn_pentity_represent,
                                     orderby="instance_type",
                                     filterby="instance_type",
                                     filter_opts=("pr_person", "pr_group"))


    def address_onaccept(form):
        """
            Updates the Base Location to be the same as the Address

            NB This doesn't apply globally but is only activated for specific
               parts of the workflow
        """

        if "location_id" in form.vars and \
           "base_location" in request.vars and request.vars.base_location == "on":
            location_id = form.vars.location_id
            pe_id = request.post_vars.pe_id
            s3tracker(db.pr_pentity, pe_id).set_base_location(location_id)

    if not deployment_settings.get_gis_building_name():
        table.building_name.readable = False

    configure(tablename,
              onvalidation=address_onvalidation,
              list_fields = ["id",
                             "type",
                             #"building_name",
                             "address",
                             "postcode",
                             #"L4",
                             "L3",
                             "L2",
                             "L1",
                             "L0"
                             ])

    add_component(table,
                  pr_pentity=super_key(db.pr_pentity))

    ADD_ADDRESS = T("Add Address")
    LIST_ADDRESS = T("List of addresses")
    crud_strings[tablename] = Storage(
        title_create = ADD_ADDRESS,
        title_display = T("Address Details"),
        title_list = LIST_ADDRESS,
        title_update = T("Edit Address"),
        title_search = T("Search Addresses"),
        subtitle_create = T("Add New Address"),
        subtitle_list = T("Addresses"),
        label_list_button = LIST_ADDRESS,
        label_create_button = ADD_ADDRESS,
        msg_record_created = T("Address added"),
        msg_record_modified = T("Address updated"),
        msg_record_deleted = T("Address deleted"),
        msg_list_empty = T("There is no address for this person yet. Add new address."))

# Provide a handle to this load function
s3mgr.model.loader(pr_component_tables,
                   "pr_address",
                   #"pr_pimage",
                   #"pr_identity",
                   )

# =============================================================================
# Saved Searches
#
def saved_search_tables():
    tablename = "pr_save_search"
    table = define_table(tablename,
                         Field("user_id", "integer",
                               readable = False,
                               writable = False,
                               default = auth.user_id),
                         Field("search_vars","string",
                               label = T("Search Criteria")),
                         Field("subscribed","boolean", default=False),
                         person_id(label = T("Person"),
                                   default = s3_logged_in_person()),
                         *s3_timestamp())

    import cPickle
    def get_criteria(id):
        s = ""
        try:
            id = id.replace("&apos;", "'")
            search_vars = cPickle.loads(id)
            s = "<p>"
            pat = '_'
            for var in search_vars.iterkeys():
                if var == "criteria" :
                    c_dict = search_vars[var]
                    #s = s + crud_string("pr_save_search", "Search Criteria")
                    for j in c_dict.iterkeys():
                        if not re.match(pat,j):
                            st = str(j)
                            st = st.replace("_search_", " ")
                            st = st.replace("_advanced", "")
                            st = st.replace("_simple", "")
                            st = st.replace("text", "text matching")
                            """st = st.replace(search_vars["function"], "")
                            st = st.replace(search_vars["prefix"], "")"""
                            st = st.replace("_", " ")
                            s = "%s <b> %s </b>: %s <br />" %(s, st.capitalize(), str(c_dict[j]))
                elif var == "simple" or var == "advanced":
                    continue
                else:
                    if var == "function":
                        v1 = "Resource Name"
                    elif var == "prefix":
                        v1 = "Module"
                    s = "%s<b>%s</b>: %s<br />" %(s, v1, str(search_vars[var]))
            s = s + "</p>"
            return XML(s)
        except:
            return XML(s)

    table.search_vars.represent = lambda id : get_criteria(id = id)

    configure(tablename,
              insertable = False,
              editable = False,
              listadd = False,
              deletable = True,
              list_fields=["search_vars"])

    add_component(table, pr_person="person_id")

    crud_strings[tablename] = Storage(title_create = T("Save Search"),
                                      title_display = T("Saved Search Details"),
                                      title_list = T("Saved Searches"),
                                      title_update = T("Edit Saved Search"),
                                      title_search = T("Search Saved Searches"),
                                      subtitle_create = T("Add Saved Search"),
                                      subtitle_list = T("Saved Searches"),
                                      label_list_button = T("List Saved Searches"),
                                      label_create_button = T("Save Search"),
                                      label_delete_button = T("Delete Saved Search"),
                                      msg_record_created = T("Saved Search added"),
                                      msg_record_modified = T("Saved Search updated"),
                                      msg_record_deleted = T("Saved Search deleted"),
                                      msg_list_empty = T("No Search saved"))

# Provide a handle to this load function
s3mgr.model.loader(saved_search_tables,
                   "pr_save_search")

# =============================================================================
def pr_rheader(r, tabs=[]):
    """
        Person Registry resource headers
        - used in PR, HRM, DVI, MPR, MSG, VOL
    """

    if "viewing" in r.vars:
        tablename, record_id = r.vars.viewing.rsplit(".", 1)
        record = db[tablename][record_id]
    else:
        tablename = r.tablename
        record = r.record

    if r.representation == "html":
        rheader_tabs = s3_rheader_tabs(r, tabs)

        if tablename == "pr_person":
            person = record
            if person:
                ptable = db.pr_person
                rheader = DIV(TABLE(

                    TR(TH("%s: " % T("Name")),
                       vita.fullname(person),
                       TH("%s: " % T("ID Tag Number")),
                       "%(pe_label)s" % person,
                       #TH("%s: " % T("Picture"), _rowspan=3),
                       #TD(ptable.picture.represent(person.picture),
                       #   _rowspan=3)
                       ),

                    TR(TH("%s: " % T("Date of Birth")),
                       "%s" % (person.date_of_birth or T("unknown")),
                       TH("%s: " % T("Gender")),
                       "%s" % pr_gender_opts.get(person.gender, T("unknown"))),

                    TR(TH("%s: " % T("Nationality")),
                       "%s" % (gis.get_country(person.nationality, key_type="code") or T("unknown")),
                       TH("%s: " % T("Age Group")),
                       "%s" % pr_age_group_opts.get(person.age_group, T("unknown"))),

                    ), rheader_tabs)
                return rheader

        elif tablename == "pr_group":
            group = record
            if group:
                table = db.pr_group_membership
                query = (table.group_id == record.id) & \
                        (table.group_head == True)
                leader = db(query).select(table.person_id,
                                          limitby=(0, 1)).first()
                if leader:
                    leader = vita.fullname(leader.person_id)
                else:
                    leader = ""
                rheader = DIV(TABLE(
                                TR(TH("%s: " % T("Name")),
                                   group.name,
                                   TH("%s: " % T("Leader")),
                                   leader),
                                TR(TH("%s: " % T("Description")),
                                   group.description,
                                   TH(""),
                                   "")
                                ), rheader_tabs)
                return rheader

    return None

# =============================================================================
# This requires the pr_person table:
#
# Update the allowed maximum hierarchy label now that we know what fields
# are in gis_config. This allows taking the schema into account when
# validating the site config.
# Is this really needed?
# Note that this breaks conditional model loading for Asset & CR!
#gis.update_gis_config_dependent_options()

# End
# =============================================================================

