<?xml version='1.0' encoding='UTF-8'?>
<gating:Gating-ML xmlns:data-type="http://www.isac-net.org/std/Gating-ML/v2.0/datatypes" xmlns:gating="http://www.isac-net.org/std/Gating-ML/v2.0/gating" xmlns:transforms="http://www.isac-net.org/std/Gating-ML/v2.0/transformations">
  <transforms:transformation transforms:id="FSC-A">
    <transforms:flog transforms:T="262144.0" transforms:M="4.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="SSC-A">
    <transforms:flog transforms:T="262144.0" transforms:M="4.5" />
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
  <transforms:transformation transforms:id="B690-H">
    <transforms:logicle transforms:T="262143" transforms:W="0.5" transforms:M="4.5" transforms:A="0.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="B690-A">
    <transforms:logicle transforms:T="262143" transforms:W="0.5" transforms:M="4.5" transforms:A="0.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="R660-H">
    <transforms:logicle transforms:T="262143" transforms:W="0.5" transforms:M="4.5" transforms:A="0.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="R660-A">
    <transforms:logicle transforms:T="262143" transforms:W="0.5" transforms:M="4.5" transforms:A="0.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="R712-H">
    <transforms:logicle transforms:T="262143" transforms:W="0.5" transforms:M="4.5" transforms:A="0.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="R712-A">
    <transforms:logicle transforms:T="262143" transforms:W="0.5" transforms:M="4.5" transforms:A="0.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="R780-H">
    <transforms:logicle transforms:T="262143" transforms:W="0.5" transforms:M="4.5" transforms:A="0.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="R780-A">
    <transforms:logicle transforms:T="262143" transforms:W="0.5" transforms:M="4.5" transforms:A="0.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="Y585-H">
    <transforms:logicle transforms:T="262143" transforms:W="0.5" transforms:M="4.5" transforms:A="0.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="Y585-A">
    <transforms:logicle transforms:T="262143" transforms:W="0.5" transforms:M="4.5" transforms:A="0.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="mCherry-H">
    <transforms:logicle transforms:T="262143" transforms:W="0.5" transforms:M="4.5" transforms:A="0.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="mCherry-A">
    <transforms:logicle transforms:T="262143" transforms:W="0.5" transforms:M="4.5" transforms:A="0.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="Y690-H">
    <transforms:logicle transforms:T="262143" transforms:W="0.5" transforms:M="4.5" transforms:A="0.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="Y690-A">
    <transforms:logicle transforms:T="262143" transforms:W="0.5" transforms:M="4.5" transforms:A="0.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="Y780-H">
    <transforms:logicle transforms:T="262143" transforms:W="0.5" transforms:M="4.5" transforms:A="0.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="Y780-A">
    <transforms:logicle transforms:T="262143" transforms:W="0.5" transforms:M="4.5" transforms:A="0.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="FSC-Width">
    <transforms:flog transforms:T="262143" transforms:M="4.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="Time">
    <transforms:flin transforms:T="1" transforms:A="0" />
  </transforms:transformation>
  <gating:RectangleGate gating:id="TimeQC">
    <gating:dimension gating:compensation-ref="uncompensated" gating:min="0.0" gating:max="262144.0">
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
      <gating:coordinate data-type:value="1.225897074920036" />
      <gating:coordinate data-type:value="1.133543497402644" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.1759284197651527" />
      <gating:coordinate data-type:value="1.128332403227808" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.1276828216845756" />
      <gating:coordinate data-type:value="1.0710103673046099" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.0966677943470617" />
      <gating:coordinate data-type:value="1.0058716901191576" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.1104522509415125" />
      <gating:coordinate data-type:value="0.9485496541959594" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.1500825636505578" />
      <gating:coordinate data-type:value="0.9407330129337051" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.220727903697117" />
      <gating:coordinate data-type:value="1.0527715376926832" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.2327893032172614" />
      <gating:coordinate data-type:value="1.107488026528463" />
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
      <gating:coordinate data-type:value="0.9372864803986355" />
      <gating:coordinate data-type:value="0.8983284202864501" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="0.9182385910433494" />
      <gating:coordinate data-type:value="0.921498583756432" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.1235290205668065" />
      <gating:coordinate data-type:value="1.090265169815612" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.1425769099220924" />
      <gating:coordinate data-type:value="1.0670950063456301" />
    </gating:vertex>
  </gating:PolygonGate>
  <gating:RectangleGate gating:id="mCherry_neg" gating:parent_id="Singlets">
    <gating:dimension gating:compensation-ref="uncompensated" gating:transformation-ref="mCherry-A" gating:max="0.7455144353792146">
      <data-type:fcs-dimension data-type:name="mCherry-A" />
    </gating:dimension>
  </gating:RectangleGate>
</gating:Gating-ML>