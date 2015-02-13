# -*- coding: utf-8 -*-

"""
    Volunteer Management System
"""

module = "vol"

# Component definitions should be outside conditional model loads
add_component("vol_assignment",
              req_req = dict(joinby="req_id",
                             multiple=True))
add_component("vol_application",
              req_req = dict(joinby="req_id",
                             multiple=True))

# This resource is usually only accessed via a custom form
add_component("vol_organisation",
              pr_pentity = dict(joinby=super_key(db.pr_pentity),
                                multiple=False))

add_component("vol_skill",
              pr_person = "person_id")


def vol_tables():

    # LA-specific
    # Other Orgs affiliated with
    # Also in controllers/default.py
    vol_orgs = ("ARC", "CERT", "DHV", "LAW", "VCLA")

    tablename = "vol_organisation"
    table = define_table(tablename,
                         pe_id,
                         organisations_id(requires = IS_NULL_OR(
                                            IS_ONE_OF(db, "org_organisation.id",
                                                      "%(name)s",
                                                      multiple=True,
                                                      filterby="acronym",
                                                      filter_opts=vol_orgs,
                                                      orderby="org_organisation.name",
                                                      sort=True)),
                                         comment = DIV(_class="tooltip",
                                            _title="%s|%s" % (T("Organizations"),
                                                              T("Other Organizations that you are registered with.")))
                                        ),
                         *s3_meta_fields())

    # -------------------------------------------------------------------------
    # A Volunteer's Skillset
    # -------------------------------------------------------------------------
    load("hrm_skill")
    multi_skill_id = s3.multi_skill_id

    tablename = "vol_skill"
    table = define_table(tablename,
                         person_id(ondelete = "CASCADE"),
                         multi_skill_id(label="%s (%s)" % (T("Skills"),
                                                           T("select all that apply"))),
                         comments(label = T("Please enter any other additional skills & information"),
                                  comment = DIV(_class="tooltip",
                                    _title="%s|%s" % (T("Additional Skills & Information"),
                                                      T("Please enter any other additional skills you have which are not on the list or other information which may be relevant for your volunteer assignments, such as any special needs that you have.")))),
                         *s3_meta_fields())

    crud_strings[tablename] = Storage(
        title_create = T("Add Skills"),
        title_display = T("Skills Details"),
        title_list = T("Skills"),
        title_update = T("Update Skills"),
        title_search = T("Search Skills"),
        subtitle_create = T("Add Skills"),
        subtitle_list = T("Skills"),
        label_list_button = T("List Skills"),
        label_create_button = T("Add Skills"),
        label_delete_button = T("Delete Skills"),
        msg_record_created = T("Skills added"),
        #msg_record_created = T("Thankyou - registration is complete"),
        msg_record_modified = T("Skills updated"),
        msg_record_deleted = T("Skills deleted"),
        msg_list_empty = T("Currently no skills defined"))

    # -------------------------------------------------------------------------
    # A Volunteer's Emergency Contacts
    # -------------------------------------------------------------------------
    emergency_contact_name = S3ReusableField("emergency_contact_name",
                                             label = T("Emergency Contact Name"),
                                             requires = IS_NOT_EMPTY(),
                                             )
    emergency_contact_relationship = S3ReusableField("emergency_contact_relationship",
                                                     label = T("Emergency Contact Relationship"),
                                                     requires = IS_NOT_EMPTY(),
                                                     )
    emergency_contact_phone = S3ReusableField("emergency_contact_phone",
                                              label = T("Emergency Contact Phone Number"),
                                              requires = shn_single_phone_requires,
                                              )
    def emergency_contact_fields():
        return (emergency_contact_name(),
                emergency_contact_relationship(),
                emergency_contact_phone())

    tablename = "vol_contact"
    table = define_table(tablename,
                         person_id(ondelete = "CASCADE"),
                         *(emergency_contact_fields() + s3_meta_fields()))

    crud_strings[tablename] = Storage(
        title_create = T("Add Emergency Contact"),
        title_display = T("Emergency Contact Details"),
        title_list = T("Emergency Contacts"),
        title_update = T("Update Emergency Contact"),
        title_search = T("Search Emergency Contacts"),
        subtitle_create = T("Add Emergency Contact"),
        subtitle_list = T("Emergency Contacts"),
        label_list_button = T("List Emergency Contacts"),
        label_create_button = T("Add Emergency Contact"),
        label_delete_button = T("Delete Emergency Contact"),
        msg_record_created = T("Emergency Contact added"),
        msg_record_modified = T("Emergency Contact updated"),
        msg_record_deleted = T("Emergency Contact deleted"),
        msg_list_empty = T("Currently no emergency contact defined"))

    # -------------------------------------------------------------------------
    def vol_contact_onaccept(form):
        """
            Assign ownership of contacts to the volunteer
        """

        try:
            record_id = form.vars.id
        except:
            return

        table = db.vol_contact
        query = (table.id == record_id)
        person = db(query).select(table.person_id,
                                  limitby=(0, 1)).first()
        try:
            person_id = person.person_id
        except:
            # Error!
            return

        # Assign ownership of assignments to the assigned volunteer
        user_id = auth.s3_person_to_user(person_id)
        if user_id:
            db(query).update(owned_by_user=user_id)

        return

    configure("vol_contact",
              onaccept = vol_contact_onaccept,
              )

    # -------------------------------------------------------------------------
    # Application
    # -------------------------------------------------------------------------
    load("req_req")
    req_id = s3.req_id

    tablename = "vol_application"
    table = define_table(tablename,
                         req_id(empty = False),
                         Field("number", "integer",
                               default = 1,
                               label = T("Number of Volunteers to Commit"),
                               requires = IS_NOT_EMPTY(),
                               readable = False,
                               writable = False, # Only for Volunteer Organisations
                               ),
                         person_id(ondelete = "CASCADE"), # Volunteer or Team Leader (latter populated onaccept)
                         organisation_id(readable = False,
                                         writable = False), # Only for Volunteer Organisations
                         human_resource_id("team_leader_id",
                                           label = T("Team Leader"),
                                           readable = False,
                                           writable = False, # Only for Volunteer Organisations
                                           ),
                         #Field("team_leader",
                         #      readable = False,
                         #      writable = False,
                         #      label = T("Team Leader Name")),
                         #Field("team_leader_contact",
                         #      readable = False,
                         #      writable = False,
                         #      label = T("Team Leader Contact"),
                         #      comment = DIV(_class="tooltip",
                         #        _title="%s|%s" % (T("Team Leader Contact"),
                         #                          T("Cell phone &/or Email")))),
                         *(emergency_contact_fields() + s3_meta_fields()))

    crud_strings[tablename] = Storage(
        title_create = T("Add Application"),
        title_display = T("Application Details"),
        title_list = T("Applications"),
        title_update = T("Edit Application"),
        title_search = T("Search Applications"),
        subtitle_create = T("Add Application"),
        subtitle_list = T("Applications"),
        label_list_button = T("List Applications"),
        label_create_button = T("Add Application"),
        label_delete_button = T("Delete Application"),
        #msg_record_created = T("Thankyou for your application - please check back soon to see if you have been succesful."),
        msg_record_created = T("Application created"),
        msg_record_modified = T("Application updated"),
        msg_record_deleted = T("Application cancelled"),
        msg_list_empty = T("Currently no applications defined"))

    # -------------------------------------------------------------------------
    def application_onvalidation(form):
        """
            Check for DSW (interactive forms only)
        """
        if isinstance(form, FORM):
            # Interactive form
            _vars = request.post_vars

            checkCommitmentLevels(request.args[0], None, form)

            # Check for DSW
            if "dsw" not in _vars or _vars.dsw != "on":
                form.errors.dsw = T("You must agree to these conditions to commit to a Request for Volunteers")

        return

    # -------------------------------------------------------------------------
    def application_onaccept_interactive(form):
        """
            For interactive forms:
                Copy Emergency Contacts to Profile
                Check whether full
                if full:
                    Give the applicant a suitable message
                else:
                    Add a vol_assignment record
                    Update the req's commit qty
                    If req now full then mail out Roster
                    Show them the Assignment details
            Not used for non-interactive requests as:
                These shouldn't have redirects
                Sync won't be happy if we create assignments onaccept at each end

            Called from req() controller
        """

        atable = db.vol_application
        if auth.user.organisation_id:
            # OrgVol: Populate person_id() from team_leader_id()
            table = db.hrm_human_resource
            query = (table.id == form.vars.team_leader_id)
            person = db(query).select(table.person_id,
                                      limitby=(0, 1)).first()
            if person:
                query = (atable.id == form.vars.id)
                db(query).update(person_id = person.person_id)
        else:
            # Vol: Update Emergency Contacts
            # Find record to update
            person = s3_logged_in_person()
            table = db.vol_contact
            query = (table.person_id == person)
            contacts = db(query).select(table.id,
                                        limitby=(0, 1)).first()
            if contacts:
                # Update
                db(query).update(emergency_contact_name = form.vars.emergency_contact_name,
                                 emergency_contact_relationship = form.vars.emergency_contact_relationship,
                                 emergency_contact_phone = form.vars.emergency_contact_phone)
            else:
                # Create
                table.insert(person_id = person,
                             emergency_contact_name = form.vars.emergency_contact_name,
                             emergency_contact_relationship = form.vars.emergency_contact_relationship,
                             emergency_contact_phone = form.vars.emergency_contact_phone)

        rtable = db.req_req
        query = (atable.id == form.vars.id) & \
                (rtable.id == atable.req_id)
        record = db(query).select(rtable.id,
                                  rtable.request_number,
                                  limitby=(0, 1)).first()
        if record:
            # Check whether the assignment has spaces
            (result, assign) = application_manage_totals(record.request_number, s3_logged_in_person(), form.vars)
            if result == False:
                session.warning = T("Unfortunately this Request is already full - please apply for another")
                redirect(URL(c="vol", f="req_skill"))
            else:
                if result == "Full":
                    # Mail out Volunteer Roster
                    current.s3task.async("vol_rostermail", [record.id])
                session.confirmation = T("Your application for this Volunteer Assignment has been successful")
                redirect(URL(c="vol", f="req", args=["assignment", assign]))
        return

    # -------------------------------------------------------------------------
    def application_manage_totals(req_num, person_id, vars):
        """
            Check whether full
            if full:
                return false
            else:
                Add a vol_assignment record
                Update the req's commit qty
                If req now full then return "Full"
                Else return True
        """

        rrtable = db.req_req
        rstable = db.req_req_skill
        vastable = db.vol_assignment
        query = (rrtable.request_number == req_num) & \
                (rrtable.id == rstable.req_id)
        record = db(query).select(rrtable.id,
                                  rstable.quantity,
                                  rstable.quantity_commit,
                                  limitby=(0, 1)).first()
        if record and \
           record.req_req_skill.quantity > record.req_req_skill.quantity_commit:

            req_id = record.req_req.id

            _req = db(rrtable.id == req_id).select(rrtable.request_for_id,
                                                   limitby=(0, 1)).first()
            if _req:
                report_to = _req.request_for_id
            else:
                report_to = None

            if person_id != None:
                # Only do this for non-CSV imports
                # Lookup the Point of Contact

                # Add Assignment
                if auth.user.organisation_id:
                    assign = vastable.insert(req_id = req_id,
                                             person_id = person_id,
                                             organisation_id = auth.user.organisation_id,
                                             team_leader_id = vars.team_leader_id,
                                             number = vars.number,
                                             report_to_id = report_to)
                else:
                    assign = vastable.insert(req_id = req_id,
                                             person_id = person_id,
                                             report_to_id = report_to)
            else: # for CSV imports
                db(vastable.req_id == req_id).update(report_to_id = report_to,
                                                     created_by = vastable.person_id,
                                                     modified_by = vastable.person_id,
                                                     owned_by_user = vastable.person_id,
                                                     )
                assign = None

            # Calculate the number of people assigned to a request
            query = (vastable.req_id == req_id) & \
                    (vastable.deleted == False)
            rows = db(query).select(vastable.number)
            qty = 0
            for row in rows:
                qty = qty + row.number
            if qty >= record.req_req_skill.quantity:
                commit_status = 2 # Complete (defined in models/req.py)
            else:
                commit_status = 1 # Partial
            db(rstable.req_id == req_id).update(quantity_commit = qty)
            db(rrtable.id == req_id).update(commit_status = commit_status)
            if commit_status == 2:
                return ("Full", assign)
            else:
                return (True, assign)
        return (False, False)

    # -------------------------------------------------------------------------
    def vol_application_onaccept_csv(req_csv):
        from csv import DictReader
        csvReader = DictReader(open(req_csv, "r"))
        for r in csvReader:
            # this relies on the named field being in the import file
            type = r["Request Type"]
            reqNum = r["Request Number"]
            if type == "Volunteer":
                application_manage_totals(reqNum, None, None)

    def vol_application_tidyup():
        vtable = db.vol_application
        ctable = db.vol_contact
        ptable = db.pr_person
        atable = db.auth_user
        query = (vtable.person_id == ptable.id) & \
                (ptable.uuid == atable.person_uuid)
        records = db(query).select(atable.id,
                                   vtable.person_id,
                                   )
        for record in records:
            auth_id = record.auth_user.id
            person_id = record.vol_application.person_id

            query = (vtable.person_id == person_id)
            db(query).update(owned_by_user = auth_id)

            query = (ctable.person_id == person_id)
            db(query).update(owned_by_user = auth_id)

    configure(tablename,
              onvalidation = application_onvalidation,
              listadd = False,
              )

    # -------------------------------------------------------------------------
    # Assignment
    # -------------------------------------------------------------------------
    vol_evaluation_opts = {
        1: "1 - %s" % T("Unsatisfactory"),
        2: "2 - %s" % T("Poor"),
        3: "3 - %s" % T("Average"),
        4: "4 - %s" % T("Good"),
        5: "5 - %s" % T("Excellent"),
    }
    def rep_yes_no(value):
        if value: 
            return T("Yes")
        else:
            return T("No")
    is_staff = s3_has_role(STAFF)
    tablename = "vol_assignment"
    table = define_table(tablename,
                         req_id(ondelete = "SET NULL",
                                readable = False,
                                writable = False,
                                ),
                         # Copy the req details to these fields so that we can retain them when the request is deleted (e.g. during archival)
                         Field("task",
                               label = T("Task"),
                               readable = not is_staff,
                               writable = False,
                               ),
                         Field("location",
                               label = T("Location"),
                               readable = not is_staff,
                               writable = False,
                               ),
                         Field("date_required",
                               label = T("Date Required"),
                               readable = not is_staff,
                               writable = False,
                               ),
                         person_id(ondelete = "CASCADE"),
                         # Only visible to STAFF
                         organisation_id(readable = is_staff,
                                         writable = is_staff),
                         Field("number", "integer",
                               default = 1,
                               # @ToDo: This should vary on Role: Staff or OrgAdmin
                               label = T("Number of Volunteers to Commit"),
                               readable = is_staff,
                               writable = is_staff,
                               ),
                         # Only visible for Volunteer Organisations
                         human_resource_id("team_leader_id",
                                           label = T("Team Leader"),
                                           readable = False,
                                           writable = False,
                                           ),
                         # Only visible to STAFF
                         Field("checkin", "datetime",
                               label = T("Check-in"),
                               represent = s3_utc_represent,
                               requires = [IS_EMPTY_OR(IS_UTC_DATETIME_IN_RANGE(
                                             maximum=request.utcnow,
                                             error_message="%s %%(max)s!" %
                                                 T("Enter a valid past date")))],
                               widget = S3DateTimeWidget(past=2160, # 3 months
                                                         future=0),
                               readable = is_staff,
                               writable = is_staff,
                               ),
                         Field("checkout", "datetime",
                               label = T("Check-out"),
                               represent = s3_utc_represent,
                               requires = [IS_EMPTY_OR(IS_UTC_DATETIME_IN_RANGE(
                                             maximum=request.utcnow,
                                             error_message="%s %%(max)s!" %
                                                 T("Enter a valid past date")))],
                               widget = S3DateTimeWidget(past=2160, # 3 months
                                                         future=0),
                               readable = is_staff,
                               writable = is_staff,
                               ),
                         # Visible to ALL - but only if vol has checked-in and (checked-out or time > time_until)
                         Field("task_evaluation", "integer",
                               label = T("Volunteer Evaluation"),
                               represent = lambda i: vol_evaluation_opts.get(i,NONE),
                               requires = IS_NULL_OR(IS_IN_SET(vol_evaluation_opts)),
                               writable = False,
                               ),
                         comments("task_eval_comments",
                                  label = T("Volunteer Comments"),
                                  comment=DIV(_class="tooltip",
                                     _title="%s|%s" % (T("Volunteer Comments"),
                                                       T("Additional comments on this assignment."))),
                                  writable = False,
                                  ),
                         # Only visible to STAFF
                         # Defaults to version in Request
                         human_resource_id("report_to_id",
                                           label = T("Reported To"),
                                           readable = is_staff,
                                           writable = is_staff
                                           ),
                         Field("evaluation", "integer",
                               label = T("EMD Evaluation"),
                               represent = lambda i: vol_evaluation_opts.get(i, NONE) ,
                               requires = IS_NULL_OR(IS_IN_SET(vol_evaluation_opts)),
                               readable = is_staff,
                               writable = is_staff,
                               ),
                         comments(label = T("EMD Comments"),
                                  readable = is_staff,
                                  writable = is_staff,
                                  comment=DIV(_class="tooltip",
                                     _title="%s|%s" % (T("EMD Comments"),
                                                       T("Additional comments on the performance of the volunteer on this assignment."))),
                                  ),
                         Field("dnr", "boolean",
                               default = True,
                               label = T("Would you work with this volunteer again?"),
                               readable = is_staff,
                               writable = is_staff,
                               # @ToDo: Not good to have this default to Off - easily skipped!
                               represent = rep_yes_no,
                               ),
                         Field("emailed", "datetime",
                               readable = False,
                               writable = False,
                               ),
                         *s3_meta_fields())

    crud_strings[tablename] = Storage(
        title_create = T("Add Assignment"),
        title_display = T("Assignment Details"),
        title_list = T("Assignments"),
        #title_update = T("Edit Assignment"),
        title_update = T("Evaluation of Assignment") if is_staff else T("Please rate this volunteer assignment"),
        title_search = T("Search Assignments"),
        subtitle_create = T("Add Assignment"),
        subtitle_list = T("Assignments"),
        label_list_button = T("List Assignments"),
        label_create_button = T("Add Assignment"),
        label_delete_button = T("Delete Assignment"),
        msg_record_created = T("Assignment created"),
        msg_record_modified = T("Assignment updated"),
        msg_record_deleted = T("Assignment deleted"),
        msg_no_match = T("Currently no assignments defined"),
        msg_list_empty = T("Currently no assignments defined"))

    if is_staff:
        # Use default fields
        pass
    else:
        if s3_has_role(ORG_VOL):
            list_fields = ["id",
                           "task",
                           "location",
                           "date_required",
                           (T("Reported To"), "report_to_id"),
                           "number",
                           "checkin",
                           "checkout",
                           ]
        else:
            # Volunteer
            list_fields = ["id",
                           "task",
                           "location",
                           "date_required",
                           (T("Reported To"), "report_to_id"),
                           "checkin",
                           "checkout",
                           ]

        configure(tablename,
                  list_fields = list_fields,
                  )

    # -------------------------------------------------------------------------
    def assignment_onvalidate(form):

        if isinstance(form, FORM):
            # Interactive form
            try:
                req_id = form.record.req_id
                vas_id = form.record.id
            except:
                req_id = request.args[0]
                if len(request.args) > 2:
                    vas_id = request.args[2]
                else:
                    vas_id = None
            checkCommitmentLevels(req_id, vas_id, form)

    # -------------------------------------------------------------------------
    def checkCommitmentLevels(req_id, vas_id, form):
        _vars = request.post_vars
        if _vars.number:
            # Not an Evaluation
            commit = int(_vars.number)
            # Get the number required
            rstable = db.req_req_skill
            record = db(rstable.req_id == req_id).select(rstable.quantity,
                                                         limitby=(0, 1)).first()
            needed = record.quantity
            # Get the number already committed (excluding this record)
            vastable = db.vol_assignment
            if vas_id == None:
                query = (vastable.req_id == req_id) & \
                        (vastable.deleted == False)
            else:
                query = (vastable.req_id == req_id) & \
                        (vastable.deleted == False) & \
                        (vastable.id != vas_id)
            rows = db(query).select(vastable.number)
            qty = 0
            for row in rows:
                qty = qty + row.number
            available = needed - qty
            # Check the number available against the number committed
            if available < commit:
                form.vars.number = available
                session.information = T("Only %s volunteers are required. The commitment total has been reduced." % available)

    # -------------------------------------------------------------------------
    def assignment_onaccept(form):
        """
            Assign ownership of assignments to the assigned volunteer
            Populate the 'Virtual' fields
            Update the req_commit status
        """

        try:
            record_id = form.vars.id
            person_id = form.vars.person_id
        except:
            # Arrived from 'check-in now' action button
            # no action required
            return

        vastable = db.vol_assignment
        rstable = db.req_req_skill
        query = (vastable.id == record_id)
        if person_id:
            # Assign ownership of assignments to the assigned volunteer
            user_id = auth.s3_person_to_user(person_id)
            if user_id:
                db(query).update(owned_by_user=user_id)

        # Update the req's commit status
        query = query & (rstable.req_id == vastable.req_id)
        record = db(query).select(rstable.req_id,
                                  rstable.quantity,
                                  limitby=(0, 1)).first()
        if record:
            # Calculate the number of volunteers now assigned
            req_id = record.req_id
            query = (vastable.req_id == req_id) & \
                    (vastable.deleted == False)
            rows = db(query).select(vastable.number)
            qty = 0
            for row in rows:
                qty = qty + row.number
            if qty >= record.quantity:
                commit_status = 2 # Complete (defined in models/req.py)
            else:
                commit_status = 1 # Partial
            db(rstable.req_id == req_id).update(quantity_commit = qty)
            rrtable = db.req_req
            db(rrtable.id == req_id).update(commit_status = commit_status)
            # Read the Request details
            record = db(rrtable.id == req_id).select(rrtable.date_required,
                                                     rrtable.location,
                                                     rrtable.purpose,
                                                     limitby=(0, 1)
                                                     ).first()
            # Update the 'Virtual' fields
            db(vastable.id == record_id).update(date_required = s3_utc_represent(record.date_required),
                                                location = record.location,
                                                task = record.purpose,
                                                )

    # -------------------------------------------------------------------------
    def assignment_onupdate(form):
        """
            Update Fulfilment Status based on Check-Ins

            OrgVols: Populate person_id from human_resource_id
        """

        try:
            # Interactive
            req = form.request_vars.req_id
        except:
            # Non-interactive
            req = form.vars.req_id

        table = db.vol_assignment

        # OrgVol: Populate person_id() from human_resource_id()
        query = (table.deleted == False) & \
                (table.req_id == req) & \
                (table.team_leader_id != None)
        hrs = db(query).select(table.id,
                               table.team_leader_id)
        if hrs:
            hrtable = db.hrm_human_resource
            for hr in hrs:
                query = (hrtable.id == hr.team_leader_id)
                person = db(query).select(hrtable.person_id,
                                          limitby=(0, 1)).first()
                if person:
                    query = (table.id == hr.id)
                    db(query).update(person_id = person.person_id)

        rtable = db.req_req_skill
        record = db(rtable.req_id == req).select(rtable.quantity,
                                                 rtable.quantity_fulfil,
                                                 limitby=(0, 1)).first()
        if record and \
           record.quantity > record.quantity_fulfil:
            # Update Fulfil Quantity in Req
            query = (table.req_id == req) & \
                    (table.deleted == False)
            rows = db(query).select(table.checkin,
                                    table.number)
            qty = 0
            for row in rows:
                if row.checkin:
                    qty = qty + row.number
            if qty == 0:
                fulfil_status = 0 # None (defined in models/req.py)
            elif qty >= record.quantity:
                fulfil_status = 2 # Complete (defined in models/req.py)
            else:
                fulfil_status = 1 # Partial
            db(rtable.req_id == req).update(quantity_fulfil = qty)
            db(db.req_req.id == req).update(fulfil_status = fulfil_status)

        query = (table.req_id == req) & (table.deleted == False)
        total = table.number.sum()
        qty = db(query).select(total).first()[total]
        if qty == 0:
            commit_status = 0 # None (defined in models/req.py)
        else:
            commit_status = 1 # Partial

        rtable = db.req_req
        vtable = db.req_req_skill

        db(rtable.id == req).update(commit_status = commit_status)
        db(vtable.req_id == req).update(quantity_commit = qty)

        # Redirect to correct page (req/x/assignment gives wrong one)
        configure("vol_assignment",
                        update_next = URL(c=request.controller,
                                          f="req",
                                          args=["assignment", "[id]"]))

        assignment_onaccept(form)

    # -------------------------------------------------------------------------
    def assignment_ondelete(row):
        """
            Remove Commitment
        """

        atable = db.vol_assignment
        assignment = db(atable.id == row.id).select(atable.deleted_fk,
                                                    limitby=(0, 1)).first()

        if not assignment:
            session.error = T("Assignment not found")
            return

        try:
            fk = json.loads(assignment.deleted_fk)
            fk = [k for k in fk if k["f"] == "req_id"][0]
            req_id = fk["k"]
        except:
            # either no JSON or no req_id
            return

        query = (atable.req_id == req_id) & (atable.deleted == False)
        total = atable.number.sum()
        qty = db(query).select(total).first()[total]
        if qty == 0:
            commit_status = 0 # None (defined in models/req.py)
        else:
            commit_status = 1 # Partial

        rtable = db.req_req
        vtable = db.req_req_skill

        db(rtable.id == req_id).update(commit_status = commit_status)
        db(vtable.req_id == req_id).update(quantity_commit = qty)

        crud_strings[atable._tablename].update(
            msg_record_deleted = T("Your application has been successfully withdrawn"))

    configure(tablename,
              create_onaccept = assignment_onaccept,
              delete_next = URL(c="vol", f="req_skill"),
              listadd = is_staff,
              ondelete = assignment_ondelete,
              onvalidation = assignment_onvalidate,
              update_onaccept = assignment_onupdate,
              )

    # -------------------------------------------------------------------------
    def vol_checkin(r, **attr):
        """
            Check-in Volunteer(s)
        """

        table = db.vol_assignment
        if r.component_id:
            # Single Record
            query = (table.id == r.component_id)
        else:
            # All Records which haven't yet been checked-in
            query = (table.req_id == r.id) & \
                    (table.checkin == None) & \
                    (table.deleted == False)
        db(query).update(checkin=request.utcnow)

        # Update Fulfillment Status
        form = Storage()
        form.request_vars = Storage()
        form.request_vars.req_id = r.id
        assignment_onupdate(form)

        session.confirmation = T("Checked-in succesfully")
        redirect(URL(c="vol", f="req",
                     args=[r.id, "assignment"]))

    # -------------------------------------------------------------------------
    def vol_checkout(r, **attr):
        """
            Check-out Volunteer(s)

            Send Thankyou Certificate & ask to complete evaluation
        """

        table = db.vol_assignment
        if r.component_id:
            # Single Record
            query = (table.id == r.component_id)
        else:
            # All Records which haven't yet been checked-out
            query = (table.req_id == r.id) & \
                    (table.checkout == None) & \
                    (table.deleted == False)
        db(query).update(checkout=request.utcnow)

        # Send Volunteer Certificate
        current.s3task.async("vol_certmail", [r.id])

        session.confirmation = T("Checked-out succesfully")
        redirect(URL(c="vol", f="req",
                     args=[r.id, "assignment"]))

    # -------------------------------------------------------------------------
    def req_cancel(r, **attr):
        """
            Cancel a Request
                Notify all Assigned Vols
                Free them up so they can Apply to new Requests
        """

        # Run this task async, if possible
        current.s3task.async("vol_req_cancel", [r.id])

        # Go to the main Requests page
        session.confirmation = T("Request Cancelled")
        redirect(URL(c="vol", f="req"))

    # -------------------------------------------------------------------------
    def getAddressFromSiteID(site_id, location=None):
        table = db.org_office
        srecord = db(table.id == site_id).select(table.name,
                                                 table.address,
                                                 table.postcode,
                                                 table.L3,
                                                 table.L1,
                                                 limitby=(0, 1)).first()
        if srecord:
            if location == None or location == "":
                location = srecord.name
            else:
                location = T("%(site)s in %(location)s") % dict(site = srecord.name,
                                                               location = location)
            ltable = db.gis_location
            state = db(ltable.name == srecord.L1).select(ltable.code,
                                                         limitby=(0, 1),
                                                         cache=gis.cache).first()
            if state:
                statecode = state.code
            else:
                # Not valid US data (e.g. prepopulate)
                statecode = None
            address = "%s<br/>%s<br/>%s<br/>%s" % (srecord.address,
                                                   srecord.L3,
                                                   statecode,
                                                   srecord.postcode)
        else:
            location = address = ""
        return (location, address)

    # -------------------------------------------------------------------------
    def getContactFromPersonID(person_id):
        phone = email = name = ""
        name = person_represent(person_id)
        table = db.pr_person
        pe = db(table.id == person_id).select(table.pe_id,
                                              limitby=(0, 1)).first()
        if pe:
            table = db.pr_contact
            query = (table.pe_id == pe.pe_id) & \
                    (table.contact_method.belongs(("SMS", "EMAIL")))
            contacts = db(query).select(table.contact_method,
                                        table.value)
            for contact in contacts:
                if contact.contact_method == "SMS":
                    phone = contact.value
                elif contact.contact_method == "EMAIL":
                    email = contact.value
        return (name, email, phone)

    # -------------------------------------------------------------------------
    def getContactFromHRMID(hrm_id):
        hrmtable = db.hrm_human_resource
        query = (hrmtable.id == hrm_id)
        row = db(query).select(hrmtable.person_id,
                              limitby=(0, 1)).first()
        return getContactFromPersonID(row.person_id)

    # =========================================================================
    def print_assignment(r, **attr):
        """
            Print out:
                Assignment (for Vols)
                Roster (for Site Admins)
                Volunteer Certificate
        """

        # ---------------------------------------------------------------------
        def tearOff(canvas, dataList):
            """
                Callback method to draw the tear off lines for the report
            """

            canvas.saveState()
            canvas.setDash(1,2)
            adjust = 5
            posn = dataList[0]
            width = dataList[1]
            marginL = dataList[2]
            marginR = dataList[3]
            marginB = dataList[4]
            canvas.line(-marginL - adjust,posn,width+marginR - adjust,posn)
            canvas.line(width/2 - adjust, posn, width/2 - adjust, -marginB)
            canvas.restoreState()

        # ---------------------------------------------------------------------
        def badgeLogo(canvas, dataList):
            """
                Callback method to draw the logo for the report
            """

            from PIL import Image
            pdf = dataList[0]
            top = dataList[1]
            margin = dataList[3]
            left1 = dataList[2] / 2 + margin
            left2 = dataList[2] - margin
            height = dataList[4]
            adjust = dataList[5]
            if pdf.logo and os.path.exists(pdf.logo):
                im = Image.open(pdf.logo)
                (iwidth, iheight) = im.size
                width = iwidth * (height/iheight)
                canvas.drawImage(pdf.logo,
                                 left1 + adjust,
                                 top - height - adjust,
                                 width = width,
                                 height = height)

        # ---------------------------------------------------------------------
        def pdfGridStyle(tableObj, startRow, rowCnt, endCol):
            from reportlab.lib.colors import Color
            style = [("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                     ("FONTSIZE", (0, 0), (-1, -1), tableObj.fontsize),
                     ("VALIGN", (0, 0), (-1, -1), "TOP"),
                     ("LINEBELOW", (0, 0), (endCol, 0), 1, Color(0, 0, 0)),
                     ("FONTNAME", (0, 0), (endCol, 0), "Helvetica-Bold"),
                     ("GRID", (0,0),(-1,-1),0.5,Color(0, 0, 0)),
                     ]
            return style

        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch

        # ---------------------------------------------------------------------
        def assignmentPDF(pdf, **args):
            """
                Callback to create a PDF of a Volunteer Assignment
            """

            # Set the banner
            pdf.setMargins(bottom = 0.3 * inch,
                           left = 0.4 * inch,
                           right = 0.4 * inch)
            pdf.setHeaderBanner("static/img/la/Give2LAbranding_BW.jpg")
            # Get the assignment details
            atable = db.vol_assignment
            rtable = db.req_req
            if "id" in args:
                id = args["id"]
            query = (atable.id == id) & \
                    (rtable.id == atable.req_id)
            record = db(query).select(rtable.site_id,
                                      rtable.location,
                                      rtable.request_for_id,
                                      rtable.date_required,
                                      rtable.date_required_until,
                                      rtable.purpose,
                                      rtable.comments,
                                      limitby=(0, 1)
                                      ).first()
            (location, address) = getAddressFromSiteID(record.site_id,
                                                       record.location)
            location = pdf.addParagraph(location, append=False)
            address = pdf.addParagraph(address, append=False)
            comments = record.comments
            if comments == None:
                comments = ""
            # Prevent partially-translated strings
            T = lambda str: str
            lbl_title1 = "%s:" % T("Assignment Details")
            lbl_title2 = "%s:" % T("Point of Contact")
            lbl_startTime = T("Arrival Time")
            lbl_endTime = T("Finish Time")
            lbl_meetingPoint = T("Location")
            lbl_contact = T("Contact Person")
            lbl_reportPlace = T("Contact Place")
            lbl_email = T("Email")
            lbl_phone = T("Phone Number")
            lbl_title3 = "%s:" % T("Check-in Slip")
            lbl_title4 = "%s:" % T("VOLUNTEER ID")
            lbl_volunteer = T("Volunteer")
            lbl_task = T("Task")
            lbl_task_comments = T("Comments")
            lbl_checkin = T("Check-in Time")
            lbl_checkout = T("Check-out Time")
            lbl_address = T("Address")
            lbl_emergenctContact = T("Emergency Contact")
            lbl_report_to = T("Point of Contact")
            txt_disclaimer1 = T("As a volunteer working to assist disaster survivors and in disaster recovery efforts, you will be required to fill out and sign the Give2LA Registration Forms.")
            txt_disclaimer2 = T("Please let us know in advance if you cannot report for your Volunteer Assignment by calling %(name)s on %(phone)s or via email at %(email)s.")

            cell1 = []
            heading = "<para align='CENTER'><b>%s</b></para>" % lbl_title1
            cell1.append([pdf.addParagraph(heading, append=False), ""])
            heading = "<b>%s</b>" % lbl_startTime
            data = s3_utc_represent(record.date_required)
            cell1.append([pdf.addParagraph(heading, append=False),
                          pdf.addParagraph(data, append=False)])
            heading = "<b>%s</b>" % lbl_endTime
            data = s3_utc_represent(record.date_required_until)
            cell1.append([pdf.addParagraph(heading, append=False),
                          pdf.addParagraph(data, append=False)])
            heading = "<b>%s</b>" % lbl_task
            cell1.append([pdf.addParagraph(heading, append=False),
                          pdf.addParagraph(record.purpose, append=False)])
            heading = "<b>%s</b>" % lbl_task_comments
            cell1.append([pdf.addParagraph(heading, append=False),
                          pdf.addParagraph(comments, append=False)])
            heading = "<b>%s</b>" % lbl_meetingPoint
            cell1.append([pdf.addParagraph(heading, append=False),
                          location])
            cell1.append(["", address])
            heading = "<b>%s</b>" % lbl_checkin
            cell1.append([pdf.addParagraph(heading, append=False),
                          pdf.addLine(9, append=False)])
            heading = "<b>%s</b>" % lbl_checkout
            cell1.append([pdf.addParagraph(heading, append=False),
                          pdf.addLine(9, append=False)])


            # Get the Point of Contact details
            (name, email, phone) = getContactFromHRMID(record.request_for_id)
            cell2 = []
            heading = "<para align='CENTER'><b>%s</b></para>" % lbl_title2
            cell2.append([pdf.addParagraph(heading, append=False), ""])
            heading = "<b>%s</b>" % lbl_contact
            cell2.append([pdf.addParagraph(heading, append=False),
                          pdf.addParagraph(name, append=False)])
            cell2.append(["", address])
            heading = "<b>%s</b>" % lbl_reportPlace
            cell2.append([pdf.addParagraph(heading, append=False),
                          location])
            heading = "<b>%s</b>" % lbl_email
            cell2.append([pdf.addParagraph(heading, append=False),
                          pdf.addParagraph(email, append=False)])
            heading = "<b>%s</b>" % lbl_phone
            cell2.append([pdf.addParagraph(heading, append=False),
                          pdf.addParagraph(phone, append=False)])

            # Get the Checkin slip data
            ctable = db.vol_contact
            query = (atable.id == id) & \
                    (ctable.person_id == atable.person_id)
            aprecord = db(query).select(atable.person_id,
                                        ctable.emergency_contact_name,
                                        ctable.emergency_contact_phone,
                                        limitby=(0, 1)
                                        ).first()
            if aprecord:
                # Emergency Contacts defined - should be a Vol
                (vol_name, vol_email, vol_phone) = getContactFromPersonID(aprecord.vol_assignment.person_id)
                emergency_name = aprecord.vol_contact.emergency_contact_name
                emergency_phone = aprecord.vol_contact.emergency_contact_phone
            else:
                # No Emergency Contacts defined - should be an OrgVol
                emergency_name = emergency_phone = ""
                query = (atable.id == id)
                aprecord = db(query).select(atable.person_id,
                                            atable.organisation_id,
                                            atable.number,
                                            limitby=(0, 1)).first()
                if aprecord:
                    if aprecord.organisation_id:
                        # Yes, it's an OrgVol
                        team_leader = aprecord.person_id
                        if team_leader:
                            (vol_name, vol_email, vol_phone) = getContactFromPersonID(team_leader)
                        else:
                            vol_name = vol_email = vol_phone = ""
                        otable = db.org_organisation
                        query = (otable.id == aprecord.organisation_id)
                        org = db(query).select(otable.name,
                                               limitby=(0, 1)).first()
                        if org:
                            if aprecord.number > 1:
                                vol_name = "%s (%s) + %s" % (vol_name,
                                                             org.name,
                                                             aprecord.number - 1)
                            else:
                                vol_name = "%s (%s)" % (vol_name, org.name)
                        else:
                            # We will crash later when trying to do the paragraph
                            session.error = T("Invalid data")
                            redirect(URL(f="req_skill", args=None))
                        if vol_email == "":
                            # Use the primary contact's Email/Phone
                            htable = db.hrm_human_resource
                            ptable = db.pr_person
                            ctable = db.pr_contact
                            query = (htable.organisation_id == aprecord.organisation_id) & \
                                    (ptable.id == htable.person_id) & \
                                    (ctable.pe_id == ptable.pe_id)
                            contacts = db(query).select(ctable.value,
                                                        ctable.contact_method)
                            for contact in contacts:
                                if contact.contact_method == "EMAIL":
                                    vol_email = contact.value
                                if contact.contact_method == "SMS":
                                    vol_phone = contact.value
                    else:
                        # Bad data - a simple Vol without Emergency Contacts
                        (vol_name, vol_email, vol_phone) = getContactFromPersonID(aprecord.person_id)
                else:
                    #vol_name = vol_email = vol_phone = ""
                    # We will crash later when trying to do the paragraph
                    session.error = T("Invalid data")
                    redirect(URL(f="req_skill", args=None))
            cell3 = []
            heading = "<para align='CENTER'><b>%s</b></para>" % lbl_title3
            cell3.append([pdf.addParagraph(heading, append=False), ""])
            heading = "<b>%s</b>" % lbl_volunteer
            cell3.append([pdf.addParagraph(heading, append=False),
                          pdf.addParagraph(vol_name, append=False)])
            heading = "<b>%s</b>" % lbl_task
            cell3.append([pdf.addParagraph(heading, append=False),
                          pdf.addParagraph(record.purpose, append=False)])
            #heading = "<b>%s</b>" % lbl_task_comments
            #cell3.append([pdf.addParagraph(heading, append=False),
            #              pdf.addParagraph(comments, append=False)])
            heading = "<b>%s</b>" % lbl_checkin
            cell3.append([pdf.addParagraph(heading, append=False),
                          pdf.addLine(9, append=False)])
            heading = "<b>%s</b>" % lbl_checkout
            cell3.append([pdf.addParagraph(heading, append=False),
                          pdf.addLine(9, append=False)])
            heading = "<b>%s</b>" % lbl_emergenctContact
            emContact = "%s<br/>%s" % (emergency_name,
                                       emergency_phone)
            emContact = pdf.addParagraph(emContact, append=False)
            cell3.append([pdf.addParagraph(heading, append=False),
                          emContact])

            cell4 = []
            heading = "<b>%s</b>" % lbl_title4
            cell4.append([pdf.addParagraph("", append=False),
                          pdf.addParagraph(heading, append=False)])
            #cell4.append([pdf.addParagraph(heading, append=False), ""])
            #heading = "<b>%s</b>" % lbl_volunteer
            cell4.append([pdf.addParagraph("", append=False),
                          pdf.addParagraph("<u><b>%s</u></b>" %vol_name, append=False)])
            heading = "<b>%s</b>" % lbl_report_to
            cell4.append([pdf.addParagraph(heading, append=False),
                          pdf.addParagraph(name, append=False)])
            heading = "<b>%s</b>" % lbl_task
            cell4.append([pdf.addParagraph(heading, append=False),
                          pdf.addParagraph(record.purpose, append=False)])
            #heading = "<b>%s</b>" % lbl_task_comments
            #cell4.append([pdf.addParagraph(heading, append=False),
            #              pdf.addParagraph(comments, append=False)])
            heading = "<b>%s</b>" % lbl_emergenctContact
            cell4.append([pdf.addParagraph(heading, append=False),
                          emContact])

            # Create the intermediate tables and calculate heights
            width = pdf.getPageWidth()
            height = pdf.getPageHeight()
            col2 = 20
            col1 = (width - col2) *.5
            col3 = (width - col2) *.5
            style1 = [("VALIGN", (0, 0), (-1, -1), "TOP"),
                      ("SPAN",(0, 0), (1, 0)),
                     ]
            style1logo = [("VALIGN", (0, 0), (-1, -1), "TOP")]
            style2 = [("VALIGN", (0, 0), (-1, -1), "TOP"),
                      ("SPAN",(0, 0), (1, 0)),
                      ("SPAN",(0,1),(0,2)),
                     ]
            table1 = pdf.getStyledTable(cell1, colWidths=[col1*.3, col1*.7], style=style1)
            table2 = pdf.getStyledTable(cell2, colWidths=[col3*.3, col3*.7], style=style2)
            style1_1 = [("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("BOX", (0, 0), (0, 0), 1, "#000000"),
                        ("BOX", (2, 0), (2, 0), 1, "#000000"),
                        ("TOPPADDING",(0, 0), (-1, -1), 10),
                       ]

            tableA = pdf.getStyledTable([[table1, "", table2]],
                                       colWidths=[col1, col2, col3],
                                       style=style1_1
                                      )
            table3 = pdf.getStyledTable(cell3, colWidths=[col1*.3, col1*.7], style=style1)
            table4 = pdf.getStyledTable(cell4, colWidths=[col3*.3, col3*.7], style=style1logo)
            tableC = pdf.getStyledTable([[table3, "", table4]],
                                       colWidths=[col1, col2, col3],
                                       style=style1_1)
            (w1, h1) = pdf.getTableMeasurements(tableA)
            (w2, h3) = pdf.getTableMeasurements(tableC)
            h2 = height - h1[0] - h3[0] - 40

            # push data to the pdf document
            pdf.subTitle = vol_name
            pdf.content.append(tableA)
            pdf.addSpacer(10)
            styleB = [("VALIGN", (0, 0), (-1, -1), "TOP"),
                     ("BOX", (0, 0), (-1, -1), 1, "#000000"),
                    ]
            disclaimer = pdf.addParagraph("%s<br/><br/>%s" % (txt_disclaimer1,
                                                              txt_disclaimer2 % dict(name = name,
                                                                                     phone = phone,
                                                                                     email = email)),
                                                              append=False)
            tableB = pdf.getStyledTable([[disclaimer]],
                                        colWidths=[width],
                                        rowHeights=[h2],
                                        style=styleB)
            pdf.content.append(tableB)
            pdf.addSpacer(10)
            pdf.content.append(tableC)
            # need to add the overlay at the end so that the canvas origin
            # is at the bottom of the printed page
            pdf.addOverlay(tearOff, (h3[0]+5, width, 0.4*inch, 0.4*inch, inch+20))
            pdf.addOverlay(badgeLogo, (pdf, h3[0], width, 5, .6*inch, 4))

        # ---------------------------------------------------------------------
        def rosterPDF(pdf, **args):
            """
                Callback to generate the PDF of the Roster
            """

            # Set the banner
            pdf.setMargins(left=0.4*inch, right = 0.4*inch)
            pdf.setHeaderBanner("static/img/la/Give2LAbranding_BW.jpg")
            # Prevent partially-translated strings
            T = lambda str: str
            # Get the request data
            rtable = db.req_req
            etable = db.event_event
            if "id" in args:
                id = args["id"]
            query = (rtable.id == id) & \
                    (etable.id == rtable.event_id)
            fieldList = [etable.name,
                         rtable.request_number,
                         rtable.purpose,
                         rtable.site_id,
                         rtable.request_for_id,
                         rtable.date_required,
                         rtable.date_required_until,
                         ]
            record = db(query).select(limitby=(0, 1),
                                      *fieldList).first()
            rdata = []
            rheadings = []
            rlist = []
            for field in fieldList:
                rheadings.append(field.label)
                text = s3mgr.represent(field,
                                       record=record,
                                       strip_markup=True,
                                       non_xml_output=True
                                       )
                if text == "-":
                    # NONE
                    text = ""
                if (field.name == "request_for_id"):
                    (name, email, phone) = getContactFromHRMID(record.req_req.request_for_id)
                    rlist.append(name)
                    text = pdf.addSpacer(30, False)
                    txt = T("Correct, if necessary")
                    rheadings.append("*GREY %s" % txt)
                rlist.append(text)
            rheadings[0] = T("Event")
            rdata = [rheadings] + [rlist]

            # Get the roster and the evaluation data
            table = db.vol_assignment
            fieldList = [table.organisation_id,
                         table.person_id,
                         table.checkin,
                         table.checkout,
                         table.evaluation,
                         table.comments,
                         ]
            data = []
            edata = []
            headings = [T("No.")]
            for field in fieldList:
                if (field.name == "evaluation") \
                or (field.name == "comments"):
                    # Skip
                    continue
                headings.append(field.label)
            headings.append(T("Signature"))
            data.append(headings)
            records = pdf.resource.select(table.ALL,
                                          orderby=fieldList[1])
            cnt = 0
            for record in records:
                cnt += 1
                person = ""
                person_label = table.person_id.label
                evaluation = ""
                eval_comments = ""
                row = [str(cnt)]
                for field in fieldList:
                    text = s3mgr.represent(field,
                                           record=record,
                                           strip_markup=True,
                                           non_xml_output=True
                                           )
                    if field.name == "person_id":
                        if record.organisation_id:
                            person_label = table.organisation_id.label
                            number = record.number
                            if number > 1:
                                text = "%s (+%s)" % (text, number - 1)
                            organisation = organisation_represent(record.organisation_id)
                            person = "%s - %s" % (organisation, text)
                        else:
                            # Single Person
                            person = text
                    if (field.name == "checkin") and text == "-":
                        #text = "*GREY YYYY-MM-DD HH:MM"
                        text = "                    "
                    elif (field.name == "checkout") and text == "-":
                        #text = "*GREY YYYY-MM-DD HH:MM"
                        text = "                    "
                    elif (field.name == "evaluation"):
                        if text == "None":
                            text = "*GREY 1  2  3  4  5"
                        evaluation = text
                        continue
                    elif (field.name == "comments"):
                        if text == "None":
                            eval_comments = pdf.addSpacer(80, False)
                        else:
                            comment = record.comments
                            eval_comments = pdf.addParagraph(comment,
                                                             append=False)
                        continue
                    row.append(text)
                row.append("                              ")
                data.append(row)
                edata.append([[person_label, person],
                              [table.evaluation.label, evaluation],
                              [table.comments.label, ""],
                              [eval_comments, ""],
                             ]
                            )

            # Push data to the PDF document
            pdf.addrHeader(raw_data = rdata,)
            pdf.addSpacer(10)
            pdf.addTable(raw_data = data, style=pdfGridStyle,)
            pdf.changePageTitle(T("Volunteer Roster - Evaluation"))
            pdf.throwPageBreak()
            # Add raw tables for the evaluation
            etable = []
            cnt = 0
            line = []
            for row in edata:
                style = [("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                         ("VALIGN", (0, 0), (-1, -1), "TOP"),
                         ("SPAN", (0, 3), (1, 3)),
                        ]
                cnt += 1
                person = pdf.getStyledTable(row, style=style)
                if cnt % 2 == 0:
                    line.append("") # Blank for padding between results
                    line.append(person)
                    etable.append(line)
                    line = []
                else:
                    line.append(person)
            if cnt %2 == 1:
                    line.append("") # Blank for padding between results
                    line.append("") # For the odd person
                    etable.append(line)
            if etable != []:
                style = [("VALIGN", (0, 0), (-1, -1), "TOP"),
                         ("LINEBELOW", (0, 0), (0, -1), 1, "#000000"),
                         ("LINEBELOW", (2, 0), (2, -1), 1, "#000000"),
                         ("TOPPADDING", (0, 0), (-1, -1), 10),
                         ("BACKGROUND",
                         (1, 0), (1, -1), "#EEEEEE"),
                        ]
                width = pdf.getPageWidth()
                col2 = 20
                col3= col1 = (width - col2) / 2
                table = pdf.getStyledTable(etable,
                                           colWidths=[col1, col2, col3],
                                           style=style
                                          )
                pdf.content.append(table)
        # end of nested function rosterPDF


        # ---------------------------------------------------------------------
        def volCertBorder(canvas, doc):
            """
                This method will add a border to the page.
                It is a callback method and will not be called directly
            """

            from PIL import Image
            folder = request.folder
            canvas.saveState()
            canvas.setStrokeColorRGB(0, 0, 0)
            inset = 3
            canvas.rect(inset,
                        inset,
                        doc.pagesize[0] - 2 * inset,
                        doc.pagesize[1] - 2 * inset,
                        stroke=1,
                        fill=0)
            canvas.setStrokeColorRGB(0.5, 0.5, 0.5)
            inset = 6
            canvas.rect(inset,
                        inset,
                        doc.pagesize[0] - 2 * inset,
                        doc.pagesize[1] - 2 * inset,
                        stroke=1,
                        fill=0)
            image = "static/img/la/city_seal.png"
            citySeal = os.path.join(folder,image)
            if os.path.exists(citySeal):
                im = Image.open(citySeal)
                (iwidth, iheight) = im.size
                height = 0.85 * inch
                width = iwidth * (height / iheight)
                canvas.drawImage(citySeal,
                         (doc.pagesize[0] - width) / 2,
                         doc.pagesize[1] - 1.1 * inch,
                         width = width,
                         height = height)
            image = "static/img/la/EMD-logo.png"
            EMDLogo = os.path.join(folder, image)
            if os.path.exists(EMDLogo):
                im = Image.open(EMDLogo)
                (iwidth, iheight) = im.size
                height = 0.85 * inch
                width = iwidth * (height / iheight)
                canvas.drawImage(EMDLogo,
                         (doc.pagesize[0] - width) / 2 - 2.2*inch,
                         0.5*inch,
                         width = width,
                         height = height)
            canvas.restoreState()

        # ---------------------------------------------------------------------
        def colCertBorder(canvas, doc):
            """
                This method will add a border to the page.
                It is a callback method and will not be called directly
            """

            folder = request.folder
            canvas.saveState()
            image = "static/img/la/cert_border.png"
            banner = os.path.join(folder, image)
            if os.path.exists(banner):
                canvas.drawImage(banner,
                                 0,
                                 0,
                                 width = doc.pagesize[0],
                                 height = doc.pagesize[1])
            image = "static/img/la/city_seal.png"
            citySeal = os.path.join(folder, image)
            if os.path.exists(citySeal):
                canvas.drawImage(citySeal,
                                 1 * inch,
                                 1 * inch,
                                 width = 1.5 * inch,
                                 height = 1.5 * inch)
            image = "static/img/la/LA-BlackWhite.JPG"
            cityLogo = os.path.join(folder, image)
            if os.path.exists(cityLogo):
                canvas.drawImage(cityLogo,
                                 doc.pagesize[0] - 2.5 * inch,
                                 1 * inch,
                                 width = 1.5 * inch,
                                 height = 1.5 * inch)
            image = "static/img/la/signature.png"
            signature = os.path.join(folder, image)
            if os.path.exists(signature):
                canvas.drawImage(signature,
                                 (doc.pagesize[0])/2.0 - 2.25 * inch,
                                 1 * inch,
                                 width = 4.5 * inch,
                                 height = 1.5 * inch)
            canvas.restoreState()

        # ---------------------------------------------------------------------
        def volunteerCertificate(pdf, **args):
            """
                Callback to generate the PDF of the Volunteer Certificate
            """

            pdf.setMargins(top=1.1*inch,
                           bottom=0.5*inch,
                           left=0.4*inch,
                           right = 0.4*inch)
            # Prevent partially-translated strings
            T = lambda str: str
            # Standard lines of text
            line1 = "ERIC GARCETTI"
            line2 = "Mayor"
            line3A = "THE CITY OF LOS ANGELES"
            line3B = "AND THE EMERGENCY MANAGEMENT DEPARTMENT"
            line4 = "CERTIFICATE OF APPRECIATION"
            line5 = "AWARDED TO"
            line6 = "In Recognition of their Outstanding Contribution and Support"
            line7 = "From a Grateful Community!"
            line8 = "Awarded this %(day)s day of %(month)s, %(year)s"
            line9 = "James G. Featherstone"
            line10 = "General Manager"
            line11 = "Emergency Management Department"

            from reportlab.lib.styles import ParagraphStyle
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            from reportlab.lib.colors import Color

            fontname = "static/fonts/la/Engravers.ttf"
            font = os.path.join(request.folder, fontname)
            pdfmetrics.registerFont(TTFont("CertFont", font))

            stylesheet=getSampleStyleSheet()
            normalStyle = stylesheet["Normal"]
            style = normalStyle
            styleA = ParagraphStyle(name="StyleA",
                                    parent=normalStyle,
                                    fontName="CertFont",
                                    fontSize = 8,
                                    leading = 12,
                                    borderPadding = (10, 2, 10, 2),
                                    alignment = 1,
                                    )
            styleB = ParagraphStyle(name="StyleB",
                                    parent=normalStyle,
                                    fontName="CertFont",
                                    fontSize = 16,
                                    textColor = Color(0.5, 0.5, 0.1),
                                    leading = 20,
                                    borderPadding = (8, 2, 8, 2),
                                    alignment = 1,
                                    )
            styleC = ParagraphStyle(name="StyleC",
                                    parent=normalStyle,
                                    fontName="CertFont",
                                    fontSize = 22,
                                    textColor = Color(0.5, 0.5, 0.1),
                                    leading = 26,
                                    borderPadding = (8, 2, 8, 2),
                                    alignment = 1,
                                    )
            styleD = ParagraphStyle(name="StyleD",
                                    parent=normalStyle,
                                    fontName="CertFont",
                                    fontSize = 14,
                                    leading = 16,
                                    borderPadding = (8, 2, 8, 2),
                                    alignment = 1,
                                    )
            styleE = ParagraphStyle(name="StyleE",
                                    parent=normalStyle,
                                    fontName="CertFont",
                                    fontSize = 24,
                                    leading = 30,
                                    borderPadding = (8, 2, 8, 2),
                                    alignment = 1,
                                    )
            styleF = ParagraphStyle(name="StyleF",
                                    parent=normalStyle,
                                    fontName="CertFont",
                                    fontSize = 12,
                                    textColor = Color(0.5, 0.5, 0.1),
                                    leading = 16,
                                    borderPadding = (8, 2, 8, 2),
                                    alignment = 1,
                                    )

            vtable = db.vol_assignment
            if "id" in args:
                id = args["id"]
            vrecord = db(vtable.id == id).select(vtable.person_id,
                                                 vtable.req_id,
                                                 vtable.checkin,
                                                 vtable.checkout,
                                                 limitby=(0, 1)
                                                 ).first()
            person_id = vrecord.person_id
            name = person_represent(person_id)
            try:
                startDay = vrecord.checkin.strftime("%d %b %Y")
                endDay = vrecord.checkout.strftime("%d %b %Y")
                if startDay == endDay:
                    date = T("On %(startDay)s") % dict(startDay=StartDay)
                else:
                    date = T("During %(startDay)s and %(endDay)s") % dict(startDay=StartDay,
                                                                          endDay=endDay)
            except:
                date = None
            load("event_event")
            rtable = db.req_req
            etable = db.event_event
            query = (rtable.id == vrecord.req_id) & \
                    (rtable.event_id == etable.id)
            erecord = db(query).select(etable.name,
                                       limitby=(0, 1)
                                       ).first()
            event = erecord.name
            now = datetime.datetime.now()
            today = {"day": now.strftime("%d"),
                     "month": now.strftime("%B"),
                     "year": now.strftime("%Y"),
                     }

            pdf.setLandscape()
            pdf.addParagraph(line1, styleA)
            pdf.addParagraph(line2, styleA)
            pdf.addSpacer(40)
            pdf.addParagraph(line3A, styleB)
            pdf.addParagraph(line3B, styleB)
            pdf.addSpacer(20)
            pdf.addParagraph(line4, styleC)
            pdf.addSpacer(30)
            pdf.addParagraph(line5, styleD)
            pdf.addSpacer(20)
            pdf.addParagraph(name, styleE)
            pdf.addSpacer(20)
            pdf.addParagraph(line6, styleF)
            pdf.addSpacer(10)
            if date != None:
                pdf.addParagraph("%s on %s" % (event, date), styleD)
            else:
                pdf.addParagraph(event, styleD)
            pdf.addSpacer(10)
            pdf.addParagraph(line7, styleF)
            pdf.addSpacer(10)
            pdf.addParagraph(line8 % today, styleD)
            pdf.addSpacer(75)
            pdf.addParagraph(line9, styleA)
            pdf.addParagraph(line10, styleA)
            pdf.addParagraph(line11, styleA)
        # end of nested function volunteerCertificate()

        T = current.T
        if r.component_id:
            table = db.vol_assignment
            record = db(table.id == r.component_id).select(table.req_id,
                                                           table.checkout,
                                                           #table.task_evaluation,
                                                           limitby=(0, 1)
                                                           ).first()
            req_id = record.req_id
            if record.checkout != None: #and record.task_evaluation != None:
                configure("vol_assignment",
                          callback = volunteerCertificate,
                          formname = str(T("Volunteer Certificate")),
                          header = volCertBorder,
                          footer = lambda x, y: None,
                          )
            else:
                configure("vol_assignment",
                          callback = assignmentPDF,
                          formname = str(T("Volunteer Assignment Form")),
                          footer = lambda x, y: None
                          )

            # Volunteer Assignment (for Vol)
            args = [str(req_id), "assignment", str(r.component_id)]
            r = s3base.S3Request(s3mgr,
                                 prefix="req",
                                 name="req",
                                 args=args,
                                 extension="pdf")
            if not r.http:
                # Async
                r.http = "GET"
            return r()
        else:
            # Roster (for Site Admin)
            if r.id:
                args = [str(r.id), "assignment"]
            else:
                args = "assignment"
            r = s3base.S3Request(s3mgr,
                                 prefix="req",
                                 name="req",
                                 args=args,
                                 extension="pdf",
                                 http="GET")
            if r.component.count():
                configure("vol_assignment",
                          callback = rosterPDF,
                          formname = str(T("Volunteer Roster - Attendance"))
                          )
                if not r.http:
                    # Async
                    r.http = "GET"
                return r()
            else:
                session.error = T("No Assignments yet")
                try:
                    request.args.remove("print")
                except ValueError:
                    # Being run from a Task where there are no real request.args
                    pass
                redirect(URL(args=request.args))

    
    set_method("req", "req",
               component_name="assignment",
               method="checkin",
               action=vol_checkin)
    set_method("req", "req",
               component_name="assignment",
               method="checkout",
               action=vol_checkout)
    set_method("req", "req",
               method="cancel",
               action=req_cancel)
    set_method("req", "req",
               component_name="assignment",
               method="print",
               action=print_assignment)

    # -------------------------------------------------------------------------
    # The Email address(es) to which the Roster should be mailed
    #
    tablename = "vol_rostermail"
    table = define_table(tablename,
                         Field("email", requires=IS_EMAIL()),
                         *s3_meta_fields())

    crud_strings[tablename] = Storage(
        title_create = T("Add Roster Email Address"),
        title_display = T("Roster Email Address Details"),
        title_list = T("Roster Email Addresses"),
        title_update = T("Edit Roster Email Address"),
        title_search = T("Search Roster Email Addresses"),
        subtitle_create = T("Add Roster Email Address"),
        subtitle_list = T("Roster Email Addresses"),
        label_list_button = T("List Roster Email Addresses"),
        label_create_button = T("Add Roster Email Address"),
        label_delete_button = T("Remove Roster Email Address"),
        msg_record_created = T("Roster Email Address added"),
        msg_record_modified = T("Roster Email Address updated"),
        msg_record_deleted = T("Roster Email Address removed"),
        msg_list_empty = T("Currently no Roster Email Addresses defined"))

    # -------------------------------------------------------------------------
    # Pass variables back to global scope (response.s3.*)
    return dict(
        application_onaccept_interactive = application_onaccept_interactive,
        vol_application_onaccept_csv = vol_application_onaccept_csv,
        vol_application_tidyup = vol_application_tidyup,
        vol_rostermail = vol_rostermail,
        print_assignment = print_assignment
        )

# Provide a handle to this load function
loader(vol_tables,
       "vol_organisation",
       "vol_skill",
       "vol_contact",
       "vol_application",
       "vol_assignment",
       "vol_rostermail")

# =============================================================================
# Tasks to be callable async
# =============================================================================
def vol_rostermail(id, user_id=None):
    """
        Mail out Volunteer Roster

        Designed to be run Async
    """

    if user_id:
        # Authenticate
        auth.s3_impersonate(user_id)

    # Find the Roster
    load("vol_assignment")
    table = db.vol_assignment
    roster = db(table.req_id == id).select(table.id,
                                           limitby=(0, 1)).first()
    if not roster:
        # Error
        return

    # Emails configured to always receive copies of the Roster
    table = db.vol_rostermail
    emails = db(table.deleted == False).select(table.email)

    # Send to the Point of Contact & Requester
    rtable = db.req_req
    rquery = (rtable.id == id)
    req = db(rquery).select(rtable.request_number,
                            rtable.requester_id,
                            rtable.request_for_id,
                            limitby=(0, 1)).first()
    try:
        req_num = req.request_number
    except:
        # Error
        req_num = "Request"
        _emails = []
    else:
        htable = db.hrm_human_resource
        ptable = db.pr_person
        ctable = db.pr_contact
        hrms = (req.requester_id, req.request_for_id)
        query = (htable.id.belongs(hrms)) & \
                (ptable.id == htable.person_id) & \
                (ctable.pe_id == ptable.pe_id) & \
                (ctable.contact_method == "EMAIL")
        #pes = db(query).select(ptable.pe_id)
        _emails = db(query).select(ctable.value)

    # Create the PDF
    r = s3mgr.parse_request("req", "req",
                            args=[str(id), "assignment"],
                            http="GET")
    pdf = s3.print_assignment(r)
    pdfpath = os.path.join(request.folder,
                           "uploads",
                           "%s.pdf" % s3_filename(req_num))
    try:
        fp = open(pdfpath, "wb")
    except IOError as e:
        if e.errno == errno.EACCESS:
            session.error = T("%(filename)s not writable!") % dict(filename=pdfpath)
            return
        # Not a permission error.
        raise
    else:
        with fp:
            fp.write(pdf)
            fp.close()

    # Craft the message (English, not localised)
    attachment = mail.Attachment(pdfpath)
    subject = "Volunteer Roster for %s" % req_num
    url = "%s/vol/req/%s/assignment" % (s3.base_url, id)
    message = """Attached is the current Volunteer Roster for %s.
The latest version can be found on the Sahana site: %s""" % (req_num, url)

    # Requester & ReportTo
    #for pe_id in pes:
    #    # @ToDo: API for Attachments
    #    # Add a message to the Outbox
    #    msg.send_email_by_pe_id(pe_id,
    #                            subject=subject,
    #                            message=message,
    #                            system_generated=True)
    #    # Trigger a queue run
    #    msg.process_outbox(contact_method="EMAIL")
    for email in _emails:
        # Send directly
        msg.send_email(email.value, subject, message,
                       attachments=[attachment])

    # Rostermails
    for email in emails:
        # @ToDo: API for non pe_id
        # Send directly
        msg.send_email(email.email, subject, message,
                       attachments=[attachment])
    # Update time sent
    db(rquery).update(emailed=request.utcnow)


# -----------------------------------------------------------------------------
def vol_certmail(id, user_id=None):
    """
        Mail out Volunteer Certificate

        Designed to be run Async
    """

    if user_id:
        # Authenticate
        auth.s3_impersonate(user_id)

    # Get the Assignments for this req which have checked-out but haven't yet been emailed
    load("vol_assignment")
    table = db.vol_assignment
    query = (table.deleted == False) & \
            (table.req_id == id) & \
            (table.checkout != None) & \
            (table.emailed == None)

    assigns = db(query).select(table.id,
                               table.emailed,
                               table.person_id)

    if not assigns:
        return

    # For each assignment
    for assign in assigns:
        # Lookup the email:
        ptable = db.pr_person
        ctable = db.pr_contact
        query = (ptable.id == assign.person_id) & \
                (ctable.pe_id == ptable.pe_id) & \
                (ctable.contact_method == "EMAIL")
        email = db(query).select(ctable.value,
                                 limitby=(0, 1)).first()
        if not email:
            continue
        # Generate the PDF
        r = s3mgr.parse_request("req", "req",
                                args=["assignment", str(assign.id)],
                                http="GET")
        pdf = s3.print_assignment(r)
        pdfpath = os.path.join(request.folder,
                               "uploads",
                               "%s.pdf" % s3_filename(email.value))
        try:
            fp = open(pdfpath, "wb")
        except IOError as e:
            if e.errno == errno.EACCESS:
                session.error = T("%s not writable!" % pdfpath)
                return
            # Not a permission error.
            raise
        else:
            with fp:
                fp.write(pdf)
                fp.close()

        # Craft the message
        attachment = mail.Attachment(pdfpath)
        subject = T("Thankyou from %(system_name)s") % \
            dict(system_name=system_name)
        message = T("Thankyou for volunteering for the City of Los Angeles. Here is a certificate in appreciation of your efforts. Please login to the site to provide your evaluation of this volunteer assignment: %(url)s") % \
            dict(url="%s/vol/req/assignment/%s" % (s3.base_url,
                                                   assign.id))
        # @ToDo: API for Attachments
        # Send directly
        msg.send_email(email.value, subject, message,
                       attachments=[attachment])

# -----------------------------------------------------------------------------
def vol_req_cancel(id, user_id=None):
    """
        Cancel a Volunteer Request

        Designed to be run Async
    """

    if user_id:
        # Authenticate
        auth.s3_impersonate(user_id)

    # Load models
    load("vol_assignment")

    # (soft) Delete the Request Skills
    rtable = db.req_req_skill
    db(rtable.req_id == id).update(deleted=True)

    # (soft) Delete the Request
    rtable = db.req_req
    db(rtable.id == id).update(deleted=True)

    # Remove all Assignments (to free up their time)
    table = db.vol_assignment
    query = (table.req_id == id)
    db(query).update(deleted=True)

    # Notify all Assigned Volunteers
    ptable = db.pr_person
    query = query & \
            (ptable.id == table.person_id) & \
            (rtable.id == table.req_id)
    rows = db(query).select(ptable.pe_id,
                            rtable.purpose)
    subject = "Give2LA Volunteer Assignment cancelled"
    message = "Apologies for the inconvenience. Give2LA Volunteer Assignment has been cancelled: '%s'. Please do not attend the site. You may apply for an alternative assignment via the website: %s. Many thanks for your support." % \
        (rows.first().req_req.purpose,
         deployment_settings.get_base_public_url())
    for row in rows:
        msg.send_by_pe_id(row.pr_person.pe_id,
                          subject,
                          message,
                          system_generated=True)


tasks["vol_rostermail"] = vol_rostermail
tasks["vol_certmail"] = vol_certmail
tasks["vol_req_cancel"] = vol_req_cancel

# END =========================================================================
