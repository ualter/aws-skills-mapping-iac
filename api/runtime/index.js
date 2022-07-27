"use strict";

const AWS       = require('aws-sdk');
const docClient = new AWS.DynamoDB.DocumentClient();

async function readMySkills(_id){
    var params = {
        Key: {
         "id": _id
        }, 
        TableName: "AwsSkillsMappingTable"
    };
    var result = await docClient.get(params).promise();
    return result;
}

exports.handler = async function (event) {
    console.log("request:", JSON.stringify(event, undefined, 2));
    try {
        var method = event.httpMethod;
        var body   = {};

        if (method === "GET") {
            if (event.path === "/") {

                body = {
                    author: "Ualter Otoni",
                    email: "ualter.junior@gmail.com",
                };
                return sendRes(200, JSON.stringify(body));
                
            } else if( event.path.includes("/skills") ) {

                body = await readMySkills("1");
                return sendRes(200, JSON.stringify(body));

            }
        }

        return sendRes(200, 'OK');

    } catch (error) {
        body = error.stack || JSON.stringify(error, null, 2);
        sendRes(500,body)
    }
};

const sendRes = (status, body) => {
    var response = {
        statusCode: status,
        headers: {
            "Content-Type": "application/json",
            "Access-Control-Allow-Headers" : "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET"
        },
        body: body
    };
    return response;
};