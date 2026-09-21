"""The hand-drawn avatar mark — an original cartoon, not Apple's Memoji system."""

AVATAR_SVG = '''<svg class="memo" viewBox="0 0 100 100" aria-hidden="true" focusable="false">
  <defs>
    <clipPath id="mclip"><circle cx="50" cy="50" r="50"/></clipPath>
    <linearGradient id="mskin" x1="30" y1="20" x2="70" y2="90" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#CE9469"/><stop offset="1" stop-color="#B57B52"/>
    </linearGradient>
  </defs>
  <g clip-path="url(#mclip)">
    <circle cx="50" cy="50" r="50" fill="#F14E1C"/>
    <circle cx="50" cy="46" r="38" fill="#D9541F" opacity=".55"/>
    <!-- neck, then shoulders over it -->
    <path d="M40 74h20v10a10 10 0 0 1-20 0z" fill="#A86E45"/>
    <path d="M12 110c0-18 15-27 38-27s38 9 38 27z" fill="#F7F4EF"/>
    <path d="M42 83h16c0 5-3.5 8-8 8s-8-3-8-8z" fill="#E6DFD4"/>
    <!-- ears -->
    <ellipse cx="23" cy="52" rx="5" ry="7" fill="#B57B52"/>
    <ellipse cx="77" cy="52" rx="5" ry="7" fill="#B57B52"/>
    <!-- face -->
    <path d="M26 42c0-15 10-25 24-25s24 10 24 25v9c0 17-11 29-24 29S26 68 26 51z" fill="url(#mskin)"/>
    <!-- beard -->
    <path d="M26 48v3c0 17 11 29 24 29s24-12 24-29v-3c-3 12-8 22-24 22S29 60 26 48z" fill="#241C17" opacity=".92"/>
    <path d="M30 44c2 14 8 24 20 24s18-10 20-24c-4 9-10 13-20 13s-16-4-20-13z" fill="#C98F66" opacity=".35"/>
    <!-- hair: the quiff -->
    <path d="M25 44c-1-16 8-29 25-29 13 0 21 6 24 15 2 5 1 9 0 14-1-8-4-12-9-14-6 6-24 8-32 3-4 3-7 6-8 11z" fill="#17120F"/>
    <path d="M62 15c6-2 13 2 16 8-5-3-11-4-16-3z" fill="#17120F"/>
    <!-- glasses -->
    <g class="glasses" fill="none" stroke="#2A211C" stroke-width="3.2">
      <rect x="28" y="44" width="19" height="14" rx="4" fill="#E8F1F6" fill-opacity=".45"/>
      <rect x="53" y="44" width="19" height="14" rx="4" fill="#E8F1F6" fill-opacity=".45"/>
      <path d="M47 50h6M28 48l-5 2M72 48l5 2" stroke-linecap="round"/>
    </g>
    <!-- eyes -->
    <circle class="eye-l" cx="37.5" cy="51" r="2.6" fill="#1A1410"/>
    <circle cx="62.5" cy="51" r="2.6" fill="#1A1410"/>
    <path class="eye-wink" d="M34.5 52c2-3 4-3 6 0" fill="none" stroke="#1A1410" stroke-width="2.4"
      stroke-linecap="round" opacity="0"/>
    <!-- brows -->
    <path class="brow-l" d="M31 39.5c4-2.5 9-2.5 13 0" stroke="#17120F" stroke-width="2.6" fill="none" stroke-linecap="round"/>
    <path class="brow-r" d="M56 39.5c4-2.5 9-2.5 13 0" stroke="#17120F" stroke-width="2.6" fill="none" stroke-linecap="round"/>
    <!-- nose -->
    <path d="M50 56c-2 4-3 5-1 6h3" stroke="#9C6842" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
    <!-- mouth: grin, swaps for a whoa on hover -->
    <g class="mouth-grin">
      <path d="M40 66c3 4 17 4 20 0 0 6-4 10-10 10s-10-4-10-10z" fill="#3A1712"/>
      <path d="M41.5 66.5h17c-1 2-3.5 3-8.5 3s-7.5-1-8.5-3z" fill="#FFFDF8"/>
    </g>
    <ellipse class="mouth-whoa" cx="50" cy="69" rx="6" ry="7.5" fill="#3A1712" opacity="0"/>
  </g>
</svg>'''

AVATAR_CSS = '''
/* ── the mark: A + face + NOWAR ── */
.wordmark{gap:0;font-family:"JetBrains Mono",monospace;font-size:14px;font-weight:500;letter-spacing:.06em;
  display:inline-flex;align-items:center}
.wordmark .memo{width:1.72em;height:1.72em;margin:0 .04em;border-radius:50%;flex:0 0 auto;
  transition:transform .55s var(--ease-back)}
.wordmark:hover .memo{transform:rotate(-9deg) scale(1.12) translateY(-1px)}
.wordmark:hover .eyes{opacity:0}
.wordmark:hover .eyes-wink{opacity:1}
.wordmark:hover .mouth-grin{opacity:0}
.wordmark:hover .mouth-whoa{opacity:1}
.wordmark:hover .brow-l{transform:translateY(-2px) rotate(-6deg)}
.memo .eyes,.memo .eyes-wink,.memo .mouth-grin,.memo .mouth-whoa{transition:opacity .22s}
.memo .brow-l{transition:transform .35s var(--ease-back);transform-origin:37px 40px}
.wordmark .reg{font-size:.62em;transform:translateY(-.55em);color:var(--ember);letter-spacing:0}
.sec-ink .wordmark,.foot .wordmark{color:inherit}
.foot .wordmark{font-size:16px}
'''

def wordmark(href="/", extra_class=""):
    return (f'<a class="wordmark {extra_class}" href="{href}" aria-label="Anowar Hossain — home">'
            f'<span>AN</span>{AVATAR_SVG}<span>WAR</span>'
            '</a>')
