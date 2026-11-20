// Read-only observer: sends no commands, preserves the original stop behavior.
// Install while DISARMED/IDLE. Do not refresh until the report is copied.
(() => {
  'use strict';
  if (window.g6StopObserve) throw Error('이미 설치됨');
  if (typeof stopLocal !== 'function' || intent || !offer || offer.phase !== 'IDLE')
    throw Error('DISARMED / IDLE에서 설치하세요');
  const events = [], started = performance.now(), original = stopLocal;
  const log = (event, extra = {}) => {
    const entry = {ms: performance.now() - started, event, ...extra};
    events.push(entry);
    console.log('G6 STOP OBSERVE', JSON.stringify(entry));
  };
  for (const name of ['blur', 'visibilitychange', 'pointercancel', 'lostpointercapture'])
    window.addEventListener(name, e => log(name, {target: e.target?.id, hidden: document.hidden}), true);
  stopLocal = function(sendStop) {
    const now = performance.now();
    log('stopLocal', {
      sendStop, intent, focused: focused(), motionReady: motionReady(),
      motion: motion && {button: motion.button.id, vx: motion.vx, w: motion.w},
      pending: pending && {id: pending.id, cmd: pending.cmd},
      offer, offer_age_ms: now - offerAt,
      tel: latestTel, tel_local_age_ms: now - latestTelAt,
      stack: new Error().stack
    });
    return original.apply(this, arguments);
  };
  window.g6StopObserve = {report: () => JSON.stringify(events, null, 2)};
  log('INSTALLED');
})();
