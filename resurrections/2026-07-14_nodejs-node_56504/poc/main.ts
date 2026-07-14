import * as fs from 'fs';
import * as https from 'https';

// GitHub API endpoint and authentication
const GITHUB_API_ENDPOINT = 'https://api.github.com';
const GITHUB_TOKEN = process.env.GITHUB_TOKEN;

// Label and event trigger
const AUTHOR_READY_LABEL = 'author-ready';
const EVENT_TRIGGER = 'schedule';

// Function to get PRs labeled as 'author-ready'
function getAuthorReadyPRs(): Promise<any[]> {
  return new Promise((resolve, reject) => {
    const options = {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${GITHUB_TOKEN}`,
        'Content-Type': 'application/json'
      },
      uri: `${GITHUB_API_ENDPOINT}/repos/nodejs/node/pulls?labels=${AUTHOR_READY_LABEL}&state=open`
    };
    https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => {
        data += chunk;
      });
      res.on('end', () => {
        try {
          const prs = JSON.parse(data);
          resolve(prs);
        } catch (error) {
          reject(error);
        }
      });
    }).on('error', (error) => {
      reject(error);
    }).end();
  });
}

// Function to check if a PR is stalled
function isPRStalled(pr: any): boolean {
  // For demonstration purposes, consider a PR stalled if it has not been updated for 7 days
  const ONE_WEEK = 7 * 24 * 60 * 60 * 1000;
  const updatedAt = new Date(pr.updated_at);
  const now = new Date();
  return now.getTime() - updatedAt.getTime() > ONE_WEEK;
}

// Function to send a notification to collaborators
function sendNotification(pr: any): Promise<any> {
  return new Promise((resolve, reject) => {
    const options = {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${GITHUB_TOKEN}`,
        'Content-Type': 'application/json'
      },
      uri: `${GITHUB_API_ENDPOINT}/repos/nodejs/node/issues/${pr.number}/comments`
    };
    const comment = `PR #${pr.number} seems to be stalled. Please review and move it forward.`;
    https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => {
        data += chunk;
      });
      res.on('end', () => {
        try {
          const commentResponse = JSON.parse(data);
          resolve(commentResponse);
        } catch (error) {
          reject(error);
        }
      });
    }).on('error', (error) => {
      reject(error);
    }).end(JSON.stringify({ body: comment }));
  });
}

// Main function
async function main(): Promise<void> {
  try {
    const prs = await getAuthorReadyPRs();
    prs.forEach(async (pr) => {
      if (isPRStalled(pr)) {
        await sendNotification(pr);
      }
    });
  } catch (error) {
    console.error(error);
  }
}

main();