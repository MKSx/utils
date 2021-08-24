function Key(key, lentext){
    const dif = lentext - key.length;
    if(dif > 0){
        return key + key.repeat(dif / key.length + (dif % key.length ? 1 : 0)).substring(0, lentext);
    }
    return dif < 0 ? key.substring(0, lentext) : key;
}
function XorFunction(text, key){
    var ret = '';
    for(var i=0,j=text.length; i < j; i++){
        ret += String.fromCharCode(text[i].charCodeAt(0) ^ key[i].charCodeAt(0));
    }
    return ret;
}

module.exports = {
    encode: (str, key=false) => {
        if(str.length < 1){
            return '';
        }
        if(key != false && key.length > 0){
            str = XorFunction(str, Key(key, str.length));
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
            key = Key(key, str.length);
            console.log(`key: '${key}'`);
            return XorFunction(str, key);
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
