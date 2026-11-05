'use strict';
// Teaching model only. No DOM, WebSocket, or real PAGE execution.
const assert = require('node:assert/strict');
const deadline = (receivedAt, ttl) => receivedAt + Math.max(0, ttl - 50);
const first = deadline(1000, 150);
assert.equal(first, 1100);
assert.equal(1099 < first, true);
assert.equal(1100 < first, false);
// Another snapshot of the same ticket must not extend its original deadline.
const sameTicketAgain = Math.min(first, deadline(1040, 130));
assert.equal(sameTicketAgain, 1100);
console.log('ticket local deadline=1100; 1099 usable, 1100 unusable');

let intent = false, commands = [], manualWaitUntil = null;
function manualArm(now, usable) {
  if (usable) { intent = true; commands.push('ARM'); }
  else if (manualWaitUntil === null) manualWaitUntil = now + 200;
}
function blur() {
  manualWaitUntil = null;
  if (intent) commands.push('DISARM');
  intent = false;
}
function offer(now) {
  if (manualWaitUntil === null) return;
  const onTime = now < manualWaitUntil;
  manualWaitUntil = null;
  if (onTime) { intent = true; commands.push('ARM'); }
}
manualArm(0, false);  // one manual click while the current ticket is unusable
blur();              // intent must be cancelled BEFORE a new ticket arrives
offer(20);
assert.deepEqual(commands, []);
manualArm(100, false);
offer(300);          // exactly at the 200 ms boundary
assert.deepEqual(commands, []);
manualArm(400, true);
blur();
assert.deepEqual(commands, ['ARM', 'DISARM']);
// Merely returning focus is not another manualArm call.
assert.equal(intent, false);
console.log('blur cancels an unsent click; active blur sends stop; focus does not re-arm');
console.log('PASS 05: simplified browser timing model');
