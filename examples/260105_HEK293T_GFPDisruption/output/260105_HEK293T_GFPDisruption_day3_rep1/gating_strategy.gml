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
      <gating:coordinate data-type:value="1.1433076912584939" />
      <gating:coordinate data-type:value="0.9639892901051195" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.0981840630273283" />
      <gating:coordinate data-type:value="0.9711498989796581" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.0840307675590575" />
      <gating:coordinate data-type:value="1.0198995126833093" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.1043599725178197" />
      <gating:coordinate data-type:value="1.1077683023706064" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.171930568787403" />
      <gating:coordinate data-type:value="1.1831075560439066" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.2242150270335208" />
      <gating:coordinate data-type:value="1.2071215793224033" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.2493870644909888" />
      <gating:coordinate data-type:value="1.145450462126719" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.2008240235324412" />
      <gating:coordinate data-type:value="1.0412260133591857" />
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
      <gating:coordinate data-type:value="0.9401072317550844" />
      <gating:coordinate data-type:value="0.9153470400287445" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="0.9256493313189128" />
      <gating:coordinate data-type:value="0.9334807852413982" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.195960916625647" />
      <gating:coordinate data-type:value="1.1489982054586727" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.2104188170618186" />
      <gating:coordinate data-type:value="1.1308644602460192" />
    </gating:vertex>
  </gating:PolygonGate>
  <gating:RectangleGate gating:id="mCherry_pos" gating:parent_id="Singlets">
    <gating:dimension gating:compensation-ref="uncompensated" gating:transformation-ref="mCherry-A" gating:min="0.5037352706224366">
      <data-type:fcs-dimension data-type:name="mCherry-A" />
    </gating:dimension>
  </gating:RectangleGate>
  <gating:RectangleGate gating:id="GFP_neg" gating:parent_id="mCherry_pos">
    <gating:dimension gating:compensation-ref="uncompensated" gating:transformation-ref="GFP-A" gating:max="0.8118377033420362">
      <data-type:fcs-dimension data-type:name="GFP-A" />
    </gating:dimension>
  </gating:RectangleGate>
</gating:Gating-ML>