# -*- coding: utf-8 -*-

"""
    Messaging module
"""

module = "msg"

def messaging_tables():
    """ Load the tables required for Messaging, when-required"""

    # Message priority
    msg_priority_opts = {
        3:T("High"),
        2:T("Medium"),
        1:T("Low")
    }
    # ---------------------------------------------------------------------
    # Message Log - all Inbound & Outbound Messages
    # ---------------------------------------------------------------------
    tablename = "msg_log"
    table = define_table(tablename,
                         super_link(db.pr_pentity), # pe_id, Sender
                         Field("sender"),        # The name to go out incase of the email, if set used
                         Field("fromaddress"),   # From address if set changes sender to this
                         Field("recipient"),
                         Field("subject", length=78),
                         Field("message", "text"),
                         #Field("attachment", "upload", autodelete = True), #TODO
                         Field("verified", "boolean", default = False),
                         Field("verified_comments", "text"),
                         Field("actionable", "boolean", default = True),
                         Field("actioned", "boolean", default = False),
                         Field("actioned_comments", "text"),
                         Field("priority", "integer", default = 1,
                              requires = IS_NULL_OR(IS_IN_SET(msg_priority_opts)),
                                label = T("Priority")),
                        Field("inbound", "boolean", default = False,
                               represent = lambda direction: \
                                 (direction and ["In"] or ["Out"])[0],
                               label = T("Direction")),
                         *s3_meta_fields())

    configure(tablename,
              list_fields=["id",
                           "inbound",
                           "pe_id",
                           "fromaddress",
                           "recipient",
                           "subject",
                           "message",
                           "verified",
                           #"verified_comments",
                           "actionable",
                           "actioned",
                           #"actioned_comments",
                           #"priority"
                           ])

    # Reusable Message ID
    message_id = S3ReusableField("message_id", db.msg_log,
                                 requires = IS_NULL_OR(IS_ONE_OF(db, "msg_log.id")),
                                 # FIXME: Subject works for Email but not SMS
                                 represent = lambda id: \
                                    db(db.msg_log.id == id).select(db.msg_log.subject,
                                                                   limitby=(0, 1)).first().subject,
                                 ondelete = "RESTRICT")

    # ---------------------------------------------------------------------
    # Message Limit - Used to limit the number of emails sent from the system
    tablename = "msg_limit"
    table = define_table(tablename,
                         s3_meta_created_on())

    # ---------------------------------------------------------------------
    # SMS
    # ---------------------------------------------------------------------
    tablename = "msg_setting"
    table = define_table(tablename,
                         Field("outgoing_sms_handler",
                               length=32,
                               requires = IS_IN_SET(msg.GATEWAY_OPTS,
                                                    zero=None)),
                         # Moved to deployment_settings
                         #Field("default_country_code", "integer", default=44),
                         *s3_timestamp())

    # ---------------------------------------------------------------------
    tablename = "msg_smtp_to_sms_settings"
    table = define_table(tablename,
                         #Field("account_name"), # Nametag to remember account - To be used later
                         Field("address", length=64, requires=IS_NOT_EMPTY()),
                         Field("subject", length=64),
                         Field("enabled", "boolean", default = True),
                         #Field("preference", "integer", default = 5), To be used later
                         *s3_timestamp())

    # ---------------------------------------------------------------------
    # Outbound Messages
    # ---------------------------------------------------------------------
    # Show only the supported messaging methods
    msg_contact_method_opts = msg.MSG_CONTACT_OPTS

    # Valid message outbox statuses
    msg_status_type_opts = {
        1:T("Unsent"),
        2:T("Sent"),
        3:T("Draft"),
        4:T("Invalid")
        }

    opt_msg_status = db.Table(None, "opt_msg_status",
                              Field("status", "integer", notnull=True,
                              requires = IS_IN_SET(msg_status_type_opts,
                                                   zero=None),
                              default = 1,
                              label = T("Status"),
                              represent = lambda opt: \
                                msg_status_type_opts.get(opt, UNKNOWN_OPT)))

    # Outbox - needs to be separate to Log since a single message sent needs different outbox entries for each recipient
    tablename = "msg_outbox"
    table = define_table(tablename,
                         message_id(),
                         super_link(db.pr_pentity), # pe_id, Person/Group to send the message out to
                         Field("address"),   # If set used instead of picking up from pe_id
                         Field("pr_message_method",
                               length=32,
                               requires = IS_IN_SET(msg_contact_method_opts,
                                                    zero=None),
                               default = "EMAIL",
                               label = T("Contact Method"),
                               represent = lambda opt: \
                                 msg_contact_method_opts.get(opt, UNKNOWN_OPT)),
                         opt_msg_status,
                         Field("system_generated", "boolean", default = False),
                         Field("log"),
                         *s3_meta_fields())

    add_component(table, msg_log="message_id")

    configure(tablename,
              list_fields=["id",
                           "message_id",
                           "pe_id",
                           "status",
                           "log",
                           ])

    # =====================================================================
    def msg_compose(redirect_module = "msg",
                    redirect_function = "compose",
                    redirect_vars = None,
                    title_name = "Send Message"):
        """
            Form to Compose a Message

            @param redirect_module: Redirect to the specified module's url after login.
            @param redirect_function: Redirect to the specified function
            @param redirect_vars:  Dict with vars to include in redirects
            @param title_name: Title of the page
        """

        table1 = db.msg_log
        table2 = db.msg_outbox

        if auth.is_logged_in() or auth.basic():
            pass
        else:
            redirect(URL(c="default", f="user", args="login",
                vars={"_next":URL(redirect_module,redirect_function, vars=redirect_vars)}))

        # Model options
        table1.sender.writable = table1.sender.readable = False
        table1.fromaddress.writable = table1.fromaddress.readable = False
        table1.pe_id.writable = table1.pe_id.readable = False
        table1.verified.writable = table1.verified.readable = False
        table1.verified_comments.writable = table1.verified_comments.readable = False
        table1.actioned.writable = table1.actioned.readable = False
        table1.actionable.writable = table1.actionable.readable = False
        table1.actioned_comments.writable = table1.actioned_comments.readable = False

        table1.subject.label = T("Subject")
        table1.message.label = T("Message")
        #table1.priority.label = T("Priority")

        table2.pe_id.writable = table2.pe_id.readable = True
        table2.pe_id.label = T("Recipients")
        table2.pe_id.comment = DIV(_class="tooltip",
                                   _title="%s|%s" % (T("Recipients"),
                                                     T("Please enter the first few letters of the Person/Group for the autocomplete.")))

        def compose_onvalidation(form):
            """ Set the sender and use msg.send_by_pe_id to route the message """
            if not request.vars.pe_id:
                session.error = T("Please enter the recipient")
                redirect(URL(redirect_module,redirect_function,
                             vars=redirect_vars))
            table = db.pr_person
            query = (table.uuid == auth.user.person_uuid)
            sender_pe_id = db(query).select(table.pe_id,
                                            limitby=(0, 1)).first().pe_id
            if msg.send_by_pe_id(request.vars.pe_id,
                                 request.vars.subject,
                                 request.vars.message,
                                 sender_pe_id,
                                 request.vars.pr_message_method):
                # Trigger a Process Outbox
                msg.process_outbox(contact_method = request.vars.pr_message_method)
                session.flash = T("Check outbox for the message status")
                redirect(URL(redirect_module,redirect_function,
                             vars=redirect_vars))
            else:
                session.error = T("Error in message")
                redirect(URL(redirect_module,redirect_function,
                             vars=redirect_vars))

        logform = crud.create(table1,
                              onvalidation = compose_onvalidation)
        outboxform = crud.create(table2)

        return dict(logform = logform,
                    outboxform = outboxform,
                    title = T(title_name))

    # ---------------------------------------------------------------------
    # Pass variables back to global scope (s3.*)
    return dict(msg_compose=msg_compose,
                message_id=message_id)

# Provide a handle to this load function
loader(messaging_tables,
       "msg_setting",
       "msg_smtp_to_sms_settings",
       "msg_log",
       "msg_limit",
       "msg_outbox",
       )

# =============================================================================
# Tasks to be callable async
# =============================================================================
def process_outbox(contact_method, user_id=None):
    """
        Process Outbox
            - will normally be done Asynchronously if there is a worker alive

        @param contact_method: s3msg.MSG_CONTACT_OPTS
        @param user_id: calling request's auth.user.id or None
    """
    if user_id:
        # Authenticate
        auth.s3_impersonate(user_id)
    # Run the Task
    result = msg.process_outbox(contact_method)
    return result

tasks["process_outbox"] = process_outbox

# END =========================================================================
