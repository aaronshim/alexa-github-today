# The Federalist Papers
An Alexa skill that reads you various fragments of The Federalist Papers.

## Motivation
I wanted to try building an Alexa skill and evaluate how easily the Alexa Skills Kit allowed developers to get started.

## Setup
This project is heavily based off of the (now old) [serverless template](https://github.com/awslabs/serverless-application-model/tree/master/examples/apps/alexa-skills-kit-color-expert-python). You will need to set up a AWS Lambda to run this script.

Once you get a Skill ID, you will also need to update the following section of code:

```
if (event['session']['application']['applicationId'] !=
  amzn1.echo-sdk-ams.app.[unique-value-here]"):
  raise ValueError("Invalid Application ID")
```
