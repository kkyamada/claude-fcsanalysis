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
      <gating:coordinate data-type:value="1.1572928516569445" />
      <gating:coordinate data-type:value="0.9631401949686921" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.1117796434912957" />
      <gating:coordinate data-type:value="0.9671356957719562" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.0942602235910883" />
      <gating:coordinate data-type:value="1.014779273883047" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.1084104907075634" />
      <gating:coordinate data-type:value="1.1038521132668808" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.1705610877299566" />
      <gating:coordinate data-type:value="1.1837213308293244" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.2210430500792773" />
      <gating:coordinate data-type:value="1.2113240365929265" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.2504557293860727" />
      <gating:coordinate data-type:value="1.1515590597091394" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.2092813155784787" />
      <gating:coordinate data-type:value="1.0442009099689415" />
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
      <gating:coordinate data-type:value="0.9212591436279314" />
      <gating:coordinate data-type:value="0.8846768737495257" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="0.899486497604409" />
      <gating:coordinate data-type:value="0.9112421270434591" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.1946546185512914" />
      <gating:coordinate data-type:value="1.1531593014704142" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.216427264574814" />
      <gating:coordinate data-type:value="1.1265940481764811" />
    </gating:vertex>
  </gating:PolygonGate>
  <gating:RectangleGate gating:id="mCherry_pos" gating:parent_id="Singlets">
    <gating:dimension gating:compensation-ref="uncompensated" gating:transformation-ref="mCherry-A" gating:min="0.6196444862127184">
      <data-type:fcs-dimension data-type:name="mCherry-A" />
    </gating:dimension>
  </gating:RectangleGate>
</gating:Gating-ML>