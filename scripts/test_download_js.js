const assert = require('node:assert/strict');
const {latestDevelopmentArtifact} = require('../site/assets/download.js');
const response = (data, ok = true) => ({ok, json: async () => data});
const run = {id: 42, head_branch:'main', conclusion:'success', head_sha:'a'.repeat(40)};
const artifact = {name:'DOTX-Windows-development-unsigned', expired:false, expires_at:'2100-01-01T00:00:00Z'};
(async () => {
  let urls=[];
  let fetcher = async url => {urls.push(url); return response(url.includes('/artifacts') ? {artifacts:[artifact]} : {workflow_runs:[run]});};
  assert.deepEqual(await latestDevelopmentArtifact(fetcher, 0), {runId:42, sha:'aaaaaaa', expiresAt:artifact.expires_at});
  assert.equal(urls.length,2); assert.ok(urls.every(x => x.startsWith('https://api.github.com/repos/dotsoftwarelk/dotx-browser/')));
  fetcher = async url => response(url.includes('/artifacts') ? {artifacts:[{...artifact,expired:true}]} : {workflow_runs:[run]});
  assert.equal(await latestDevelopmentArtifact(fetcher, 0),null);
  fetcher = async url => response(url.includes('/artifacts') ? {artifacts:[{...artifact,expires_at:'2000-01-01T00:00:00Z'}]} : {workflow_runs:[run]});
  assert.equal(await latestDevelopmentArtifact(fetcher, Date.now()),null);
  fetcher = async () => response({workflow_runs:[{...run,id:'42'}]});
  assert.equal(await latestDevelopmentArtifact(fetcher, 0),null);
  await assert.rejects(latestDevelopmentArtifact(async () => response({},false),0));
  let count = 0;
  fetcher = async url => {
    if (!url.endsWith('/artifacts')) return response({workflow_runs:[run,{...run,id:43}]});
    count++; return response({artifacts:count===1 ? [{...artifact,expired:true}] : [artifact]});
  };
  assert.equal((await latestDevelopmentArtifact(fetcher, 0)).runId, 43);
  console.log('PASS: live download metadata selection, expiration and failure handling (mocked)');
})().catch(error => {console.error(error); process.exit(1);});
