
function EncryptDecrypt(input, key){
    var output = "";
    for(var i = 0; i < input.length; i++){
        output +=  String.fromCharCode(input[i].charCodeAt(0) ^ key[i % key.length].charCodeAt(0))
    }
	return output
}

module.exports = {
    encode: (str, key=false) => {
        if(str.length < 1){
            return '';
        }
        if(key != false && key.length > 0){
            str = EncryptDecrypt(str,key);
        }
        str = Buffer.from(str).toString('base64');
        return str.length > 2 ? str.substring(0, str.length - 2).split('').reverse().join('') + str.substring(str.length - 2) : str.split('').reverse().join('');
    },
    decode: (str, key=false) => {
        if(str.length < 1){
            return '';
        }
        str = str.length > 2 ? str.substring(0, str.length - 2).split('').reverse().join('') + str.substring(str.length - 2) : str = str.split('').reverse().join('');
        
        str = Buffer.from(str, 'base64').toString();
        if(key != false && key.length > 0){
            
            return EncryptDecrypt(str, key);
        }
        return str;
    },
    unpad: (str) => {
        return str.replace(/=/g, '');
    },
    pad: (str) => {
        const pads = 4 - (str.length % 4);
        return str + (pads != 4 ? '='.repeat(pads) : '');
    }
}
