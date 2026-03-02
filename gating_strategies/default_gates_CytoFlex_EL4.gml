<?xml version='1.0' encoding='UTF-8'?>
<gating:Gating-ML xmlns:gating="http://www.isac-net.org/std/Gating-ML/v2.0/gating" xmlns:data-type="http://www.isac-net.org/std/Gating-ML/v2.0/datatypes" xmlns:transforms="http://www.isac-net.org/std/Gating-ML/v2.0/transformations">
  <transforms:transformation transforms:id="FSC-A">
    <transforms:flog transforms:T="262144" transforms:M="4.5"/>
  </transforms:transformation>
  <transforms:transformation transforms:id="SSC-A">
    <transforms:flog transforms:T="262144" transforms:M="4.5"/>
  </transforms:transformation>
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
      <gating:coordinate data-type:value="1.2417779176215593"/>
      <gating:coordinate data-type:value="1.15603805392402"/>
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.191809262466676"/>
      <gating:coordinate data-type:value="1.150826959749184"/>
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.143563664386099"/>
      <gating:coordinate data-type:value="1.093504923825986"/>
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.112548637048585"/>
      <gating:coordinate data-type:value="1.0283662466405337"/>
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.1263330936430358"/>
      <gating:coordinate data-type:value="0.9710442107173356"/>
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.1659634063520812"/>
      <gating:coordinate data-type:value="0.9632275694550814"/>
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.2366087463986404"/>
      <gating:coordinate data-type:value="1.0752660942140593"/>
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.2486701459187848"/>
      <gating:coordinate data-type:value="1.1299825830498391"/>
    </gating:vertex>
  </gating:PolygonGate>
</gating:Gating-ML>
