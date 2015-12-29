Title: Logstash Debug
Date: 2015-03-23
slug: logstash_debug
Category: Linux


Logstash 能使用 rubydebug 这个 codec 进行 debug。


    input {
        stdin {}
    }

    output {
        stdout {
            codec => rubydebug
        }
    }

用 logstash 手动启动

    logstash -f debug.conf --verbose --debug


直接输入数据，能得到详细的输出报告


    ./logstash -f debug --verbose --debug                            
    a
    Pipeline started {:level=>:info}
    {
           "message" => "a",
          "@version" => "1",
        "@timestamp" => "2015-03-23T09:55:15.226Z",
              "type" => "test",
              "host" => "jeffrey-thinkpad"
    }

# REF

* <http://logstash.net/docs/1.4.2/codecs/rubydebug>
* <http://logstash.net/docs/1.4.2/flags>
