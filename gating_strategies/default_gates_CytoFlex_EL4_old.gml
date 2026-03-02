<?xml version='1.0' encoding='UTF-8'?>
<gating:Gating-ML xmlns:gating="http://www.isac-net.org/std/Gating-ML/v2.0/gating" xmlns:data-type="http://www.isac-net.org/std/Gating-ML/v2.0/datatypes" xmlns:transforms="http://www.isac-net.org/std/Gating-ML/v2.0/transformations">
  <gating:RectangleGate gating:id="TimeQC">
    <gating:dimension gating:compensation-ref="uncompensated" gating:min="0.0" gating:max="262144.0">
      <data-type:fcs-dimension data-type:name="Time"/>
    </gating:dimension>
  </gating:RectangleGate>
  <gating:PolygonGate gating:id="Viable" gating:parent_id="TimeQC">
    <gating:dimension gating:compensation-ref="uncompensated" gating:transformation-ref="FSC-A">
      <data-type:fcs-dimension data-type:name="FSC-A"/>
    </gating:dimension>
    <gating:dimension gating:compensation-ref="uncompensated" gating:transformation-ref="SSC-A">
      <data-type:fcs-dimension data-type:name="SSC-A"/>
    </gating:dimension>
    <gating:vertex>
      <gating:coordinate data-type:value="1.2383318034729467"/>
      <gating:coordinate data-type:value="1.1456158655743478"/>
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.1831939770951445"/>
      <gating:coordinate data-type:value="1.1351936772246756"/>
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.1263330936430358"/>
      <gating:coordinate data-type:value="1.0648439058643868"/>
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.115994751197198"/>
      <gating:coordinate data-type:value="1.007521869941189"/>
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.1315022648659547"/>
      <gating:coordinate data-type:value="0.9658331165424994"/>
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.1659634063520812"/>
      <gating:coordinate data-type:value="0.9736497578047537"/>
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.2366087463986404"/>
      <gating:coordinate data-type:value="1.0830827354763137"/>
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.2383318034729467"/>
      <gating:coordinate data-type:value="1.1143493005253307"/>
    </gating:vertex>
  </gating:PolygonGate>
</gating:Gating-ML>
