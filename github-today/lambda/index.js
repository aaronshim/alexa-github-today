/* eslint-disable  func-names */
/* eslint quote-props: ["error", "consistent"]*/
/**
 * This sample demonstrates a simple skill built with the Amazon Alexa Skills
 * nodejs skill development kit.
 * This sample supports multiple lauguages. (en-US, en-GB, de-DE).
 * The Intent Schema, Custom Slots and Sample Utterances for this skill, as well
 * as testing instructions are located at https://github.com/alexa/skill-sample-nodejs-fact
 **/

'use strict';

const Alexa = require('alexa-sdk');
const https = require('https');

const APP_ID = undefined;  // TODO replace with your app ID (OPTIONAL).
const GITHUB_API_TOKEN = '637618306120ac717543593c8827501fb662d79d'; // TODO replace with your Github API token

const languageStrings = {
    'en-US': {
        translation: {
            SKILL_NAME: 'Github Today',
            GET_REPO_MESSAGE: 'Check out this repo: ',
            GET_COMMIT_MESSAGE: 'Here is a commit: ',
            GET_TOP_REPOS_MESSAGE: 'Here are the top repos today: ',
            ERROR_MESSAGE: "An error occured.",
            HELP_MESSAGE: 'You can ask me about some trending repos, the top repos today, or some commits.',
            HELP_REPROMPT: 'What can I help you with?',
            STOP_MESSAGE: 'Goodbye!',
        },
    }
};

// helper for display
const repoDisplayString = (repo) => { return repo.name + " written in " + repo.language + " by " + repo.owner.login + " with " + repo.watchers + " watchers and " + repo.forks + " forks;\n"; };
const commitDisplayString = (commit) => { return commit.author.login + ' committed to ' + commit.repository.owner.login + "'s repository " + commit.repository.name + ' with the message ' + commit.commit.message; };
// helper for query
const trendingQuery = () => {
    const weekAgo = new Date();
    weekAgo.setDate(weekAgo.getDate() - 7);
    return '/search/repositories?access_token=' + encodeURIComponent(GITHUB_API_TOKEN) +
            '&sort=stars' +
            '&order=desc' +
            '&q=' + encodeURIComponent('created:"' + weekAgo.toISOString().slice(0,10) + ' .. ' + (new Date()).toISOString().slice(0,10) + '"');
};
const randomElem = (elems) => { return elems.items[Math.floor(Math.random() * elems.items.length)]; };

const handlers = {
    'LaunchRequest': function () {
        this.emit('GetTopTrendingReposIntent');
    },
    'GetTrendingRepoIntent': function () {
        // construct our query
        const path = trendingQuery();
        
        // determine how to handle the result
        const handler = (results) => {
            const randomRepo = randomElem(results);
            const speakString = repoDisplayString(randomRepo);

            const speechOutput = this.t('GET_REPO_MESSAGE') + speakString;
            this.emit(':tellWithCard', speechOutput, this.t('SKILL_NAME'), speakString);
        }

        // pass it off to the helper
        this.emit('GetGithubAPI', path, handler.bind(this));
    },
    'GetTopTrendingReposIntent': function () {
        // construct our query
        const path = trendingQuery();

        // determine how to handle the result
        const handler = (results) => {
            var speakString = '';
            for (var repo of results.items.slice(0,5)) {
              speakString += repoDisplayString(repo)
            }

            // where we really send the skill message
            const speechOutput = this.t('GET_TOP_REPOS_MESSAGE') + speakString;
            this.emit(':tellWithCard', speechOutput, this.t('SKILL_NAME'), speakString);
        }

        // pass it off to the helper
        this.emit('GetGithubAPI', path, handler.bind(this));
    },
    'GetCommitIntent': function () {
        // construct our query
        const path = '/search/commits?access_token=' + encodeURIComponent(GITHUB_API_TOKEN) +
            '&sort=committer-date' +
            '&order=desc' +
            '&q=' + encodeURIComponent('committer-date:"' + (new Date()).toISOString().slice(0,10) + ' .. ' + (new Date()).toISOString().slice(0,19) + '"');

        // determine how to handle the result
        const handler = (results) => {
            const randomCommit = randomElem(results);
            const speakString = commitDisplayString(randomCommit);

            // where we really send the skill message
            const speechOutput = this.t('GET_COMMIT_MESSAGE') + speakString;
            this.emit(':tellWithCard', speechOutput, this.t('SKILL_NAME'), speakString);
        }

        // pass it off to the helper
        this.emit('GetGithubAPI', path, handler.bind(this));
    },
    'GetGithubAPI': function (apiSearchPath, resultHandler) {
        https.request({
            hostname: 'api.github.com',
            path: apiSearchPath,
            headers: {
              'User-Agent': 'lambda',
              'Accept': 'application/vnd.github.cloak-preview;application/json'
            },
            agent: false
        }, (res) => {

          console.log('statusCode:', res.statusCode);
          console.log('headers:', res.headers);

          // capture data
          var rawData = '';
          res.on('data', (chunk) => { rawData += chunk; });

          // process our captured data
          res.on('end', () => {
            const results = JSON.parse(rawData);
            resultHandler(results);
          });

        }).on('error', ((e) => {

          console.error(e);
          this.emit('ErrorOccured');

        }).bind(this)).end();
    },
    'ErrorOccured': function() {
        this.emit(':tellWithCard', this.t('ERROR_MESSAGE'), this.t('ERROR_MESSAGE'), '');
    },
    'AMAZON.HelpIntent': function () {
        const speechOutput = this.t('HELP_MESSAGE');
        const reprompt = this.t('HELP_MESSAGE');
        this.emit(':ask', speechOutput, reprompt);
    },
    'AMAZON.CancelIntent': function () {
        this.emit(':tell', this.t('STOP_MESSAGE'));
    },
    'AMAZON.StopIntent': function () {
        this.emit(':tell', this.t('STOP_MESSAGE'));
    },
    'SessionEndedRequest': function () {
        this.emit(':tell', this.t('STOP_MESSAGE'));
    },
};

exports.handler = (event, context) => {
    const alexa = Alexa.handler(event, context);
    alexa.APP_ID = APP_ID;
    // To enable string internationalization (i18n) features, set a resources object.
    alexa.resources = languageStrings;
    alexa.registerHandlers(handlers);
    alexa.execute();
};
