# -*- coding: utf-8 -*-

"""
    Donations
"""

module = "don"

# Component definitions should be outside conditional model loads
add_component("don_don_item",
              org_organisation = "organisation_id")

def don_tables():
    """ Load the Request Tables when needed """

    load("hrm_human_resource")

    load("event_event")
    event_id = s3.event_id

    load("supply_item")
    item_id = s3.item_id
    item_category_id = s3.item_category_id
    item_pack_id = s3.item_pack_id
    item_pack_virtualfields = s3.item_pack_virtualfields

    # =========================================================================
    # Inventory Item
    #
    commit_type_opts = {1:T("Permanent Donation"),
                        2:T("Temporary Loan")}

    tablename = "don_don_item"
    table = define_table(tablename,
                         # @LA: Need to be able to link inv_items directly to organisations
                         # @ToDo: Filter this field by organisation.has_items == True
                         organisation_id(label = T("Corporation/Organization")),
                         item_category_id(required = True),
                         item_id(),
                         Field("specs", "text",
                               label=T("Specifications"),
                               length=500,
                               comment = DIV(_class="tooltip",
                                             _title="%s|%s" % (T("Specifications"),
                                                               T("500 character limit.")
                                                               ),
                                             )
                               ),
                         item_pack_id(writable = False,
                                      readable = False,
                                      ),
                         Field("quantity", "double",
                               label = T("Quantity"),
                               notnull = True),
                         Field("pack_value", "double",
                               label = T("Estimated Value ($) per Unit")),
                         # @ToDo: Move this into a Currency Widget for the pack_value field
                         currency_type("currency",
                                       readable = False),
                         #Field("pack_quantity",
                         #      "double",
                         #      compute = record_pack_quantity), # defined in 06_supply
                         Field("lead_time",
                               "double",
                               label = T("Lead Time (hours)"),
                               comment = DIV(_class="tooltip",
                                             _title="%s|%s" % (T("Lead Time"),
                                                               T("Hours until Goods can be available for donation.")
                                                               ),
                                             ),
                               writable = False,
                               readable = False,
                               ),
                         Field("type", "integer",
                               label = T("Type of Donation"),
                               requires = IS_IN_SET(commit_type_opts),
                               represent = lambda opt: \
                                            commit_type_opts.get(opt, NONE),
                               default = 1,
                               widget = SQLFORM.widgets.radio.widget,
                               writable = False,
                               readable = False,
                               # @ToDo: 1 donation 2 loan
                               ),
                         Field("upload", "upload",
                               label = T("Documents"),
                               comment = DIV(_class="tooltip",
                                             _title="%s|%s" % (T("Documents"),
                                                               T("Detailed Specifications, Insurance, etc")
                                                               )
                                             )
                               ),
                         comments(),
                         *s3_meta_fields())

    table.virtualfields.append(item_pack_virtualfields(tablename="don_don_item"))

    # Virtual Field for don_item
    class don_item_virtualfields(dict, object):
        def org_phone(self):
            org_id = self.don_don_item.organisation_id
            otable = db.org_organisation
            query = (otable.id == org_id)
            record = db(query).select(otable.phone,
                                      limitby=(0, 1)).first()
            if record:
                return record.phone
            else:
                return NONE

        def org_human_resource_email(self):
            org_id = self.don_don_item.organisation_id
            htable = db.hrm_human_resource
            query = (htable.organisation_id == org_id)
            record = db(query).select(htable.id,
                                      orderby=htable.created_on,
                                      limitby=(0, 1)).first()
            if record:
                return human_resource_contact(record.id,"EMAIL")
            else:
                return NONE

    table.virtualfields.append(don_item_virtualfields())
    
    configure(tablename,
              sortby = [[1, "asc"]],
              orderby = table.organisation_id
              )

    # -------------------------------------------------------------------------
    # Collections (Donation Drives)
    tablename = "don_collect"
    table = define_table(tablename,
                         event_id(default=session.s3.event),
                         Field("start_datetime", "datetime",
                               label = T("Start"),
                               requires = IS_EMPTY_OR(
                                          IS_UTC_DATETIME_IN_RANGE(
                                            minimum=request.utcnow - datetime.timedelta(days=1),
                                            error_message="%s %%(min)s!" %
                                                T("Enter a valid future date"))),
                               widget = S3DateTimeWidget(past=0,
                                                         future=8760), # Hours, so 1 year
                               represent = s3_utc_represent
                               ),
                         Field("end_datetime", "datetime",
                               label = T("End"),
                               requires = IS_EMPTY_OR(
                                           IS_UTC_DATETIME_IN_RANGE(
                                             minimum=request.utcnow - datetime.timedelta(days=1),
                                             error_message="%s %%(min)s!" %
                                                 T("Enter a valid future date"))),
                               widget = S3DateTimeWidget(past=0,
                                                         future=8760), # Hours, so 1 year
                               represent = s3_utc_represent
                               ),
                         super_link(db.org_site,
                                    label = T("Collection At"),
                                    readable = True,
                                    writable = True,
                                    empty = False,
                                    # Comment these to use a Dropdown & not an Autocomplete
                                    #widget = S3SiteAutocompleteWidget(),
                                    #comment = DIV(_class="tooltip",
                                    #              _title="%s|%s" % (T("Requested By Facility"),
                                    #                                T("Enter some characters to bring up a list of possible matches"))),
                                    represent = shn_site_represent),
                         organisation_id(label = T("Collected By Organization"),
                                         empty = False,
                                         widget = None
                                         ),
                         comments("donation_comments",
                                  writable = True,
                                  label = T("Donation Comments"),
                                  comment=DIV(_class="tooltip",
                                     _title="%s|%s" % (T("Donation Comments"),
                                                       T("Additional comments concerning this donation drive.")))),
                         Field("volume", "double",
                               label = T("Volume Collected (cub. ft)")),
                         Field("weight", "double",
                               label = T("Weight Collected (lbs)")),
                         *s3_meta_fields())

    # CRUD strings
    ADD_COLLECT = T("Add New Donation Drive")
    LIST_COLLECT = T("List Donation Drives")
    crud_strings[tablename] = Storage(
        title_create = ADD_COLLECT,
        title_display = T("Donation Drive Details"),
        title_list = LIST_COLLECT,
        title_update = T("Edit Donation Drive"),
        title_search = T("Search Donation Drives"),
        subtitle_create = T("Schedule Donation Drive"),
        subtitle_list = T("Donation Drives"),
        label_list_button = LIST_COLLECT,
        label_create_button = ADD_COLLECT,
        label_delete_button = T("Delete Donation Drive"),
        msg_record_created = T("Donation Drive scheduled"),
        msg_record_modified = T("Donation Drive updated"),
        msg_record_deleted = T("Donation Drive cancelled"),
        msg_list_empty = T("No Donation Drives currently scheduled"))
    
    configure(table,
              orderby = ~table.start_datetime)

    # -------------------------------------------------------------------------
    # Voucher Distribution
    tablename = "don_distribute"
    table = define_table(tablename,
                         event_id(default=session.s3.event),
                         Field("date", "date"),
                         #human_resource_id("requested_by_id",
                         #                  label = T("Requested By"),
                         #                  empty = False,
                         #                  default = s3_logged_in_human_resource()),
                         organisation_id(label = T("Distributed By Organization"),
                                         empty = False,
                                         ),
                         Field("households", "double",
                               label = T("Number of Households")),
                         Field("value", "double",
                               label = T("Total Value of Vouchers")),
                         currency_type("currency"),
                         super_link(db.org_site,
                                    label = T("Distributed At"),
                                    readable = True,
                                    writable = True,
                                    empty = False,
                                    # Comment these to use a Dropdown & not an Autocomplete
                                    #widget = S3SiteAutocompleteWidget(),
                                    #comment = DIV(_class="tooltip",
                                    #              _title="%s|%s" % (T("Requested By Facility"),
                                    #                                T("Enter some characters to bring up a list of possible matches"))),
                                    represent = shn_site_represent),
                         comments("distribute_comments",
                                  writable = True,
                                  label = T("Voucher Comments"),
                                  comment=DIV(_class="tooltip",
                                     _title="%s|%s" % (T("Distribution Comments"),
                                                       T("Additional comments about this voucher distribution.")))),
                         *s3_meta_fields())

    # CRUD strings
    ADD_DISTRIBUTE = T("Record Voucher Distribution")
    LIST_DISTRIBUTE = T("Voucher Distributions")
    crud_strings[tablename] = Storage(
        title_create = ADD_DISTRIBUTE,
        title_display = T("Voucher Distribution Details"),
        title_list = LIST_DISTRIBUTE,
        title_update = T("Edit Voucher Distribution Details    "),
        title_search = T("Search Voucher Distributions"),
        subtitle_create = T("Record Voucher Distribution"),
        subtitle_list = T("Voucher Distributions"),
        label_list_button = LIST_DISTRIBUTE,
        label_create_button = ADD_DISTRIBUTE,
        label_delete_button = T("Delete Voucher Distribution"),
        msg_record_created = T("Voucher Distribution Recorded"),
        msg_record_modified = T("Voucher Distribution Updated"),
        msg_record_deleted = T("Voucher Distribution Deleted"),
        msg_list_empty = T("No Voucher Distribution Currently Recorded"))

    # -------------------------------------------------------------------------
    def donCertBorder(canvas, doc):
        """
            This method will add a border to the page.
            It is a callback method and will not be called directly
        """

        from PIL import Image
        from reportlab.lib.units import inch

        canvas.saveState()
        canvas.setStrokeColorRGB(0,0,0)
        inset = 3
        canvas.rect(inset,
                    inset,
                    doc.pagesize[0]-2*inset,
                    doc.pagesize[1]-2*inset,
                    stroke=1,
                    fill=0)
        canvas.setStrokeColorRGB(0.5,0.5,0.5)
        inset = 6
        canvas.rect(inset,
                    inset,
                    doc.pagesize[0]-2*inset,
                    doc.pagesize[1]-2*inset,
                    stroke=1,
                    fill=0)
        # signature line
        canvas.line((doc.pagesize[0]/2)-1.50*inch,
                     1.35*inch,
                     (doc.pagesize[0]/2)+1.50*inch,
                     1.35*inch,
                    )

        image = "static/img/la/city_seal.png"
        citySeal = os.path.join(current.request.folder,image)
        if os.path.exists(citySeal):
            im = Image.open(citySeal)
            (iwidth, iheight) = im.size
            height = 0.85 * inch
            width = iwidth * (height/iheight)
            canvas.drawImage(citySeal,
                     (doc.pagesize[0]-width)/2,
                     doc.pagesize[1]-1.1*inch,
                     width = width,
                     height = height)
        image = "static/img/la/LA-EPF.png"
        EPFLogo = os.path.join(current.request.folder,image)
        if os.path.exists(EPFLogo):
            im = Image.open(EPFLogo)
            (iwidth, iheight) = im.size
            height = 0.5 * inch
            width = iwidth * (height/iheight)
            canvas.drawImage(EPFLogo,
                     0.75*inch,
                     0.75*inch,
                     width = width,
                     height = height)
        image = "static/img/la/EMD-logo.png"
        EMDLogo = os.path.join(current.request.folder,image)
        if os.path.exists(EMDLogo):
            im = Image.open(EMDLogo)
            (iwidth, iheight) = im.size
            height = 0.85 * inch
            width = iwidth * (height/iheight)
            canvas.drawImage(EMDLogo,
                     (doc.pagesize[0]-width)-0.75*inch,
                     0.95*inch,
                     width = width,
                     height = height)
        image = "static/img/la/Brent Signature.png"
        SignatureLogo = os.path.join(current.request.folder,image)
        if os.path.exists(SignatureLogo):
            im = Image.open(SignatureLogo)
            (iwidth, iheight) = im.size
            height = 0.5 * inch
            width = iwidth * (height/iheight)
            canvas.drawImage(SignatureLogo,
                     (doc.pagesize[0]-width)/2,
                     1.36*inch,
                     width = width,
                     height = height)
        canvas.setFont("CertFont", 8)
        canvas.drawCentredString((doc.pagesize[0]-width/2)-0.75*inch,
                                 0.70*inch,
                                 "James G. Featherstone"
                                )
        canvas.drawCentredString((doc.pagesize[0]-width/2)-0.75*inch,
                                 0.50*inch,
                                 "General Manager"
                                )
        canvas.restoreState()

    # -------------------------------------------------------------------------
    def donationFooter(canvas, doc):
        """
            This method will generate the basic look of a page.
            It is a callback method and will not be called directly
        """

        from reportlab.lib.units import inch

        canvas.saveState()
        canvas.setFont("Helvetica", 9)
        canvas.drawString(inch, 0.75 * inch,
                          "Page %d of 3" % doc.page
                         )
        canvas.restoreState()

    # -------------------------------------------------------------------------
    def donationRequest(pdf, **args):
        def getValue(record, field, addBox=True):
            width = 24
            height = 14
            if record == None:
                value = None
            else:
                value = record[field.name]
            if value != None:
                try:
                    value = field.represent(value, show_link = False)
                except:
                    try:
                        value = field.represent(value)
                    except:
                        pass
            if value == "" or value == "-" or value == None:
                if addBox:
                    value = pdf.addBox(width, height, append=False)
                else:
                    value = ""
            return value

        # get the data for this report
        dtable = db.don_distribute

        if "id" in args:
            id = args["id"]
            reqtable = db.req_req
            query = (reqtable.id == id)
            req_fieldList = [reqtable.request_number,
                             reqtable.event_id,
                             reqtable.incident_id,
                             reqtable.date,
                             reqtable.request_for_id,
                            ]
            req_record = db(query).select(limitby=(0, 1),
                                       *req_fieldList).first()
        if "id" in args:
            id = args["id"]
            ritemtable = db.req_req_item
            query = (ritemtable.req_id == id)
            item_fieldList = [ritemtable.item,
                              ritemtable.specs,
                              ritemtable.item_id,
                              ritemtable.quantity,
                             ]
            item_record = db(query).select(limitby=(0, 1),
                                       *item_fieldList).first()

        if "id" in args:
            id = args["id"]
            reqtable = db.req_req
            query = (reqtable.id == id)
            del_fieldList = [reqtable.site_id,
                             reqtable.date_required,
                             reqtable.date_required_until,
                            ]
            del_record = db(query).select(limitby=(0, 1),
                                       *del_fieldList).first()

        if "id" in args:
            id = args["id"]
            comtable = db.req_commit
            query = (comtable.req_id == id)
            don_fieldList = [comtable.donated_by_id,
                             comtable.datetime,
                             comtable.specs,
                             comtable.quantity_commit,
                             comtable.pack_value,
                             comtable.currency,
                             comtable.datetime_available,
                             comtable.type,
                             comtable.loan_value,
                             comtable.return_contact_id,
                             comtable.site_id,
                             comtable.datetime_return,
                             comtable.return_penalty,
                             comtable.return_instruct,
                             comtable.insured,
                             comtable.insure_details,
                             comtable.warrantied,
                             comtable.warranty_details,
                             comtable.transport_req,
                             comtable.security_req,
                             comtable.committer_id,
                             comtable.comments,
                            ]
            don_record = db(query).select(limitby=(0, 1),
                                       *don_fieldList).first()

        if "id" in args:
            id = args["id"]
            rectable = db.req_fulfill
            query = (rectable.req_id == id)
            rec_fieldList = [rectable.accepted_by_id,
                             rectable.datetime_fulfill,
                             rectable.quantity_fulfill,
                             rectable.fulfill_by_id,
                             rectable.datetime_returned,
                             rectable.comments,
                            ]
            rec_record = db(query).select(limitby=(0, 1),
                                       *rec_fieldList).first()


        if "id" in args:
            id = args["id"]
            surtable = db.req_surplus_item
            query = (surtable.req_id == id)
            sur_fieldList = [surtable.item_id,
                             surtable.item_pack_id,
                             surtable.quantity_surplus,
                             surtable.human_resource_id,
                             surtable.comments,
                            ]
            sur_record = db(query).select(limitby=(0, 1),
                                       *sur_fieldList).first()

        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch

        reqtable.request_for_id.label = T("Deliver To Person")

        # Set page dimensions...
        pdf.setMargins(bottom=0.3*inch, left=0.4*inch, right = 0.4*inch)
        width = pdf.getPageWidth()
        height = pdf.getPageHeight()
        col = width
        # Set styles
        stylePlain = [("VALIGN", (0, 0), (-1, -1), "TOP"),]
        styleBoxed = [("VALIGN", (0, 0), (-1, -1), "TOP"),
                      ("BOX", (0, 0), (-1, -1), 1, "#000000"),
                     ]

        # Header ...
        cell1 = []
        for field in req_fieldList:
            heading = "<para><b>%s</b></para>" % field.label
            value = getValue(req_record,field)
            cell1.append([pdf.addParagraph(heading, append=False), value])
        table1 = pdf.getStyledTable(cell1,
                                    colWidths=[col*.2, col*.8],
                                    style=stylePlain,
                                   )
        # Requested Item ...
        cell2 = []
        for field in item_fieldList:
            heading = "<para><b>%s</b></para>" % field.label
            value = getValue(item_record,field)
            cell2.append([pdf.addParagraph(heading, append=False), value])
        table2 = pdf.getStyledTable(cell2,
                                    colWidths=[col*.2, col*.8],
                                    style=styleBoxed,
                                   )
        # Delivery ...
        cell3 = []
        for field in del_fieldList:
            heading = "<para><b>%s</b></para>" % field.label
            value = getValue(del_record,field)
            cell3.append([pdf.addParagraph(heading, append=False), value])
        table3 = pdf.getStyledTable(cell3,
                                    colWidths=[col*.2, col*.8],
                                    style=styleBoxed,
                                   )
        # Donation ...
        cell4 = []
        for field in don_fieldList:
            heading = "<para><b>%s</b></para>" % field.label
            value = getValue(don_record,field)
            cell4.append([pdf.addParagraph(heading, append=False), value])
        table4 = pdf.getStyledTable(cell4,
                                    colWidths=[col*.2, col*.8],
                                    style=styleBoxed,
                                   )
        # Approved ...
        signature = "<para><b>%s</b><br/> </para>" % T("Signature")
        cell7 = []
        heading = "<para><b>%s</b></para>" % T("Name")
        cell7.append([pdf.addParagraph(heading, append=False),
                      pdf.addBox(24, 14, append=False)])
        cell7.append([pdf.addParagraph(signature, append=False),
                      pdf.addLine(12, append=False)])
        table7 = pdf.getStyledTable(cell7,
                                    colWidths=[col*.2, col*.8],
                                    style=styleBoxed,
                                   )
        # Received ...
        cell5 = []
        for field in rec_fieldList:
            heading = "<para><b>%s</b></para>" % field.label
            value = getValue(rec_record,field)
            cell5.append([pdf.addParagraph(heading, append=False), value])
        cell5.append([pdf.addParagraph(signature, append=False),
                      pdf.addLine(12, append=False)])
        table5 = pdf.getStyledTable(cell5,
                                    colWidths=[col*.2, col*.8],
                                    style=styleBoxed,
                                   )
        # Surplus ...
        cell6 = []
        for field in sur_fieldList:
            heading = "<para><b>%s</b></para>" % field.label
            value = getValue(sur_record,field)
            cell6.append([pdf.addParagraph(heading, append=False), value])
        cell6.append([pdf.addParagraph(signature, append=False),
                      pdf.addLine(12, append=False)])
        table6 = pdf.getStyledTable(cell6,
                                    colWidths=[col*.2, col*.8],
                                    style=styleBoxed,
                                   )

        # set the banner
        pdf.setHeaderBanner("static/img/la/Give2LAbranding_BW.jpg")

        pdf.addParagraph("<para align='CENTER'><b>%s</b></para>" % T("Request"))
        pdf.addSpacer(10)
        pdf.content.append(table1)
        pdf.addSpacer(20)
        pdf.addParagraph("<para align='CENTER'><b>%s</b></para>" % T("Request Resources"))
        pdf.addSpacer(10)
        pdf.content.append(table2)
        pdf.addSpacer(20)
        pdf.addParagraph("<para align='CENTER'><b>%s</b></para>" % T("Delivery Details"))
        pdf.addSpacer(10)
        pdf.content.append(table3)
        pdf.addSpacer(20)
        pdf.addParagraph("<para align='CENTER'><b>%s</b></para>" % T("Approval by Donor"))
        pdf.addSpacer(10)
        pdf.content.append(table7)
        pdf.addSpacer(20)
        pdf.addParagraph("<para align='CENTER'><b>%s</b></para>" % T("Approval by Los Angeles Emergency Preparedness Foundation"))
        pdf.addSpacer(10)
        pdf.content.append(table7)
        pdf.throwPageBreak()
        pdf.addParagraph("<para align='CENTER'><b>%s</b></para>" % T("Donation Details"))
        pdf.addSpacer(10)
        pdf.content.append(table4)
        pdf.throwPageBreak()
        pdf.addParagraph("<para align='CENTER'><b>%s</b></para>" % T("Received Details"))
        pdf.addSpacer(10)
        pdf.content.append(table5)
        pdf.addSpacer(20)
        pdf.addParagraph("<para align='CENTER'><b>%s</b></para>" % T("Surplus Details"))
        pdf.addSpacer(10)
        pdf.content.append(table6)

    # -------------------------------------------------------------------------
    def donationCertificate(pdf, **args):

        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.lib.colors import Color
        from reportlab.lib.units import inch

        pdf.setMargins(top=1.1*inch, bottom=0.5*inch, left=0.4*inch, right = 0.4*inch)
        # Prevent partially-translated strings
        T = lambda str: str
        # Standard lines of text
        line1 = "ANTONIO R. VILLARAIGOSA"
        line2 = "Mayor"
        line3A = "THE CITY OF LOS ANGELES"
        line3B = "AND LOS ANGELES EMERGENCY PREPAREDNESS FOUNDATION"
        line4 = "CERTIFICATE OF APPRECIATION"
        line5 = "AWARDED TO"
        line6 = "In Recognition of their Outstanding Contribution and Support"
        line7 = "From a Grateful Community!"
        line8 = "Awarded this %(day)s day of %(month)s, %(year)s"
        line9 = "Brent H. Woodworth"
        line10 = "President & CEO"
        line11 = "Los Angeles Emergency Preparedness Foundation"

        load("event_event")

        fontname = "static/fonts/la/Engravers.ttf"
        font = os.path.join(current.request.folder,fontname)
        pdfmetrics.registerFont(TTFont('CertFont', font))

        stylesheet=getSampleStyleSheet()
        normalStyle = stylesheet["Normal"]
        style = normalStyle
        styleA = ParagraphStyle(name="StyleA",
                                parent=normalStyle,
                                fontName="CertFont",
                                fontSize=8,
                                leading=12,
                                borderPadding = (10, 2, 10, 2),
                                alignment = 1,
                                )
        styleB = ParagraphStyle(name="StyleB",
                                parent=normalStyle,
                                fontName="CertFont",
                                fontSize=16,
                                textColor = Color(0.5, 0.5, 0.1),
                                leading=20,
                                borderPadding = (8, 2, 8, 2),
                                alignment = 1,
                                )
        styleC = ParagraphStyle(name="StyleC",
                                parent=normalStyle,
                                fontName="CertFont",
                                fontSize=22,
                                textColor = Color(0.5, 0.5, 0.1),
                                leading=26,
                                borderPadding = (8, 2, 8, 2),
                                alignment = 1,
                                )
        styleD = ParagraphStyle(name="StyleD",
                                parent=normalStyle,
                                fontName="CertFont",
                                fontSize=14,
                                leading=16,
                                borderPadding = (8, 2, 8, 2),
                                alignment = 1,
                                )
        styleE = ParagraphStyle(name="StyleE",
                                parent=normalStyle,
                                fontName="CertFont",
                                fontSize=24,
                                leading=30,
                                borderPadding = (8, 2, 8, 2),
                                alignment = 1,
                                )
        styleF = ParagraphStyle(name="StyleF",
                                parent=normalStyle,
                                fontName="CertFont",
                                fontSize=12,
                                textColor = Color(0.5, 0.5, 0.1),
                                leading=16,
                                borderPadding = (8, 2, 8, 2),
                                alignment = 1,
                                )
        rtable = db.req_req
        ctable = db.req_commit
        ftable = db.req_fulfill
        etable = db.event_event
        if "id" in args:
            id = args["id"]
        query = (rtable.id == id) & \
                (ctable.req_id == rtable.id) & \
                (ftable.req_id == rtable.id) & \
                (rtable.event_id == etable.id)
        fieldList = [ctable.donated_by_id,
                     ftable.datetime_fulfill,
                     etable.name,
                    ]
        record = db(query).select(limitby=(0, 1),
                                   *fieldList).first()
        if record != None:
            org = record.req_commit.donated_by_id
            name = organisation_represent(org)
            date = record.req_fulfill.datetime_fulfill.strftime("%d %b %Y")
            event = record.event_event.name
        else:
            name = "Organization Name"
            date = "Date"
            event = "Event"
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
            pdf.addParagraph("%s on %s" %(event, date), styleD)
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

    # -------------------------------------------------------------------------
    # Pass variables back to global scope (response.s3.*)
    return dict(donationRequest = donationRequest,
                donationFooter = donationFooter,
                donationCertificate = donationCertificate,
                donCertBorder = donCertBorder,
                )

# -----------------------------------------------------------------------------
# Provide a handle to this load function
loader(don_tables,
       "don_don_item",
       "don_collect",
       "don_distribute")

# END -------------------------------------------------------------------------