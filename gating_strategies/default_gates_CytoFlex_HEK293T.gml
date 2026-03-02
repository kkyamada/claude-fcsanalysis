<?xml version='1.0' encoding='UTF-8'?>
<gating:Gating-ML xmlns:gating="http://www.isac-net.org/std/Gating-ML/v2.0/gating" xmlns:data-type="http://www.isac-net.org/std/Gating-ML/v2.0/datatypes" xmlns:transforms="http://www.isac-net.org/std/Gating-ML/v2.0/transformations">
  <transforms:transformation transforms:id="FSC-A">
    <transforms:flog transforms:T="262143" transforms:M="4.5"/>
  </transforms:transformation>
  <transforms:transformation transforms:id="SSC-A">
    <transforms:flog transforms:T="262143" transforms:M="4.5"/>
  </transforms:transformation>
  <gating:RectangleGate gating:id="TimeQC">
    <gating:dimension gating:compensation-ref="uncompensated" gating:min="0.0" gating:max="100000.0">
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
      <gating:coordinate data-type:value="1.1303337270933254"/>
      <gating:coordinate data-type:value="0.930571133820477"/>
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.086005896075761"/>
      <gating:coordinate data-type:value="0.9416372777503574"/>
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.0761552669607468"/>
      <gating:coordinate data-type:value="0.9914349254348196"/>
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.1040653827866205"/>
      <gating:coordinate data-type:value="1.0771975408913934"/>
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.177945101149228"/>
      <gating:coordinate data-type:value="1.1463609404531463"/>
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.2321235612818067"/>
      <gating:coordinate data-type:value="1.1657266923304372"/>
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.2518248195118353"/>
      <gating:coordinate data-type:value="1.1020963647336244"/>
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.1943628163409183"/>
      <gating:coordinate data-type:value="1.0025010693647"/>
    </gating:vertex>
  </gating:PolygonGate>
</gating:Gating-ML>
