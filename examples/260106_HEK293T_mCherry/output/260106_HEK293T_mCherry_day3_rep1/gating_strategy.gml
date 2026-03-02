<?xml version='1.0' encoding='UTF-8'?>
<gating:Gating-ML xmlns:data-type="http://www.isac-net.org/std/Gating-ML/v2.0/datatypes" xmlns:gating="http://www.isac-net.org/std/Gating-ML/v2.0/gating" xmlns:transforms="http://www.isac-net.org/std/Gating-ML/v2.0/transformations">
  <transforms:transformation transforms:id="FSC-A">
    <transforms:flog transforms:T="262143.0" transforms:M="4.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="SSC-A">
    <transforms:flog transforms:T="262143.0" transforms:M="4.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="FSC-H">
    <transforms:flog transforms:T="262143" transforms:M="4.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="SSC-H">
    <transforms:flog transforms:T="262143" transforms:M="4.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="GFP-H">
    <transforms:logicle transforms:T="262143" transforms:W="0.5" transforms:M="4.5" transforms:A="0.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="GFP-A">
    <transforms:logicle transforms:T="262143" transforms:W="0.5" transforms:M="4.5" transforms:A="0.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="mCherry-H">
    <transforms:logicle transforms:T="262143" transforms:W="0.5" transforms:M="4.5" transforms:A="0.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="mCherry-A">
    <transforms:logicle transforms:T="262143" transforms:W="0.5" transforms:M="4.5" transforms:A="0.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="FSC-Width">
    <transforms:flog transforms:T="262143" transforms:M="4.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="Time">
    <transforms:flin transforms:T="1" transforms:A="0" />
  </transforms:transformation>
  <gating:RectangleGate gating:id="TimeQC">
    <gating:dimension gating:compensation-ref="uncompensated" gating:min="0.0" gating:max="100000.0">
      <data-type:fcs-dimension data-type:name="Time" />
    </gating:dimension>
  </gating:RectangleGate>
  <gating:PolygonGate gating:id="Viable" gating:parent_id="TimeQC">
    <gating:dimension gating:compensation-ref="uncompensated" gating:transformation-ref="FSC-A">
      <data-type:fcs-dimension data-type:name="FSC-A" />
    </gating:dimension>
    <gating:dimension gating:compensation-ref="uncompensated" gating:transformation-ref="SSC-A">
      <data-type:fcs-dimension data-type:name="SSC-A" />
    </gating:dimension>
    <gating:vertex>
      <gating:coordinate data-type:value="1.1514371999052413" />
      <gating:coordinate data-type:value="0.9553016763516935" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.1059239917395927" />
      <gating:coordinate data-type:value="0.9592971771549577" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.0884045718393853" />
      <gating:coordinate data-type:value="1.0069407552660483" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.1025548389558604" />
      <gating:coordinate data-type:value="1.0960135946498821" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.1647054359782536" />
      <gating:coordinate data-type:value="1.1758828122123257" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.2151873983275743" />
      <gating:coordinate data-type:value="1.2034855179759278" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.2446000776343698" />
      <gating:coordinate data-type:value="1.1437205410921407" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.2034256638267757" />
      <gating:coordinate data-type:value="1.0363623913519429" />
    </gating:vertex>
  </gating:PolygonGate>
  <gating:PolygonGate gating:id="Singlets" gating:parent_id="Viable">
    <gating:dimension gating:compensation-ref="uncompensated" gating:transformation-ref="SSC-A">
      <data-type:fcs-dimension data-type:name="SSC-A" />
    </gating:dimension>
    <gating:dimension gating:compensation-ref="uncompensated" gating:transformation-ref="SSC-H">
      <data-type:fcs-dimension data-type:name="SSC-H" />
    </gating:dimension>
    <gating:vertex>
      <gating:coordinate data-type:value="0.9526400637885803" />
      <gating:coordinate data-type:value="0.9159291034577552" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="0.9259192840606145" />
      <gating:coordinate data-type:value="0.9518887810792576" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.1881318706177284" />
      <gating:coordinate data-type:value="1.1467327071300066" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.2148526503456942" />
      <gating:coordinate data-type:value="1.110773029508504" />
    </gating:vertex>
  </gating:PolygonGate>
  <gating:RectangleGate gating:id="mCherry_pos" gating:parent_id="Singlets">
    <gating:dimension gating:compensation-ref="uncompensated" gating:transformation-ref="mCherry-A" gating:min="0.6111766109515325">
      <data-type:fcs-dimension data-type:name="mCherry-A" />
    </gating:dimension>
  </gating:RectangleGate>
</gating:Gating-ML>