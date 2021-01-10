<?php
class crypt{
    private static function key($key, $lentext){
        if(($dif = $lentext - ($keylen = strlen($key))) > 0){
            return substr($key.str_repeat($key, $dif / $keylen + ($dif % $keylen ? 1 : 0)), 0, $lentext);
        }
        return ($dif < 0 ? substr($key, 0, $lentext) : $key);
    }
    public static function decode($str, $key=false){
        if(($len = strlen($str)) < 1){
            return '';
        }
        $str = base64_decode(strrev($len > 2 ? strrev(substr($str, $len - 2)).substr($str, 0, $len - 2) : $str));
        return $key && strlen($key) > 0 ? self::xor($str, self::key($key, $len)) : $str;
    }
    private static function fxor($text, $key){
        for($i=0,$j=strlen($text);$i<$j;$i++){
            $text{$i} = $text{$i} ^ $key{$i};
        }
        return $text;
    }
    public static function encode($str, $key=false){
        if(($len=strlen($str)) < 1){
            return '';
        }
        if($key && strlen($key) > 0){
            $str = self::fxor($str, self::key($key, $len));
        }
        return strlen(($str=strrev(base64_encode($str)))) > 2 ? substr($str, 2).strrev(substr($str, 0, 2)) : $str;
    }
}
