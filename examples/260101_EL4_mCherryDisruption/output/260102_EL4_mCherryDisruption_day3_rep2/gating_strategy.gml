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
      <gating:coordinate data-type:value="1.231909127537966" />
      <gating:coordinate data-type:value="1.1389388949258565" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.1818571367177693" />
      <gating:coordinate data-type:value="1.1346006677047913" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.1326184792067184" />
      <gating:coordinate data-type:value="1.078129363991822" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.1004713489390652" />
      <gating:coordinate data-type:value="1.0135418946051689" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.113253298625266" />
      <gating:coordinate data-type:value="0.955988017166684" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.1527411562454486" />
      <gating:coordinate data-type:value="0.9474809220921199" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.2253310785352678" />
      <gating:coordinate data-type:value="1.0582694516537137" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.2383455754478276" />
      <gating:coordinate data-type:value="1.1127671064565905" />
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
      <gating:coordinate data-type:value="0.9421445713399901" />
      <gating:coordinate data-type:value="0.9002210337306153" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="0.9217869184287892" />
      <gating:coordinate data-type:value="0.9254092105172695" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.1262283541815046" />
      <gating:coordinate data-type:value="1.0906433926088668" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.1465860070927054" />
      <gating:coordinate data-type:value="1.0654552158222126" />
    </gating:vertex>
  </gating:PolygonGate>
  <gating:RectangleGate gating:id="mCherry_neg" gating:parent_id="Singlets">
    <gating:dimension gating:compensation-ref="uncompensated" gating:transformation-ref="mCherry-A" gating:max="0.7743005617039496">
      <data-type:fcs-dimension data-type:name="mCherry-A" />
    </gating:dimension>
  </gating:RectangleGate>
</gating:Gating-ML>