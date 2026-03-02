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
  <transforms:transformation transforms:id="mCherry-H">
    <transforms:logicle transforms:T="16777215" transforms:W="0.5" transforms:M="4.5" transforms:A="0.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="mCherry-A">
    <transforms:logicle transforms:T="16777215" transforms:W="0.5" transforms:M="4.5" transforms:A="0.5" />
  </transforms:transformation>
  <transforms:transformation transforms:id="mCherry-W">
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
      <gating:coordinate data-type:value="1.465723127382942" />
      <gating:coordinate data-type:value="1.4333738202228492" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.4301933614989577" />
      <gating:coordinate data-type:value="1.4443666153757808" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.3886795997560042" />
      <gating:coordinate data-type:value="1.42411458395253" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.3561503691647687" />
      <gating:coordinate data-type:value="1.375612377248561" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.342200345375239" />
      <gating:coordinate data-type:value="1.2973403479309553" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.3573681580338819" />
      <gating:coordinate data-type:value="1.2394951940372079" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.411554180071676" />
      <gating:coordinate data-type:value="1.2613170919850367" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.4623300580301202" />
      <gating:coordinate data-type:value="1.3498527782062306" />
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
      <gating:coordinate data-type:value="1.228233093075133" />
      <gating:coordinate data-type:value="1.2179588363710878" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.2217766886906596" />
      <gating:coordinate data-type:value="1.2248835676066814" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.440234212001055" />
      <gating:coordinate data-type:value="1.4285665790241697" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.4466906163855284" />
      <gating:coordinate data-type:value="1.4216418477885762" />
    </gating:vertex>
  </gating:PolygonGate>
  <gating:RectangleGate gating:id="Live" gating:parent_id="Singlets">
    <gating:dimension gating:compensation-ref="uncompensated" gating:transformation-ref="LDAqua-A" gating:min="0.5873623509192789" gating:max="0.777280978599788">
      <data-type:fcs-dimension data-type:name="LDAqua-A" />
    </gating:dimension>
  </gating:RectangleGate>
  <gating:RectangleGate gating:id="mCherry_pos" gating:parent_id="Live">
    <gating:dimension gating:compensation-ref="uncompensated" gating:transformation-ref="mCherry-A" gating:min="1.0823318944770586">
      <data-type:fcs-dimension data-type:name="mCherry-A" />
    </gating:dimension>
  </gating:RectangleGate>
  <gating:RectangleGate gating:id="APC_neg" gating:parent_id="mCherry_pos">
    <gating:dimension gating:compensation-ref="uncompensated" gating:transformation-ref="APC-A" gating:max="1.0144179421913324">
      <data-type:fcs-dimension data-type:name="APC-A" />
    </gating:dimension>
  </gating:RectangleGate>
</gating:Gating-ML>