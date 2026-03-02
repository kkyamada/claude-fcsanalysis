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
      <gating:coordinate data-type:value="1.4411425993658058" />
      <gating:coordinate data-type:value="1.4478939268302864" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.4039591713668838" />
      <gating:coordinate data-type:value="1.4486675490210377" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.3696357987405006" />
      <gating:coordinate data-type:value="1.4177573034320827" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.3517357153819725" />
      <gating:coordinate data-type:value="1.362167718852145" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.3599007870512045" />
      <gating:coordinate data-type:value="1.2830826675348395" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.3904253096372263" />
      <gating:coordinate data-type:value="1.2316591525758787" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.4364973268281793" />
      <gating:coordinate data-type:value="1.2675713990425408" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.4609024909418173" />
      <gating:coordinate data-type:value="1.3666730916703407" />
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
      <gating:coordinate data-type:value="1.2397124999042144" />
      <gating:coordinate data-type:value="1.2228814212674635" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.2297547972696719" />
      <gating:coordinate data-type:value="1.2335202911380436" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.4430828451817221" />
      <gating:coordinate data-type:value="1.433189738227524" />
    </gating:vertex>
    <gating:vertex>
      <gating:coordinate data-type:value="1.4530405478162647" />
      <gating:coordinate data-type:value="1.4225508683569439" />
    </gating:vertex>
  </gating:PolygonGate>
  <gating:RectangleGate gating:id="Live" gating:parent_id="Singlets">
    <gating:dimension gating:compensation-ref="uncompensated" gating:transformation-ref="LDAqua-A" gating:min="0.5769601395382067" gating:max="0.7786910822418316">
      <data-type:fcs-dimension data-type:name="LDAqua-A" />
    </gating:dimension>
  </gating:RectangleGate>
  <gating:RectangleGate gating:id="APC_neg" gating:parent_id="Live">
    <gating:dimension gating:compensation-ref="uncompensated" gating:transformation-ref="APC-A" gating:max="1.160904353829057">
      <data-type:fcs-dimension data-type:name="APC-A" />
    </gating:dimension>
  </gating:RectangleGate>
</gating:Gating-ML>