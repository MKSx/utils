from burp import IBurpExtender, IHttpListener
from java.io import PrintWriter


class BurpExtender(IBurpExtender, IHttpListener):
    def registerExtenderCallbacks(self, callbacks):
        self._helpers = callbacks.getHelpers()
        self._stdout = PrintWriter(callbacks.getStdout(), True)
        self._callbacks = callbacks
        callbacks.setExtensionName("Replace Status Code")
        callbacks.registerHttpListener(self)

    def _headersToDict(self, headers):
        h = {}
        for i in headers:
            i = str(i).split(':', 1)
            if len(i) != 2 or len(i[1]) < 1 or len(i[0]) < 1:
                continue
            h[i[0].lower()] = i[1][1:] if i[1].startswith(' ') else i[1]
        return h


    def processHttpMessage(self, toolFlag, messageIsRequest, messageInfo):
        if not messageIsRequest:

            # Get Response
            responseInfo = self._helpers.analyzeResponse(messageInfo.getResponse())

            # Get Body
            body = messageInfo.getResponse()[responseInfo.getBodyOffset():]


            # Get headers
            headers = list(responseInfo.getHeaders())

            # Headers List to Dict
            temp = self._headersToDict(headers)

            '''
            # body search and replace
            body = str(self._helpers.bytesToString(messageInfo.getRequest()[requestInfo.getBodyOffset():]).encode('utf-8'))


            if body.find('test-123') > -1:
                body = 'hello world'

            # send message
            messageInfo.setRequest(self._helpers.buildHttpMessage(headers, self._helpers.stringToBytes(body)))
            
            '''

            # Get Content Length
            content_length = int(temp['content-length']) if 'content-length' in temp else 0

            # Example based in Content-Length
            if headers[0].endswith(' 200 OK') and ('content-type' in temp and temp['content-type'].find('text/html') > -1) and content_length >= 11000 and content_length <= 13000:

                # Replace status code 200 to 404
                headers[0] = headers[0].replace('200 OK','404 Not Found')

                # Send Message
                messageInfo.setResponse(self._helpers.buildHttpMessage(headers, body))
                return
            
