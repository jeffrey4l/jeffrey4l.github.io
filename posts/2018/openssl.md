title: 如何生成证书
date: 2018-1-1
category: Linux
tags: Linux OpenSSL
status: draft

## 直接生自签证书

    ::bash
    openssl req -x509 -newkey rsa:4096 -keyout key.pem \
        -out cert.pem -days 365 -nodes \
        -subj "/C=CN/ST=Beijing/L=Beijing/O=Xcodest/OU=Xcodest/CN=hub.xcodest.me"
