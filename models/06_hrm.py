# -*- coding: utf-8 -*-

"""
    Human Resource Management
"""

module = "hrm"

# =========================================================================
# Human Resource
#
# People who are either Staff or Volunteers
#
# @ToDo: Allocation Status for Events (link table)
#

# NB These numbers are hardcoded into KML Export stylesheet
hrm_type_opts = {
    1: T("staff"),
    2: T("volunteer")
}

hrm_status_opts = {
    1: T("active"),
    2: T("obsolete") # retired is a better term?
}

tablename = "hrm_human_resource"
table = define_table(tablename,
                     super_link(db.sit_trackable),
                     # Administrative data
                     organisation_id(empty = False,
                                     widget = S3OrganisationAutocompleteWidget(default_from_profile=True),
                                     ),
                     person_id(comment = None,
                               ondelete = "CASCADE",
                               requires = IS_ADD_PERSON_WIDGET(),
                               widget = S3AddPersonWidget(select_existing = False),
                               ),
                     Field("type", "integer",
                           default = 1,
                           label = T("Type"),
                           represent = lambda opt: \
                             hrm_type_opts.get(opt,
                                               UNKNOWN_OPT),
                           requires = IS_IN_SET(hrm_type_opts,
                                                zero=None),
                           readable=False,
                           writable=False,
                           ),
                     #Field("code", label=T("Staff ID")),
                     Field("job_title", label=T("Job Title")),
                     Field("focal_point", "boolean",
                           label=T("Focal Point"),
                           comment = DIV(_class="tooltip",
                                         _title="%s|%s" % (T("Focal Point"),
                                                           T("Should receive notifications of new volunteer opportunities for this Organization")))),
                     # Current status
                     Field("status", "integer",
                           requires = IS_IN_SET(hrm_status_opts,
                                                zero=None),
                           readable=False,
                           writable=False,
                           default = 1,
                           label = T("Status"),
                           represent = lambda opt: \
                            hrm_status_opts.get(opt,
                                                UNKNOWN_OPT)),
                     # Base location + Site
                     location_id(label=T("Base Location"),
                                 readable=False,
                                 writable=False),
                     site_id,
                     *s3_meta_fields())

table.site_id.readable = False
table.site_id.writeable = False

# -------------------------------------------------------------------------
def hrm_human_resource_represent(id,
                                 show_link = False,
                                 none_value = NONE
                                 ):
    """
        Representation of human resource records
        @ToDo: This function will not work if the human_resource doesn't have
               an organisation_id (which shouldn't happen for properly-entered data)
    """

    repr_str = none_value
    htable = db.hrm_human_resource
    ptable = db.pr_person
    otable = db.org_organisation

    query = (htable.id == id) & \
            (ptable.id == htable.person_id)
    row = db(query).select(htable.job_title,
                           otable.name,
                           otable.acronym,
                           ptable.first_name,
                           ptable.middle_name,
                           ptable.last_name,
                           left=otable.on(otable.id == htable.organisation_id),
                           limitby=(0, 1)).first()
    if row:
        org = row[str(otable)]
        if org.acronym:
            repr_str = ", %s" % org.acronym
        elif org.name:
            repr_str = ", %s" % org.name
        else:
            repr_str = ""

        hr = row[str(htable)]
        if hr.job_title:
            repr_str = ", %s%s" % (hr.job_title, repr_str)
        person = row[str(ptable)]
        repr_str = "%s%s" % (vita.fullname(person), repr_str)
    if show_link:
        local_request = request
        local_request.extension = "html"
        return A(repr_str,
                 _href = URL(r = local_request,
                             c = "hrm",
                             f = "human_resource",
                             args = [id]
                             )
                 )
    else:
        return repr_str

s3.hrm_human_resource_represent = hrm_human_resource_represent

hrm_human_resource_requires = IS_NULL_OR(IS_ONE_OF(db,
                                "hrm_human_resource.id",
                                hrm_human_resource_represent,
                                orderby="hrm_human_resource.type"))

ADD_HUMAN_RESOURCE = T("Add Human Resource")

# Used by Scenarios, Events, Tasks & RAT
human_resource_id = S3ReusableField("human_resource_id",
                                    db.hrm_human_resource,
                                    sortby = ["type", "status"],
                                    requires = hrm_human_resource_requires,
                                    represent = hrm_human_resource_represent,
                                    #widget = S3AutocompleteOrAddWidget(
                                    #    autocomplete_widget = S3SearchAutocompleteWidget(tablename="hrm_human_resource",
                                    #        represent=lambda id: \
                                    #            hrm_human_resource_represent(id,
                                    #                                         none_value = None),
                                    #    ),
                                    #    add_widget = S3AddObjectWidget(
                                    #        form_url = URL(c="hrm",
                                    #                       f="create_inline",
                                    #                       vars=dict(format="inner_form")
                                    #                    ),
                                    #        table_name="hrm_human_resource",
                                    #        # this is not a good way
                                    #        # there needs to be a single representation
                                    #        # field that multiple widgets can share
                                    #        dummy_field_selector = (
                                    #            lambda table_name, field_name:
                                    #                'input[name="%s_search_simple_simple"]' % field_name
                                    #        ),
                                    #        on_show = "$('div.form-container[fieldname=\"request_for_id\"]').hide()",
                                    #        on_hide = "$('div.form-container[fieldname=\"request_for_id\"]').show()",
                                    #    )
                                    #),
                                    label = T("Human Resource"),
                                    ondelete = "CASCADE")
# For pickup by RAT
s3.human_resource_id = human_resource_id

def human_resource_contact(hr_id, contact_method):
    htable = db.hrm_human_resource
    ptable = db.pr_person
    ctable = db.pr_contact
    query = ( ( htable.id == hr_id ) & \
              ( ptable.id == htable.person_id ) & \
              ( ctable.pe_id == ptable.pe_id ) & \
              ( ctable.contact_method == contact_method)
            )
    contact = db(query).select(ctable.value,
                               limitby=(0, 1)).first()
    if contact:
        return contact.value
    else:
        return NONE

class human_resource_virtualfields(dict, object):
    def phone(self):
        return human_resource_contact(self.hrm_human_resource.id,"SMS")
    def email(self):
        return human_resource_contact(self.hrm_human_resource.id,"EMAIL")


table.virtualfields.append(human_resource_virtualfields())

# -------------------------------------------------------------------------
def human_resource_search_simple_widget(type):
    return s3base.S3SearchSimpleWidget(
                name = "human_resource_search_simple_%s" % type,
                label = T("Name"),
                comment = T("To search by person name, enter any of the first, middle or last names, separated by spaces. You may use % as wildcard. Press 'Search' without input to list all persons."),
                field = ["person_id$first_name",
                         "person_id$middle_name",
                         "person_id$last_name",
                         "person_id$occupation"]
              )

human_resource_search = s3base.S3Search(
    simple=( human_resource_search_simple_widget("simple") ),
    advanced=(human_resource_search_simple_widget("advanced"),
              s3base.S3SearchOptionsWidget(
                name="human_resource_search_org",
                label=T("Organization"),
                comment=T("Search by organization."),
                field=["organisation_id"],
                represent ="%(name)s",
                cols = 3
              ),
              s3base.S3SearchSimpleWidget(
                name="human_resource_jobtitle",
                label=T("Job Title"),
                comment=T("To search by job title, enter any portion of the title. You may use % as wildcard."),
                field=["job_title"]
              ),
              s3base.S3SearchLocationWidget(
                name="human_resource_search_map",
                label=T("Map"),
              ),
              s3base.S3SearchSkillsWidget(
                name="human_resource_skills",
                label=T("Skills"),
                field=["skill_id"]
              ),
    ))

# -------------------------------------------------------------------------
def hrm_human_resource_deduplicate(item):
    """
        HR record duplicate detection, used for the deduplicate hook

        @param item: the S3ImportItem to check
    """

    if item.tablename == "hrm_human_resource":

        hrtable = db.hrm_human_resource

        data = item.data

        person_id = data.person_id
        org = "organisation_id" in data and data.organisation_id

        # This allows only one HR record per person and organisation,
        # if multiple HR records of the same person with the same org
        # are desired, then this needs an additional criteria in the
        # query (e.g. job title, or type):

        query = (hrtable.deleted != True) & \
                (hrtable.person_id == person_id)
        if org:
            query = query & \
                (hrtable.organisation_id == org)
        row = db(query).select(hrtable.id,
                               limitby=(0, 1)).first()
        if row:
            item.id = row.id
            item.method = item.METHOD.UPDATE

configure("hrm_human_resource",
          resolve=hrm_human_resource_deduplicate)

# -------------------------------------------------------------------------
def hrm_update_staff_role(record, user_id):
    """
        Set/retract the Org/Site staff role

        @param record: the hrm_human_resource record
        @param user_id: the auth_user record ID of the person the
                        record belongs to.
    """

    htable = db.hrm_human_resource
    utable = auth.settings.table_user
    mtable = auth.settings.table_membership

    org_role = record.owned_by_organisation
    fac_role = record.owned_by_facility

    if record.deleted:
        try:
            fk = json.loads(record.deleted_fk)
            organisation_id = fk.get("organisation_id", None)
            site_id = fk.get("site_id", None)
            person_id = fk.get("person_id", None)
        except:
            return
    else:
        organisation_id = record.get("organisation_id", None)
        site_id = record.get("site_id", None)
        person_id = record.get("person_id", None)

    if record.deleted or record.status != 1:
        remove_org_role = True
        if org_role:
            if organisation_id and person_id:
                # Check whether the person has another active
                # HR record in the same organisation
                query = (htable.person_id == person_id) & \
                        (htable.organisation_id == organisation_id) & \
                        (htable.id != record.id) & \
                        (htable.status == 1) & \
                        (htable.deleted != True)
                if db(query).select(htable.id, limitby=(0, 1)).first():
                    remove_org_role = False
            if remove_org_role:
                query = (mtable.user_id == user_id) & \
                        (mtable.group_id == org_role)
                db(query).delete()
        remove_fac_role = True
        if fac_role:
            if site_id and person_id:
                # Check whether the person has another active
                # HR record at the same site
                query = (htable.person_id == person_id) & \
                        (htable.site_id == site_id) & \
                        (htable.id != record.id) & \
                        (htable.status == 1) & \
                        (htable.deleted != True)
                if db(query).select(htable.id, limitby=(0, 1)).first():
                    remove_fac_role = False
            if remove_fac_role:
                query = (mtable.user_id == user_id) & \
                        (mtable.group_id == fac_role)
                db(query).delete()
    else:
        if org_role:
            query = (mtable.user_id == user_id) & \
                    (mtable.group_id == org_role)
            role = db(query).select(limitby=(0, 1)).first()
            if not role:
                mtable.insert(user_id = user_id,
                              group_id = org_role)
        if fac_role:
            query = (mtable.user_id == user_id) & \
                    (mtable.group_id == fac_role)
            role = db(query).select(limitby=(0, 1)).first()
            if not role:
                mtable.insert(user_id = user_id,
                              group_id = fac_role)

# -------------------------------------------------------------------------
def hrm_human_resource_onaccept(form):
    """ On-accept routine for HR records """

    ptable = db.pr_person
    utable = auth.settings.table_user
    mtable = db.auth_membership
    htable = db.hrm_human_resource

    # Get the full record
    if form.vars.id:
        record = htable[form.vars.id]
    else:
        return

    data = Storage()

    # For Staff, update the location ID from the selected site
    if record.type == 1 and record.site_id:
        table = db.org_site
        query = (table._id == record.site_id)
        site = db(query).select(table.location_id,
                                limitby=(0, 1)).first()
        if site:
            data.location_id = site.location_id

    # Add record owner (user)
    query = (ptable.id == record.person_id) & \
            (utable.person_uuid == ptable.uuid)
    user = db(query).select(utable.id,
                            utable.organisation_id,
                            limitby=(0, 1)).first()
    if user:
        user_id = user.id
        data.owned_by_user = user.id

    if not data:
        return
    record.update_record(**data)

    if record.organisation_id:
        if user and not user.organisation_id:
            # Set the Organisation in the Profile, if not already set
            query = (utable.id == user.id)
            db(query).update(organisation_id=record.organisation_id)
        if user:
            # Set/retract the staff role
            hrm_update_staff_role(record, user_id)

# -------------------------------------------------------------------------
def hrm_human_resource_ondelete(record):
    """ On-delete routine for HR records """

    ptable = db.pr_person
    utable = db.auth_user

    user = None
    if record.id and record.deleted:
        try:
            fk = json.loads(record.deleted_fk)
            person_id = fk.get("person_id", None)
        except:
            return
        if not person_id:
            return

        query = (ptable.id == person_id) & \
                (utable.person_uuid == ptable.uuid)
        user = db(query).select(utable.id,
                                limitby=(0, 1)).first()
    if not user:
        return
    else:
        user_id = user.id
        # Set/retract the staff role
        hrm_update_staff_role(record, user_id)

configure(tablename,
          super_entity = db.sit_trackable,
          deletable = False,
          search_method = human_resource_search,
          onaccept = hrm_human_resource_onaccept,
          ondelete = hrm_human_resource_ondelete,
          list_fields = ["person_id",
                         (T("Phone"),"phone"),
                         (T("Email"),"email"),
                         "job_title",
                         "organisation_id",
                         #"site_id",
                         ])

# Add Staff as component of Organisations & Facilities
add_component(table,
              org_organisation="organisation_id",
              org_site=super_key(db.org_site),
              )

# =========================================================================
# Skills
#
def skills_tables():
    """ Load the HRM Skills Tables when needed """

    tablename = "hrm_skill_type"
    table = define_table(tablename,
                         Field("name", notnull=True, unique=True,
                               length=64,
                               label=T("Name")),
                         comments(),
                         *s3_meta_fields())

    crud_strings[tablename] = Storage(
        title_create = T("Add Skill Type"),
        title_display = T("Details"),
        title_list = T("Skill Type Catalog"),
        title_update = T("Edit Skill Type"),
        title_search = T("Search Skill Types"),
        subtitle_create = T("Add Skill Type"),
        subtitle_list = T("Skill Types"),
        label_list_button = T("List Skill Types"),
        label_create_button = T("Add Skill Type"),
        label_delete_button = T("Delete Skill Type"),
        msg_record_created = T("Skill Type added"),
        msg_record_modified = T("Skill Type updated"),
        msg_record_deleted = T("Skill Type deleted"),
        msg_list_empty = T("Currently no entries in the catalog"))

    label_create = crud_strings[tablename].label_create_button
    skill_type_id = S3ReusableField("skill_type_id", db.hrm_skill_type,
                                    sortby = "name",
                                    label = T("Skill Type"),
                                    requires = IS_NULL_OR(IS_ONE_OF(db,
                                                                    "hrm_skill_type.id",
                                                                    "%(name)s")),
                                    represent = lambda id: \
                                        (id and [db.hrm_skill_type[id].name] or [NONE])[0],
                                    comment = DIV(A(label_create,
                                                    _class="colorbox",
                                                    _href=URL(c="hrm",
                                                              f="skill_type",
                                                              args="create",
                                                              vars=dict(format="popup")),
                                                    _target="top",
                                                    _title=label_create),
                                                  DIV(DIV(_class="tooltip",
                                                          _title="%s|%s" % (label_create,
                                                                            T("Add a new skill type to the catalog."))))),
                                    ondelete = "RESTRICT")


    # ---------------------------------------------------------------------
    tablename = "hrm_skill"
    table = define_table(tablename,
                         skill_type_id(empty=False),
                         Field("name", notnull=True, unique=True,
                               length=64,    # Mayon compatibility
                               label=T("Name")),
                         comments(),
                         *s3_meta_fields())

    crud_strings[tablename] = Storage(
        title_create = T("Add Skill"),
        title_display = T("Skill Details"),
        title_list = T("Skill Catalog"),
        title_update = T("Edit Skill"),
        title_search = T("Search Skills"),
        subtitle_create = T("Add Skill"),
        subtitle_list = T("Skills"),
        label_list_button = T("List Skills"),
        label_create_button = T("Add Skill"),
        label_delete_button = T("Delete Skill"),
        msg_record_created = T("Skill added"),
        msg_record_modified = T("Skill updated"),
        msg_record_deleted = T("Skill deleted"),
        msg_list_empty = T("Currently no entries in the catalog"))

    if auth.s3_has_role(ADMIN):
        label_create = crud_strings[tablename].label_create_button
        skill_help = DIV(A(label_create,
                           _class="colorbox",
                           _href=URL(c="hrm",
                                     f="skill",
                                     args="create",
                                    vars=dict(format="popup")),
                           _target="top",
                           _title=label_create))
    else:
        skill_help = DIV(_class="tooltip",
                         _title="%s|%s" % (T("Skill"),
                         T("Enter some characters to bring up a list of possible matches")))

    skill_id = S3ReusableField("skill_id", db.hrm_skill,
                    sortby = "name",
                    label = T("Skill"),
                    requires = IS_NULL_OR(IS_ONE_OF(db,
                                                    "hrm_skill.id",
                                                    "%(name)s",
                                                    sort=True)),
                    represent = lambda id: \
                        (id and [db.hrm_skill[id].name] or [T("None")])[0],
                    comment = skill_help,
                    ondelete = "RESTRICT",
                    # Comment this to use a Dropdown & not an Autocomplete
                    widget = S3AutocompleteWidget("hrm",
                                                  "skill")
                    )

    def hrm_multi_skill_represent(opt):
        """
            Skill representation
            for multiple=True options
        """
        if isinstance(opt, Row):
            return T(opt.name)
        else:
            table = db.hrm_skill
            set = db(table.id > 0).select(table.id,
                                          table.name).as_dict()

            if isinstance(opt, (list, tuple)):
                opts = opt
                vals = [str(T(set.get(o)["name"])) for o in opts]
            elif isinstance(opt, int):
                opts = [opt]
                vals = str(T(set.get(opt)["name"]))
            else:
                return T("No Skills Required")

            if len(opts) > 1:
                vals = ", ".join(vals)
            else:
                vals = len(vals) and vals[0] or T("No Skills Required")
            return vals

    multi_skill_id = S3ReusableField("skill_id", "list:reference hrm_skill",
                    sortby = "name",
                    label = T("Skills"),
                    requires = IS_NULL_OR(IS_ONE_OF(db,
                                                    "hrm_skill.id",
                                                    hrm_multi_skill_represent,
                                                    sort=True,
                                                    multiple=True)),
                    represent = hrm_multi_skill_represent,
                    #comment = skill_help,
                    ondelete = "RESTRICT",
                    widget = S3MultiSelectWidget()
                    )
    
    configure(tablename,
              orderby = table.name
              )

    # Pass variables back to global scope (response.s3.*)
    return dict(skill_id = skill_id,
                multi_skill_id = multi_skill_id,
                hrm_multi_skill_represent = hrm_multi_skill_represent
                )

# Provide a handle to this load function
loader(skills_tables, "hrm_skill_type",
                      "hrm_skill",
                      )

def hrm_skill_duplicate(job):
    """
      This callback will be called when importing records
      it will look to see if the record being imported is a duplicate.

      @param job: An S3ImportJob object which includes all the details
                  of the record being imported

      If the record is a duplicate then it will set the job method to update

      Rules for finding a duplicate:
       - Look for a record with the same name, ignoring case
    """
    # ignore this processing if the id is set
    if job.id:
        return
    if job.tablename == "hrm_skill":
        table = job.table
        if "name" in job.data:
            name = job.data.name
        else:
            return

        query = (table.name.lower().like('%%%s%%' % name.lower()))
        _duplicate = db(query).select(table.id,
                                      limitby=(0, 1)).first()
        if _duplicate:
            job.id = _duplicate.id
            job.data.id = _duplicate.id
            job.method = job.METHOD.UPDATE

configure("hrm_skill",
          resolve=hrm_skill_duplicate)

def hrm_skill_type_duplicate(job):
    """
      This callback will be called when importing records
      it will look to see if the record being imported is a duplicate.

      @param job: An S3ImportJob object which includes all the details
                  of the record being imported

      If the record is a duplicate then it will set the job method to update

      Rules for finding a duplicate:
       - Look for a record with the same name, ignoring case
    """
    # ignore this processing if the id is set
    if job.id:
        return
    if job.tablename == "hrm_skill_type":
        table = job.table
        name = "name" in job.data and job.data.name

        query = (table.name.lower().like('%%%s%%' % name.lower()))
        _duplicate = db(query).select(table.id,
                                      limitby=(0, 1)).first()
        if _duplicate:
            job.id = _duplicate.id
            job.data.id = _duplicate.id
            job.method = job.METHOD.UPDATE

configure("hrm_skill_type",
          resolve=hrm_skill_type_duplicate)

def hrm_competency_rating_duplicate(job):
    """
      This callback will be called when importing records
      it will look to see if the record being imported is a duplicate.

      @param job: An S3ImportJob object which includes all the details
                  of the record being imported

      If the record is a duplicate then it will set the job method to update

      Rules for finding a duplicate:
       - Look for a record with the same name, ignoring case and skill_type
    """
    # ignore this processing if the id is set
    if job.id:
        return
    if job.tablename == "hrm_competency_rating":
        table = job.table
        stable = db.hrm_skill_type
        name = "name" in job.data and job.data.name
        skill = False
        for cjob in job.components:
            if cjob.tablename == "hrm_skill_type":
                if "name" in cjob.data:
                    skill = cjob.data.name
        if skill == False:
            return

        query = (table.name.lower().like('%%%s%%' % name.lower())) & \
            (table.skill_type_id == stable.id) & \
            (stable.value.lower() == skill.lower())
        _duplicate = db(query).select(table.id,
                                      limitby=(0, 1)).first()
        if _duplicate:
            job.id = _duplicate.id
            job.data.id = _duplicate.id
            job.method = job.METHOD.UPDATE

configure("hrm_competency_rating",
          resolve=hrm_competency_rating_duplicate)

add_component("hrm_human_resource",
              pr_person="person_id")
add_component("hrm_competency",
              pr_person="person_id")
add_component("hrm_training",
              pr_person="person_id")

# END =========================================================================