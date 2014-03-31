<?xml version="1.0"?>
<xsl:stylesheet
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

    <!-- **********************************************************************
         Sector - CSV Import Stylesheet

         - use for import to org/sector resource
         - example raw URL usage:
           Let URLpath be the URL to Sahana Eden appliation
           Let Resource be org/organisation/create
           Let Type be s3csv
           Let CSVPath be the path on the server to the CSV file to be imported
           Let XSLPath be the path on the server to the XSL transform file
           Then in the browser type:
           
           URLpath/Resource.Type?filename=CSVPath&transform=XSLPath
           
           You can add a third argument &ignore_errors
         CSV fields:
         UUID....................org_sector
         name....................org_sector
         abrv....................org_sector

    *********************************************************************** -->
    <xsl:template match="/">
        <s3xml>
            <!-- ********************************************************** -->
            <!-- Create each record -->
            <xsl:for-each select="table/row">
                <!-- Create the Sector -->
                <resource name="org_sector">
                    <xsl:if test="col[@field='UUID']!=''">
                        <xsl:attribute name="uuid">
                            <xsl:value-of select="col[@field='UUID']"/>
                        </xsl:attribute>
                    </xsl:if>
                    <data field="name"><xsl:value-of select="col[@field='name']"/></data>
                    <data field="abrv"><xsl:value-of select="col[@field='abrv']"/></data>
                </resource>
            </xsl:for-each>
        </s3xml>
    </xsl:template>
</xsl:stylesheet>
