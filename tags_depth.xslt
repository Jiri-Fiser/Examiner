<xsl:stylesheet version="1.0"
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
 <xsl:output method="text"/>

 <xsl:template match="/">
     <xsl:apply-templates select="//*">
       <xsl:sort data-type="number" order="descending" select="count(ancestor::*[contains(@tags, $tag)])"/>
     </xsl:apply-templates>
 </xsl:template>

 <xsl:template match="*">
    <xsl:if test="position()=1">
     <xsl:value-of select="count(ancestor::*[contains(@tags, $tag)])"/>
    </xsl:if>
 </xsl:template>
</xsl:stylesheet>
