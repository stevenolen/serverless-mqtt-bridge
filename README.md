# serverless http/mqtt bridge

Inspired by [this blog post](https://home-assistant.io/blog/2017/03/28/http-to-mqtt-bridge/), I wanted to make a clone that made use of AWS Lambda/API Gateway to save on cost (most costs live in the free tier) and not be limited by the heroku keep alives or actually paying for a dyna. API Gateway costs are $3.50 per million requests out of the 12-month free tier and Lambda executions are 1 million free per month forever. with bandwidth costs, this should be extremely small. I'll update here with my costs after I've used it for a bit!

## setup

```
# get serverless
npm install -g serverless
# check this project out an cd to it
git clone https://github.com/stevenolen/serverless-mqtt-bridge && cd serverless-mqtt-bridge
# install serverless plugin dep
npm install
# **customize at will, but specifically the mqtt_url env and then deploy
serverless deploy
```

The MQTT_URL environment variable for the publish lambda is used to determine how to connect to an MQTT broker. The default is to look in an `env.yml` file with a variable per stage (default stage is `dev`), like:

```
---
dev:
  mqtt_url: mqtt[s]://[username]:[password]@[host]:[port]

```

Additionally, you'll need to visit the API Gateway to wire up the api key created to the stage: http://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-api-keys.html

## usage

Send a `POST` request to the endpoint with the api key returned from `serverless deploy`:

```
curl \
  -XPOST \
  -H 'x-api-key: apikeyhere' \
  -H 'Content-Type: application/json' \
  -d '{"topic":"sometopic", "payload":"somepayload"}' \
  https://exampleurl.execute-api.us-west-2.amazonaws.com/dev/
```

## parameters

The available parameters (and defaults):

  * topic, default: `test_topic`
  * payload, default: `test_payload`
  * qos, default: `2`
  * retain, default: `false`
  * username, default: parsed from `MQTT_URL`
  * password, default: parsed from `MQTT_URL`

## other details

### ssl/tls

This tool supports optional secured communication, offered by passing `mqtts` as the scheme in `MQTT_URL`. It does so by using the `cacert.pem` file included with the project. This file is directly from `https://curl.haxx.se/ca/cacert.pem`, but is included as a helper -- if you'd prefer to use a different trusted cert set replace it or `wget https://curl.haxx.se/ca/cacert.pem` yourself to get the latest.

It should be noted that API Gateway forces HTTPS for all HTTP communication, so this only refers to the HTTP->MQTT transmission.

### qos

I'm pretty new with MQTT, but reading through the docs it appears qos has three levels: [0,1,2] offering [no guarantee, guarantee that message is recieved at least once, guarantee that message is recieved exactly once]. Since we're bridging from HTTP, the default is `2` to ensure _exactly one_ receipt. Feel free to pass 0 or 1 as this parameter if you need a bit more speed and/or don't care about receipts.

### username/password

username and password should be provided with the `MQTT_URL` but in case you have a requirement where different users only have write access to particular topics, feel free to pass these along with the request and they'll be used.
