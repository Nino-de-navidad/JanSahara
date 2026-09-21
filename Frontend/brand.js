// JanSahara shared UI helpers. No API calls are changed by this file.
function getJanSaharaUserId(){return localStorage.getItem('jansahara_user_id')||sessionStorage.getItem('jansahara_user_id')}
function getJanSaharaEmail(){return localStorage.getItem('jansahara_email')||sessionStorage.getItem('jansahara_email')}
function logoutJanSahara(){['jansahara_user_id','jansahara_email'].forEach(k=>{localStorage.removeItem(k);sessionStorage.removeItem(k)});location.href='login.html'}
