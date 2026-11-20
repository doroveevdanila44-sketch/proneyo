'use strict';
(() => {
 const hero=document.querySelector('.hero[data-banner]');
 if(!hero)return;
 const videos=[...hero.querySelectorAll('[data-video]')];
 const buttons=[...hero.querySelectorAll('[data-banner-option]')];
 const mobile=matchMedia('(max-width:600px)');
 const files={1:'/assets/hero-mobile-silent.mp4',2:'/assets/hero-mobile-2.mp4'};
 const query=new URLSearchParams(location.search).get('banner');
 let selected=query==='2'?'2':'1';
 let retryTimer;
 const pending=new WeakSet();
 const activeVideo=()=>videos.find(video=>video.dataset.video===selected);
 const shouldPlay=video=>!!video&&video===activeVideo()&&mobile.matches&&!document.hidden;
 const prepare=video=>{
  video.defaultMuted=true;
  video.muted=true;
  video.autoplay=true;
  video.loop=true;
  video.playsInline=true;
  video.controls=false;
  video.setAttribute('muted','');
  video.setAttribute('playsinline','');
  video.setAttribute('webkit-playsinline','');
  video.removeAttribute('controls');
 };
 const retry=()=>{
  clearTimeout(retryTimer);
  if(shouldPlay(activeVideo()))retryTimer=setTimeout(playActive,800);
 };
 const playActive=()=>{
  const video=activeVideo();
  if(!shouldPlay(video)||pending.has(video))return;
  prepare(video);
  if(!video.paused&&!video.ended)return;
  pending.add(video);
  const attempt=video.play();
  if(!attempt){pending.delete(video);return;}
  attempt.then(()=>{
   pending.delete(video);
   if(!shouldPlay(video))video.pause();
  }).catch(()=>{
   pending.delete(video);
   if(shouldPlay(video))retry();
  });
 };
 const sync=()=>{
  clearTimeout(retryTimer);
  hero.dataset.banner=selected;
  buttons.forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.bannerOption===selected)));
  videos.forEach(video=>{
   const active=video.dataset.video===selected;
   prepare(video);
   video.hidden=!active;
   if(!shouldPlay(video)){video.pause();return;}
   video.preload='auto';
   // A source media query is not reselected when the viewport changes.
   // Set the active URL explicitly so desktop-to-mobile transitions also load it.
   if(video.getAttribute('src')!==files[selected]){
    video.src=files[selected];
    video.load();
   }
  });
  playActive();
 };
 videos.forEach(video=>{
  prepare(video);
  ['loadedmetadata','loadeddata','canplay'].forEach(event=>video.addEventListener(event,playActive));
  video.addEventListener('playing',()=>{
   if(shouldPlay(video))clearTimeout(retryTimer);
   else video.pause();
  });
  video.addEventListener('pause',()=>{if(shouldPlay(video))retry();});
  video.addEventListener('ended',()=>{
   if(shouldPlay(video)){video.currentTime=0;playActive();}
  });
 });
 buttons.forEach(button=>button.addEventListener('click',()=>{
  selected=button.dataset.bannerOption;
  const url=new URL(location.href);url.searchParams.set('banner',selected);
  history.replaceState(null,'',url);
  sync();
 }));
 mobile.addEventListener('change',sync);
 document.addEventListener('visibilitychange',sync);
 window.addEventListener('pageshow',sync);
 window.addEventListener('focus',playActive);
 ['touchstart','touchend','pointerdown','click'].forEach(event=>document.addEventListener(event,playActive,{passive:true}));
 sync();
})();
