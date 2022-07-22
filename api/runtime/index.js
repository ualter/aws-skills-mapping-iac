"use strict";

const mockSkills = require('./mock-skills.js');

// const { DynamoDB, Lambda } = require('aws-sdk');

exports.handler = async function (event) {
    
    console.log("request:", JSON.stringify(event, undefined, 2));
    try {
        var method = event.httpMethod;

        if (method === "GET") {
            if (event.path === "/") {
                var body = {
                    author: "Ualter Otoni",
                    email: "ualter.junior@gmail.com",
                };
                return sendRes(200, JSON.stringify(body));
            } else if(event.path === "/skills") {
                body  = mockSkills.getSkills(1);
                return sendRes(200, JSON.stringify(body));
            }
        }

        return sendRes(200, 'OK');

    } catch (error) {
        var body = error.stack || JSON.stringify(error, null, 2);
        sendRes(500,body)
    }
    

    // create AWS SDK clients
    // const dynamo = new DynamoDB();
    // update dynamo entry for "path" with hits++
    // await dynamo.updateItem({
    //     TableName: process.env.HITS_TABLE_NAME,
    //     Key: { path: { S: event.rawPath } },
    //     UpdateExpression: 'ADD hits :incr',
    //     ExpressionAttributeValues: { ':incr': { N: '1' } }
    // }).promise();
    // console.log('inserted counter for ' + event.rawPath);

    // return response back to upstream caller
    
};

const sendRes = (status, body) => {
    var response = {
        statusCode: status,
        headers: {
            "Content-Type": "application/json"
        },
        body: body
    };
    return response;
};