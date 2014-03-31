# -*- coding: utf-8 -*-

"""
    Organization Registry
"""

module = "org"

#==============================================================================
# Sector
# (Cluster in UN-style terminology)
#
tablename = "org_sector"
table = define_table(tablename,
                        Field("abrv", length=68, notnull=True, unique=True, # 64 is normal, but EMD want one with 68-characters
                              label=T("Abbreviation")),
                        Field("name", length=128, notnull=True, unique=True,
                              label=T("Name")),
                        *s3_meta_fields())

# CRUD strings
SECTOR = T("Sector")
s3.crud_strings[tablename] = Storage(
    title_create = T("Add Sector"),
    title_display = T("Sector Details"),
    title_list = T("List Sectors"),
    title_update = T("Edit Sector"),
    title_search = T("Search Sectors"),
    subtitle_create = T("Add New Sector"),
    subtitle_list = T("Sectors"),
    label_list_button = T("List Sectors"),
    label_create_button = T("Add Sector"),
    label_delete_button = T("Delete Sector"),
    msg_record_created = T("Sector added"),
    msg_record_modified = T("Sector updated"),
    msg_record_deleted = T("Sector deleted"),
    msg_list_empty = T("No Sectors currently registered"))

def org_sector_represent(opt):
    """
        Sector/Cluster representation
        for multiple=True options
    """

    table = db.org_sector
    set = db(table.id > 0).select(table.id,
                                  table.abrv).as_dict()

    if isinstance(opt, (list, tuple)):
        opts = opt
        vals = [str(set.get(o)["abrv"]) for o in opts]
    elif isinstance(opt, int):
        opts = [opt]
        vals = str(set.get(opt)["abrv"])
    else:
        return NONE

    if len(opts) > 1:
        vals = ", ".join(vals)
    else:
        vals = len(vals) and vals[0] or ""
    return vals

def org_sector_duplicate(job):
    """
      This callback will be called when importing records
      it will look to see if the record being imported is a duplicate.

      @param job: An S3ImportJob object which includes all the details
                  of the record being imported

      If the record is a duplicate then it will set the job method to update

      Rules for finding a duplicate:
       - Look for a record with the same abrv, ignoring case
    """
    # ignore this processing if the id is set
    if job.id:
        return
    if job.tablename == "org_sector":
        table = job.table
        if "abrv" in job.data:
            abrv = job.data.abrv
        else:
            return

        query = (table.abrv.lower().like('%%%s%%' % abrv.lower()))
        _duplicate = db(query).select(table.id,
                                      limitby=(0, 1)).first()
        if _duplicate:
            job.id = _duplicate.id
            job.data.id = _duplicate.id
            job.method = job.METHOD.UPDATE

configure("org_sector", resolve=org_sector_duplicate)

sector_id = S3ReusableField("sector_id", "list:reference org_sector",
                            sortby="abrv",
                            requires = IS_NULL_OR(IS_ONE_OF(db,
                                                            "org_sector.id",
                                                            "%(abrv)s",
                                                            sort=True,
                                                            multiple=True)),
                            represent = org_sector_represent,
                            label = SECTOR,
                            ondelete = "RESTRICT")

# =============================================================================
# Organizations
#
organisation_type_opts = {
    1:T("Government"),
    2:T("Embassy"),
    3:T("International NGO"),
    4:T("Donor"),               # Don't change this number without changing organisation_popup.html
    6:T("National NGO"),
    7:T("UN"),
    8:T("International Organization"),
    9:T("Military"),
    10:T("Private"),
    11:T("Intergovernmental Organization"),
    12:T("Institution"),
    13:T("Red Cross / Red Crescent")
}

tablename = "org_organisation"
table = define_table(tablename,
                        super_link(db.pr_pentity), # pe_id
                        #Field("privacy", "integer", default=0),
                        #Field("archived", "boolean", default=False),
                        Field("name", notnull=True, unique=True,
                              length=128,           # Mayon Compatibility
                              label = T("Name"),
                              represent = lambda name: name.replace("&apos;","'") # fixes &apos; in IE8 DataTables
                              ),
                        Field("acronym", length=8, label = T("Acronym"),
                              comment = DIV( _class="tooltip",
                                             _title="%s|%s" % (T("Acronym"),
                                                               T("Acronym of the organization's name, eg. IFRC.")))),
                        Field("type", "integer", label = T("Type"),
                              readable = False,
                              writable = False,
                              requires = IS_NULL_OR(IS_IN_SET(organisation_type_opts)),
                              represent = lambda opt: \
                                organisation_type_opts.get(opt, UNKNOWN_OPT)),
                        sector_id(readable = False,
                                  writable = False),
                        # @LA: Address Details directly in the resource, no need to create a Facility
                        Field("phone", label = T("Phone"),
                              #required = True,
                              requires = shn_phone_requires),
                        Field("phone_mobile", label = deployment_settings.get_ui_label_mobile_phone(),
                              requires = IS_NULL_OR(shn_phone_requires)),
                        #address_building_name(),
                        address_address(requires = IS_NOT_EMPTY()),
                        #address_direction(),
                        address_address2(),
                        address_L3(label=T("City"),
                                   requires = IS_NOT_EMPTY(),),
                        address_L1(label=T("State"),
                                   requires = IS_NOT_EMPTY(),
                                   represent=gis_location_represent,
                                   widget=S3LocationDropdownWidget(level="L1",
                                                                   default="California",
                                                                   empty=False)),
                        address_postcode(requires = IS_NOT_EMPTY(),),
                        # @LA: ORG_VOL
                        Field("has_vols",
                              "boolean",
                              label = T("Has Volunteers"),
                              #readable = False,
                              #writable = False,
                              ),
                        # @LA: ORG_DON
                        Field("has_items",
                              "boolean",
                              label = T("Donates Resources"),
                              #readable = False,
                              #writable = False,
                              ),
                        #Field("registration", label=T("Registration")),    # Registration Number
                        Field("country", "string", length=2,
                              readable = False,
                              writable = False,
                              label = T("Home Country"),
                              requires = IS_NULL_OR(IS_IN_SET_LAZY(
                                  lambda: gis.get_countries(key_type="code"),
                                  zero = SELECT_LOCATION)),
                              represent = lambda code: \
                                  gis.get_country(code, key_type="code") or UNKNOWN_OPT),
                        Field("website", label = T("Website"),
                              readable = False,
                              writable = False,
                              requires = IS_NULL_OR(IS_URL()),
                              represent = shn_url_represent),
                        Field("twitter",                        # deprecated by contact component
                              readable = False,
                              writable = False,
                              comment = DIV( _class="tooltip",
                                             _title="%s|%s" % (T("Twitter"),
                                                               T("Twitter ID or #hashtag")))),
                        Field("donation_phone", label = T("Donation Phone #"),
                              readable = False,
                              writable = False,
                              requires = IS_NULL_OR(shn_phone_requires),
                              comment = DIV( _class="tooltip",
                                             _title="%s|%s" % (T("Donation Phone #"),
                                                               T("Phone number to donate to this organization's relief efforts.")))),
                        Field("upload",
                               "upload",
                               label = T("Documents"),
                               comment = DIV(_class="tooltip",
                                             _title="%s|%s" % (T("Documents"),
                                                               T("Legal, Insurance, etc")
                                                               )
                                            )
                              ),
                        comments(),
                        #document_id(), # Better to have multiple Documents on a Tab
                        *s3_meta_fields())

# Virtual Field for don_item
class org_organisation_virtualfields(dict, object):
    def org_human_resource_email(self):
        org_id = self.org_organisation.id
        table = db.hrm_human_resource
        query = (table.organisation_id == org_id)
        record = db(query).select(table.id,
                                  orderby=table.created_on,
                                  limitby=(0, 1)).first()
        if record:
            return human_resource_contact(record.id, "EMAIL")
        else:
            return NONE
    def org_contact_email(self):
        org_id = self.org_organisation.id
        table = db.org_contact
        query = (table.organisation_id == org_id) & ( table.focal_point == True )
        emails = [row.email for row in db(query).select(table.email)]
        represent = ""
        return ", ".join(emails)

table.virtualfields.append( org_organisation_virtualfields() )

# Organisation table CRUD settings --------------------------------------------
#
ADD_ORGANIZATION = T("Add Organization")
LIST_ORGANIZATIONS = T("List Organizations")
s3.crud_strings[tablename] = Storage(
    title_create = ADD_ORGANIZATION,
    title_display = T("Organization Details"),
    title_list = LIST_ORGANIZATIONS,
    title_update = T("Edit Organization"),
    title_search = T("Search Organizations"),
    subtitle_create = T("Add New Organization"),
    subtitle_list = T("Organizations"),
    label_list_button = LIST_ORGANIZATIONS,
    label_create_button = ADD_ORGANIZATION,
    label_delete_button = T("Delete Organization"),
    msg_record_created = T("Organization added"),
    msg_record_modified = T("Organization updated"),
    msg_record_deleted = T("Organization deleted"),
    msg_list_empty = T("No Organizations currently registered"))

configure(tablename,
                super_entity = db.pr_pentity,
                orderby = table.name,
                list_fields = ["id",
                               "name",
                               "acronym",
                               #"type",
                               #"sector_id",
                               #"country",
                               #"website"
                            ])

# organisation_id reusable field ----------------------------------------------
#
def organisation_represent(id, showlink = False):
    if isinstance(id, Row):
        # Do not repeat the lookup if already done by IS_ONE_OF or RHeader
        org = id
    else:
        table = db.org_organisation
        query = (table.id == id)
        org = db(query).select(table.name,
                               table.acronym,
                               limitby = (0, 1)).first()
    if org:
        represent = org.name
        if org.acronym:
            represent = "%s (%s)" % (represent,
                                     org.acronym)
        if showlink:
            represent = A(represent,
                         _href = URL(c="org", f="organisation", args = [id]))
    else:
        represent = "-"

    return represent

organisation_popup_url = URL(c="org", f="organisation",
                             args="create",
                             vars=dict(format="popup"))

organisation_comment = DIV(A(ADD_ORGANIZATION,
                           _class="colorbox",
                           _href=organisation_popup_url,
                           _target="top",
                           _title=ADD_ORGANIZATION),
                         DIV(DIV(_class="tooltip",
                                 _title="%s|%s" % (T("Organization"),
                                                   #T("Enter some characters to bring up a list of possible matches")))))
                                                   # Replace with this one if using dropdowns & not autocompletes
                                                   T("If you don't see the Organization in the list, you can add a new one by clicking link 'Add Organization'.")))))

from_organisation_comment = copy.deepcopy(organisation_comment)
from_organisation_comment[0]["_href"] = organisation_comment[0]["_href"].replace("popup", "popup&child=from_organisation_id")

organisation_id = S3ReusableField("organisation_id",
                                  db.org_organisation, sortby="name",
                                  requires = IS_NULL_OR(IS_ONE_OF(db, "org_organisation.id",
                                                                  organisation_represent,
                                                                  orderby="org_organisation.name",
                                                                  sort=True)),
                                  represent = organisation_represent,
                                  label = T("Organization"),
                                  comment = organisation_comment,
                                  ondelete = "CASCADE",
                                  # Comment this to use a Dropdown & not an Autocomplete
                                  widget = S3OrganisationAutocompleteWidget()
                                 )

# -----------------------------------------------------------------------------
def organisation_multi_represent(opt):
    """
        Organisation representation
        for multiple=True options
    """

    table = db.org_organisation
    query = (table.deleted == False)
    set = db(query).select(table.id,
                           table.name).as_dict()

    if isinstance(opt, (list, tuple)):
        opts = opt
        vals = [str(set.get(o)["name"]) for o in opts]
    elif isinstance(opt, int):
        opts = [opt]
        vals = str(set.get(opt)["name"])
    else:
        return NONE

    if len(opts) > 1:
        vals = ", ".join(vals)
    else:
        vals = len(vals) and vals[0] or ""
    return vals

organisations_id = S3ReusableField("organisations_id",
                                   "list:reference org_organisation",
                                   sortby="name",
                                   requires = IS_NULL_OR(IS_ONE_OF(db, "org_organisation.id",
                                                                   "%(name)s",
                                                                   multiple=True,
                                                                   #filterby="acronym",
                                                                   #filter_opts=vol_orgs,
                                                                   orderby="org_organisation.name",
                                                                   sort=True)),
                                   represent = organisation_multi_represent,
                                   widget = S3MultiSelectWidget(),
                                   label = T("Organizations"),
                                   ondelete = "SET NULL")

# -----------------------------------------------------------------------------
organisation_search = s3base.S3OrganisationSearch(
        simple = (s3base.S3SearchSimpleWidget(
            name="org_search_text_simple",
            label = T("Search"),
            comment = T("Search for an Organization by name or acronym."),
            field = [ "name",
                      "acronym",
                    ]
            )
        ),
        advanced = (s3base.S3SearchSimpleWidget(
            name = "org_search_text_advanced",
            label = T("Search"),
            comment = T("Search for an Organization by name or acronym"),
            field = [ "name",
                      "acronym",
                    ]
            ),
            s3base.S3SearchOptionsWidget(
                name = "org_search_type",
                label = T("Type"),
                field = ["type"],
                cols = 2
            ),
            s3base.S3SearchOptionsWidget(
                name = "org_search_sector",
                label = T("Sector"),
                field = ["sector_id"],
                represent = "%(name)s",
                cols = 2
            ),
            # Doesn't work on all versions of gluon/sqlhtml.py
            s3base.S3SearchOptionsWidget(
                name = "org_search_home_country",
                label = T("Home Country"),
                field = ["country"],
                cols = 3
            ),
        )
    )

configure(tablename,
                search_method=organisation_search)

# -----------------------------------------------------------------------------
def organisation_duplicate(job):
    """
      UNUSED
      This callback will be called when importing organisation records.
      It will look to see if the record being imported is a duplicate.

      @param job: An S3ImportJob object which includes all the details
                  of the record being imported

      If the record is a duplicate then it will set the job method to update

      Rules for finding a duplicate:
       - Look for a record with the same name, ignoring case
       - and the same location, if provided
    """
    # ignore this processing if the id is set
    if job.id:
        return
    if job.tablename == "org_organisation":
        table = job.table
        name = "name" in job.data and job.data.name
        #query = table.name.lower().like('%%%s%%' % name.lower()) or
        #        table.acronym.lower().like('%%%s%%' % name.lower())
        if "location_id" in job.data:
            location_id = job.data.location_id
            query = query & \
                 (table.location_id == location_id)
        if "location_id" in job.data:
            location_id = job.data.location_id
            query = query & \
                 (table.location_id == location_id)

        _duplicate = db(query).select(table.id,
                                      limitby=(0, 1)).first()
        if _duplicate:
            job.id = _duplicate.id
            job.data.id = _duplicate.id
            job.method = job.METHOD.UPDATE

#configure(tablename,
#                resolve=organisation_duplicate)

# -----------------------------------------------------------------------------
def organisation_rheader(r, tabs=[]):
    """ Organization page headers """

    if r.representation == "html":

        if r.record is None:
            # List or Create form: rheader makes no sense here
            return None

        rheader_tabs = s3_rheader_tabs(r, tabs)

        organisation = r.record
        if organisation.sector_id:
            _sectors = org_sector_represent(organisation.sector_id)
        else:
            _sectors = None

        try:
            _type = organisation_type_opts[organisation.type]
        except KeyError:
            _type = None

        if deployment_settings.get_ui_cluster():
            sector_label = T("Cluster(s)")
        else:
            sector_label = T("Sector(s)")

        rheader = DIV(TABLE(
            TR(
                TH("%s: " % T("Organization")),
                organisation.name,
                TH("%s: " % T("Has Volunteers?")),
                T("Yes") if organisation.has_vols else T("No"),
                TH("%s: " % T("Donates Resources?")),
                T("Yes") if organisation.has_items else T("No"),
                #TH("%s: " % sector_label),
                #_sectors
                ),
            TR(
                #TH(A(T("Edit Organization"),
                #    _href=URL(c="org", f="organisation",
                              #args=[r.id, "update"],
                              #vars={"_next": _next})))
                #TH("%s: " % T("Type")),
                #_type,
                )
        ), rheader_tabs)

        return rheader

    return None

# -----------------------------------------------------------------------------
def organisation_controller(organisation_rheader = organisation_rheader,
                            org_prep = None):
    """ RESTful CRUD controller """

    # @LA: Add inv_item directly to Org
    load("inv_inv_item")

    # Tabs
    tabs = [(T("Basic Details"), None),
            (T("Contacts"), "contact"),
            (T("Facilities"), "office"),
           ]

    # Pre-process
    def prep(r):
        if org_prep:
            org_prep(r)
        if r.interactive:
            r.table.country.default = gis.get_default_country("code")
            if r.component_name == "human_resource" and r.component_id:
                # Workaround until widget is fixed:
                pfield = db.hrm_human_resource.person_id
                pfield.widget = None
                pfield.writable = False
            elif r.component_name == "office" and \
               r.method and r.method != "read":
                # Don't want to see in Create forms
                # inc list_create (list_fields over-rides)
                address_hide(r.component.table)
                # Process Base Location
                #configure(r.component.table._tablename,
                #                onaccept=address_onaccept)
            elif r.component_name == "task" and \
                 r.method != "update" and r.method != "read":
                    # Create or ListCreate
                    r.component.table.organisation_id.default = r.id
                    r.component.table.status.writable = False
                    r.component.table.status.readable = False
        return True

    # Set hooks
    response.s3.prep = prep

    rheader = lambda r: organisation_rheader(r, tabs=tabs)
    configure("org_organisation",
                    update_next = URL(f="organisation", args=["[id]"]))
    output = s3_rest_controller("org", "organisation",
                                native=False, rheader=rheader)
    return output

# -----------------------------------------------------------------------------
# Donors are a type of Organization
#
def donor_represent(donor_ids):
    """ Representation of donor record IDs """
    table = db.org_organisation
    if not donor_ids:
        return NONE
    elif isinstance(donor_ids, (list, tuple)):
        query = (table.id.belongs(donor_ids))
        donors = db(query).select(table.name)
        return ", ".join([donor.name for donor in donors])
    else:
        query = (table.id == donor_ids)
        donor = db(query).select(table.name,
                                 limitby=(0, 1)).first()
        return donor and donor.name or NONE

ADD_DONOR = T("Add Donor")
ADD_DONOR_HELP = T("The Donor(s) for this project. Multiple values can be selected by holding down the 'Control' key.")
donor_id = S3ReusableField("donor_id",
                           "list:reference org_organisation",
                           sortby="name",
                           requires = IS_NULL_OR(IS_ONE_OF(db, "org_organisation.id",
                                                           "%(name)s",
                                                           multiple=True,
                                                           filterby="type",
                                                           filter_opts=[4])),
                           represent = donor_represent,
                           label = T("Funding Organization"),
                           comment = DIV(A(ADD_DONOR,
                                           _class="colorbox",
                                           _href=URL(c="org", f="organisation",
                                                     args="create",
                                                     vars=dict(format="popup",
                                                               child="donor_id")),
                                           _target="top",
                                           _title=ADD_DONOR),
                                        DIV( _class="tooltip",
                                             _title="%s|%s" % (ADD_DONOR,
                                                               ADD_DONOR_HELP))),
                           ondelete = "SET NULL")

# =============================================================================
# Site
#
# @ToDo: Rename as Facilities (ICS terminology)
#
# Site is a generic type for any facility (office, hospital, shelter,
# warehouse, etc.) and serves the same purpose as pentity does for person
# entity types:  It provides a common join key name across all types of
# sites, with a unique value for each sites.  This allows other types that
# are useful to any sort of site to have a common way to join to any of
# them.  It's especially useful for component types.
#
org_site_types = auth.org_site_types

tablename = "org_site"
table = super_entity(tablename, "site_id", org_site_types,
                     #Field("code",
                     #      length=10,           # Mayon compatibility
                     #      notnull=True,
                     #      unique=True,
                     #      label=T("Code")),
                     Field("name",
                           length=64,           # Mayon compatibility
                           notnull=True,
                           #unique=True,
                           label=T("Name")),
                     location_id(),
                     organisation_id(),
                     *s3_ownerstamp())

# -----------------------------------------------------------------------------
def shn_site_represent(site_id,
                       default_label="[no label]",
                       show_link = True,
                       address = False):
    """ Represent a facility in option fields or list views """

    site_str = NONE

    if not site_id:
        return site_str

    if isinstance(site_id, Row):
        # Lookup already done by IS_ONE_OF
        site_id = site_id.site_id

    table = db.org_office
    query = (table.site_id == site_id)

    if not address:
        record = db(query).select(table.id,
                                  table.name, limitby=(0, 1)).first()
        if record:
            site_str = record.name
        else:
            site_str = "[%s %s]" % (T("Facility"), site_id)

        if show_link and record:
            c = "org"
            f = "office"
            site_str = A(site_str,
                         _href = URL(c=c, f=f,
                                     args = [record.id],
                                     extension = "" # removes the .aaData extension in paginated views!
                                     ))
    else:
        record = db(query).select(#table.id,
                                  table.name,
                                  table.address,
                                  table.address_2,
                                  table.L3,
                                  table.L1,
                                  table.postcode,
                                  limitby=(0, 1)).first()
        if record:
            if record.address_2:
                address2 = DIV(SPAN(record.address_2 or ""),
                               BR())
            else:
                address2 = ""
            site_str = DIV( SPAN(record.name or ""), BR(),
                            SPAN(record.address or ""), BR(),
                            address2,
                            SPAN(record.L3 or ""), BR(),
                            SPAN(record.L1 or ""), " ",
                            SPAN(record.postcode  or ""),
                            )

    return site_str
response.s3.shn_site_represent = shn_site_represent

# -----------------------------------------------------------------------------
site_id = super_link(db.org_site,
                     #writable = True,
                     #readable = True,
                     label = T("Facility"),
                     default = auth.user.site_id if auth.is_logged_in() else None,
                     represent = shn_site_represent,
                     # Comment these to use a Dropdown & not an Autocomplete
                     widget = S3SiteAutocompleteWidget(),
                     comment = DIV(_class="tooltip",
                                   _title="%s|%s" % (T("Facility"),
                                                     T("Enter some characters to bring up a list of possible matches")))
                    )

# -----------------------------------------------------------------------------
# For the User Profile:
_table_user.organisation_id.represent = organisation_represent
_table_user.organisation_id.comment = DIV(_class="tooltip",
                                          _title="%s|%s|%s" % (T("Organization"),
                                                               T("The default Organization for whom you are acting."),
                                                               T("This setting can only be controlled by the Administrator.")))
_table_user.site_id.represent = shn_site_represent
_table_user.site_id.comment = DIV(_class="tooltip",
                                  _title="%s|%s|%s" % (T("Facility"),
                                                       T("The default Facility for which you are acting."),
                                                       T("This setting can only be controlled by the Administrator.")))

# =============================================================================
# Rooms (for Sites)
# @ToDo: Validate to ensure that rooms are unique per facility
#
tablename = "org_room"
table = define_table(tablename,
                        site_id, # site_id
                        Field("name", length=128, notnull=True),
                        *s3_meta_fields())

# CRUD strings
ADD_ROOM = T("Add Room")
LIST_ROOMS = T("List Rooms")
s3.crud_strings[tablename] = Storage(
    title_create = ADD_ROOM,
    title_display = T("Room Details"),
    title_list = LIST_ROOMS,
    title_update = T("Edit Room"),
    title_search = T("Search Rooms"),
    subtitle_create = T("Add New Room"),
    subtitle_list = T("Rooms"),
    label_list_button = LIST_ROOMS,
    label_create_button = ADD_ROOM,
    label_delete_button = T("Delete Room"),
    msg_record_created = T("Room added"),
    msg_record_modified = T("Room updated"),
    msg_record_deleted = T("Room deleted"),
    msg_list_empty = T("No Rooms currently registered"))

room_comment = DIV(A(ADD_ROOM,
                     _class="colorbox",
                     _href=URL(c="org", f="room",
                               args="create",
                               vars=dict(format="popup")),
                     _target="top",
                     _title=ADD_ROOM),
                   DIV( _class="tooltip",
                        _title="%s|%s" % (ADD_ROOM,
                                          T("Select a Room from the list or click 'Add Room'"))),
                   # Filters Room based on site
                   SCRIPT("""S3FilterFieldChange({
                                 'FilterField':   'site_id',
                                 'Field':         'room_id',
                                 'FieldPrefix':   'org',
                                 'FieldResource': 'room',
                                 });""")
                    )

# Reusable field for other tables to reference
room_id = S3ReusableField("room_id", db.org_room, sortby="name",
                          requires = IS_NULL_OR(IS_ONE_OF(db, "org_room.id", "%(name)s")),
                          represent = lambda id: \
                            (id and [db(db.org_room.id == id).select(db.org_room.name,
                                                                     limitby=(0, 1)).first().name] or [NONE])[0],
                          label = T("Room"),
                          comment = room_comment,
                          ondelete = "SET NULL")

# =============================================================================
# Offices
#
org_office_type_opts = {    # @ToDo: Migrate these to constants: s3.OFFICE_TYPE
    1:T("Headquarters"),
    2:T("Regional"),
    3:T("National"),
    4:T("Field"),
    5:T("Warehouse"),       # Don't change this number, as it affects the Inv module, KML Export stylesheet & OrgAuth
}

ADD_OFFICE = T("Add Facility")
office_comment = DIV(A(ADD_OFFICE,
                       _class="colorbox",
                       _href=URL(c="org", f="office",
                                 args="create",
                                 vars=dict(format="popup")),
                       _target="top",
                       _title=ADD_OFFICE),
                     DIV( _class="tooltip",
                          _title="%s|%s" % (ADD_OFFICE,
                                            T("If you don't see the Facility in the list, you can add a new one by clicking link 'Add Facility'."))))

tablename = "org_office"
table = define_table(tablename,
                        super_link(db.pr_pentity), # pe_id
                        super_link(db.org_site),   # site_id
                        Field("name", notnull=True,
                              length=64,           # Mayon Compatibility
                              label = T("Name")),
                        Field("code",
                              length=10,
                              # Deployments that don't wants office codes can hide them
                              readable=False,
                              writable=False,
                              # Mayon compatibility
                              # @ToDo: Deployment Setting to add validator to make these unique
                              #notnull=True,
                              #unique=True,
                              label=T("Code")),
                        organisation_id(widget = S3OrganisationAutocompleteWidget(default_from_profile = True)),
                        Field("type", "integer", label = T("Type"),
                              readable = False,
                              writable = False,
                              requires = IS_NULL_OR(IS_IN_SET(org_office_type_opts)),
                              represent = lambda opt: \
                                org_office_type_opts.get(opt, UNKNOWN_OPT)),
                        Field("office_id", "reference org_office", # This form of hierarchy may not work on all Databases
                              readable = False,
                              writable = False,
                              label = T("Parent Office"),
                              comment = office_comment),
                        address_building_name(),
                        address_address(),
                        #address_direction(),
                        address_address2(),
                        address_L3(),
                        address_L1(),
                        address_postcode(),
                        location_id(),
                        Field("phone1", label = T("Phone"),
                              requires = IS_NULL_OR(shn_phone_requires)),
                        Field("phone2", label = T("Phone 2"),
                              readable = False,
                              writable = False,
                              requires = IS_NULL_OR(shn_phone_requires)),
                        Field("email", label = T("Email"),
                              readable = False,
                              writable = False,
                              requires = IS_NULL_OR(IS_EMAIL())),
                        Field("fax", label = T("Fax"),
                              readable = False,
                              writable = False,
                              requires = IS_NULL_OR(shn_phone_requires)),
                        # @ToDo: Calculate automatically from org_staff (but still allow manual setting for a quickadd)
                        #Field("international_staff", "integer",
                        #      label = T("# of National Staff"),
                        #      requires = IS_NULL_OR(IS_INT_IN_RANGE(0, 9999))),
                        #Field("national_staff", "integer",
                        #      label = T("# of International Staff"),
                        #      requires = IS_NULL_OR(IS_INT_IN_RANGE(0, 99999))),
                        # @ToDo: Move to Fixed Assets
                        #Field("number_of_vehicles", "integer",
                        #      label = T("# of Vehicles"),
                        #      requires = IS_NULL_OR(IS_INT_IN_RANGE(0, 9999))),
                        #Field("vehicle_types", label = T("Vehicle Types")),
                        #Field("equipment", label = T("Equipment")),
                        Field("obsolete", "boolean",
                              label = T("Obsolete"),
                              readable = False,
                              writable = False,
                              represent = lambda bool: \
                                (bool and [T("Obsolete")] or [NONE])[0],
                              default = False),
                        #document_id(),  # Better to have multiple Documents on a Tab
                        comments(),
                        *s3_meta_fields())

# Field settings
table.office_id.requires = IS_NULL_OR(IS_ONE_OF(db, "org_office.id",
                                                "%(name)s",
                                                filterby = "type",
                                                filter_opts = [1, 2, 3, 4] # All bar '5' (Warehouse)
                                                ))
table.office_id.represent = lambda id: \
    (id and [db(db.org_office.id == id).select(db.org_office.name,
                                               limitby=(0, 1)).first().name] or [NONE])[0]
table.location_id.readable=False
table.location_id.writable=False

if not deployment_settings.get_gis_building_name():
    table.building_name.readable = False

# CRUD strings
LIST_OFFICES = T("List Facilities")
s3.crud_strings[tablename] = Storage(
    title_create = ADD_OFFICE,
    title_display = T("Facility Details"),
    title_list = LIST_OFFICES,
    title_update = T("Edit Facility"),
    title_search = T("Search Facilities"),
    subtitle_create = T("Add New Facility"),
    subtitle_list = T("Facilities"),
    label_list_button = LIST_OFFICES,
    label_create_button = ADD_OFFICE,
    label_delete_button = T("Delete Facility"),
    msg_record_created = T("Facility added"),
    msg_record_modified = T("Facility updated"),
    msg_record_deleted = T("Facility deleted"),
    msg_list_empty = T("No Facilities currently registered"))

# CRUD strings
ADD_WH = T("Add Warehouse")
LIST_WH = T("List Warehouses")
s3_warehouse_crud_strings = Storage(
    title_create = ADD_WH,
    title_display = T("Warehouse Details"),
    title_list = LIST_WH,
    title_update = T("Edit Warehouse"),
    title_search = T("Search Warehouses"),
    subtitle_create = T("Add New Warehouse"),
    subtitle_list = T("Warehouses"),
    label_list_button = LIST_WH,
    label_create_button = ADD_WH,
    label_delete_button = T("Delete Warehouse"),
    msg_record_created = T("Warehouse added"),
    msg_record_modified = T("Warehouse updated"),
    msg_record_deleted = T("Warehouse deleted"),
    msg_list_empty = T("No Warehouses currently registered"))

# Reusable field for other tables to reference
office_id = S3ReusableField("office_id", db.org_office,
                sortby="default/indexname",
                requires = IS_NULL_OR(IS_ONE_OF(db, "org_office.id", "%(name)s")),
                represent = lambda id: \
                    (id and [db(db.org_office.id == id).select(db.org_office.name,
                                                               limitby=(0, 1)).first().name] or [NONE])[0],
                label = T("Facility"),
                comment = office_comment,
                ondelete = "SET NULL")

# -----------------------------------------------------------------------------
def org_office_duplicate(job):
    """
      This callback will be called when importing office records it will look
      to see if the record being imported is a duplicate.

      @param job: An S3ImportJob object which includes all the details
                  of the record being imported

      If the record is a duplicate then it will set the job method to update

      Rules for finding a duplicate:
       - Look for a record with the same name, ignoring case
       - and the same location, if provided
    """
    # ignore this processing if the id is set
    if job.id:
        return
    if job.tablename == "org_office":
        table = job.table
        if "name" in job.data:
            name = job.data.name
        else:
            return
        #query = table.name.lower().like('%%%s%%' % name.lower())
        query = (table.name.lower() == name.lower())
        if "location_id" in job.data:
            location_id = job.data.location_id
            query = query & \
                 (table.location_id == location_id)

        _duplicate = db(query).select(table.id,
                                      limitby=(0, 1)).first()
        if _duplicate:
            job.id = _duplicate.id
            job.data.id = _duplicate.id
            job.method = job.METHOD.UPDATE

# -----------------------------------------------------------------------------
# Offices as component of Organisations
add_component(table,
                          org_organisation="organisation_id")

configure(tablename,
                super_entity=(db.pr_pentity, db.org_site),
                onvalidation=address_onvalidation,
                resolve=org_office_duplicate,
                orderby = table.name,
                list_fields=[ "id",
                              "name",
                              "organisation_id",   # Filtered in Component views
                              #"type",
                              #"L0",
                              #"L1",
                              #"L2",
                              "L3",
                              #"L4",
                              "phone1",
                              #"email"
                            ])

# -----------------------------------------------------------------------------
def office_rheader(r, tabs=[]):

    """ Office/Warehouse page headers """

    if r.representation == "html":

        tablename, record = s3_rheader_resource(r)
        if tablename == "org_office" and record:
            office = record

            tabs = [(T("Basic Details"), None),
                    #(T("Contact Data"), "contact"),
                    ]
            if has_module("hrm"):
                tabs.append((T("Staff"), "human_resource"))
            try:
                tabs = tabs + response.s3.req_tabs(r)
            except:
                pass
            try:
                tabs = tabs + response.s3.inv_tabs(r)
            except:
                pass

            rheader_tabs = s3_rheader_tabs(r, tabs)

            table = db.org_organisation
            query = (table.id == office.organisation_id)
            organisation = db(query).select(table.name,
                                            limitby=(0, 1)).first()
            if organisation:
                org_name = organisation.name
            else:
                org_name = None

            rheader = DIV(TABLE(
                          TR(
                             TH("%s: " % T("Name")),
                             office.name,
                             TH("%s: " % T("Type")),
                             org_office_type_opts.get(office.type,
                                                      UNKNOWN_OPT),
                             ),
                          TR(
                             TH("%s: " % T("Organization")),
                             org_name or NONE,
                             TH("%s: " % T("Location")),
                             gis_location_represent(office.location_id),
                             ),
                          TR(
                             TH("%s: " % T("Email")),
                             office.email or NONE,
                             TH("%s: " % T("Telephone")),
                             office.phone1 or NONE,
                             ),
                          #TR(TH(A(T("Edit Office"),
                          #        _href=URL(c="org", f="office",
                          #                  args=[r.id, "update"],
                          #                  vars={"_next": _next})))
                          #   )
                              ),
                          rheader_tabs)

            if r.component and r.component.name == "req":
                # Inject the helptext script
                rheader.append(response.s3.req_helptext_script)

            return rheader
    return None
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
def office_controller():
    """ RESTful CRUD controller """

    tablename = "org_office"
    table = db[tablename]

    # Load Models to add tabs
    if has_module("inv"):
        load("inv_inv_item")
    elif has_module("req"):
        # (gets loaded by Inv if available)
        load("req_req")

    if isinstance(request.vars.organisation_id, list):
        request.vars.organisation_id = request.vars.organisation_id[0]

    office_search = s3base.S3Search(
        advanced=(s3base.S3SearchSimpleWidget(
                    name="office_search_text",
                    label=T("Search"),
                    comment=T("Search for office by text."),
                    field=["name", "comments", "email"]
                  ),
                  s3base.S3SearchOptionsWidget(
                    name="office_search_org",
                    label=T("Organization"),
                    comment=T("Search for office by organization."),
                    field=["organisation_id"],
                    represent ="%(name)s",
                    cols = 3
                  ),
                  s3base.S3SearchLocationHierarchyWidget(
                    gis,
                    name="office_search_location",
                    comment=T("Search for office by location."),
                    represent ="%(name)s",
                    cols = 3
                  ),
                  s3base.S3SearchLocationWidget(
                    name="office_search_map",
                    label=T("Map"),
                  ),
        ))
    configure(tablename,
                    search_method = office_search)

    # Pre-processor
    def prep(r):
        table = r.table
        if r.record and r.record.type == 5: # 5 = Warehouse
            s3.crud_strings[tablename] = s3_warehouse_crud_strings

        if r.representation == "popup":
            organisation = r.vars.organisation_id or \
                           session.s3.organisation_id or ""
            if organisation:
                table.organisation_id.default = organisation

        elif r.representation == "plain":
            # Map popups want less clutter
            table.obsolete.readable = False


        if r.record and has_module("hrm"):
            # Cascade the organisation_id from the office to the staff
            hrm_table = db.hrm_human_resource
            hrm_table.organisation_id.default = r.record.organisation_id
            hrm_table.organisation_id.writable = False

        if r.interactive:
            if r.method == "create":
                table.obsolete.readable = table.obsolete.writable = False
                if r.vars.organisation_id and r.vars.organisation_id != "None":
                    table.organisation_id.default = r.vars.organisation_id

            if r.method and r.method != "read":
                # Don't want to see in Create forms
                # inc list_create (list_fields over-rides)
                r.table.obsolete.writable = False
                r.table.obsolete.readable = False
                address_hide(table)

            if r.component:
                if r.component.name == "inv_item" or \
                   r.component.name == "recv" or \
                   r.component.name == "send":
                    # Filter out items which are already in this inventory
                    response.s3.inv_prep(r)
                elif r.component.name == "human_resource":
                    # Filter out people which are already staff for this office
                    s3_filter_staff(r)
                    # Cascade the organisation_id from the office to the staff
                    hrm_table.organisation_id.default = r.record.organisation_id
                    hrm_table.organisation_id.writable = False

                elif r.component.name == "req":
                    if r.method != "update" and r.method != "read":
                        # Hide fields which don't make sense in a Create form
                        # inc list_create (list_fields over-rides)
                        response.s3.req_create_form_mods()

        return True
    response.s3.prep = prep

    rheader = office_rheader

    return s3_rest_controller("org", "office", rheader=rheader)

# =============================================================================
# Domain table
#
# When users register their email address is checked against this list.
# If the Domain matches, then they are automatically assigned to the
# Organization.
# If there is no Approvals email then the user is automatically approved.
# If there is an Approvals email then the approval request goes to this
# address
# If a user registers for an Organization & the domain doesn't match (or
# isn't listed) then the approver gets the request
tablename = "auth_organisation"

if deployment_settings.get_auth_registration_requests_organisation():
    ORG_HELP = T("If this field is populated then a user who specifies this Organization when signing up will be assigned as a Staff of this Organization unless their domain doesn't match the domain field.")
else:
    ORG_HELP = T("If this field is populated then a user with the Domain specified will automatically be assigned as a Staff of this Organization")

DOMAIN_HELP = T("If a user verifies that they own an Email Address with this domain, the Approver field is used to determine whether & by whom further approval is required.")
APPROVER_HELP = T("The Email Address to which approval requests are sent (normally this would be a Group mail rather than an individual). If the field is blank then requests are approved automatically if the domain matches.")

table = define_table(tablename,
                        organisation_id(
                              comment=DIV(_class="tooltip",
                                          _title="%s|%s" % (T("Organization"),
                                                            ORG_HELP))),
                        Field("domain",
                              label=T("Domain"),
                              comment=DIV(_class="tooltip",
                                          _title="%s|%s" % (T("Domain"),
                                                            DOMAIN_HELP))),
                        Field("approver",
                              label=T("Approver"),
                              requires=IS_NULL_OR(IS_EMAIL()),
                              comment=DIV(_class="tooltip",
                                          _title="%s|%s" % (T("Approver"),
                                                            APPROVER_HELP))),
                        comments(),
                        *s3_meta_fields())

# =============================================================================
# Organisation Contact Table
tablename = "org_contact"
table = define_table(tablename,
                        organisation_id(
                              comment=DIV(_class="tooltip",
                                          _title="%s|%s" % (T("Organization"),
                                                            ORG_HELP))),
                        Field("focal_point",
                              "boolean",
                              label = T("Point of Contact"),
                              represent = lambda focal_point: T("Yes") if focal_point else T("No")),
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
                        Field("email", 
                              notnull=True, 
                              label= T("Email"),
                              requires = IS_EMAIL(error_message='Enter a valid email!')),
                        Field("work_phone", 
                              notnull=True, 
                              label= T("Work Number")),
                        Field("mobile_phone", 
                              label= T("Cell Phone Number")),
                        *s3_meta_fields())

# CRUD strings
s3.crud_strings[tablename] = Storage(
    title_create = T("Add Contact"),
    title_display = T("Contact Details"),
    title_list = T("List Contacts"),
    title_update = T("Edit Contact"),
    title_search = T("Search Contacts"),
    subtitle_create = T("Add New Contact"),
    subtitle_list = T("Contacts"),
    label_list_button = T("List Contact"),
    label_create_button = T("Add Contact"),
    label_delete_button = T("Delete Contact"),
    msg_record_created = T("Contact added"),
    msg_record_modified = T("Contact updated"),
    msg_record_deleted = T("Contact deleted"),
    msg_list_empty = T("No Contacts currently registered"))

# -----------------------------------------------------------------------------
# Contacts as component of Organisations
add_component(table,
                          org_organisation="organisation_id")

# END =========================================================================
