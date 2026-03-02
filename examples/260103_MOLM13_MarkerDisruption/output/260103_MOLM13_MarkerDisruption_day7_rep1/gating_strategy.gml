<?xml version='1.0' encoding='UTF-8'?>
<gating:Gating-ML xmlns:data-type="http://www.isac-net.org/std/Gating-ML/v2.0/datatypes" xmlns:gating="http://www.isac-net.org/std/Gating-ML/v2.0/gating" xmlns:transforms="http://www.isac-net.org/std/Gating-ML/v2.0/transformations">
  <transforms:transformation transforms:id="FSC-A">
    <transforms:flog transforms:T="16777215.0" transforms:M="4.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="SSC-A">
    <transforms:flog transforms:T="16777215.0" transforms:M="4.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="FSC-H">
    <transforms:flog transforms:T="16777215" transforms:M="4.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="FSC-W">
    <transforms:flog transforms:T="16777215" transforms:M="4.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="SSC-H">
    <transforms:flog transforms:T="16777215" transforms:M="4.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="SSC-W">
    <transforms:flog transforms:T="16777215" transforms:M="4.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="APC-H">
    <transforms:logicle transforms:T="16777215" transforms:W="0.5" transforms:M="4.5" transforms:A="0.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="APC-A">
    <transforms:logicle transforms:T="16777215" transforms:W="0.5" transforms:M="4.5" transforms:A="0.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="APC-W">
    <transforms:logicle transforms:T="16777215" transforms:W="0.5" transforms:M="4.5" transforms:A="0.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="LDAqua-H">
    <transforms:logicle transforms:T="16777215" transforms:W="0.5" transforms:M="4.5" transforms:A="0.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="LDAqua-A">
    <transforms:logicle transforms:T="16777215" transforms:W="0.5" transforms:M="4.5" transforms:A="0.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="LDAqua-W">
    <transforms:logicle transforms:T="16777215" transforms:W="0.5" transforms:M="4.5" transforms:A="0.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="TIME">
    <transforms:flin transforms:T="1" transforms:A="0" />
  </transforms:transformation>
  <gating:RectangleGate gating:id="TimeQC">
    <gating:dimension gating:compensation-ref="uncompensated" gating:min="0.0" gating:max="100000.0">
      <data-type:fcs-dimension data-type:name="TIME" />
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
      <gating:coordinate data-type:value="1.462041928629269" />
      <gating:coordinate data-type:value="1.4262491040254237" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.4265121627452846" />
      <gating:coordinate data-type:value="1.4372418991783553" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.384998401002331" />
      <gating:coordinate data-type:value="1.4169898677551045" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.3524691704110958" />
      <gating:coordinate data-type:value="1.3684876610511354" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.3385191466215658" />
      <gating:coordinate data-type:value="1.2902156317335298" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.3536869592802088" />
      <gating:coordinate data-type:value="1.2323704778397824" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.4078729813180029" />
      <gating:coordinate data-type:value="1.2541923757876112" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.458648859276447" />
      <gating:coordinate data-type:value="1.3427280620088051" />
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
      <gating:coordinate data-type:value="1.2321896539536812" />
      <gating:coordinate data-type:value="1.220906367033372" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.2258633849634413" />
      <gating:coordinate data-type:value="1.227637261319816" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.4334422859396605" />
      <gating:coordinate data-type:value="1.422737631105549" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.4397685549299004" />
      <gating:coordinate data-type:value="1.416006736819105" />
    </gating:vertex>
  </gating:PolygonGate>
  <gating:RectangleGate gating:id="Live" gating:parent_id="Singlets">
    <gating:dimension gating:compensation-ref="uncompensated" gating:transformation-ref="LDAqua-A" gating:min="0.5746016014379594" gating:max="0.7558501896929506">
      <data-type:fcs-dimension data-type:name="LDAqua-A" />
    </gating:dimension>
  </gating:RectangleGate>
  <gating:RectangleGate gating:id="APC_neg" gating:parent_id="Live">
    <gating:dimension gating:compensation-ref="uncompensated" gating:transformation-ref="APC-A" gating:max="1.113557502705437">
      <data-type:fcs-dimension data-type:name="APC-A" />
    </gating:dimension>
  </gating:RectangleGate>
</gating:Gating-ML>