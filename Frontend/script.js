const menuButton=document.querySelector('.menu-btn');
const nav=document.querySelector('nav');
menuButton?.addEventListener('click',()=>{nav.style.display=nav.style.display==='flex'?'none':'flex';nav.style.position='absolute';nav.style.top='72px';nav.style.right='5%';nav.style.flexDirection='column';nav.style.alignItems='flex-end';nav.style.padding='16px';nav.style.background='#fff';nav.style.border='1px solid #d9e2ec';nav.style.borderRadius='12px';});
