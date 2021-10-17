package cryptoxor

import (
	"encoding/base64"
	"errors"
	"strings"
)

type CryptoXOR struct {
	Internal CryptoXOR_Internal
}

type CryptoXOR_Internal struct {
	Data   []rune
	Key    []rune
	KeyLen int
}

func NewCryptoXOR(key string) (*CryptoXOR, error) {

	key_len := len(key)

	if key_len < 1 {
		return nil, errors.New("Key cannot be empty")
	}
	return &CryptoXOR{
		Internal: CryptoXOR_Internal{
			Key:    []rune(key),
			KeyLen: key_len,
		},
	}, nil
}

func (c *CryptoXOR) Encode(data string) (output string) {
	c.Internal.Data = []rune(data)

	c.Internal.Data = c.Internal.XORFunction()

	output = c.Internal.B64_Encode()
	return
}

func (c *CryptoXOR) Decode(data string) (output string, err error) {

	err = c.Internal.B64_Decode(data)

	if err != nil {
		return
	}

	output = string(c.Internal.XORFunction())
	return
}

func (i *CryptoXOR_Internal) B64_Decode(data string) (err error) {
	l := len(data)

	if l > 2 {
		data = reverseString(data[l-2:]) + data[0:l-2]
	}

	data = reverseString(data)

	dataByte, err := base64.StdEncoding.DecodeString(data)

	if err != nil {
		return
	}

	i.Data = []rune(string(dataByte))
	return
}
func (i *CryptoXOR_Internal) XORFunction() (output []rune) {
	output = make([]rune, len(i.Data))
	for index := range i.Data {
		output[index] = i.Data[index] ^ i.Key[index%i.KeyLen]
	}
	return
}

func reverseRune(data []rune) (output []rune) {

	size := len(data)
	output = make([]rune, size)

	size -= 1
	for index := range data {
		output[index] = data[size-index]
	}
	return
}

func reverseString(str string) (result string) {
	for _, v := range str {
		result = string(v) + result
	}
	return
}

func (i *CryptoXOR_Internal) B64_Encode() (output string) {

	output = reverseString(base64.StdEncoding.EncodeToString([]byte(string(i.Data))))

	if len(output) > 2 {
		output = output[2:] + reverseString(output[0:2])
	}
	return
}

func (x *CryptoXOR) Pad(str string) string {

	return str + (func(l int) string {
		if l != 4 {
			return strings.Repeat("=", l)
		}
		return ""
	})(4-(len(str)%4))
}

func (x *CryptoXOR) Unpad(str string) string {
	return strings.Replace(str, "=", "", 2)
}
