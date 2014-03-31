<?xml version="1.0"?>
<xsl:stylesheet
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    
    <!-- **********************************************************************
         Request Items - CSV Import Stylesheet

         - example raw URL usage:
           Let URLpath be the URL to Sahana Eden appliation
           Let Resource be req/req_item/create
           Let Type be s3csv
           Let CSVPath be the path on the server to the CSV file to be imported
           Let XSLPath be the path on the server to the XSL transform file
           Then in the browser type:
           
           URLpath/Resource.Type?filename=CSVPath&transform=XSLPath
           
           You can add a third argument &ignore_errors
         CSV fields:
         Request........................req_req_skill.req_id & req_req.request_number (lookup only)
         Skill..........................req_req_skill.skill_id & hrm_skill.name (lookup only)
         Quantity.......................req_req_skill.quantity
         Comments.......................req_req_skill.comments
            
    *********************************************************************** -->

    <xsl:output method="xml"/>

    <xsl:template match="/">
        <s3xml>
            <!-- Create each record -->
            <xsl:for-each select="table/row">

                <!-- Request -->
                <xsl:variable name="Request"><xsl:value-of select="col[@field='Request']"/></xsl:variable>
                <resource name="req_req">
                    <xsl:attribute name="tuid">
                        <xsl:value-of select="$Request"/>
                    </xsl:attribute>
                    <data field="request_number"><xsl:value-of select="$Request"/></data>
                </resource>

                <!-- HRM Skill -->
                <!-- @todo enable multiple skills -->
                <resource name="hrm_skill">
	                <xsl:attribute name="tuid">
	                    <xsl:value-of select="col[@field='Skill']"/>
	                </xsl:attribute>
	                <data field="name"><xsl:value-of select="col[@field='Skill']"/></data>
	            </resource>
	            
                <!-- Request Skill -->
                <resource name="req_req_skill">
                    <reference field="req_id" resource="req_req">
                        <xsl:attribute name="tuid">
                            <xsl:value-of select="$Request"/>
                        </xsl:attribute>
                    </reference>
                    <reference field="skill_id" resource="hrm_skill">
                        <xsl:attribute name="tuid">
                            <xsl:value-of select="concat('[&quot;', col[@field='Skill']/text(), '&quot;]')"/>
                        </xsl:attribute>
                    </reference>
                    <data field="quantity"><xsl:value-of select="col[@field='Quantity']"/></data>
                    <data field="comments"><xsl:value-of select="col[@field='Comments']"/></data>
	            </resource>
            </xsl:for-each>
        </s3xml>
    </xsl:template>
</xsl:stylesheet>
