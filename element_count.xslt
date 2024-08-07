<xsl:stylesheet version="1.0"
                xmlns:qc = "http:/ki.ujep.cz/ns/qc_ast"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
 <xsl:output method="text"/>
    <xsl:template match="/">
        <xsl:value-of select="count(descendant::*[local-name() = $name and namespace-uri() = $ns])"/>
    </xsl:template>
</xsl:stylesheet>