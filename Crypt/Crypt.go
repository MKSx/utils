package crypt

import (
	"fmt"
	"encoding/base64"
	"strings"
)

func Reverse(str string) (result string) {
    for _, v := range str { 
		result = string(v) + result 
    }
    return
}

func Key(key string, lenstr int) (result string){
	keylen := len(key)
	dif := lenstr - keylen

	if dif > 0 {
		return (key + strings.Repeat(key, dif / keylen + func() int {if dif % lenstr > 0 {return 1} else {return 0}}()))[0:lenstr]
	}
	return func() string {if dif < 0 {return key[0:lenstr]}else {return key}}()
}

func XOR(str string, key string) (result string){
	ret := []byte(str)
	for i := range ret{
		ret[i] = ret[i] ^ key[i]
	}
	return string(ret)
}

func Encode(str string, key string) (result string){
	l := len(str)

	if l < 1{
		return ""
	}
	str = XOR(str, Key(key, l))
	return func() string {str = Reverse(base64.StdEncoding.EncodeToString([] byte(str)));if len(str) > 2{return str[2:] + Reverse(str[0:2])}else{return str}}()
}

func Decode(str string, key string) (result string){
	l := len(str)

	if l < 1{
		return ""
	}
	if l > 2{
		str = Reverse(str[l - 2:]) + str[0:l - 2]
	}
	str = Reverse(str)
	ret, err := base64.StdEncoding.DecodeString(str)
	if err != nil{
		fmt.Printf("Error decoding string: %s ", err.Error())
	}
	return XOR(string(ret), Key(key, len(ret)))
}
