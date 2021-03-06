<?xml version="1.0"?>
<xsl:stylesheet
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    
    <!-- **********************************************************************
         Contacts - CSV Import Stylesheet

         - example raw URL usage:
           Let URLpath be the URL to Sahana Eden appliation
           Let Resource be vol/contact/create
           Let Type be s3csv
           Let CSVPath be the path on the server to the CSV file to be imported
           Let XSLPath be the path on the server to the XSL transform file
           Then in the browser type:
           
           URLpath/Resource.Type?filename=CSVPath&transform=XSLPath
           
           You can add a third argument &ignore_errors
         CSV fields:
         First Name......................pr_person.first_name (lookup only)
         Last Name.......................pr_person.last_name (lookup only)
         Emergency Contact Name..........vol_contact.emergency_contact_name
         Emergency Contact Relationship..vol_contact.emergency_contact_relationship
         Emergency Contact Phone.........vol_contact.emergency_contact_phone
            
    *********************************************************************** -->

    <xsl:output method="xml"/>

    <xsl:template match="/">
        <s3xml>
            <!-- Create each record -->
            <xsl:for-each select="table/row">

                <!-- Request -->
                <xsl:variable name="Request"><xsl:value-of select="col[@field='Request Number']"/></xsl:variable>
                <resource name="req_req">
                    <xsl:attribute name="tuid">
                        <xsl:value-of select="$Request"/>
                    </xsl:attribute>
                    <data field="request_number"><xsl:value-of select="$Request"/></data>
                </resource>

                <!-- Person record -->
                <xsl:variable name="FName"><xsl:value-of select="col[@field='First Name']"/></xsl:variable>
                <xsl:variable name="LName"><xsl:value-of select="col[@field='Last Name']"/></xsl:variable>
                <xsl:variable name="Person"><xsl:value-of select="concat($FName, $LName)"/></xsl:variable>
                <resource name="pr_person">
                    <xsl:attribute name="tuid">
                        <xsl:value-of select="$Person"/>
                    </xsl:attribute>
                    <data field="first_name"><xsl:value-of select="$FName"/></data>
                    <data field="last_name"><xsl:value-of select="$LName"/></data>
                </resource>

                <!-- Volunteer Application -->
                <resource name="vol_contact">
                    <reference field="req_id" resource="req_req">
                        <xsl:attribute name="tuid">
                            <xsl:value-of select="$Request"/>
                        </xsl:attribute>
                    </reference>
                    <reference field="person_id" resource="pr_person">
                        <xsl:attribute name="tuid">
                            <xsl:value-of select="$Person"/>
                        </xsl:attribute>
                    </reference>
                    <data field="emergency_contact_name"><xsl:value-of select="col[@field='Emergency Contact Name']"/></data>
                    <data field="emergency_contact_relationship"><xsl:value-of select="col[@field='Emergency Contact Relationship']"/></data>
                    <data field="emergency_contact_phone"><xsl:value-of select="col[@field='Emergency Contact Phone']"/></data>
	            </resource>
            </xsl:for-each>
        </s3xml>
    </xsl:template>
</xsl:stylesheet>
