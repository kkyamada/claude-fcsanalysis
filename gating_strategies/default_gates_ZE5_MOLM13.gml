<?xml version='1.0' encoding='UTF-8'?>
<gating:Gating-ML xmlns:gating="http://www.isac-net.org/std/Gating-ML/v2.0/gating" xmlns:data-type="http://www.isac-net.org/std/Gating-ML/v2.0/datatypes" xmlns:transforms="http://www.isac-net.org/std/Gating-ML/v2.0/transformations">
  <transforms:transformation transforms:id="FSC-A">
    <transforms:flog transforms:T="16777215" transforms:M="4.5"/>
  </transforms:transformation>
  <transforms:transformation transforms:id="SSC-A">
    <transforms:flog transforms:T="16777215" transforms:M="4.5"/>
  </transforms:transformation>
  <gating:RectangleGate gating:id="TimeQC">
    <gating:dimension gating:compensation-ref="uncompensated" gating:min="0.0" gating:max="100000.0">
      <data-type:fcs-dimension data-type:name="TIME"/>
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
      <gating:coordinate data-type:value="1.4542319821540417"/>
      <gating:coordinate data-type:value="1.4530773327639643"/>
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.4174199946173098"/>
      <gating:coordinate data-type:value="1.458376708448"/>
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.3795854518712243"/>
      <gating:coordinate data-type:value="1.4318798300278222"/>
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.3550441268467366"/>
      <gating:coordinate data-type:value="1.3788860731874664"/>
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.353510294032706"/>
      <gating:coordinate data-type:value="1.299395437926933"/>
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.3775403414525171"/>
      <gating:coordinate data-type:value="1.2446352225252324"/>
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.4276455467108464"/>
      <gating:coordinate data-type:value="1.2746650180681005"/>
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.4639462566429013"/>
      <gating:coordinate data-type:value="1.3700537803807404"/>
    </gating:vertex>
  </gating:PolygonGate>
</gating:Gating-ML>
