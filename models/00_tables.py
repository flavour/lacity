# -*- coding: utf-8 -*-

"""
    Global tables and re-usable fields
"""

# =============================================================================
# Import S3 meta fields into global namespace
#
exec("from applications.%s.modules.s3.s3fields import *" % request.application)
# Faster for Production (where app-name won't change):
#from applications.eden.modules.s3.s3fields import *

# =============================================================================
# Representations for Auth Users & Groups
def s3_user_represent(id):

    table = db.auth_user
    user = db(table.id == id).select(table.email,
                                     limitby=(0, 1),
                                     cache=(cache.ram, 10)).first()
    if user:
        return user.email
    return None

def s3_role_represent(id):

    table = db.auth_group
    role = db(table.id == id).select(table.role,
                                     limitby=(0, 1),
                                     cache=(cache.ram, 10)).first()
    if role:
        return role.role
    return None

# =============================================================================
# Record authorship meta-fields

# Author of a record
s3_meta_created_by = S3ReusableField("created_by", db.auth_user,
                                     readable=False,
                                     writable=False,
                                     requires=None,
                                     default=session.auth.user.id
                                                if auth.is_logged_in()
                                                else None,
                                     represent=s3_user_represent,
                                     ondelete="RESTRICT")

# Last author of a record
s3_meta_modified_by = S3ReusableField("modified_by", db.auth_user,
                                      readable=False,
                                      writable=False,
                                      requires=None,
                                      default=session.auth.user.id
                                                if auth.is_logged_in()
                                                else None,
                                      update=session.auth.user.id
                                                if auth.is_logged_in()
                                                else None,
                                      represent=s3_user_represent,
                                      ondelete="RESTRICT")

def s3_authorstamp():
    return (s3_meta_created_by(),
            s3_meta_modified_by())

# =============================================================================
# Record ownership meta-fields

# Individual user who owns the record
s3_meta_owned_by_user = S3ReusableField("owned_by_user", db.auth_user,
                                        readable=False,
                                        writable=False,
                                        requires=None,
                                        default=session.auth.user.id
                                                    if auth.is_logged_in()
                                                    else None,
                                        represent=lambda id: \
                                            id and s3_user_represent(id) or UNKNOWN_OPT,
                                        ondelete="RESTRICT")

# Role of users who collectively own the record
s3_meta_owned_by_role = S3ReusableField("owned_by_role", "integer",
                                        readable=False,
                                        writable=False,
                                        requires=None,
                                        default=None,
                                        represent=s3_role_represent)

# Role of the Organisation the record belongs to
s3_meta_owned_by_organisation = S3ReusableField("owned_by_organisation", "integer",
                                                readable=False,
                                                writable=False,
                                                requires=None,
                                                default=None,
                                                represent=s3_role_represent)

# Role of the Facility the record belongs to
s3_meta_owned_by_facility = S3ReusableField("owned_by_facility", "integer",
                                            readable=False,
                                            writable=False,
                                            requires=None,
                                            default=None,
                                            represent=s3_role_represent)

def s3_ownerstamp():
    return (s3_meta_owned_by_user(),
            s3_meta_owned_by_role(),
            s3_meta_owned_by_organisation(),
            s3_meta_owned_by_facility())

# =============================================================================
# Common meta-fields

def s3_meta_fields():

    fields = (s3_meta_uuid(),
              s3_meta_mci(),
              s3_meta_deletion_status(),
              s3_meta_deletion_fk(),
              s3_meta_created_on(),
              s3_meta_modified_on(),
              s3_meta_created_by(),
              s3_meta_modified_by(),
              s3_meta_owned_by_user(),
              s3_meta_owned_by_role(),
              s3_meta_owned_by_organisation(),
              s3_meta_owned_by_facility())

    return fields

# =============================================================================
s3.all_meta_field_names = [field.name for field in
    [s3_meta_uuid(),
     s3_meta_mci(),
     s3_meta_deletion_status(),
     s3_meta_deletion_fk(),
     s3_meta_created_on(),
     s3_meta_modified_on(),
     s3_meta_created_by(),
     s3_meta_modified_by(),
     s3_meta_owned_by_user(),
     s3_meta_owned_by_role()
    ]]

# =============================================================================
# Reusable field for scheduler task links
#
scheduler_task_id = S3ReusableField("scheduler_task_id",
                                    "reference %s" % s3base.S3Task.TASK_TABLENAME,
                                    ondelete="CASCADE")

# =============================================================================
# Reusable roles fields for map layer permissions management (GIS)

role_required = S3ReusableField("role_required", db.auth_group,
                                sortby="role",
                                requires = IS_NULL_OR(IS_ONE_OF(db,
                                                                "auth_group.id",
                                                                "%(role)s",
                                                                zero=T("Public"))),
                                widget = S3AutocompleteWidget(
                                                              "auth",
                                                              "group",
                                                              fieldname="role"),
                                represent = s3_role_represent,
                                label = T("Role Required"),
                                comment = DIV(_class="tooltip",
                                              _title="%s|%s" % (T("Role Required"),
                                                                T("If this record should be restricted then select which role is required to access the record here."))),
                                ondelete = "RESTRICT")

roles_permitted = S3ReusableField("roles_permitted", db.auth_group,
                                  sortby="role",
                                  requires = IS_NULL_OR(IS_ONE_OF(db,
                                                                  "auth_group.id",
                                                                  "%(role)s",
                                                                  multiple=True)),
                                  # @ToDo
                                  #widget = S3CheckboxesWidget(db,
                                  #                            lookup_table_name = "auth_group",
                                  #                            lookup_field_name = "role",
                                  #                            multiple = True),
                                  represent = s3_role_represent,
                                  label = T("Roles Permitted"),
                                  comment = DIV(_class="tooltip",
                                                _title="%s|%s" % (T("Roles Permitted"),
                                                                  T("If this record should be restricted then select which role(s) are permitted to access the record here."))),
                                  ondelete = "RESTRICT")

# =============================================================================
# Other reusable fields

# -----------------------------------------------------------------------------
# Reusable name field to include in other table definitions
name_field = S3ReusableField("name", length=64,
                             label=T("Name"), required=IS_NOT_EMPTY())

# -----------------------------------------------------------------------------
# Reusable comments field to include in other table definitions
comments = S3ReusableField("comments", 
                           "text",
                           length = 800,
                           label = T("Comments"),
                           comment = DIV(_class="tooltip",
                                         _title="%s|%s|%s" % (T("Comments"),
                                                              T("Please use this field to record any additional information, including a history of the record if it is updated."),
                                                              T("800 character limit."))))

# -----------------------------------------------------------------------------
# Reusable currency field to include in other table definitions
#
# @ToDo: Move to a Finance module
#
currency_type_opts = deployment_settings.get_fin_currencies()
default_currency = deployment_settings.get_fin_currency_default()

currency_type = S3ReusableField("currency_type", "string",
                                length = 3,
                                #notnull=True,
                                requires = IS_IN_SET(currency_type_opts.keys(),
                                                     zero=None),
                                default = default_currency,
                                label = T("Currency"),
                                #represent = lambda opt: \
                                #    currency_type_opts.get(opt, UNKNOWN_OPT),
                                readable = deployment_settings.get_fin_currency_readable(),
                                writable = deployment_settings.get_fin_currency_writable())

# =============================================================================
# Addresses
#
# These fields are populated onaccept from location_id
#
# Labels that need gis_config data are set by gis.set_config() calling
# gis.update_gis_config_dependent_options()
#

address_building_name = S3ReusableField("building_name",
                                        #label=T("Street Number"),
                                        label=T("Building Name"),
                                        readable=False,
                                        writable=False
                                        )
address_address = S3ReusableField("address",
                                  #label=T("Street Name"),
                                  label=T("Address 1"),
                                  #label=T("Address"),
                                  #readable=False,
                                  #writable=False
                                  )
# LA fields
#address_direction = S3ReusableField("direction",
#                                    label=T("Street Direction"))
address_address2 = S3ReusableField("address_2",
                                    label=T("Address 2"))
address_postcode = S3ReusableField("postcode",
                                   label=deployment_settings.get_ui_label_postcode(),
                                   #readable=False,
                                   #writable=False
                                   )
address_L4 = S3ReusableField("L4",
                             #label=gis.get_location_hierarchy("L4"),
                             readable=False,
                             writable=False)
address_L3 = S3ReusableField("L3",
                             #label=gis.get_location_hierarchy("L3"),
                             #readable=False,
                             #writable=False
                             )
address_L2 = S3ReusableField("L2",
                             #label=gis.get_location_hierarchy("L2"),
                             readable=False,
                             writable=False)
address_L1 = S3ReusableField("L1",
                             #label=gis.get_location_hierarchy("L1"),
                             #readable=False,
                             #writable=False
                             )
address_L0 = S3ReusableField("L0",
                             label=T("Country"), # L0 Location Name never varies except with a Translation
                             readable=False,
                             writable=False)


def address_fields():
    # return multiple reusable fields
    fields = (
            address_building_name(),
            address_address(),
            address_L4(),
            address_L3(),
            address_L2(),
            address_L1(),
            address_L0(),
            address_postcode(),
           )
    return fields


# Hide Address fields in Create forms
# inc list_create (list_fields over-rides)
def address_hide(table):
    # LA doesn't hide fields
    #table.building_name.readable = False
    #table.address.readable = False
    #table.L4.readable = False
    #table.L3.readable = False
    #table.L2.readable = False
    #table.L1.readable = False
    #table.L0.readable = False
    #table.postcode.readable = False
    return

def address_onvalidation(form):
    """
        Write the Postcode & Street Address fields from the Location
        - used by pr_address, org_office & cr_shelter

        @ToDo: Allow the reverse operation.
        If these fields are populated then create/update the location
    """

    # LA doesn't use this - simple flat hierarchy with directly-editable fields
    return
    if "location_id" in form.vars:
        table = db.gis_location
        # Read Postcode & Street Address
        query = (table.id == form.vars.location_id)
        location = db(query).select(table.addr_street,
                                    table.addr_postcode,
                                    table.name,
                                    table.level,
                                    table.parent,
                                    table.path,
                                    limitby=(0, 1)).first()
        if location:
            form.vars.address = location.addr_street
            form.vars.postcode = location.addr_postcode
            if location.level == "L0":
                form.vars.L0 = location.name
            elif location.level == "L1":
                form.vars.L1 = location.name
                if location.parent:
                    query = (table.id == location.parent)
                    country = db(query).select(table.name,
                                               limitby=(0, 1)).first()
                    if country:
                        form.vars.L0 = country.name
            else:
                if location.level is None:
                    form.vars.building_name = location.name
                # Get Names of ancestors at each level
                gis.get_parent_per_level(form.vars,
                                         form.vars.location_id,
                                         feature=location,
                                         ids=False,
                                         names=True)

def address_update(table, record_id):
    """
        Write the Postcode & Street Address fields from the Location
        - used by asset_asset

        @ToDo: Allow the reverse operation.
        If these fields are populated then create/update the location
    """

    if "location_id" in table:

        locations = db.gis_location
        # Read Postcode & Street Address
        query = (table.id == record_id) & \
                (locations.id == table.location_id)
        location = db(query).select(locations.addr_street,
                                    locations.addr_postcode,
                                    locations.name,
                                    locations.level,
                                    locations.parent,
                                    locations.path,
                                    limitby=(0, 1)).first()
        if location:
            vars = Storage()
            vars.address = location.addr_street
            vars.postcode = location.addr_postcode
            if location.level == "L0":
                vars.L0 = location.name
            elif location.level == "L1":
                vars.L1 = location.name
                if location.parent:
                    query = (locations.id == location.parent)
                    country = db(query).select(locations.name,
                                               limitby=(0, 1)).first()
                    if country:
                        vars.L0 = country.name
            else:
                if location.level is None:
                    vars.building_name = location.name
                # Get Names of ancestors at each level
                gis.get_parent_per_level(vars,
                                         vars.location_id,
                                         feature=location,
                                         ids=False,
                                         names=True)
            # Update record
            db(table.id == record_id).update(**vars)

# =============================================================================
# Default CRUD strings
ADD_RECORD = T("Add Record")
LIST_RECORDS = T("List Records")
s3.crud_strings = Storage(
    title_create = ADD_RECORD,
    title_display = T("Record Details"),
    title_list = LIST_RECORDS,
    title_update = T("Edit Record"),
    title_search = T("Search Records"),
    subtitle_create = T("Add New Record"),
    subtitle_list = T("Available Records"),
    label_list_button = LIST_RECORDS,
    label_create_button = ADD_RECORD,
    label_delete_button = T("Delete Record"),
    msg_record_created = T("Record added"),
    msg_record_modified = T("Record updated"),
    msg_record_deleted = T("Record deleted"),
    msg_list_empty = T("No Records currently available"),
    msg_match = T("Matching Records"),
    msg_no_match = T("No Matching Records"))

# =============================================================================
# Define CRUD strings (NB These apply to all Modules' "settings" too)
crud_strings = s3.crud_strings
ADD_SETTING = T("Add Setting")
LIST_SETTINGS = T("List Settings")
crud_strings["setting"] = Storage(
    title_create = ADD_SETTING,
    title_display = T("Setting Details"),
    title_list = LIST_SETTINGS,
    title_update = T("Edit Setting"),
    title_search = T("Search Settings"),
    subtitle_create = T("Add New Setting"),
    subtitle_list = T("Settings"),
    label_list_button = LIST_SETTINGS,
    label_create_button = ADD_SETTING,
    msg_record_created = T("Setting added"),
    msg_record_modified = T("Setting updated"),
    msg_record_deleted = T("Setting deleted"),
    msg_list_empty = T("No Settings currently defined"))

# Shortcuts
add_component = s3mgr.model.add_component
configure = s3mgr.configure
define_table = db.define_table
has_module = deployment_settings.has_module
load = s3mgr.load
loader = s3mgr.loader
set_method = s3mgr.model.set_method
# =============================================================================

