# -*- coding: utf-8 -*-

"""
    Event Module
"""

module = "event"

# -------------------------------------------------------------------------
# Events
#
#   Events can be Exercises or real Incidents.
#
# -------------------------------------------------------------------------
def event_tables():
    """ Load the Event Tables when required """

    module = "event"

    tablename = "event_event"
    table = define_table(tablename,
                         Field("name", notnull=True, # Name could be a code, e.g. to link to WebEOC
                               length=64,    # Mayon compatiblity
                               label=T("Name")),
                         #Field("code",       # e.g. to link to WebEOC
                         #      length=64,    # Mayon compatiblity
                         #      label=T("Code")),
                         Field("exercise", "boolean",
                               represent = lambda opt: "√" if opt else NONE,
                               comment = DIV(_class="tooltip",
                                             _title="%s|%s" % (T("Exercise"),
                                                               T("Exercises mean all screens have a watermark & all notifications have a prefix."))),
                               readable = False,
                               writable = False,
                               label=T("Exercise?")),
                         Field("zero_hour", "datetime",
                               default = request.utcnow,
                               #required = True,
                               requires = IS_EMPTY_OR(IS_UTC_DATETIME()),
                                           #IS_UTC_DATETIME_IN_RANGE(
                                           #  maximum=request.utcnow,
                                           #  error_message="%s %%(max)s!" %
                                           #      T("Enter a valid past date")))],
                               widget = S3DateTimeWidget(past=8760, # Hours, so 1 year
                                                         future=0),
                               represent = s3_utc_represent,
                               comment = DIV(_class="tooltip",
                                             _title="%s|%s" % (T("Zero Hour"),
                                                               T("The time at which the Event started."))),
                               label=T("Zero Hour")),
                         Field("closed", "boolean",
                               default = False,
                               label=T("Closed")),
                         comments(),
                         *s3_meta_fields())

    def event_create_onaccept(form):
        """ When an Event is instantiated, populate defaults """
        event = form.vars.id
        # Set the Event in the session
        session.s3.event = event
        #ctable = db.gis_config

        # Read the Map Config
        # Currently this is the Default one
        # @ToDo: Find the best match for the Location of the Event
        #query = (ctable.id == 1)
        #mapconfig = db(query).select(ctable.ALL).first()

        #if mapconfig:
        #    # Event's Map Config is a copy of the Default / Scenario's
        #    # so that it can be changed within the Event without
        #    # contaminating the base one
        #    del mapconfig["id"]
        #    del mapconfig["uuid"]
        #    #mapconfig["name"] = "Event %s" % form.vars.name
        #    mapconfig["name"] = form.vars.name
        #    mapconfig["show_in_menu"] = True
        #    config = ctable.insert(**mapconfig.as_dict())
        #    mtable = db.event_config
        #    mtable.insert(event_id=event,
        #                  config_id=config)
        #    # Activate this config
        #    gis.set_config(config)

    def event_update_onaccept(form):
        """ When an Event is updated, check for closure """
        event = form.vars.id
        if form.vars.closed:
            # Ensure this event isn't active in the session
            if session.s3.event == event:
                session.s3.event = None
            # Hide the Event from the Map menu
            #table = db.event_config
            #query = (table.event_id == event)
            #config = db(query).select(table.config_id,
            #                          limitby=(0, 1)).first()
            #if config:
            #    table = db.gis_config
            #    query = (table.id == config.config_id)
            #    db(query).update(show_in_menu=False)
            #config = gis.get_config()
            #if config == config.config_id:
            #    # Reset to the Default Map
            #    gis.set_config(1)

    configure(tablename,
              create_onaccept=event_create_onaccept,
              update_onaccept=event_update_onaccept,
              list_fields = ["id",
                             "name",
                             "exercise",
                             "closed",
                             "comments",
                             ])

    # CRUD strings
    ADD_EVENT = T("New Event")
    LIST_EVENTS = T("List Events")
    crud_strings[tablename] = Storage(
        title_create = ADD_EVENT,
        title_display = T("Event Details"),
        title_list = LIST_EVENTS,
        title_update = T("Edit Event"),
        title_search = T("Search Events"),
        subtitle_create = T("Add New Event"),
        subtitle_list = T("Events"),
        label_list_button = LIST_EVENTS,
        label_create_button = ADD_EVENT,
        label_delete_button = T("Delete Event"),
        msg_record_created = T("Event added"),
        msg_record_modified = T("Event updated"),
        msg_record_deleted = T("Event deleted"),
        msg_list_empty = T("No Events currently registered"))

    def event_represent(id):
        if not id:
            return NONE
        table = db.event_event
        query = (table.id == id)
        event = db(query).select(table.name,
                                 limitby=(0, 1)).first()
        if event:
            return event.name
        else:
            return UNKNOWN_OPT

    event_id = S3ReusableField("event_id", db.event_event,
                               sortby="name",
                               requires = IS_NULL_OR(IS_ONE_OF(db,
                                                               "event_event.id",
                                                               event_represent,
                                                               filterby="closed",
                                                               filter_opts=(False,),
                                                               orderby="event_event.name",
                                                               sort=True)),
                               represent = event_represent,
                               label = T("Event"),
                               ondelete = "RESTRICT",
                               # Uncomment these to use an Autocomplete & not a Dropdown
                               #widget = S3AutocompleteWidget()
                               #comment = DIV(_class="tooltip",
                               #              _title="%s|%s" % (T("Event"),
                               #                                T("Enter some characters to bring up a list of possible matches")))
                                )

    # ---------------------------------------------------------------------
    # Incidents
    #
    #  Incidents are a smaller sub-component of an Event
    #  They will be instances of Scenarios.
    #   They can be Exercises or real Incidents.
    #
    tablename = "event_incident"
    table = define_table(tablename,
                         event_id(),
                         Field("name", notnull=True,
                               length=64,
                               label=T("Name")),
                         *s3_meta_fields())

    #add_component(table, event_event="event_id")

    crud_strings[tablename] = Storage(
        title_create = T("Add Incident"),
        title_display = T("Incident Details"),
        title_list = T("List Incidents"),
        title_update = T("Edit Incident"),
        title_search = T("Search Incidents"),
        subtitle_create = T("Add New Incident"),
        subtitle_list = T("Incidents"),
        label_list_button = T("List Incidents"),
        label_create_button = T("Add Incident"),
        label_delete_button = T("Remove Incident from this event"),
        msg_record_created = T("Incident added"),
        msg_record_modified = T("Incident updated"),
        msg_record_deleted = T("Incident removed"),
        msg_list_empty = T("No Incidents currently registered in this event"))

    def incident_represent(id):
        if not id:
            return NONE
        table = db.event_incident
        query = (table.id == id)
        incident = db(query).select(table.name,
                                    limitby=(0, 1)).first()
        if incident:
            return incident.name
        else:
            return UNKNOWN_OPT

    incident_id = S3ReusableField("incident_id", db.event_incident,
                                  sortby="name",
                                  requires = IS_NULL_OR(IS_ONE_OF(db,
                                                                  "event_incident.id",
                                                                  incident_represent,
                                                                  orderby="event_incident.name",
                                                                  sort=True)),
                                  represent = incident_represent,
                                  label = T("Incident"),
                                  ondelete = "RESTRICT",
                                  # Uncomment these to use an Autocomplete & not a Dropdown
                                  #widget = S3AutocompleteWidget()
                                  #comment = DIV(_class="tooltip",
                                  #              _title="%s|%s" % (T("Incident"),
                                  #                                T("Enter some characters to bring up a list of possible matches")))
                                )
    # ---------------------------------------------------------------------
    # Link Tables for Resources used in this (Event)
    # ---------------------------------------------------------------------
    # Staff/Volunteers
    # @ToDo: Use Positions, not individual HRs
    # @ToDo: Search Widget
    #tablename = "event_human_resource"
    #table = define_table(tablename,
    #                     event_id(),
    #                     human_resource_id(),
    #                     *s3_meta_fields())

    #add_component(table, event_event="event_id")

    #crud_strings[tablename] = Storage(
    #    title_create = T("Add Human Resource"),
    #    title_display = T("Human Resource Details"),
    #    title_list = T("List Human Resources"),
    #    title_update = T("Edit Human Resource"),
    #    title_search = T("Search Human Resources"),
    #    subtitle_create = T("Add New Human Resource"),
    #    subtitle_list = T("Human Resources"),
    #    label_list_button = T("List Human Resources"),
    #    label_create_button = T("Add Human Resource"),
    #    label_delete_button = T("Remove Human Resource from this event"),
    #    msg_record_created = T("Human Resource added"),
    #    msg_record_modified = T("Human Resource updated"),
    #    msg_record_deleted = T("Human Resource removed"),
    #    msg_list_empty = T("No Human Resources currently registered in this event"))

    # ---------------------------------------------------------------------
    # Facilities
    # @ToDo: Search Widget
    #tablename = "event_site"
    #table = define_table(tablename,
    #                     event_id(),
    #                     site_id,
    #                     *s3_meta_fields())

    #table.site_id.readable = table.site_id.writable = True

    #add_component(table, event_event="event_id")

    #crud_strings[tablename] = Storage(
    #    title_create = T("Add Facility"),
    #    title_display = T("Facility Details"),
    #    title_list = T("List Facilities"),
    #    title_update = T("Edit Facility"),
    #    title_search = T("Search Facilities"),
    #    subtitle_create = T("Add New Facility"),
    #    subtitle_list = T("Facilities"),
    #    label_list_button = T("List Facilities"),
    #    label_create_button = T("Add Facility"),
    #    label_delete_button = T("Remove Facility from this event"),
    #    msg_record_created = T("Facility added"),
    #    msg_record_modified = T("Facility updated"),
    #    msg_record_deleted = T("Facility removed"),
    #    msg_list_empty = T("No Facilities currently registered in this event"))

    # ---------------------------------------------------------------------
    # Tasks
    # Tasks are to be assigned to resources managed by this EOC
    # @ToDo: Search Widget
    #if has_module("project"):
    #    load("project_task")
    #    # Retrieve from the Global
    #    task_id = s3.task_id

    #    tablename = "event_task"
    #    table = define_table(tablename,
    #                         event_id(),
    #                         task_id(),
    #                         *s3_meta_fields())

    #    add_component(table, event_event="event_id")

    #    crud_strings[tablename] = Storage(
    #        title_create = T("Add Task"),
    #        title_display = T("Task Details"),
    #        title_list = T("List Tasks"),
    #        title_update = T("Edit Task"),
    #        title_search = T("Search Tasks"),
    #        subtitle_create = T("Add New Task"),
    #        subtitle_list = T("Tasks"),
    #        label_list_button = T("List Tasks"),
    #        label_create_button = T("Add Task"),
    #        label_delete_button = T("Remove Task from this event"),
    #        msg_record_created = T("Task added"),
    #        msg_record_modified = T("Task updated"),
    #        msg_record_deleted = T("Task removed"),
    #        msg_list_empty = T("No Tasks currently registered in this event"))

    # ---------------------------------------------------------------------
    # Activities
    # Activities are completed by external Organisations
    # @ToDo: Search Widget
    #if has_module("project"):
    #    load("project_activity")
    #    # Retrieve from the Global
    #    activity_id = s3.activity_id

    #    tablename = "event_activity"
    #    table = define_table(tablename,
    #                         event_id(),
    #                         activity_id(),
    #                         *s3_meta_fields())

    #    add_component(table, event_event="event_id")

    #    crud_strings[tablename] = Storage(
    #        title_create = T("Add Activity"),
    #        title_display = T("Activity Details"),
    #        title_list = T("List Activities"),
    #        title_update = T("Edit Activity"),
    #        title_search = T("Search Activities"),
    #        subtitle_create = T("Add New Activity"),
    #        subtitle_list = T("Activities"),
    #        label_list_button = T("List Activities"),
    #        label_create_button = T("Add Activity"),
    #        label_delete_button = T("Remove Activity from this event"),
    #        msg_record_created = T("Activity added"),
    #        msg_record_modified = T("Activity updated"),
    #        msg_record_deleted = T("Activity removed"),
    #        msg_list_empty = T("No Activities currently registered in this event"))

    # ---------------------------------------------------------------------
    # Map Config
    #tablename = "event_config"
    #table = define_table(tablename,
    #                     event_id(),
    #                     config_id(),
    #                     *s3_meta_fields())

    #add_component(table,
    #              event_event=dict(joinby="event_id",
    #                               multiple=False))

    #crud_strings[tablename] = Storage(
    #    title_create = T("Add Map Configuration"),
    #    title_display = T("Map Configuration Details"),
    #    title_list = T("List Map Configurations"),
    #    title_update = T("Edit Map Configuration"),
    #    title_search = T("Search Map Configurations"),
    #    subtitle_create = T("Add New Map Configuration"),
    #    subtitle_list = T("Map Configurations"),
    #    label_list_button = T("List Map Configurations"),
    #    label_create_button = T("Add Map Configuration"),
    #    label_delete_button = T("Remove Map Configuration from this event"),
    #    msg_record_created = T("Map Configuration added"),
    #    msg_record_modified = T("Map Configuration updated"),
    #    msg_record_deleted = T("Map Configuration removed"),
    #    msg_list_empty = T("No Map Configurations currently registered in this event"))

    # Pass variables back to global scope (s3.*)
    return dict(event_id = event_id,
                incident_id = incident_id
                )

# Provide a handle to this load function
loader(event_tables,
       "event_event",
       "event_incident",
       #"event_human_resource",
       #"event_site",
       # Optional Tables in here cause problems
       #"event_task",
       #"event_activity",
       #"event_config",
       )

# ---------------------------------------------------------------------
def event_event_duplicate(job):
    """
      This callback will be called when importing records
      it will look to see if the record being imported is a duplicate.

      @param job: An S3ImportJob object which includes all the details
                  of the record being imported

      If the record is a duplicate then it will set the job method to update

      Rules for finding a duplicate:
       - If the name exists then it's a duplicate
    """
    # ignore this processing if the id is set
    if job.id:
        return
    if job.tablename == "event_event":
        table = job.table
        if "name" in job.data:
            name = job.data.name
        else:
            return

        query = (table.name == name)
        _duplicate = db(query).select(table.id,
                                      limitby=(0, 1)).first()
        if _duplicate:
            job.id = _duplicate.id
            job.data.id = _duplicate.id
            job.method = job.METHOD.UPDATE

configure("event_event", resolve=event_event_duplicate)

def event_incident_duplicate(job):
    """
      This callback will be called when importing records
      it will look to see if the record being imported is a duplicate.

      @param job: An S3ImportJob object which includes all the details
                  of the record being imported

      If the record is a duplicate then it will set the job method to update

      Rules for finding a duplicate:
       - If the Event & Name exists then it's a duplicate
    """
    # ignore this processing if the id is set
    if job.id:
        return
    if job.tablename == "event_incident":
        table = job.table
        if "name" in job.data and \
           "event_id" in job.data:
            name = job.data.name
            event_id = job.data.event_id
        else:
            return

        query = (table.name == name) & \
                (table.event_id == event_id)
        _duplicate = db(query).select(table.id,
                                      limitby=(0, 1)).first()
        if _duplicate:
            job.id = _duplicate.id
            job.data.id = _duplicate.id
            job.method = job.METHOD.UPDATE

configure("event_incident", resolve=event_incident_duplicate)

# END =========================================================================
