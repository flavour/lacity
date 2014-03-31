# -*- coding: utf-8 -*-

"""
    Organization Registry - Controllers

    @author: Fran Boon
    @author: Michael Howden
"""

module = request.controller
resourcename = request.function

if not deployment_settings.has_module(module):
    raise HTTP(404, body="Module disabled: %s" % module)

# Options Menu (available in all Functions" Views)
shn_menu(module)

# =============================================================================
def index():
    """ Module's Home Page """

    module_name = deployment_settings.modules[module].name_nice
    response.title = module_name
    return dict(module_name=module_name)

# =============================================================================
def sector():
    """ RESTful CRUD controller """

    #tablename = "%s_%s" % (module, resourcename)
    #table = db[tablename]

    return s3_rest_controller(module, resourcename)

# -----------------------------------------------------------------------------
def subsector():
    """ RESTful CRUD controller """

    #tablename = "%s_%s" % (module, resourcename)
    #table = db[tablename]

    return s3_rest_controller(module, resourcename)

# =============================================================================
def site():
    """ RESTful CRUD controller """
    return s3_rest_controller(module, resourcename)

# -----------------------------------------------------------------------------
def site_org_json():

    table = db.org_site
    otable = db.org_organisation
    response.headers["Content-Type"] = "application/json"
    #db.req_commit.date.represent = lambda dt: dt[:10]
    query = (table.site_id == request.args[0]) & \
            (table.organisation_id == otable.id)
    records = db(query).select(otable.id,
                               otable.name)
    return records.json()

# =============================================================================
def organisation():
    """ RESTful CRUD controller """

    # Defined in the Model for use from Multiple Controllers for unified menus
    #return response.s3.organisation_controller()
    return organisation_controller()

# -----------------------------------------------------------------------------
def organisation_list_represent(l):
    if l:
        max = 4
        if len(l) > max:
            count = 1
            for x in l:
                if count == 1:
                    output = organisation_represent(x)
                elif count > max:
                    return "%s, etc" % output
                else:
                    output = "%s, %s" % (output, organisation_represent(x))
                count += 1
        else:
            return ", ".join([organisation_represent(x) for x in l])
    else:
        return NONE

# =============================================================================
def office():
    """ RESTful CRUD controller """

    # Defined in the Model for use from Multiple Controllers for unified menus
    #return response.s3.office_controller()
    return office_controller()

# =============================================================================
def person():
    """ Person controller for AddPersonWidget """

    def prep(r):
        if r.representation != "s3json":
            # Do not serve other representations here
            return False
        else:
            s3mgr.show_ids = True
        return True
    response.s3.prep = prep

    return s3_rest_controller("pr", "person")

# =============================================================================
def room():
    """ RESTful CRUD controller """

    return s3_rest_controller(module, resourcename)

# =============================================================================
def incoming():
    """ Incoming Shipments """

    s3mgr.load("inv_inv_item")
    return response.s3.inv_incoming()

# =============================================================================
def req_match():
    """ Match Requests """

    s3mgr.load("req_req")
    return response.s3.req_match()

# =============================================================================
def donor():
    """ RESTful CRUD controller """

    tablename = "org_donor"
    table = db[tablename]

    tablename = "org_donor"
    s3.crud_strings[tablename] = Storage(
        title_create = ADD_DONOR,
        title_display = T("Donor Details"),
        title_list = T("Donors Report"),
        title_update = T("Edit Donor"),
        title_search = T("Search Donors"),
        subtitle_create = T("Add New Donor"),
        subtitle_list = T("Donors"),
        label_list_button = T("List Donors"),
        label_create_button = ADD_DONOR,
        label_delete_button = T("Delete Donor"),
        msg_record_created = T("Donor added"),
        msg_record_modified = T("Donor updated"),
        msg_record_deleted = T("Donor deleted"),
        msg_list_empty = T("No Donors currently registered"))

    s3mgr.configure(tablename, listadd=False)
    output = s3_rest_controller(module, resourcename)

    return output


# =============================================================================
def add_site_inline():
    """ Form to be pulled in by AJAX by the S3AddObjectWidget """
    formstyle = s3_formstyle
    field_name = field.name
    
    # Set up fields
    org_office = db.org_office
    
    field_names = [
        "type",
        "name",
        "address",
        "address_2",
        "L3",
        "L1",
        "postcode",
        "phone1",
    ]
    fields = []
    for field_name in field_names:
        fields.append(getattr(org_office, field_name))
    
    labels, required = s3_mark_required(fields)
    if required:
        response.s3.has_required = True

    form = SQLFORM.factory(table_name="org_office",
                           labels=labels,
                           formstyle=formstyle,
                           separator = "",
                           *fields)
    
    # change submit button text
    submit_line = form[0][-1][0]
    submit_button = submit_line[0]
    submit_button.attributes["_value"] = T("Save")

    # add cancel and reset buttons
    submit_line.append(
        INPUT(_type="button", _value=T("Cancel"), _onclick="close_iframe()")
    )
    submit_line.append(
        INPUT(_type="reset", _value=T("Clear"))
    )

    # JavaScript
    def add_script(script_name):
        response.s3.scripts.append(
            "%s/%s" % (response.s3.script_dir, script_name)
        )
    
    result = dict(
        form = TAG[""](
            # to stop some browsers appying a default table style to unstyled tables
            XML("""<style type="text/css">table { font-size:inherit; }</style>"""),
            form
        ),
        created_object_id = None,
        created_object_representation = "",
        errors = form.errors
    )
    
    accepted = form.accepts(request.vars)#, session):
    # more validation, don't let other validation errors upset this, 
    # as the user wants to see all errors in one go
    def var(name):
        return request.vars.get(name, None)
    def check_request_var_matches_value_if_given(var_name, value):
        if var(var_name):
            if var(var_name) != value:
                if not form.errors.has_key(var_name):
                    form.errors[var_name] = (
                        T("There is a existing record, but the %(property)s is different. "
                        "(Clearing this field allows use of the existing record)")
                    ) % dict(
                        property = var_name.replace("_", " ")
                    )
    def existing(*query):
        return db(*query).select().first()
    # look for an office with the same name
    name = var("name")
    if name:
        existing_office = existing(
            org_office.name == name
        )
        if existing_office is not None:
            for field_name in field_names:
                check_request_var_matches_value_if_given(
                    field_name,
                    getattr(existing_office, field_name)
                )
    else:
        existing_office = None
    if accepted:
        # create objects as necessary
        if form.errors:
            response.flash = "form is invalid"
        else:
            if existing_office is not None:
                result.update(
                    created_object_id = existing_office.id,
                    created_object_representation = existing_office.name
                )
                # nothing needs adding?            
            else:
                created_office = db.org_office.insert(
                    **dict(
                        (field_name, var(field_name)) for field_name in field_names
                    )
                )
                db.commit()
                result.update(
                    created_object_id = created_office.id,
                    created_object_representation = created_office.name
                )
            response.flash = T("form accepted")

    result["vars"] = form.vars
    response.view="inner_form.html"
    return result

# END =========================================================================
