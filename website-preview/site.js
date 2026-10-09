// ===== 全站通用脚本 =====
// 深浅主题切换（记忆选择）
(function(){
  const btn=document.querySelector('.theme-toggle');
  function apply(light){
    document.body.classList.toggle('light',light);
    if(btn) btn.querySelector('.ticon').textContent=light?'☾':'☀';
    localStorage.setItem('theme',light?'light':'dark');
  }
  const saved=localStorage.getItem('theme');
  apply(saved ? saved==='light' : true);
  if(btn) btn.addEventListener('click',()=>apply(!document.body.classList.contains('light')));
})();

// 模块手风琴
document.querySelectorAll('.acc-head').forEach(h=>{
  h.addEventListener('click',()=>{
    const acc=h.parentElement, body=acc.querySelector('.acc-body');
    const open=acc.classList.toggle('open');
    body.style.maxHeight=open?body.scrollHeight+'px':'0';
  });
});
// 认知六层（嵌套手风琴）
document.querySelectorAll('.layer-head').forEach(h=>{
  h.addEventListener('click',e=>{
    e.stopPropagation();
    const l=h.parentElement, body=l.querySelector('.layer-body');
    const open=l.classList.toggle('open');
    body.style.maxHeight=open?body.scrollHeight+'px':'0';
    setTimeout(()=>{
      const pb=document.querySelector('#cog.open .acc-body');
      if(pb) pb.style.maxHeight=pb.scrollHeight+'px';
    },480);
  });
});
// 认知体系展开时修正嵌套高度
const cogHead=document.querySelector('#cog .acc-head');
if(cogHead) cogHead.addEventListener('click',()=>{
  setTimeout(()=>{
    const pb=document.querySelector('#cog.open .acc-body');
    if(pb) pb.style.maxHeight=pb.scrollHeight+'px';
  },520);
});

// 地基图分层展开
document.querySelectorAll('.flayer .fl-head').forEach(h=>{
  h.addEventListener('click',()=>{
    const l=h.parentElement, body=l.querySelector('.fl-body');
    const open=l.classList.toggle('open');
    body.style.maxHeight=open?body.scrollHeight+'px':'0';
  });
});
// 元能力三项（嵌套，不冒泡）
document.querySelectorAll('.trio .titem2').forEach(t=>{
  t.addEventListener('click',e=>{
    e.stopPropagation();
    t.classList.toggle('open');
    setTimeout(()=>{
      const fl=t.closest('.flayer.open');
      if(fl){const b=fl.querySelector('.fl-body');b.style.maxHeight=b.scrollHeight+'px';}
    },80);
  });
});
// 问题树节点展开
document.querySelectorAll('.ptree .pn-head').forEach(h=>{
  h.addEventListener('click',()=>{
    const n=h.parentElement, body=n.querySelector('.pn-body');
    const open=n.classList.toggle('open');
    body.style.maxHeight=open?body.scrollHeight+'px':'0';
  });
});

// 七类问题 chips
document.querySelectorAll('.chip').forEach(c=>{
  c.addEventListener('click',()=>c.classList.toggle('open'));
});

// 问题卡片展开
document.querySelectorAll('.pcard').forEach(c=>{
  c.addEventListener('click',()=>c.classList.toggle('open'));
});

// 问题导航筛选
document.querySelectorAll('.filter-btn').forEach(btn=>{
  btn.addEventListener('click',()=>{
    document.querySelectorAll('.filter-btn').forEach(b=>b.classList.remove('active'));
    btn.classList.add('active');
    const f=btn.dataset.filter;
    document.querySelectorAll('.pcard').forEach(card=>{
      card.style.display=(f==='all'||card.dataset.layers.includes(f))?'flex':'none';
    });
  });
});

// 滚动显现
const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting)e.target.classList.add('in')}),{threshold:.08});
document.querySelectorAll('section > .wrap, .hero .wrap, .page-hero .wrap').forEach(el=>{el.classList.add('reveal');io.observe(el)});