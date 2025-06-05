
(function (ph){
try{
var A = self['DSPCounter' || 'AdriverCounterJS'],
	a = A(ph);
a.reply = {
ph:ph,
rnd:'50291',
bt:62,
sid:229418,
pz:0,
sz:'%2fbook%2folga%2dpticeva%2fvesna%2dvody%2d72039913%2f',
bn:0,
sliceid:0,
netid:0,
ntype:0,
tns:0,
pass:'',
adid:0,
bid:2864425,
geoid:158,
cgihref:'//ad.adriver.ru/cgi-bin/click.cgi?sid=229418&ad=0&bid=2864425&bt=62&bn=0&pz=0&xpid=DuawXNCVzEy8cjlYy0DWYJzqmRvid8BkcICUWVLwm2cLTr5fdWM3mm1SYGwQ9ZKPak7aVVrHD73t0Pt1ciN_aU-QWRw&ref=https:%2f%2fwww.litres.ru%2fbook%2folga%2dpticeva%2fvesna%2dvody%2d72039913%2f&custom=128%3D1544%3B129%3D1.9.5%3B206%3DDSPCounter',
target:'_blank',
width:'0',
height:'0',
alt:'AdRiver',
mirror:A.httplize('//mlb3.adriver.ru'), 
comp0:'0/script.js',
custom:{"128":"1544","129":"1.9.5","206":"DSPCounter"},
cid:'AkBBSL_1exHtqcLI58EdJ6w',
uid:1895481705808,
xpid:'DuawXNCVzEy8cjlYy0DWYJzqmRvid8BkcICUWVLwm2cLTr5fdWM3mm1SYGwQ9ZKPak7aVVrHD73t0Pt1ciN_aU-QWRw'
}
var r = a.reply;

r.comppath = r.mirror + '/images/0002864/0002864425/' + (/^0\//.test(r.comp0) ? '0/' : '');
r.comp0 = r.comp0.replace(/^0\//,'');
if (r.comp0 == "script.js" && r.adid){
	A.defaultMirror = r.mirror; 
	A.loadScript(r.comppath + r.comp0 + '?v' + ph) 
} else if ("function" === typeof (A.loadComplete)) {
   A.loadComplete(a.reply);
}
}catch(e){} 
}('0'));
