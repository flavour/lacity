# -*- coding: utf-8 -*-

"""
    Supply

    @author: Michael Howden (michael@sahanafoundation.org)
    @date-created: 2010-08-16

    Generic Supply functionality such as catalogs and items that are used across multiple applications
"""

module = request.controller
resourcename = request.function

if not (deployment_settings.has_module("inv") or deployment_settings.has_module("asset")):
    raise HTTP(404, body="Module disabled: %s" % module)

shn_menu(module)

# Load Models
s3mgr.load("supply_item")

# =============================================================================
def index():
    """
        Application Home page
        @todo - custom View
    """

    module_name = deployment_settings.modules[module].name_nice
    response.title = module_name
    return dict(module_name=module_name)

# -----------------------------------------------------------------------------
def catalog():
    """ RESTful CRUD controller """

    return s3_rest_controller(module, resourcename, rheader=catalog_rheader)

# -----------------------------------------------------------------------------
def catalog_rheader(r):

    """ Resource Header for Catalogs """

    if r.representation == "html":
        catalog = r.record
        if catalog:
            tabs = [
                    (T("Edit Details"), None),
                    (T("Categories"), "item_category"),
                    (T("Items"), "catalog_item"),
                   ]
            rheader_tabs = s3_rheader_tabs(r, tabs)
            rheader = DIV(TABLE(TR( TH("%s: " % T("Name")), catalog.name,
                                  ),
                                TR( TH("%s: " % T("Organisation")), 
                                    organisation_represent(catalog.organisation_id),
                                  ),
                               ),
                          rheader_tabs
                         )
            return rheader
    return None


# =============================================================================
def item_category():
    """ RESTful CRUD controller """

    return s3_rest_controller(module, resourcename)

# -----------------------------------------------------------------------------
def item_pack():
    """ RESTful CRUD controller """

    tablename = "%s_%s" % (module, resourcename)

    s3mgr.configure(tablename,
                    listadd=False)
    return s3_rest_controller(module, resourcename)

# -----------------------------------------------------------------------------
def brand():
    """ RESTful CRUD controller """

    return s3_rest_controller(module, resourcename)

# =============================================================================
def item():
    """ RESTful CRUD controller """
    itable = db.supply_item
    if "item_category_id" in request.vars:
        itable.item_category_id.default = request.vars.item_category_id
        itable.item_category_id.writable = False

    # LA: Hide Extra Item Fields
    itable.code.readable = itable.code.writable = False
    itable.brand_id.readable = itable.brand_id.writable = False
    itable.model.readable = itable.model.writable = False
    itable.year.readable = itable.year.writable = False
    itable.weight.readable = itable.weight.writable = False
    itable.length.readable = itable.length.writable = False
    itable.width.readable = itable.width.writable = False
    itable.height.readable = itable.height.writable = False
    itable.volume.readable = itable.volume.writable = False
        
    # Sort Alphabetically for the AJAX-pulled dropdown
    configure("supply_item",
              orderby=itable.name)
    
    # Separate Goods, Services and Facilities
    ctable = db.supply_item_category

    query = (ctable.code == "FACILITY")
    record = db(query).select(ctable.id,
                                       limitby = (0, 1),
                                       cache = gis.cache).first()
    if record:
        facility_cat_id = record.id
    else:
        facility_cat_id = None
        
    query = (ctable.code == "SERVICES")
    record = db(query).select(ctable.id,
                                       limitby = (0, 1),
                                       cache = gis.cache).first()
    if record:
        service_cat_id = record.id
    else:
        service_cat_id = None

    item_type = request.vars.item
    if item_type == "goods":
        ADD_GOODS = T("Add Goods")
        LIST_GOODS = T("List Goods")
        s3.crud_strings["supply_item"] = Storage(
            title_create = ADD_GOODS,
            title_display = T("Good Details"),
            title_list = LIST_GOODS,
            title_update = T("Edit Goods"),
            title_search = T("Search Goods"),
            subtitle_create = ADD_GOODS,
            subtitle_list = T("Donate Goods"),
            label_list_button = LIST_GOODS,
            label_create_button = ADD_GOODS,
            label_delete_button = T("Remove Goods"),
            msg_record_created = T("Goods Added"),
            msg_record_modified = T("Goods updated"),
            msg_record_deleted = T("Goods removed"),
            msg_list_empty = T("No Goods for this Corporation"))
        
        query = (itable.item_category_id != facility_cat_id) & \
                (itable.item_category_id != service_cat_id)
                
        itable.item_category_id.requires = IS_NULL_OR(IS_ONE_OF(db,
                                            "supply_item_category.id",
                                            "%(name)s",
                                            not_filterby = "id",
                                            not_filter_opts = [facility_cat_id, service_cat_id],
                                            sort=True))
    elif item_type in ["services", "facilities"]:
        if item_type == "services":
            ADD_SERVICE = T("Add Service")
            LIST_SERVICES = T("List Services")
            s3.crud_strings["supply_item"] = Storage(
                title_create = ADD_SERVICE,
                title_display = T("Service Details"),
                title_list = LIST_SERVICES,
                title_update = T("Edit Service"),
                title_search = T("Search Services"),
                subtitle_create = ADD_SERVICE,
                subtitle_list = T("Donate Services"),
                label_list_button = LIST_SERVICES,
                label_create_button = ADD_SERVICE,
                label_delete_button = T("Remove Service"),
                msg_record_created = T("Service Added"),
                msg_record_modified = T("Service updated"),
                msg_record_deleted = T("Service removed"),
                msg_list_empty = T("No Services for this Corporation"))

            item_category_filter = service_cat_id
            itable.um.label = T("Unit of Time")
            itable.um.default = "hour"
            db.supply_item_pack.name.label = T("Unit of Time")

        elif item_type == "facilities":
            ADD_FACILITY = T("Add Facility")
            LIST_FACILITYS = T("List Facilities")
            s3.crud_strings["supply_item"] = Storage(
                title_create = ADD_FACILITY,
                title_display = T("Facility Details"),
                title_list = LIST_FACILITYS,
                title_update = T("Edit Facility"),
                title_search = T("Search Facilities"),
                subtitle_create = ADD_FACILITY,
                subtitle_list = T("Donate Facilities"),
                label_list_button = LIST_FACILITYS,
                label_create_button = ADD_FACILITY,
                label_delete_button = T("Remove Facility"),
                msg_record_created = T("Facility Added"),
                msg_record_modified = T("Facility updated"),
                msg_record_deleted = T("Facility removed"),
                msg_list_empty = T("No Facilities for this Corporation"))

            item_category_filter = facility_cat_id
            itable.um.readable = itable.um.writable = False

        itable.item_category_id.readable = itable.item_category_id.writable = False
        itable.item_category_id.default = item_category_filter

        query = (itable.item_category_id == item_category_filter)

    s3.filter = query

    # Defined in the Model for use from Multiple Controllers for unified menus
    return response.s3.supply_item_controller()

# =============================================================================
def catalog_item():
    """ RESTful CRUD controller """

    return s3_rest_controller(module, resourcename)

# END =========================================================================
