'use strict';
(() => {
 const hero=document.querySelector('.hero[data-banner]');
 if(!hero)return;
 const videos=[...hero.querySelectorAll('[data-video]')];
 const buttons=[...hero.querySelectorAll('[data-banner-option]')];
 const mobile=matchMedia('(max-width:600px)');
 const files={1:'/assets/hero-mobile.mp4',2:'/assets/hero-mobile-2.mp4'};
 const query=new URLSearchParams(location.search).get('banner');
 let selected=query==='2'?'2':'1';
 const playActive=()=>{
  const video=videos.find(item=>item.dataset.video===selected);
  if(!video||!mobile.matches||document.hidden)return;
  video.defaultMuted=true;
  video.muted=true;
  video.autoplay=true;
  video.loop=true;
  video.playsInline=true;
  video.controls=false;
  if(video.paused)video.play().catch(()=>{});
 };
 const sync=()=>{
  hero.dataset.banner=selected;
  buttons.forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.bannerOption===selected)));
  videos.forEach(video=>{
   const active=video.dataset.video===selected;
   video.hidden=!active;
   if(!active||!mobile.matches||document.hidden){video.pause();return;}
   video.defaultMuted=true;
   video.muted=true;
   if(!video.getAttribute('src')){video.src=files[selected];video.load();}
  });
  playActive();
 };
 videos.forEach(video=>{
  video.addEventListener('loadeddata',playActive);
  video.addEventListener('canplay',playActive);
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
 document.addEventListener('touchstart',playActive,{passive:true});
 document.addEventListener('pointerdown',playActive,{passive:true});
 sync();
})();
