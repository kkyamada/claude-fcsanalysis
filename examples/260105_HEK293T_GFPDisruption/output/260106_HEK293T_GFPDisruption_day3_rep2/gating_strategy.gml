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
      <gating:coordinate data-type:value="1.1331806456962297" />
      <gating:coordinate data-type:value="0.9673756434735168" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.0894927216549724" />
      <gating:coordinate data-type:value="0.9807465610622204" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.0822617999950215" />
      <gating:coordinate data-type:value="1.030991504895556" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.1146221344669756" />
      <gating:coordinate data-type:value="1.1151758830676912" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.1920203358963024" />
      <gating:coordinate data-type:value="1.180377930886623" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.2471380714750802" />
      <gating:coordinate data-type:value="1.1968816611552058" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.2634821757745824" />
      <gating:coordinate data-type:value="1.1323074525222616" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.2008865072615127" />
      <gating:coordinate data-type:value="1.0358559779278333" />
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
      <gating:coordinate data-type:value="0.9324552764832966" />
      <gating:coordinate data-type:value="0.9029590820989404" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="0.9091469728627241" />
      <gating:coordinate data-type:value="0.9335790278591423" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.1832089735422886" />
      <gating:coordinate data-type:value="1.1421986110787676" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.206517277162861" />
      <gating:coordinate data-type:value="1.1115786653185658" />
    </gating:vertex>
  </gating:PolygonGate>
  <gating:RectangleGate gating:id="mCherry_pos" gating:parent_id="Singlets">
    <gating:dimension gating:compensation-ref="uncompensated" gating:transformation-ref="mCherry-A" gating:min="0.48900593155030675">
      <data-type:fcs-dimension data-type:name="mCherry-A" />
    </gating:dimension>
  </gating:RectangleGate>
  <gating:RectangleGate gating:id="GFP_neg" gating:parent_id="mCherry_pos">
    <gating:dimension gating:compensation-ref="uncompensated" gating:transformation-ref="GFP-A" gating:max="0.7863697642918229">
      <data-type:fcs-dimension data-type:name="GFP-A" />
    </gating:dimension>
  </gating:RectangleGate>
</gating:Gating-ML>