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
      <gating:coordinate data-type:value="1.4414944911305787" />
      <gating:coordinate data-type:value="1.449210145060634" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.4043067152462356" />
      <gating:coordinate data-type:value="1.448685613058813" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.3710830035050752" />
      <gating:coordinate data-type:value="1.4165963287265109" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.3551338729174263" />
      <gating:coordinate data-type:value="1.3604159039193735" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.3660539991332756" />
      <gating:coordinate data-type:value="1.2816639859703198" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.3983545817956242" />
      <gating:coordinate data-type:value="1.2313370873025915" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.443145213831386" />
      <gating:coordinate data-type:value="1.2688353472110558" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.4640769117833754" />
      <gating:coordinate data-type:value="1.3687283977098528" />
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
      <gating:coordinate data-type:value="1.240272366841364" />
      <gating:coordinate data-type:value="1.2282044399059828" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.2331948331686813" />
      <gating:coordinate data-type:value="1.235837433742326" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.4449497325343024" />
      <gating:coordinate data-type:value="1.4321827292775993" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.452027266206985" />
      <gating:coordinate data-type:value="1.4245497354412562" />
    </gating:vertex>
  </gating:PolygonGate>
  <gating:RectangleGate gating:id="Live" gating:parent_id="Singlets">
    <gating:dimension gating:compensation-ref="uncompensated" gating:transformation-ref="LDAqua-A" gating:min="0.590945331108255" gating:max="0.7739291677402034">
      <data-type:fcs-dimension data-type:name="LDAqua-A" />
    </gating:dimension>
  </gating:RectangleGate>
  <gating:RectangleGate gating:id="mCherry_pos" gating:parent_id="Live">
    <gating:dimension gating:compensation-ref="uncompensated" gating:transformation-ref="mCherry-A" gating:min="1.0808575566148075">
      <data-type:fcs-dimension data-type:name="mCherry-A" />
    </gating:dimension>
  </gating:RectangleGate>
  <gating:RectangleGate gating:id="APC_neg" gating:parent_id="mCherry_pos">
    <gating:dimension gating:compensation-ref="uncompensated" gating:transformation-ref="APC-A" gating:max="1.0197976552929084">
      <data-type:fcs-dimension data-type:name="APC-A" />
    </gating:dimension>
  </gating:RectangleGate>
</gating:Gating-ML>