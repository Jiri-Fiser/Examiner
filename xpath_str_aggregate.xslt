<xsl:stylesheet version="1.0"
                xmlns:qc = "http:/ki.ujep.cz/ns/qc_ast"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:ex="http://jf.cz/ns/pyex">
    <xsl:output method="text"/>
    <!--<xsl:param name="xp" select="//qc:function/@name"/>-->

    <xsl:template name="concat-text">
        <xsl:param name="nodes" />
        <xsl:param name="result" select="''" />
        <xsl:choose>
            <xsl:when test="$nodes">
                <!-- Rekurzivní volání s odstraněným prvním uzlem a přidaným textem k výsledku -->
                <xsl:call-template name="concat-text">
                    <xsl:with-param name="nodes" select="$nodes[position() > 1]" />
                    <xsl:with-param name="result" select="concat($result, $nodes[1], ',')" />
                </xsl:call-template>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="$result" />
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="/">
        <xsl:value-of select="ex:join($xp, ';')" />
    </xsl:template>
</xsl:stylesheet>