/* ── 포트폴리오 비디오 (메인 index.html · portfolio/ 공용) ──
   메인: .vid-more 버튼이 있으면 숏폼 1줄 + 롱폼 1줄만 보임 → 더보기 = portfolio/ 페이지
         (전체 탭의 숏폼 줄은 카테고리마다 1개씩 골고루)
   portfolio/: 전체 표시, ?cat=외식 처럼 필터 지정 가능 */
(function initVidPortfolio() {
  const root = document.getElementById('portfolio');
  if (!root) return;
  const moreBtn = root.querySelector('.vid-more');
  const limited = !!moreBtn;
  const grid = root.querySelector('.vid-grid:not(.vid-grid--long)');
  const longWrap = root.querySelector('.vid-long');
  let current = 'all';

  function stopAll() {
    root.querySelectorAll('.vid-thumb.playing').forEach(p => {
      p.classList.remove('playing');
      const f = p.querySelector('iframe');
      if (f) f.remove();
    });
  }

  function apply(filter) {
    current = filter;
    root.querySelectorAll('.vid-filter').forEach(b => b.classList.toggle('active', b.dataset.filter === filter));
    root.querySelectorAll('.vid-card').forEach(card => {
      const catMatch = filter === 'all' || card.dataset.cat === filter;
      const driveHidden = filter === 'all' && card.dataset.drive === 'true';
      card.style.display = (catMatch && !driveHidden) ? '' : 'none';
    });
    if (longWrap) longWrap.style.display =
      [...longWrap.querySelectorAll('.vid-card')].some(c => c.style.display !== 'none') ? '' : 'none';
    if (limited) limitRows();
  }

  // 메인: 숏폼·롱폼 각각 1줄(열 수)까지만. 전체 탭 숏폼은 카테고리별 1개씩 먼저
  function colsOf(g) {
    return getComputedStyle(g).gridTemplateColumns.split(' ').filter(Boolean).length || 1;
  }
  function limitRows() {
    let hidden = 0;
    const cols = colsOf(grid);
    const visible = [...grid.querySelectorAll('.vid-card')].filter(c => c.style.display !== 'none');
    let pick = visible;
    if (current === 'all') {
      const seen = new Set(), first = [], rest = [];
      visible.forEach(c => (seen.has(c.dataset.cat) ? rest : (seen.add(c.dataset.cat), first)).push(c));
      pick = first.concat(rest);
    }
    const keep = new Set(pick.slice(0, cols));
    visible.forEach(c => c.classList.toggle('vid-over', !keep.has(c)));
    hidden += visible.length - keep.size;
    if (longWrap) {
      const lg = longWrap.querySelector('.vid-grid--long');
      const lv = [...lg.querySelectorAll('.vid-card')].filter(c => c.style.display !== 'none');
      const lc = colsOf(lg);
      lv.forEach((c, i) => c.classList.toggle('vid-over', i >= lc));
      hidden += Math.max(0, lv.length - lc);
    }
    moreBtn.parentElement.style.display = hidden > 0 ? '' : 'none';
    moreBtn.href = moreBtn.dataset.base + (current === 'all' ? '' : '?cat=' + encodeURIComponent(current));
  }

  root.querySelectorAll('.vid-filter').forEach(btn => {
    btn.addEventListener('click', () => { stopAll(); apply(btn.dataset.filter); });
  });

  // 클릭 자동재생
  root.querySelectorAll('.vid-thumb').forEach(thumb => {
    thumb.addEventListener('click', function () {
      if (this.classList.contains('playing')) return;
      stopAll();
      const iframe = document.createElement('iframe');
      if (this.dataset.ig) {
        iframe.src = `https://www.instagram.com/reel/${this.dataset.ig}/embed/`;
        iframe.allow = 'autoplay; fullscreen; encrypted-media';
        iframe.scrolling = 'no';
      } else if (this.dataset.driveSrc) {
        iframe.src = this.dataset.driveSrc;
        iframe.allow = 'autoplay; fullscreen';
      } else {
        iframe.src = `https://www.youtube.com/embed/${this.dataset.id}?autoplay=1&rel=0&modestbranding=1&playsinline=1`;
        iframe.allow = 'autoplay; fullscreen; encrypted-media; picture-in-picture';
      }
      iframe.allowFullscreen = true;
      this.appendChild(iframe);
      this.classList.add('playing');
    });
  });

  if (limited) {
    moreBtn.dataset.base = moreBtn.getAttribute('href');
    window.addEventListener('resize', limitRows);
  }
  const want = new URLSearchParams(location.search).get('cat');
  apply(want && root.querySelector(`.vid-filter[data-filter="${CSS.escape(want)}"]`) ? want : 'all');
})();
