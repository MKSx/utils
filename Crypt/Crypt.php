
<?php
if(!function_exists("mb_ord")){
    function mb_ord($charUTF8){
        $charUCS4 = mb_convert_encoding($charUTF8, 'UCS-4BE', 'UTF-8');
        $byte1 = ord(substr($charUCS4, 0, 1));
        $byte2 = ord(substr($charUCS4, 1, 1));
        $byte3 = ord(substr($charUCS4, 2, 1));
        $byte4 = ord(substr($charUCS4, 3, 1));
        return ($byte1 << 32) + ($byte2 << 16) + ($byte3 << 8) + $byte4;
    }
}

if(!function_exists('mb_str_split')){
    function mb_str_split($str, $l = 0) {
        if ($l > 0) {
            $ret = array();
            $len = mb_strlen($str, "UTF-8");
            for ($i = 0; $i < $len; $i += $l) {
                $ret[] = mb_substr($str, $i, $l, "UTF-8");
            }
            return $ret;
        }
        return preg_split("//u", $str, -1, PREG_SPLIT_NO_EMPTY);
    }
}
if(!function_exists('mb_chr')){
    function mb_chr($u) {
        return mb_convert_encoding('&#' . intval($u) . ';', 'UTF-8', 'HTML-ENTITIES');
    }
}

class CryptoXOR{
    private $key;
    private $key_len=0;
    public function __construct(string $key){
        $this->key_len = strlen($key);
        if($this->key_len > 0){
            $this->key = $key;

        }else{
            throw new Exception("Chave não deve ser vazia");
        }
    }
    public function setKey(string $key){
        if(strlen($key) > 0){
            $this->key_len = strlen($key);
            $this->key = $key;
            return true;
        }
        return false;
    }
    public function execute(string $text){
        $output = '';
        
        $data = mb_str_split($text);

        for($i = 0, $j = sizeof($data); $i < $j; $i++){
            $output .= mb_chr(mb_ord($data[$i]) ^ mb_ord($this->key[$i % $this->key_len]));
        }
        return $output;
    }
    public function encode(string $text){
        $data = [];
        if(strlen($text) > 0){
            return $this->b64_encode($this->execute(($text)));
        }
        return '';
    }
    public function decode(string $text){
        if(strlen($text) > 0){
            return ($this->execute($this->b64_decode($text)));
        }
        return '';
    }
    private function b64_encode(string $text){
        if(strlen($text) < 1){
            return '';
        }
        return strlen(
            ($text=strrev(base64_encode($text)))
        ) > 2 ? substr($text, 2).strrev(substr($text, 0, 2)) : $text;
    }
    private function b64_decode(string $text){
        if(($len = strlen($text)) < 1){
            return '';
        }
        return base64_decode(strrev($len > 2 ? strrev(substr($text, $len - 2)).substr($text, 0, $len - 2) : $text));
    }
}
