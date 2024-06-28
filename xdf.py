import http.client
import json
import time
import hashlib
import hmac

def calculate_sha1(input_string):
    # 创建 SHA-1 哈希对象
    sha1 = hashlib.sha1()

    # 更新哈希对象
    sha1.update(input_string.encode('utf-8'))

    # 获取十六进制哈希值
    return sha1.hexdigest()

def calculate_hmac_sha1(message, key):
    # 创建 HMAC-SHA1 哈希对象
    hmac_sha1 = hmac.new(key.encode('utf-8'), message.encode('utf-8'), hashlib.sha1)

    # 获取十六进制哈希值
    return hmac_sha1.hexdigest()

def getSecretInfo():

    conn = http.client.HTTPSConnection("open-api.ai.xdf.cn")

    payload = ""

    headers = {
        'Accept': "application/json, text/plain, */*",
        # 'Accept-Encoding': "gzip, deflate, br, zstd",
        'Accept-Language': "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,ja;q=0.5",
        'Origin': "https://ai.xdf.cn",
        'Priority': "u=1, i",
        'Referer': "https://ai.xdf.cn/",
        'Sec-Ch-Ua': "\"Microsoft Edge\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
        'Sec-Ch-Ua-Mobile': "?0",
        'Sec-Ch-Ua-Platform': "\"Windows\"",
        'Sec-Fetch-Dest': "empty",
        'Sec-Fetch-Mode': "cors",
        'Sec-Fetch-Site': "same-site",
        'U2-Token': "85061bd9-ef00-4d57-a45b-fce300207093",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0"
        }

    conn.request("GET", "/xdf-ai-platform-console/ocrTemplate/vod/credential?securityLevel=PUBLIC", payload, headers)

    res = conn.getresponse()
    data = res.read()

    return data.decode("utf-8")

def uploadFile(secretData, filePath):
    fileName = filePath.split('/')[-1]
    print("fileName:" + fileName)
    # 读取文件内容
    with open(filePath, 'rb') as f:
        payload = f.read()

    data = secretData["data"]
    secretId = data["credentials"]["tmpSecretId"]
    secretKey = data["credentials"]["tmpSecretKey"]
    sessionToken = data["credentials"]["sessionToken"]
    startTime = str(data["startTime"])
    expireTime = str(data["expiredTime"])
    keyPrefix = data["keyPrefix"]+fileName
    print("keyPrefix:", "https://k12static.xdf.cn/" + keyPrefix)
    length = str(len(payload))

    R = calculate_hmac_sha1(startTime + ";" + expireTime,secretKey)
    b = "put\n/"+keyPrefix+"\n\ncontent-length="+length+"&host=k12-1252350207.cos.ap-beijing.myqcloud.com\n"
    T = "sha1\n"+ startTime + ";" + expireTime+ "\n"+ calculate_sha1(b)+"\n"
    sign = calculate_hmac_sha1(T, R)
    token = "q-sign-algorithm=sha1&q-ak="+secretId+"&q-sign-time="+startTime+";"+expireTime+"&q-key-time="+startTime+";"+expireTime+"&q-header-list=content-length;host&q-url-param-list=&q-signature="+sign

    print("token: ",token)

    conn = http.client.HTTPSConnection("k12-1252350207.cos.ap-beijing.myqcloud.com")

    headers = {
        'Accept': "*/*",
        'Accept-Encoding': "gzip, deflate, br, zstd",
        'Accept-Language': "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,ja;q=0.5",
        'Authorization': token,
        "Content-Length": length,
        # 'Content-Type': "image/jpeg",
        'Content-Type': "text/html;charset=utf-8",
        'Host': "k12-1252350207.cos.ap-beijing.myqcloud.com",
        'Origin': "https://ai.xdf.cn",
        'Referer': "https://ai.xdf.cn/",
        'Sec-Ch-Ua': "\"Microsoft Edge\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
        'Sec-Ch-Ua-Mobile': "?0",
        'Sec-Ch-Ua-Platform': "\"Windows\"",
        'Sec-Fetch-Dest': "empty",
        'Sec-Fetch-Mode': "cors",
        'Sec-Fetch-Site': "cross-site",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
        'X-Cos-Security-Token': sessionToken
    }
    
    conn.request("PUT", "/"+keyPrefix , payload, headers)

    res = conn.getresponse()
    data = res.read()

    print(data.decode("utf-8"))

if __name__ == "__main__":
    secretJsonData = getSecretInfo()
    print(secretJsonData)
    secretData = json.loads(secretJsonData)
    uploadFile(secretData, "./test.html")
    # print(calculate_hmac_sha1("sha1\n1718507164;1718507464\ncabae1af848f10ea6f3c68fa9cb4fc4142e8d7c7\n", "12fcdc0434dbabb3a901eb9cd7534d3707c97d4f"))
    # print(calculate_sha1("put\n/ai-open-platform/2024/06/16/1718507709480@i2Pn6tVwsn49BRfOaOrd7OHcRL5kgr1jwGqNlStj.jpg\n\ncontent-length=5230&host=k12-1252350207.cos.ap-beijing.myqcloud.com\n"))