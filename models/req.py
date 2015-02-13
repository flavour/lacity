# -*- coding: utf-8 -*-

"""
    Request Management

    A module to record requests & commitments for:
     - inventory items
     - people (actually request skills, but commit people)
     - assets
     - other
"""

module = "req"

# -----------------------------------------------------------------------------
# NB Hardcoded in controllers/req.py & models/vol.py
REQ_STATUS_NONE       = 0
REQ_STATUS_PARTIAL    = 1
REQ_STATUS_COMPLETE   = 2

req_status_opts = { REQ_STATUS_NONE:     SPAN(T("None"),
                                              _class = "req_status_none"),
                    REQ_STATUS_PARTIAL:  SPAN(T("Partial"),
                                              _class = "req_status_partial"),
                    REQ_STATUS_COMPLETE: SPAN(T("Complete"),
                                              _class = "req_status_complete")
                   }

# Component definitions should be outside conditional model loads
#add_component("req_req",
#              org_site=super_key(db.org_site),

add_component("req_req", event_event="event_id")

if has_module("doc"):
    add_component("req_document", req_req="req_id")

# Should we have multiple Items/Skills per Request?
multiple_req_items = deployment_settings.get_req_multiple_req_items()

# Request Items as component of Request & Items
add_component("req_req_item",
              req_req=dict(joinby="req_id",
                           multiple=multiple_req_items),
              supply_item="item_id")

# Surplus Items as component of Request & Items
add_component("req_surplus_item",
              req_req=dict(joinby="req_id",
                           multiple=multiple_req_items),
              supply_item="item_id")

# Request Skills as component of Request & Skills
add_component("req_req_skill",
              req_req=dict(joinby="req_id",
                           multiple=multiple_req_items),
              hrm_skill="skill_id")

# Commitment as a component of Requests, Sites & Orgs
add_component("req_commit",
              req_req=dict(joinby="req_id",
                           multiple=False),
              org_site=super_key(db.org_site),
              org_organisation = "donated_by_id")

add_component("req_fulfill",
              req_req=dict(joinby="req_id",
                           multiple=False)
              )


# Commitment Items as component of Commitment
add_component("req_commit_item",
              req_commit="commit_id")

def req_tables():
    """ Load the Request Tables when needed """

    if "req_req" in db.tables:
        return

    module = "req"

    load("supply_item")
    item_category_id = s3.item_category_id
    item_id = s3.item_id
    item_pack_id = s3.item_pack_id
    item_pack_virtualfields = s3.item_pack_virtualfields
    supply_item_represent = s3.item_represent

    load("hrm_skill")
    multi_skill_id = s3.multi_skill_id

    load("event_event")
    event_id = s3.event_id
    incident_id = s3.incident_id

    req_status = S3ReusableField("req_status", "integer",
                                 label = T("Request Status"),
                                 requires = IS_NULL_OR(IS_IN_SET(req_status_opts,
                                                                 zero = None)),
                                 represent = lambda opt: \
                                    req_status_opts.get(opt, UNKNOWN_OPT),
                                 default = REQ_STATUS_NONE,
                                 writable = deployment_settings.get_req_status_writable(),
                                )

    req_priority_opts = {3: T("High"),
                         2: T("Medium"),
                         1: T("Low")
                         }

    req_type_opts = {9 :T("Other"),
                     }

    # Number hardcoded in controller
    req_type_opts[1] = deployment_settings.get_req_type_inv_label()
    req_type_opts[3] = deployment_settings.get_req_type_hrm_label()

    def req_priority_represent(id):
        req_priority_color = {3: "red",
                              2: "darkorange",
                              1: "black"
                              }
        return SPAN(req_priority_opts[id],
                    _style = "color:%s" % req_priority_color[id])

    # -------------------------------------------------------------------------
    def req_hide_quantities(table):
        """
            Hide the Update Quantity Status Fields from Request create forms
        """

        if not deployment_settings.get_req_quantities_writable():
            table.quantity_commit.writable = table.quantity_commit.readable = False
            table.quantity_transit.writable = table.quantity_transit.readable= False
            table.quantity_fulfil.writable = table.quantity_fulfil.readable = False

    # -------------------------------------------------------------------------
    # Requests
    eoc_req_status_opts = {2: T("Pending (Action Required)"), # Red
                           3: T("Pushed to BOC"), # Yellow
                           4: T("Approved (Pushed to BOC)"), # Gray
                           5: T("Cancelled"), # Gray
                           6: T("Cancelled (Pushed to BOC)"), # Gray
                           7: T("Committed"), # Green
                           8: T("Loan"), # Yellow
                           9: T("Fulfilled") # Green
                           }

    eoc_req_status_color = {2: "DarkRed",
                            3: "GoldenRod",
                            4: "DimGray",
                            5: "DimGray",
                            6: "DimGray",
                            7: "DarkGreen",
                            8: "GoldenRod",
                            9: "DarkGreen",
                            }

    def eoc_req_status_represent(opt):
        represent = eoc_req_status_opts.get(opt, NONE)
        color = eoc_req_status_color.get(opt)
        if color:
            represent = SPAN(represent, _style = "font-weight:bold;color:%s;" % color)
        return represent

    tablename = "req_req"
    table = define_table(tablename,
                         Field("status", "integer",
                               default = 2,
                               label = T("EOC Status"),
                               represent = eoc_req_status_represent,
                               requires = IS_IN_SET(eoc_req_status_opts),
                               ),
                         event_id(default = session.s3.event,
                                  empty = False,
                                  ),
                         incident_id(empty = False),
                         Field("type", "integer",
                               default = 1,
                               label = T("Request Type"),
                               represent = lambda opt: \
                                req_type_opts.get(opt, UNKNOWN_OPT),
                               requires = IS_IN_SET(req_type_opts, zero=None),
                               ),
                         Field("request_number", unique = True,
                               label = T("Request Number"),
                               ),
                         Field("priority", "integer",
                               default = 2,
                               label = T("Request Priority"),
                               represent = req_priority_represent,
                               requires = IS_NULL_OR(
                                            IS_IN_SET(req_priority_opts))
                               ),
                         Field("date_required", "datetime",
                               label = T("Date Required"),
                               represent = s3_utc_represent,
                               requires = IS_EMPTY_OR(IS_UTC_DATETIME()),
                                           # Can be done in onvalidation if-required, or we could rely on the widget
                                           #IS_UTC_DATETIME_IN_RANGE(
                                           #  minimum=request.utcnow - datetime.timedelta(days=1),
                                           #  error_message="%s %%(min)s!" %
                                           #      T("Enter a valid future date"))),
                               widget = S3DateTimeWidget(past=0,
                                                            future=8760),  # Hours, so 1 year
                               ),
                         Field("date_required_until", "datetime",
                               label = T("Date Required Until"),
                               represent = s3_utc_represent,
                               requires = IS_EMPTY_OR(IS_UTC_DATETIME()),
                                           #IS_UTC_DATETIME_IN_RANGE(
                                           #  minimum=request.utcnow - datetime.timedelta(days=1),
                                           #  error_message="%s %%(min)s!" %
                                           #      T("Enter a valid future date"))),
                               widget = S3DateTimeWidget(past=0,
                                                         future=8760), # Hours, so 1 year
                               #readable = False,
                               #writable = False
                               ),
                         super_link(db.org_site,
                                    default = auth.user.site_id if auth.is_logged_in() else None,
                                    empty = False,
                                    label = T("Requested For Facility"),
                                    represent = shn_site_represent,
                                    readable = True,
                                    writable = True,
                                    widget = S3SiteAutocompleteWidget(),
                                    ),
                         Field("location",
                               label = T("Neighborhood"),
                               readable = False,
                               writable = False,
                               ),
                         human_resource_id("request_for_id",
                                           #default = s3_logged_in_human_resource()
                                           empty = False,
                                           label = T("Requested For"),
                                           ),
                         Field("purpose", "text", length=300,
                               label = T("Purpose"),
                               requires = IS_NOT_EMPTY(),
                               comment = DIV(_class="tooltip",
                                             _title="%s|%s" % (T("Details"),
                                                               T("300 character limit.")
                                                               ),
                                             )
                               ), # Donations: What will the Items be used for?; People: Task Details
                         Field("date", # DO NOT CHANGE THIS
                               "datetime",
                               default = request.utcnow,
                               label = T("Date Requested"),
                               represent = s3_utc_represent,
                               required = True,
                               requires = IS_EMPTY_OR(IS_UTC_DATETIME()),
                                           #IS_UTC_DATETIME_IN_RANGE(
                                           #  maximum=request.utcnow,
                                           #  error_message="%s %%(max)s!" %
                                           #      T("Enter a valid past date")))],
                               widget = S3DateTimeWidget(past=8760, # Hours, so 1 year
                                                         future=0),
                               ),
                         human_resource_id("requester_id",
                                           default = s3_logged_in_human_resource(),
                                           empty = False,
                                           label = T("Requester"),
                                           comment = T("Person who initially requested this resource")
                                           ),
                         # Not used for LA
                         human_resource_id("assigned_to_id", # This field should be in req_commit, but that complicates the UI
                                           label = T("Assigned To"),
                                           readable = False,
                                           writable = False,
                                           ),
                         human_resource_id("approved_by_id",
                                           empty = False,
                                           label = T("Approved By"),
                                           ),
                         Field("public", "boolean",
                               label = T("Publish to Public Site?"),
                               readable = False,
                               writable = False,
                               ),
                         organisations_id(label = T("Publish to Organizations"),
                                          comment = DIV(_class="tooltip",
                                                        _title="%s|%s" % (T("Publish to Organizations"),
                                                                          T("If you select an Organization(s) here then they will be notified of this request. Organizations will also be able to see any requests publshed to the public site."))),
                                          readable = False,
                                          writable = False,
                                          requires = IS_NULL_OR(IS_ONE_OF(db, "org_organisation.id",
                                                           organisation_represent,
                                                           multiple=True,
                                                           orderby="org_organisation.name",
                                                           filterby="has_vols",
                                                           filter_opts=(True,),
                                                           sort=True)),
                                         ),
                         req_status("commit_status",
                                    label = T("Commit. Status"),
                                    readable = False,
                                    writable = False,
                                    ),
                         req_status("transit_status",
                                    label = T("Transit Status"),
                                    readable = False,
                                    writable = False,
                                    ),
                         req_status("fulfil_status",
                                    label = T("Fulfil. Status"),
                                    readable = False,
                                    writable = False,
                                    ),
                         comments(),
                         Field("cancel", "boolean",
                               default = False,
                               label = T("Cancel"),
                               represent = lambda value: T("Yes") if value else T("No"),
                               ),
                         Field("roster_lead_time", "double",
                               default=2,
                               label = T("Send Volunteer Roster Time"),
                               readable = False,
                               writable = False,   # Only editable via WebEOC
                               ),
                         Field("emailed", "datetime",
                               label = T("Time that Roster was emailed"),
                               represent = s3_utc_represent,
                               readable = False,
                               writable = False,
                               ),
                         *s3_meta_fields())

    # Virtual Field
    class req_virtualfields(dict, object):
        def req_commit_status(self):
            ctable = db.req_commit
            req_id = self.req_req.id
            query = (ctable.req_id == req_id)
            commit = db(query).select(ctable.status,
                                      limitby=(0, 1)).first()
            if commit:
                return ctable.status.represent(commit.status)
            else:
                return None

        def item(self):
            itable = db.req_req_item
            req_id = self.req_req.id
            query = (itable.req_id == req_id)
            item = db(query).select(itable.item,
                                    itable.item_pack,
                                    itable.quantity,
                                    limitby=(0, 1)).first()
            if item:
                return s3.concat_item_pack_quantity(item.item,
                                                             item.item_pack,
                                                             item.quantity)
            else:
                return NONE

        def item_quantity(self):
            req_item_table = db.req_req_item
            req_id = self.req_req.id
            query = (req_item_table.req_id == req_id)
            req_item = db(query).select(req_item_table.quantity,
                                        limitby=(0, 1)).first()
            if req_item:
                return req_item.quantity
            else:
                return None

    table.virtualfields.append(req_virtualfields())

    # @ToDo: Change get_req_show_quantity_transit ->  get_req_show_transit
    if not deployment_settings.get_req_show_quantity_transit():
        table.transit_status.writable = table.transit_status.readable= False

    # CRUD strings
    ADD_REQUEST = T("Make Request")
    LIST_REQUEST = T("List Requests")
    crud_strings[tablename] = Storage(
        title_create = ADD_REQUEST,
        title_display = T("Request Details"),
        title_list = LIST_REQUEST,
        title_update = T("Edit Request"),
        title_search = T("Search Requests"),
        subtitle_create = ADD_REQUEST,
        subtitle_list = T("Requests"),
        label_list_button = LIST_REQUEST,
        label_create_button = ADD_REQUEST,
        label_delete_button = T("Delete Request"),
        msg_record_created = T("Request Added"),
        msg_record_modified = T("Request Updated"),
        msg_record_deleted = T("Request Canceled"),
        msg_list_empty = T("No Requests"))

    # Represent
    def req_represent(id, link = True):
        id = int(id)
        table = db.req_req
        if id:
            query = (table.id == id)
            req = db(query).select(table.date,
                                   table.type,
                                   table.site_id,
                                   limitby=(0, 1)).first()
            if not req:
                return NONE
            req = "%s - %s" % (shn_site_represent(req.site_id,
                                                  show_link = False),
                               req.date)
            if link:
                return A(req,
                         _href = URL(c = "req",
                                     f = "req",
                                     args = [id]),
                         _title = T("Go to Request"))
            else:
                return req
        else:
            return NONE

    # Reusable Field
    req_id = S3ReusableField("req_id", db.req_req, sortby="date",
                             label = T("Request"),
                             ondelete = "CASCADE",
                             represent = req_represent,
                             requires = IS_ONE_OF(db,
                                                  "req_req.id",
                                                  lambda id:
                                                    req_represent(id,
                                                                  False),
                                                  orderby="req_req.date",
                                                  sort=True),
                             )

    #--------------------------------------------------------------------------
    def req_onvalidation(form):

        if "id" not in form.vars:
            # Create form
            # - be strict on dates
            pass
            # date_required = form.vars.date_required
            #if date_required and date_required < request.utcnow - datetime.timedelta(days=1)
            #    form.errors.date_required = "%s %%(min)s!" % T("Enter a valid future date")

        if not form.vars.location:
            # Default to the Zip
            otable = db.org_office
            query = (otable.site_id == form.vars.site_id)
            office = db(query).select(otable.postcode,
                                      limitby=(0, 1)).first()
            if office:
                form.vars.location = office.postcode

    #--------------------------------------------------------------------------
    def req_onaccept(form):
        """
            Configure the next page to go to based on the request type
            When a new request is created:
                Schedule rostermail to run (Vol requests only)
                Add a new Commit record
            When a request is updated:
                Update req_commit.status based on req_req.status
        """

        form_vars = form.vars
        req_id = form_vars.id

        table = db.req_req

        # Read the record details
        record = db(table.id == req_id).select(table.date_required,
                                               table.location,
                                               table.purpose,
                                               table.status,
                                               table.type,
                                               limitby=(0, 1)).first()

        # Configure the next page to go to based on the request type
        tablename = "req_req"
        if "default_type" in request.get_vars:
            type = request.get_vars.default_type
        else:
            type = form_vars.type

        if type is None:
            type = str(record.type)

        controller = request.controller
        if type == "1":
            configure(tablename,
                      create_next = URL(c=controller,
                                        f="req",
                                        args=["[id]", "req_item"]),
                      update_next = URL(c=controller,
                                        f="req",
                                        args=["[id]", "req_item"]))
        elif type == "3":
            configure(tablename,
                      create_next = URL(c=controller,
                                        f="req",
                                        args=["[id]", "req_skill"]),
                      update_next = URL(c=controller,
                                        f="req",
                                        args=["[id]", "req_skill"]))
            if form_vars.date_required:
                # Schedule rostermail to run
                if form_vars.roster_lead_time:
                    lead_time = form_vars.roster_lead_time
                else:
                    lead_time = 2
                lead_time = datetime.timedelta(hours=lead_time)
                mailout_time = form_vars.date_required - lead_time

                current.s3task.schedule_task("vol_rostermail",
                                             args=[form_vars.id],
                                             start_time=mailout_time)
            # Update all the 'Virtual' Fields in the vol_assignment records
            load("vol_assignment")
            atable = db.vol_assignment
            db(atable.req_id == req_id).update(date_required = s3_utc_represent(record.date_required),
                                               location = record.location,
                                               task = record.purpose,
                                               )

        # Automatically update req_commit.status based on req_req.status
        req_status = record.status
        ctable = db.req_commit
        commit_record = db(ctable.req_id == req_id).select(ctable.status,
                                                           limitby=(0,1)
                                                           ).first()
        if commit_record:
            commit_status = commit_record.status
        else:
            # Add New Commit Record
            ctable.insert()
            commit_status = 2 # Pending (Action Required)

        # BOC Receives EOC update on Donation Approval or Cancellation and changes BOC Status
        # BOC Receives EOC update on Donation Cancellation and changes BOC Status
        # BOC Receives EOC Status update on fulfillment and changes BOC Status
        # BOC Receives EOC Status update on return of loan and changes BOC Status
        if (req_status in (4, 6) and  commit_status in (11, 12)) \
        or (req_status == 6 and commit_status == 13) \
        or (req_status == 9 and commit_status == 13) \
        or (req_status == 9 and commit_status == 8):
            # Commit Status -> Pending (Action Required)
            db(ctable.req_id == req_id).update(status = 2)

        # BOC Receives EOC Status on receipt of loan and changes BOC Status
        if req_status == 8 and commit_status == 13:
            # Commit Status -> Loan
            db(ctable.req_id == req_id).update(status = 8)

    # -------------------------------------------------------------------------
    def req_ondelete(form):
        """
            If the selected request was deleted, cancel the volunteers
        """

        if form.vars.type == 3:
            current.s3task.async("vol_req_cancel", [form.vars.id])


    webeoc_is_master = deployment_settings.get_req_webeoc_is_master()
    configure(tablename,
              deletable = not webeoc_is_master,
              editable = not webeoc_is_master,
              insertable = not webeoc_is_master,
              #listadd = False,
              onaccept = req_onaccept,
              onvalidation = req_onvalidation,
              ondelete = req_ondelete,
              # Set in the controller to be varied based on type
              #list_fields = ["id",
              #               "type",
              #               "priority",
              #               "commit_status",
              #               #"transit_status",
              #               "fulfil_status",
              #               "date_required",
              #               "event_id",
              #               "site_id",
              #               (T("Item"), "item"),
              #               (T("Quantity"), "item_quantity"),
              #               #"request_number",
              #               #"date",
              #               #"requester_id",
              #               #"comments",
              #            ]
              )

    #--------------------------------------------------------------------------
    def req_create_form_mods():
        """
            Function to be called from REST prep functions
             - main module & components (sites & events)
        """

        # Hide fields which don't make sense in a Create form
        table = db.req_req
        table.commit_status.readable = table.commit_status.writable = False
        table.transit_status.readable = table.transit_status.writable = False
        table.fulfil_status.readable = table.fulfil_status.writable = False
        table.cancel.readable = table.cancel.writable = False
        table.emailed.readable = table.emailed.writable = False

        return

    # Script to inject into Pages which include Request create forms
    req_help_msg = ""
    req_help_msg_template = T("If the request is for %s, please enter the details on the next screen.")
    types = [T("Resources"),
             T("Staff")
            ]
    message = types.pop(0)
    for type in types:
        message = "%s or %s" % (message, type)
    req_help_msg = req_help_msg_template % message

    req_helptext_script = SCRIPT(
'''$(function(){
 var req_help_msg='%s\\n%s'
 // Provide some default help text in the Details box if empty
 if(!$('#req_req_comments').val()){
  $('#req_req_comments').addClass('default-text').attr({value: req_help_msg}).focus(function(){
   if($(this).val()==req_help_msg){
    // Clear on click if still default
    $(this).val('').removeClass('default-text')
   }
  })
  $('form').submit(function(){
   // Do the normal form-submission tasks
   // @ToDo: Look to have this happen automatically
   // http://forum.jquery.com/topic/multiple-event-handlers-on-form-submit
   // http://api.jquery.com/bind/
   S3ClearNavigateAwayConfirm()
   if($('#req_req_comments').val()==req_help_msg){
    // Default help still showing
    if($('#req_req_type').val()==9){
     // Requests of type 'Other' need this field to be mandatory
     $('#req_req_comments').after('<div id="type__error" class="error" style="display: block;">%s</div>')
     // Reset Navigation protection
     S3SetNavigateAwayConfirm()
     // Move focus to this field
     $('#req_req_comments').focus()
     // Prevent Form save from continuing
     return false
    }else{
     // Clear the default help
     $('#req_req_comments').val('')
     // Allow Form save to continue
     return true
    }
   }else{
    // Allow Form save to continue
    return true
   }
  })
 }
})''' % (T('If the request type is "Other", please enter request details here.'),
         req_help_msg,
         T("Details field is required!"))
        )

    # -------------------------------------------------------------------------
    def req_match():
        """
            Function to be called from controller functions to display all
            requests as a tab for a site.
            @ToDo: Filter out requests from this site
        """

        output = dict()

        # Load Models (for tabs at least)
        #load("inv_inv_item")
        #if has_module("hrm"):
        #    # Load Models (for tabs at least)
        #    load("hrm_skill")

        if "viewing" not in request.vars:
            return output
        else:
            viewing = request.vars.viewing
        if "." in viewing:
            tablename, id = viewing.split(".", 1)
        else:
            return output
        site_id = db[tablename][id].site_id
        s3.actions = [dict(url = URL(c = request.controller,
                                     f = "req",
                                     args = ["[id]","check"],
                                     vars = {"site_id": site_id}
                                     ),
                                    _class = "action-btn",
                                    label = str(T("Check")),
                                    ),
                               dict(url = URL(c = "req",
                                              f = "commit_req",
                                              args = ["[id]"],
                                              vars = {"site_id": site_id}
                                             ),
                                    _class = "action-btn",
                                    label = str(T("Commit")),
                                    ),
                               dict(url = URL(c = "req",
                                              f = "send_req",
                                              args = ["[id]"],
                                              vars = {"site_id": site_id}
                                             ),
                                    _class = "action-btn",
                                    label = str(T("Send")),
                                    )
                               ]

        configure("req_req", insertable=False)
        output = s3_rest_controller("req", "req",
                                    method = "list",
                                    rheader = office_rheader)
        if isinstance(output, dict):
            output["title"] = crud_strings[tablename]["title_display"]

        return output

    # -------------------------------------------------------------------------
    def req_check(r, **attr):
        """
            Check to see if your Inventory can be used to match any open Requests
        """

        # Load Models (for tabs at least)
        #load("inv_inv_item")

        site_id = r.vars.site_id
        site_name = shn_site_represent(site_id, show_link = False)
        output = {}
        output["title"] = T("Check Request")
        output["rheader"] = req_rheader(r, check_page = True)

        stable = db.org_site
        ltable = db.gis_location
        query = (stable.id == site_id ) & \
                (stable.location_id == ltable.id)
        location_r = db(query).select(ltable.lat,
                                      ltable.lon,
                                      limitby=(0, 1)).first()
        query = (stable.id == r.record.site_id ) & \
                (stable.location_id == ltable.id)
        req_location_r = db(query).select(ltable.lat,
                                          ltable.lon,
                                          limitby=(0, 1)).first()
        try:
            distance = gis.greatCircleDistance(location_r.lat, location_r.lon,
                                               req_location_r.lat, req_location_r.lon,)
            output["rheader"][0].append(TR(TH( T("Distance from %s:") % site_name),
                                           TD( T("%.1f km") % distance)
                                           ))
        except:
            pass

        output["subtitle"] = T("Request Resources")

        # Get req_items & inv_items from this site
        table = db.req_req_item
        query = (table.req_id == r.id) & \
                (table.deleted == False)
        req_items = db(query).select(table.id,
                                     table.item_id,
                                     table.quantity,
                                     table.item_pack_id,
                                     table.quantity_commit,
                                     table.quantity_transit,
                                     table.quantity_fulfil)
        #itable = db.inv_inv_item
        #query = (itable.site_id == site_id) & \
        #        (itable.deleted == False)
        #inv_items = db(query).select(itable.item_id,
        #                             itable.quantity,
        #                             itable.item_pack_id)
        #inv_items_dict = inv_items.as_dict(key = "item_id")

        if len(req_items):
            items = TABLE(THEAD(TR(#TH(""),
                                   TH(table.item_id.label),
                                   TH(table.quantity.label),
                                   TH(table.item_pack_id.label),
                                   TH(table.quantity_commit.label),
                                   TH(table.quantity_transit.label),
                                   TH(table.quantity_fulfil.label),
                                   TH(T("Quantity in %s's Inventory") % site_name),
                                   TH(T("Match?"))
                                  )
                                ),
                          _id = "list",
                          _class = "dataTable display")

            for req_item in req_items:
                # Convert inv item quantity to req item quantity
                try:
                    inv_item = Storage(inv_items_dict[req_item.item_id])
                    inv_quantity = inv_item.quantity * \
                                   inv_item.pack_quantity / \
                                   req_item.pack_quantity

                except:
                    inv_quantity = NONE

                if inv_quantity and inv_quantity != NONE:
                    if inv_quantity < req_item.quantity:
                        status = SPAN(T("Partial"), _class = "req_status_partial")
                    else:
                        status = SPAN(T("YES"), _class = "req_status_complete")
                else:
                    status = SPAN(T("NO"), _class = "req_status_none"),

                items.append(TR( #A(req_item.id),
                                 supply_item_represent(req_item.item_id),
                                 req_item.quantity,
                                 s3.item_pack_represent(req_item.item_pack_id),
                                 # This requires an action btn to get the req_id
                                 req_item.quantity_commit,
                                 req_item.quantity_fulfil,
                                 req_item.quantity_transit,
                                 #req_quantity_represent(req_item.quantity_commit, "commit"),
                                 #req_quantity_represent(req_item.quantity_fulfil, "fulfil"),
                                 #req_quantity_represent(req_item.quantity_transit, "transit"),
                                 inv_quantity,
                                 status,
                                )
                            )
                output["items"] = items
                #s3.actions = [req_item_inv_item_btn]
                s3.no_sspag = True # pag won't work
        else:
            output["items"] = crud_strings.req_req_item.msg_list_empty

        response.view = "list.html"
        s3.no_formats = True

        return output

    set_method(module, "req",
               method = "check", action=req_check)

    # -------------------------------------------------------------------------
    def req_quantity_represent(quantity, type):
        # @ToDo: There should be better control of this feature - currently this only works
        #        with req_items which are being matched by commit / send / recv
        if quantity and not deployment_settings.get_req_quantities_writable():
            return TAG[""]( quantity,
                            A(DIV(_class = "quantity %s ajax_more collapsed" % type
                                  ),
                                _href = "#",
                              )
                            )
        else:
            return quantity

    # =========================================================================
    # Request Items
    tablename = "req_req_item"
    quantities_writable = deployment_settings.get_req_quantities_writable()
    table = define_table(tablename,
                         req_id(),
                         Field("item", "text",
                               label = T("Requested Resource"),
                               length = 150,
                               requires = IS_NOT_EMPTY(),
                               comment = DIV(_class="tooltip",
                                             _title="%s|%s" % (T("Requested Resource"),
                                                               T("From WebEOC.")
                                                               ),
                                             )
                               ),
                         Field("item_pack",
                               label = T("Resource Unit")
                               ),
                         Field("specs", "text",
                               label=T("Specifications"),
                               length=350,
                               comment = DIV(_class="tooltip",
                                             _title="%s|%s" % (T("Specifications"),
                                                               T("300 character limit.")
                                                               ),
                                             )
                               ),
                         item_category_id(label = "Look Up Catalog Category",
                                          comment = DIV(_class="tooltip",
                                                _title="%s|%s" % (T("Look Up Catalog Category"),
                                                                  T("Look Up Catalog Category in Give2LA for Resource Requested in WebEOC")
                                                                  ),
                                           ),
                                           ),
                         item_id(label=T("Match To Catalog Resource"),
                                 requires = IS_NULL_OR(IS_ONE_OF(db, "supply_item.id",
                                                                 supply_item_represent,
                                                                  sort=True)),
                                 comment = DIV(_class="tooltip",
                                               _title="%s|%s" % (T("Match To Catalog Resource"),
                                                                 T("Match Resource Requested in WebEOC to Catalog Resource in Give2LA.")
                                                                 ),
                                            ),
                                 script = SCRIPT(
'''S3FilterFieldChange({
'FilterField':'item_category_id',
'Field':'item_id',
'FieldResource':'item',
'FieldPrefix':'supply',
})'''),
                                  widget = None,
                                  ),
                         item_pack_id(label = T("Unit")),
                         Field("quantity", "double",
                               notnull = True,
                               ),
                         site_id,
                         Field("quantity_commit", "double",
                               default = 0,
                               label = T("Quantity Donated"),
                               represent = lambda quantity_commit: \
                                    req_quantity_represent(quantity_commit,
                                                           "commit"),
                               readable = False,
                               writable = False,
                               #writable = quantities_writable
                               ),
                         Field("quantity_transit", "double",
                               default = 0,
                               label = T("Quantity in Transit"),
                               represent = lambda quantity_transit: \
                                 req_quantity_represent(quantity_transit,
                                                        "transit"),
                               writable = quantities_writable,
                               ),
                         Field("quantity_fulfil", "double",
                               default = 0,
                               label = T("Quantity Received"),
                               represent = lambda quantity_fulfil: \
                                req_quantity_represent(quantity_fulfil,
                                                       "fulfil"),
                               readable = False,
                               writable = False,
                               #writable = quantities_writable
                               ),
                         #comments("surplus_instruct",
                         #         label = T("Instruction for Surplus Items")),
                         comments(),
                         *s3_meta_fields())

    table.site_id.label = T("Requested From")

    if not deployment_settings.get_req_show_quantity_transit():
        table.quantity_transit.writable = table.quantity_transit.readable= False

    # pack_quantity virtual field
    table.virtualfields.append(item_pack_virtualfields(tablename = tablename))

    # CRUD strings
    ADD_REQUEST_ITEM = T("Add Resource to Request")
    LIST_REQUEST_ITEM = T("List Request Resources")
    crud_strings[tablename] = Storage(
        title_create = ADD_REQUEST_ITEM,
        title_display = T("Request Resource Details"),
        title_list = LIST_REQUEST_ITEM,
        title_update = T("Edit Request Resource"),
        title_search = T("Search Request Resources"),
        subtitle_create = T("Add New Request Resource"),
        subtitle_list = T("Requested Resources"),
        label_list_button = LIST_REQUEST_ITEM,
        label_create_button = ADD_REQUEST_ITEM,
        label_delete_button = T("Delete Request Resource"),
        msg_record_created = T("Request Resource added"),
        msg_record_modified = T("Request Resource updated"),
        msg_record_deleted = T("Request Resource deleted"),
        msg_list_empty = T("No Request Resources currently registered"))

    # -------------------------------------------------------------------------
    def req_item_represent (id):
        query = (db.req_req_item.id == id) & \
                (db.req_req_item.item_id == db.supply_item.id)
        record = db(query).select( db.supply_item.name,
                                   limitby = (0, 1)).first()
        if record:
            return record.name
        else:
            return None

    # Reusable Field
    req_item_id = S3ReusableField("req_item_id",
                                  db.req_req_item,
                                  requires = IS_NULL_OR(IS_ONE_OF(db,
                                                                  "req_req_item.id",
                                                                  req_item_represent,
                                                                  orderby="req_req_item.id",
                                                                  sort=True)),
                                  represent = req_item_represent,
                                  label = T("Request Resource"),
                                  comment = DIV(_class="tooltip",
                                                _title="%s|%s" % (T("Request Resource"),
                                                                  T("Select Resources from the Request"))),
                                  ondelete = "CASCADE",
                                  script = SCRIPT(
'''$(document).ready(function(){
 S3FilterFieldChange({
  'FilterField':'req_item_id',
  'Field':'item_pack_id',
  'FieldResource':'item_pack',
  'FieldPrefix':'supply',
  'url':S3.Ap.concat('/req/req_item_packs/'),
  'msgNoRecords':S3.i18n.no_packs,
  'fncPrep':fncPrepItem,
  'fncRepresent':fncRepresentItem
 })
})'''),
                                )

    # On Accept to update req_req
    def req_item_onaccept(form):
        """
            Update req_req. commit_status, transit_status, fulfil_status
            None = quantity = 0 for ALL items
            Partial = some items have quantity > 0
            Complete = quantity_x = quantity(requested) for ALL items
        """
        table = db.req_req_item

        if form and form.vars.req_id:
            req_id = form.vars.req_id
        else:
            req_id = s3mgr.get_session("req", "req")
        if not req_id:
            # @todo: should raise a proper HTTP status here
            raise Exception("can not get req_id")

        if isinstance(form, FORM):
            # Interactive Request
            # @LA: create new surplus_item for the req_item
            db.req_surplus_item.insert(req_id = req_id,
                                       item_id = form.vars.item_id,
                                       item_pack_id = form.vars.item_pack_id
                                    )

        is_none = dict(commit = True,
                       transit = True,
                       fulfil = True)

        is_complete = dict(commit = True,
                           transit = True,
                           fulfil = True)

        # Must check all items in the req
        query = (table.req_id == req_id) & \
                (table.deleted == False )
        req_items = db(query).select(table.quantity,
                                     table.quantity_commit,
                                     table.quantity_transit,
                                     table.quantity_fulfil)

        for req_item in req_items:
            for status_type in ["commit", "transit", "fulfil"]:
                if req_item["quantity_%s" % status_type] < req_item.quantity:
                    is_complete[status_type] = False
                if req_item["quantity_%s" % status_type]:
                    is_none[status_type] = False

        status_update = {}
        for status_type in ["commit", "transit", "fulfil"]:
            if is_complete[status_type]:
                status_update["%s_status" % status_type] = REQ_STATUS_COMPLETE
            elif is_none[status_type]:
                status_update["%s_status" % status_type] = REQ_STATUS_NONE
            else:
                status_update["%s_status" % status_type] = REQ_STATUS_PARTIAL
        db(db.req_req.id == req_id).update(**status_update)

    configure(tablename,
              #create_next = URL(c="req",
              #                  # Shows the inventory items which match a requested item
              #                  # @ToDo: Make this page a component of req_item
              #                  f="req_item_inv_item",
              #                  args=["[id]"]),
              deletable = multiple_req_items,
              list_fields = ["id",
                             "item_id",
                             "item_pack_id",
                             "site_id",
                             "quantity",
                             "quantity_commit",
                             "quantity_transit",
                             "quantity_fulfil",
                             "comments",
                             ],
              onaccept = req_item_onaccept,
              )

    # -------------------------------------------------------------------------
    # Surplus Items
    tablename = "req_surplus_item"
    quantities_writable = deployment_settings.get_req_quantities_writable()
    table = define_table(tablename,
                         req_id(),
                         item_id(writable = False),
                         item_pack_id(writable = False),
                         Field("quantity_surplus", "double"),
                         human_resource_id(label = T("Recipient of Surplus Resources")),
                         comments(),
                         *s3_meta_fields())

    # pack_quantity virtual field
    table.virtualfields.append(item_pack_virtualfields(tablename = tablename))

    # CRUD strings
    ADD_SURPLUS_ITEM = T("Record Surplus Resources")
    LIST_SURPLUS_ITEM = T("List Surplus Resources")
    crud_strings[tablename] = Storage(
        title_create = ADD_SURPLUS_ITEM,
        title_display = T("Surplus Resource Details"),
        title_list = LIST_SURPLUS_ITEM,
        title_update = T("Edit Surplus Resource"),
        title_search = T("Search Surplus Resources"),
        subtitle_create = T("Record New Surplus Resource"),
        subtitle_list = T("Surplus Resources"),
        label_list_button = LIST_SURPLUS_ITEM,
        label_create_button = ADD_SURPLUS_ITEM,
        label_delete_button = T("Delete Surplus Resource"),
        msg_record_created = T("Surplus Resource Recoded"),
        msg_record_modified = T("Surplus Resource Updated"),
        msg_record_deleted = T("Surplus Resource Deleted"),
        msg_list_empty = T("No Surplus Resources currently Recorded"))

    # =========================================================================
    if has_module("doc"):

        # Documents Link Table
        load("doc_document")
        document_id = s3.document_id

        tablename = "req_document"
        table = define_table(tablename,
                             req_id(),
                             document_id())

        crud_strings[tablename] = Storage(
            title_create = T("Add Document"),
            title_display = T("Document Details"),
            title_list = T("List Documents"),
            title_update = T("Edit Document"),
            title_search = T("Search Documents"),
            subtitle_create = T("Add New Document"),
            subtitle_list = T("Documents"),
            label_list_button = T("List Documents"),
            label_create_button = T("Add Document"),
            # @ToDo: option to delete document (would likely be usual case)
            label_delete_button = T("Remove Document from this request"),
            msg_record_created = T("Document added"),
            msg_record_modified = T("Document updated"),
            msg_record_deleted = T("Document removed"),
            msg_list_empty = T("No Documents currently attached to this request"))

    # =========================================================================
    # Request Skills

    tablename = "req_req_skill"
    skill_quantities_writable = deployment_settings.get_req_skill_quantities_writable()
    table = define_table(tablename,
                         req_id(),
                         # @ToDo: Add a minimum competency rating?
                         Field("quantity", "integer",
                               default = 1,
                               label = T("Number of People Required"),
                               notnull = True,
                               ),
                         multi_skill_id(label = T("Required Skills"),
                                        comment = T("Leave blank to request an unskilled person")
                                        ),
                         site_id,
                         Field("quantity_commit", "integer",
                               label = T("Number of People Assigned"),
                               #represent = lambda quantity_commit: \
                                #req_quantity_represent(quantity_commit,
                                #                       "commit"),
                               default = 0,
                               writable = skill_quantities_writable,
                               ),
                         # Not used in LA
                         Field("quantity_transit", "integer",
                               default = 0,
                               label = T("Quantity in Transit"),
                               readable = False,
                               writable = False,
                               #writable = skill_quantities_writable,
                               #represent = lambda quantity_transit: \
                               # req_quantity_represent(quantity_transit,
                               #                        "transit"),
                               ),
                         Field("quantity_fulfil", "integer",
                               default = 0,
                               label = T("Number of People Checked In"),
                               #represent = lambda quantity_fulfil: \
                               #  req_quantity_represent(quantity_fulfil,
                               #                         "fulfil"),
                               writable = skill_quantities_writable,
                               ),
                         comments(label = T("Additional Information"),
                                  length = 300,
                                  comment = DIV(_class="tooltip",
                                                _title="%s|%s|%s" % (T("Additional Information"),
                                                                     T("Include any special requirements such as equipment which they need to bring, specific location, parking, accessibility."),
                                                                     T("300 character limit.")))),
                         *s3_meta_fields())

    table.site_id.label = T("Requested From")

    # Virtual Fields
    class req_skill_virtualfields(dict, object):

        # Fields to be loaded by sqltable as qfields
        # without them being list_fields
        # (These cannot contain VirtualFields)
        extra_fields = [
                    "req_id",
                    "quantity",
                    "quantity_commit",
                ]

        def task(self):
            rtable = db.req_req
            # Prevent recursive queries
            #rtable.virtualfields = []
            try:
                query = (rtable.id == self.req_req_skill.req_id)
            except AttributeError:
                # We are being instantiated inside one of the other methods
                return None
            req = db(query).select(rtable.purpose,
                                   limitby=(0, 1),
                                   cache=gis.cache).first()
            if req:
                return req.purpose
            return None

        def location(self):
            rtable = db.req_req
            # Prevent recursive queries
            #rtable.virtualfields = []
            try:
                query = (rtable.id == self.req_req_skill.req_id)
            except AttributeError:
                # We are being instantiated inside one of the other methods
                return None
            req = db(query).select(rtable.location,
                                   limitby=(0, 1),
                                   cache=gis.cache).first()
            if req:
                return req.location
            return None

        def date(self):
            rtable = db.req_req
            # Prevent recursive queries
            #rtable.virtualfields = []
            try:
                query = (rtable.id == self.req_req_skill.req_id)
            except AttributeError:
                # We are being instantiated inside one of the other methods
                return None
            req = db(query).select(rtable.date_required,
                                   rtable.date_required_until,
                                   limitby=(0, 1),
                                   cache=gis.cache).first()
            if req:
                save = deployment_settings.L10n.datetime_format
                deployment_settings.L10n.datetime_format = T("%I:%M %p")
                time_req = s3_utc_represent(req.date_required)
                try:
                    time_until = s3_utc_represent(req.date_required_until)
                except AttributeError:
                    # None!
                    time_until = ""
                # Restore in case used later
                deployment_settings.L10n.datetime_format = save
                return DIV(B(s3_date_represent_utc(req.date_required)),
                           BR(),
                           "%s - %s" % (time_req,
                                        time_until),
                           _style = "width:63px",
                          )
            return None

        def priority(self):
            rtable = db.req_req
            # Prevent recursive queries
            #rtable.virtualfields = []
            try:
                query = (rtable.id == self.req_req_skill.req_id)
            except AttributeError:
                # We are being instantiated inside one of the other methods
                return None
            req = db(query).select(rtable.priority,
                                   limitby=(0, 1),
                                   cache=gis.cache).first()
            if req:
                return req_priority_represent(req.priority)
            return None

        def needed(self):
            #rstable = db.req_req_skill
            # Prevent recursive queries
            #rstable.virtualfields = []
            quantity = self.req_req_skill.quantity
            left = quantity
            if self.req_req_skill.quantity_commit is not None:
                left = quantity - self.req_req_skill.quantity_commit
            return DIV(B(left),
                       #" / %s" % quantity,
                       _class="red")

    table.virtualfields.append(req_skill_virtualfields())

    if not deployment_settings.get_req_show_quantity_transit():
        table.quantity_transit.writable = table.quantity_transit.readable= False

    # CRUD strings
    ADD_REQUEST_SKILL = T("Add Volunteers to Request")
    if s3_has_role(STAFF):
        LIST_REQUEST_SKILL = T("List Requested Volunteers")
        subtitle_list = T("Requested Volunteers")
        msg_list_empty = T("No Volunteers currently requested")
        msg_no_match = T("No matching records")
    else:
        LIST_REQUEST_SKILL = T("Requests for Volunteers")
        subtitle_list = T("List of Requests for Volunteers")
        msg_list_empty = T("Currently there are no Requests for Volunteers to apply for.  Please register to receive updates of new Requests for Volunteers.")
        msg_no_match = msg_list_empty
    crud_strings[tablename] = Storage(
        title_create = ADD_REQUEST_SKILL,
        title_display = T("Requested Volunteers Details"),
        title_list = LIST_REQUEST_SKILL,
        title_update = T("Edit Requested Volunteers"),
        title_search = T("Search Requested Volunteers"),
        subtitle_create = T("Add Skills Required"),
        subtitle_list = subtitle_list,
        label_list_button = LIST_REQUEST_SKILL,
        label_create_button = ADD_REQUEST_SKILL,
        label_delete_button = T("Remove Volunteers from Request"),
        msg_record_created = T("Volunteers added to Request"),
        msg_record_modified = T("Requested Volunteers updated"),
        msg_record_deleted = T("Volunteers removed from Request"),
        msg_list_empty = msg_list_empty,
        msg_no_match = msg_no_match
        )

    # -------------------------------------------------------------------------
    def req_skill_represent (id):
        rstable = db.req_req_skill
        hstable = db.hrm_skill
        query = (rstable.id == id) & \
                (rstable.skill_id == hstable.id)
        record = db(query).select(hstable.name,
                                  limitby = (0, 1)).first()
        if record:
            return record.name
        else:
            return None

    # -------------------------------------------------------------------------
    def req_skill_onaccept(form):
        """
            Update req_req. commit_status, transit_status, fulfil_status
            None = quantity = 0 for ALL skills
            Partial = some skills have quantity > 0
            Complete = quantity_x = quantity(requested) for ALL skills
        """

        if form and form.vars.req_id:
            req_id = form.vars.req_id
        else:
            req_id = s3mgr.get_session("req", "req")
        if not req_id:
            # @ToDo: should raise a proper HTTP status here
            raise Exception("can not get req_id")

        is_none = dict(commit = True,
                       transit = True,
                       fulfil = True)

        is_complete = dict(commit = True,
                           transit = True,
                           fulfil = True)

        # Must check all skills in the req
        table = db.req_req_skill
        query = (table.req_id == req_id)
        req_skills = db(query).select(table.quantity,
                                      table.quantity_commit,
                                      table.quantity_transit,
                                      table.quantity_fulfil)

        for req_skill in req_skills:
            for status_type in ["commit", "transit", "fulfil"]:
                if req_skill["quantity_%s" % status_type] < req_skill.quantity:
                    is_complete[status_type] = False
                if req_skill["quantity_%s" % status_type]:
                    is_none[status_type] = False

        status_update = {}
        for status_type in ["commit", "transit", "fulfil"]:
            if is_complete[status_type]:
                status_update["%s_status" % status_type] = REQ_STATUS_COMPLETE
            elif is_none[status_type]:
                status_update["%s_status" % status_type] = REQ_STATUS_NONE
            else:
                status_update["%s_status" % status_type] = REQ_STATUS_PARTIAL
        table = db.req_req
        query = (table.id == req_id)
        db(query).update(**status_update)

    # -------------------------------------------------------------------------
    def req_skill_create_onaccept(form):
        """
            Send a notification to registered users which match the requested skill
            Send a notification to registered orgs which the request is published to

            #Create a Task for People to be assigned to
        """

        if form and form.vars.req_id:
            req_id = form.vars.req_id
        else:
            req_id = s3mgr.get_session("req", "req")
        if not req_id:
            # @ToDo: should raise a proper HTTP status here
            raise Exception("can not get req_id")

        if has_module("msg"):
            current.s3task.async("notify_vols", [req_id])

    configure("req_req_skill",
              create_onaccept = req_skill_create_onaccept,
              deletable = multiple_req_items and not webeoc_is_master,
              editable = not webeoc_is_master,
              insertable = not webeoc_is_master,
              onaccept = req_skill_onaccept,
              )

    # -------------------------------------------------------------------------
    def req_skill_controller():
        """
            Request Controller - unused for LA
                               - see controllers/vol.py req_skill()
        """

        tablename = "req_req_skill"
        table = db[tablename]

        configure(tablename,
                  insertable = False,
                  )

        if not s3_has_role(STAFF):
            req_table = db.req_req
            load("vol_assignment")
            vtable = db.vol_assignment
            person = auth.s3_logged_in_person()

            # Filter out:
            #   Reqs which haven't been published to the public site
            #   Reqs which are complete (status defined in models/req.py)
            #   Reqs which the Vol has already got an Assignment for
            #   Reqs for which the user doesn't have the relevant skills?
            #   No longer: Reqs which aren't published
            #((req_table.id == table.req_id) & (req_table.approved_by_id != None)) &
            # @ToDo: if s3_has_role(ORG) then also allow reqs for that Org
            s3.filter = \
                ((req_table.id == table.req_id) & (req_table.public == True)) & \
                ((req_table.id == table.req_id) & (req_table.commit_status != 2)) #&
                #~((vtable.req_id == table.req_id) & (vtable.person_id == person))

            configure(tablename,
                      list_fields=["id",
                                   (T("Task"), "task"),
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
            actions = [
                    dict(url = URL(c = request.controller,
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
                                BR(),
                                XML( T("If you have already registered please %(sign_in)s.") %
                                     dict( sign_in = A( T("Sign In"),
                                                        _href = URL(c = "default",
                                                                    f = "user",
                                                                    args = ["login"],
                                                                    vars = dict(_next = "/la/vol/req_skill")
                                                                    )
                                                       )
                                          )
                                 )
                                 )
                    output["rheader"] = DIV( P( B(T("The City of Los Angeles has the following Requests for Volunteers.") ),
                                                BR(),
                                                line
                                               )
                                               #T(" or "),
                                               #A( T("Sign In"), _href = URL(c = "default",
                                               #                              f = "user",
                                               #                              args = ["login"],
                                               #                              vars = dict(_next = "/la/vol/req_skill")
                                               #                              )
                                            )
                                          #T("The City of Los Angeles requests your participation in the following volunteering opportunities. When you see a request that appeals to you click apply. If you have not registered to volunteer yet, please "),
                                          #A(T("sign up"),
                                          #  _href="/%s/vol/register" % request.application,
                                          #  _class="signup"),
                                          #T(" first. You can narrow down the list by for example searching for a specific task or your neighborhood."))
            return output
        s3.postp = postp

        output = s3_rest_controller("req", "req_skill")

        return output

    # =========================================================================
    # Commitments (Pledges)
    commit_status_opts = {  2:T("Pending (Action Required)"), #Red
                            5:T("Cancelled"), #Gray
                            8:T("Loan"), #Yellow
                            9:T("Fulfilled"), #Green
                            10:T("In Process"), #Yellow
                            11:T("Matched (Pushed to EOC)"), #gray
                            12:T("Unable to Match (Pushed to EOC)"), #Gray
                            13:T("Committed (Pushed to EOC)"), #Green
                            14:T("Pending") #Red
                          }

    commit_status_color = {2: "DarkRed",
                           5: "DimGray",
                           8: "GoldenRod",
                           9: "DarkGreen",
                           10:"GoldenRod",
                           11: "DimGray",
                           12: "DimGray",
                           13: "DarkGreen",
                           14: "DarkRed",
                           }

    def commit_status_represent(opt):
        represent = commit_status_opts.get(opt, T("Unassigned"))
        color = commit_status_color.get(opt)
        if color:
            represent = SPAN(represent, _style = "font-weight:bold; fontcolor:%s;" % color)
        return represent

    commit_type_opts = {1:T("Permanent Donation"),
                        2:T("Temporary Loan")}
    donated_by_comment = copy.deepcopy(organisation_comment)
    donated_by_comment[0]["_href"] = organisation_comment[0]["_href"].replace("popup", "popup&child=donated_by_id").replace("/org/", "/don/")

    tablename = "req_commit"
    table = define_table(tablename,
                            #super_link(db.org_site,
                            #           label = T("From Facility"),
                            #           default = auth.user.site_id if auth.is_logged_in() else None,
                            #           # Non-Item Requests make False in the prep
                            #           writable = True,
                            #           readable = True,
                            #           # Comment these to use a Dropdown & not an Autocomplete
                            #           #widget = S3SiteAutocompleteWidget(),
                            #           #comment = DIV(_class="tooltip",
                            #           #              _title="%s|%s" % (T("From Facility"),
                            #           #                                T("Enter some characters to bring up a list of possible matches"))),
                            #           represent = shn_site_represent),
                            ## Non-Item Requests make True in the prep
                            #organisation_id(readable = False,
                            #                writable = False),
                            req_id(),
                            Field("status",
                                  "integer",
                                  label = T("BOC Status"),
                                  requires = IS_IN_SET(commit_status_opts),
                                  represent = commit_status_represent,
                                  default = 2,
                                  ),
                            organisation_id("donated_by_id",
                                            label = T("Donated By Corporation/Organization"),
                                            requires = IS_NULL_OR(IS_ONE_OF(db, "org_organisation.id",
                                                              organisation_represent,
                                                              orderby="org_organisation.name",
                                                              sort=True,
                                                              filterby = "has_items",
                                                              filter_opts = (True,))),
                                            widget = None,
                                            comment = donated_by_comment,
                                            ),
                            #Field("type",
                            #      # These are copied automatically from the Req
                            #      readable=False,
                            #      writable=False),
                            Field("datetime",
                                  "datetime",
                                  label = T("Date+Time Donor Identified"),
                                  requires = [IS_EMPTY_OR(
                                              IS_UTC_DATETIME_IN_RANGE(
                                                minimum=request.utcnow - datetime.timedelta(days=1),
                                                error_message="%s %%(min)s!" %
                                                    T("Enter a valid future date")))],
                                  widget = S3DateTimeWidget(past=0,
                                                            future=8760),  # Hours, so 1 year
                                  represent = s3_utc_represent,
                                  default = request.utcnow),
                            Field("specs",
                                  "text",
                                  label=T("Donation Resource Specifications"),
                                  length=350,
                                  comment = DIV(_class="tooltip",
                                                _title="%s|%s" % (T("Specifications"),
                                                                  T("300 character limit.")
                                                                  ),
                                                )
                                  ),
                            Field( "item_pack",
                                   label = T("Donation Resource Unit")
                                   ),
                            Field( "quantity_commit",
                                   "double",
                                   label = T("Quantity Donated"),
                                   represent = lambda quantity_commit: \
                                    req_quantity_represent(quantity_commit,
                                                           "commit"),
                                   default = 0,
                                   writable = quantities_writable),
                            Field("pack_value",
                                   "double",
                                   label = T("Value ($) per Unit")),
                            # @ToDo: Move this into a Currency Widget for the pack_value field
                            currency_type("currency"),
                            Field("datetime_available",
                                  "datetime",
                                  label = T("Date+Time Available"),
                                  requires = [IS_EMPTY_OR(
                                              IS_UTC_DATETIME_IN_RANGE(
                                                minimum=request.utcnow - datetime.timedelta(days=1),
                                                error_message="%s %%(min)s!" %
                                                    T("Enter a valid future date")))],
                                  widget = S3DateTimeWidget(past=0,
                                                            future=8760),  # Hours, so 1 year
                                  represent = s3_utc_represent),
                            Field("type",
                                  "integer",
                                  label = T("Type of Donation"),
                                  requires = IS_IN_SET(commit_type_opts),
                                  represent = lambda opt: \
                                                    commit_type_opts.get(opt, NONE),
                                  default = 1,
                                  widget = SQLFORM.widgets.radio.widget,

                                  # @ToDo: 1 donation 2 loan
                                  ),
                            Field("loan_value",
                                  "double",
                                  label = T("Loan Value per. Day")
                                  ), # pre day
                            human_resource_id("return_contact_id",
                                              label = T("Return Contact")), #HR
                            super_link(db.org_site,
                                       label = T("Return to Facility"),
                                       readable = True,
                                       writable = True,
                                       # Comment these to use a Dropdown & not an Autocomplete
                                       #widget = S3SiteAutocompleteWidget(),
                                       #comment = DIV(_class="tooltip",
                                       #              _title="%s|%s" % (T("Requested By Facility"),
                                       #                                T("Enter some characters to bring up a list of possible matches"))),
                                       represent = shn_site_represent),
                            Field("datetime_return",
                                  "datetime",
                                  label = T("Return by Date+Time"),
                                  requires = [IS_EMPTY_OR(
                                              IS_UTC_DATETIME_IN_RANGE(
                                                minimum=request.utcnow - datetime.timedelta(days=1),
                                                error_message="%s %%(min)s!" %
                                                    T("Enter a valid future date")))],
                                  widget = S3DateTimeWidget(past=0,
                                                            future=17520),  # Hours, so 2 years
                                  represent = s3_utc_represent),
                            Field("return_penalty",
                                  label = T("Penalty for Late Return")),
                            Field("return_instruct",
                                  label = T("Instructions for Return or Surplus")),
                            Field("insured",
                                   "boolean",
                                  label = T("Insured")
                                  ),
                            Field("insure_details",
                                  "text",
                                  label = T("Insurance Details"),
                                  length=300,
                                  comment = DIV(_class="tooltip",
                                                _title="%s|%s" % (T("Insurance Details"),
                                                                  T("300 character limit.")
                                                                  ),
                                                )
                                  ),
                            Field("warrantied",
                                   "boolean",
                                  label = T("Under Warranty")
                                  ),
                            Field("warranty_details",
                                  "text",
                                  length=300,
                                  comment = DIV(_class="tooltip",
                                                _title="%s|%s" % (T("Details"),
                                                                  T("300 character limit.")
                                                                  ),
                                                )
                                  ),
                            Field("transport_req",
                                   "boolean",
                                  label = T("Transportation Required")
                                  ),
                            Field("security_req",
                                  "boolean",
                                  label = T("Security Required"),
                                  ),
                            human_resource_id("committer_id",
                                              label = T("Processed in BOC by"),
                                              empty = False,
                                              default = s3_logged_in_human_resource(),
                                              ),
                            Field("upload",
                                  "upload",
                                   label = T("Completed Request for Donations Form"),
                                   ),
                            Field("upload_additional",
                                   "upload",
                                   label = T("Additional Documents"),
                                  comment = DIV(_class="tooltip",
                                                _title="%s|%s" % (T("Additional Documents"),
                                                                  T("Legal, Insurance, etc")
                                                                  ),
                                                )
                                   ),
                            comments(label = T("Donation Comments")),
                            *s3_meta_fields())

    # CRUD strings
    ADD_COMMIT = T("Donation Commitment Status")
    LIST_COMMIT = T("List Donation Commitment Statuses")
    crud_strings[tablename] = Storage(
        title_create = ADD_COMMIT,
        title_display = T("Donation Commitment Status Details"),
        title_list = LIST_COMMIT,
        title_update = T("Donation Commitment Status"),
        title_search = T("Search Donation Commitment Statuses"),
        subtitle_create = ADD_COMMIT,
        subtitle_list = T("Donation Commitment Status"),
        label_list_button = LIST_COMMIT,
        label_create_button = ADD_COMMIT,
        label_delete_button = T("Delete Donation"),
        msg_record_created = T("Donation Commitment Status Added"),
        msg_record_modified = T("Donation Commitment Status Updated"),
        msg_record_deleted = T("Donation Commitment Status Canceled"),
        msg_list_empty = T("No Donation Commitment Status"))

    # -------------------------------------------------------------------------
    def commit_represent(id):
        if id:
            table = db.req_commit
            r = db(table.id == id).select(table.type,
                                          table.date,
                                          table.organisation_id,
                                          table.site_id,
                                          limitby=(0, 1)).first()
            if r.type == 1: # Items
                return "%s - %s" % (shn_site_represent(r.site_id),
                                    r.date)
            else:
                return "%s - %s" % (organisation_represent(r.organisation_id),
                                    r.date)
        else:
            return NONE

    # -------------------------------------------------------------------------
    # Reusable Field
    commit_id = S3ReusableField("commit_id", db.req_commit, sortby="date",
                                requires = IS_NULL_OR( \
                                                IS_ONE_OF(db,
                                                          "req_commit.id",
                                                          commit_represent,
                                                          orderby="req_commit.date",
                                                          sort=True)),
                                represent = commit_represent,
                                label = T("Commitment"),
                                ondelete = "CASCADE")

    # -------------------------------------------------------------------------
    def commit_onvalidation(form):
        # Copy the request_type to the commitment
        req_id = s3mgr.get_session("req", "req")
        if req_id:
            rtable = db.req_req
            query = (rtable.id == req_id)
            req_record = db(query).select(rtable.type,
                                          limitby=(0, 1)).first()
            if req_record:
                form.vars.type = req_record.type

    # -------------------------------------------------------------------------
    def commit_onaccept(form):
        table = db.req_commit

        # Update owned_by_role to the organisation's owned_by_role
        # @ToDo: Facility
        if form.vars.organisation_id:
            otable = db.org_organisation
            query = (otable.id == form.vars.organisation_id)
            org = db(query).select(otable.owned_by_organisation,
                                   limitby=(0, 1)).first()
            if org:
                query = (table.id == form.vars.id)
                db(query).update(owned_by_organisation=org.owned_by_organisation)

        rtable = db.req_req
        if form.vars.type == 3: # People
            # If no organisation_id, then this is a single person commitment, so create the commit_person record automatically
            table = db.req_commit_person
            table.insert(commit_id = form.vars.id,
                         #skill_id = ???,
                         person_id = auth.s3_logged_in_person())
            # @ToDo: Mark Person's allocation status as 'Committed'
        elif form.vars.type == 9:
            # Non-Item requests should have commitment status updated if a commitment is made
            query = (table.id == form.vars.id) & \
                    (rtable.id == table.req_id)
            req_record = db(query).select(rtable.id,
                                          rtable.commit_status,
                                          limitby=(0, 1)).first()
            if req_record and req_record.commit_status == REQ_STATUS_NONE:
                # Assume Partial not Complete
                # @ToDo: Provide a way for the committer to specify this
                query = (rtable.id == req_record.id)
                db(query).update(commit_status=REQ_STATUS_PARTIAL)

    # -------------------------------------------------------------------------
    configure(tablename,
              # Commitments should only be made to a specific request
              listadd = False,
              list_fields = ["req_id",
                             "status",
                             "donated_by_id",
                             "datetime",
                             (T("Donated Resource"), "item"),
                             "specs",
                             "quantity_commit",
                             "pack_value",
                             "datetime_available",
                             "type",
                             "loan_value",
                             "return_contact_id",
                             "site_id",
                             "datetime_return",
                             "return_penalty",
                             "return_instruct",
                             "insured",
                             "insure_details",
                             "warrantied",
                             "warranty_details",
                             "transport_req",
                             "security_req",
                             "committer_id",
                             "upload",
                             "upload_additional",
                             "comments"
                             ]
              #onvalidation = commit_onvalidation,
              #onaccept = commit_onaccept
              )
    
    # Virtual Field
    class req_commit_virtualfields(dict, object):

        def item(self):
            ritable = db.req_req_item
            iptable = db.supply_item_pack
            req_id = self.req_commit.req_id
            
            query = (ritable.req_id == req_id) & \
                    (iptable.id == ritable.item_pack_id)
            item = db(query).select(ritable.item_id,
                                    iptable.name,
                                    limitby=(0, 1)).first()
            if item:
                return s3.concat_item_pack_quantity(s3.item_represent(item.req_req_item.item_id),
                                                    item.supply_item_pack.name,
                                                    None)
            else:
                return NONE

        def item_quantity(self):
            req_item_table = db.req_req_item
            req_id = self.req_commit.id
            query = (req_item_table.req_id == req_id)
            req_item = db(query).select(req_item_table.quantity,
                                        limitby=(0, 1)).first()
            if req_item:
                return req_item.quantity
            else:
                return None

    table.virtualfields.append(req_commit_virtualfields())

    # =========================================================================
    # Commitment Items
    # @ToDo: Update the req_item_id in the commit_item if the req_id of the commit is changed

    tablename = "req_commit_item"
    table = define_table(tablename,
                            commit_id(),
                            #item_id(),
                            req_item_id(),
                            item_pack_id(),
                            Field("quantity",
                                  "double",
                                  notnull = True),
                            comments(),
                            *s3_meta_fields())

    # pack_quantity virtual field
    table.virtualfields.append(item_pack_virtualfields(tablename = tablename))

    # CRUD strings
    ADD_COMMIT_ITEM = T("Add Resource to Commitment")
    LIST_COMMIT_ITEM = T("List Commitment Resources")
    crud_strings[tablename] = Storage(
        title_create = ADD_COMMIT_ITEM,
        title_display = T("Commitment Resource Details"),
        title_list = LIST_COMMIT_ITEM,
        title_update = T("Edit Commitment Resource"),
        title_search = T("Search Commitment Resources"),
        subtitle_create = T("Add New Commitment Resource"),
        subtitle_list = T("Commitment Resources"),
        label_list_button = LIST_COMMIT_ITEM,
        label_create_button = ADD_COMMIT_ITEM,
        label_delete_button = T("Delete Commitment Resource"),
        msg_record_created = T("Commitment Resource added"),
        msg_record_modified = T("Commitment Resource updated"),
        msg_record_deleted = T("Commitment Resource deleted"),
        msg_list_empty = T("No Commitment Resources currently registered"))

    # -------------------------------------------------------------------------
    def commit_item_onaccept(form):
        table = db.req_commit_item

        # Try to get req_item_id from the form
        req_item_id = 0
        if form:
            req_item_id = form.vars.get("req_item_id")
        if not req_item_id:
            commit_item_id = s3mgr.get_session("req", "commit_item")
            r_commit_item = table[commit_item_id]

            req_item_id = r_commit_item.req_item_id

        query = (table.req_item_id == req_item_id) & \
                (table.deleted == False)
        commit_items = db(query).select(table.quantity ,
                                        table.item_pack_id)
        quantity_commit = 0
        for commit_item in commit_items:
            quantity_commit += commit_item.quantity * commit_item.pack_quantity

        r_req_item = db.req_req_item[req_item_id]
        quantity_commit = quantity_commit / r_req_item.pack_quantity
        db.req_req_item[req_item_id] = dict(quantity_commit = quantity_commit)

        # Update status_commit of the req record
        s3mgr.store_session("req", "req_item", r_req_item.id)
        req_item_onaccept(None)


    configure(tablename,
              onaccept = commit_item_onaccept)

    # =========================================================================
    # Committed Persons

    tablename = "req_commit_person"
    table = define_table(tablename,
                            commit_id(),
                            # For reference
                            multi_skill_id(writable=False, comment=None),
                            # This should be person as we want to mark them as allocated
                            person_id(ondelete = "CASCADE"),
                            comments(),
                            *s3_meta_fields())

    # CRUD strings
    ADD_COMMIT_PERSON = T("Add Person to Commitment")
    LIST_COMMIT_PERSON = T("List Committed People")
    crud_strings[tablename] = Storage(
        title_create = ADD_COMMIT_PERSON,
        title_display = T("Committed Person Details"),
        title_list = LIST_COMMIT_PERSON,
        title_update = T("Edit Committed Person"),
        title_search = T("Search Committed People"),
        subtitle_create = T("Add New Person to Commitment"),
        subtitle_list = T("Committed People"),
        label_list_button = LIST_COMMIT_PERSON,
        label_create_button = ADD_COMMIT_PERSON,
        label_delete_button = T("Remove Person from Commitment"),
        msg_record_created = T("Person added to Commitment"),
        msg_record_modified = T("Committed Person updated"),
        msg_record_deleted = T("Person removed from Commitment"),
        msg_list_empty = T("No People currently committed"))

    # -------------------------------------------------------------------------
    def commit_person_onaccept(form):
        table = db.req_commit_person

        # Try to get req_skill_id from the form
        req_skill_id = 0
        if form:
            req_skill_id = form.vars.get("req_skill_id")
        if not req_skill_id:
            commit_skill_id = s3mgr.get_session("req", "commit_skill")
            r_commit_skill = table[commit_skill_id]
            req_skill_id = r_commit_skill.req_skill_id

        query = (table.req_skill_id == req_skill_id) & \
                (table.deleted == False)
        commit_skills = db(query).select(table.quantity)
        quantity_commit = 0
        for commit_skill in commit_skills:
            quantity_commit += commit_skill.quantity

        r_req_skill = db.req_req_skill[req_skill_id]
        db.req_req_skill[req_skill_id] = dict(quantity_commit = quantity_commit)

        # Update status_commit of the req record
        s3mgr.store_session("req", "req_skill", r_req_skill.id)
        req_skill_onaccept(None)


    # @ToDo: Fix this before enabling
    #configure(tablename,
    #          onaccept = commit_person_onaccept)

    # =========================================================================
    # Fulfillment

    tablename = "req_fulfill"
    table = define_table(tablename,
                            req_id(),
                            human_resource_id("accepted_by_id",
                                              label = T("Accepted by"),
                                              comment = DIV( _class="tooltip",
                                                             _title="%s|%s" % (T("Accepted by"),
                                                                               T("EOC Staff who accepts the donation and coordinates its delivery.")
                                                                              )
                                                            ),
                                              ),
                            Field("datetime_fulfill",
                                  "datetime",
                                  label = T("Date Received"), # Could be T("Date Delivered") - make deployment_setting
                                  requires = [IS_EMPTY_OR(
                                              IS_UTC_DATETIME_IN_RANGE(
                                                maximum=request.utcnow,
                                                error_message="%s %%(max)s!" %
                                                    T("Enter a valid past date")))],
                                  widget = S3DateTimeWidget(past=8760, # Hours, so 1 year
                                                            future=0),
                                  represent = s3_utc_represent,
                                  ),
                            Field( "quantity_fulfill",
                                   "double",
                                   label = T("Quantity Received"),
                                   represent = lambda quantity_fulfil: \
                                    req_quantity_represent(quantity_fulfil,
                                                           "fulfil"),
                                   default = 0,
                                   writable = quantities_writable),

                            human_resource_id("fulfill_by_id",
                                              label = T("Delivery of Donation Received By"),
                                              # @ToDo: Set this in Update forms? Dedicated 'Receive' button?
                                              # (Definitely not in Create forms)
                                              #default = s3_logged_in_human_resource()
                                              ),
                            Field("datetime_returned",
                                  "datetime",
                                  label = T("Date+Time Returned"), # Could be T("Date Delivered") - make deployment_setting
                                  requires = [IS_EMPTY_OR(
                                              IS_UTC_DATETIME_IN_RANGE(
                                                maximum=request.utcnow,
                                                error_message="%s %%(max)s!" %
                                                    T("Enter a valid past date")))],
                                  widget = S3DateTimeWidget(past=8760, # Hours, so 1 year
                                                            future=0),
                                  represent = s3_utc_represent,
                                  ),
                            comments(),
                            *s3_meta_fields())

    # CRUD strings
    ADD_COMMIT_PERSON = T("Add Request Fulfilment Details")
    LIST_COMMIT_PERSON = T("List Fulfilment Details")
    crud_strings[tablename] = Storage(
        title_create = ADD_COMMIT_PERSON,
        title_display = T("Request Fulfilment Details"),
        title_list = LIST_COMMIT_PERSON,
        title_update = T("Edit Request Fulfilment Details"),
        title_search = T("Search Request Fulfilments"),
        subtitle_create = ADD_COMMIT_PERSON,#T("Add Request Fulfilment Details"),
        subtitle_list = T("Request Fulfilments"),
        label_list_button = LIST_COMMIT_PERSON,
        label_create_button = ADD_COMMIT_PERSON,
        label_delete_button = T("Remove Request Fulfilment"),
        msg_record_created = T("Request Fulfilment Details Added"),
        msg_record_modified = T("Request Fulfilment Details Updated"),
        msg_record_deleted = T("Request Fulfilment Details Deleted"),
        msg_list_empty = T("No Request Fulfilments"))

    # =========================================================================
    def req_tabs(r):
        """
            Add a set of Tabs for a Site's Request Tasks

            @ToDo: Roll these up like inv_tabs in 08_inv.py
        """
        if has_module("req") and \
            auth.s3_has_permission("read", db.req_req):
            return [(T("Requests"), "req"),
                    (T("Match Requests"), "req_match/"),
                    (T("Commit"), "commit")
                    ]
        else:
            return []

    # Pass variables back to global scope (s3.*)
    return_dict = dict(
        req_id = req_id,
        req_item_id = req_item_id,
        req_item_onaccept = req_item_onaccept,
        req_represent = req_represent,
        req_item_represent = req_item_represent,
        req_create_form_mods = req_create_form_mods,
        req_helptext_script = req_helptext_script,
        req_tabs = req_tabs,
        req_match = req_match,
        req_priority_represent = req_priority_represent,
        req_hide_quantities = req_hide_quantities,
        req_skill_controller = req_skill_controller
        )

    if deployment_settings.get_req_use_commit():
        return_dict["commit_item_onaccept"] = commit_item_onaccept

    return return_dict

# Provide a handle to this load function
loader(req_tables,
       "req_req",
       "req_req_item",
       "req_req_skill",
       "req_commit",
       "req_commit_item",
       "req_commit_person",
       #"project_task_req",
       )

# -----------------------------------------------------------------------------
def req_req_duplicate(job):
    """
      This callback will be called when importing records
      it will look to see if the record being imported is a duplicate.

      @param job: An S3ImportJob object which includes all the details
                  of the record being imported

      If the record is a duplicate then it will set the job method to update

      Rules for finding a duplicate:
       - If the Request Number exists then it's a duplicate
    """
    # ignore this processing if the id is set or there is no data
    if job.id or job.data == None:
        return
    if job.tablename == "req_req":
        table = job.table
        if "request_number" in job.data:
            request_number = job.data.request_number
        else:
            return

        query = (table.request_number == request_number)
        _duplicate = db(query).select(table.id,
                                      limitby=(0, 1)).first()
        if _duplicate:
            job.id = _duplicate.id
            job.data.id = _duplicate.id
            job.method = job.METHOD.UPDATE

configure("req_req", resolve=req_req_duplicate)

# -----------------------------------------------------------------------------
def req_item_duplicate(job):
    """
      This callback will be called when importing records
      it will look to see if the record being imported is a duplicate.

      @param job: An S3ImportJob object which includes all the details
                  of the record being imported

      If the record is a duplicate then it will set the job method to update

      Rules for finding a duplicate:
       - If the Request Number matches
       - The item is the same
    """
    # ignore this processing if the id is set or there is no data
    if job.id or job.data == None:
        return
    if job.tablename == "req_req_item":
        itable = job.table
        rtable = db.req_req
        stable = db.supply_item
        req_id = None
        item_id = None
        for ref in job.references:
            if ref.entry.tablename == "req_req":
                if ref.entry.id != None:
                    req_id = ref.entry.id
                else:
                    uuid = ref.entry.item_id
                    jobitem = job.job.items[uuid]
                    req_id = jobitem.id
            elif ref.entry.tablename == "supply_item":
                if ref.entry.id != None:
                    item_id = ref.entry.id
                else:
                    uuid = ref.entry.item_id
                    jobitem = job.job.items[uuid]
                    item_id = jobitem.id

        if req_id != None and item_id != None:
            query = (itable.req_id == req_id) & \
                    (itable.item_id == item_id)
        else:
            return

        _duplicate = db(query).select(itable.id,
                                      limitby=(0, 1)).first()
        if _duplicate:
            job.id = _duplicate.id
            job.data.id = _duplicate.id
            job.method = job.METHOD.UPDATE

configure("req_req_item", resolve=req_item_duplicate)

# =============================================================================
# Tasks to be callable async
# =============================================================================
def notify_vols(req_id, user_id=None):
    """
        Notify volunteers of a new volunteer opportunity
            - will normally be done Asynchronously if there is a worker alive

        @param req_id: id of the record in db.req_req
        @param user_id: calling request's auth.user.id or None
    """
    if user_id:
        # Authenticate
        auth.s3_impersonate(user_id)

    # Run the Task
    current.manager.load("req_req")
    table = db.req_req
    query = (table.id == req_id)
    record = db(query).select(table.public,
                              table.organisations_id,
                              #table.purpose,
                              #table.location,
                              limitby=(0, 1)).first()

    if not record:
        return

    rstable = db.req_req_skill
    query = (rstable.req_id == req_id)
    skill = db(query).select(rstable.id,
                             rstable.skill_id,
                             limitby=(0, 1)).first()
    if not skill:
        return

    message = "%s\n%s%s%i" % (T("A new Volunteer Opportunity has become available at GIVE2LA web site. Please log-in to view and indicate your availability. Thank you."),
                              s3.base_url,
                              "/vol/req_skill/",
                              skill.id)

    ptable = db.pr_person
    people = []

    if record.public:
        # Send a notification to all registered users which match
        # the requested skills
        load("vol_skill")
        table = db.vol_skill
        query = (table.deleted == False)
        # Skip Disabled Users
        utable = db[auth.settings.table_user]
        query = query & \
                (ptable.id == table.person_id) & \
                (utable.person_uuid == ptable.uuid) & \
                (utable.registration_key != "disabled")

        if skill.skill_id:
            query = query & (table.skill_id.contains(skill.skill_id[0]))
            for i in range(1, (len(skill.skill_id) - 1)):
                query = query & \
                        (table.skill_id.contains(skill.skill_id[i]))
        #else:
            # Unskilled - everyone matches
        rows = db(query).select(table.person_id)
        if rows is not None:
            for row in rows:
                people.append(row)

    orgs = record.organisations_id
    if orgs is not None:
        for org in orgs:
            # Send a notification to the Organisational contacts for each
            # volunteer organisation selected
            table = db.hrm_human_resource
            query = (table.organisation_id == org) & \
                    (table.focal_point == True)
            rows = db(query).select(table.person_id)
            if rows is not None:
                for row in rows:
                    people.append(row)

    for person in people:
        # Lookup Subscription preferences
        ctable = db.pr_contact
        query = (ptable.id == person.person_id) & \
                (ctable.pe_id == ptable.pe_id)
        contacts = db(query).select(ctable.pe_id,
                                    ctable.contact_method,
                                    ctable.priority)
        for contact in contacts:
            if contact.priority != 10: # 10 == Unsubscribed
                if contact.contact_method == "SMS":
                    # Send SMS
                    msg.send_by_pe_id(contact.pe_id,
                                      message=message,
                                      pr_message_method = "SMS")
                elif contact.contact_method == "EMAIL":
                    # Send Email
                    msg.send_by_pe_id(contact.pe_id,
                                      message=message,
                                      pr_message_method = "EMAIL")
    # Process outbox
    msg.process_outbox(contact_method="SMS")
    msg.process_outbox(contact_method="EMAIL")

tasks["notify_vols"] = notify_vols

# END =========================================================================