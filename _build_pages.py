#!/usr/bin/env python3
"""Monta as landing pages temáticas a partir das partes reaproveitadas do index.html.

Cada grupo de anúncios do Google Ads passa a ter uma página que fala do SEU tema,
em vez de todos apontarem para a home. Rodar de dentro de site-analytics/repo/.
"""
import os
import re

P = {k: open(f"_partes/{k}.html", encoding="utf-8").read()
     for k in ("analytics", "estilo", "nav", "enroll", "footer", "scripts")}


def links_para_home(html: str) -> str:
    """Âncoras do menu/rodapé precisam voltar para a home; #enrollment fica na própria página.

    Também torna caminhos de imagem absolutos: dentro de /infant-care/ um src relativo
    como "logo.webp" resolveria para /infant-care/logo.webp e quebraria.
    """
    html = re.sub(r'href="#(?!enrollment")([a-z-]+)"', r'href="/#\1"', html)
    html = re.sub(r'(src|href)="(?!https?:|/|#|tel:|mailto:|data:)([^"]+\.(?:webp|jpg|jpeg|png|svg|ico|css|js))"',
                  r'\1="/\2"', html)
    return html.replace('href="#"', 'href="/"')


NAV = links_para_home(P["nav"])
FOOTER = links_para_home(P["footer"])
P["enroll"] = links_para_home(P["enroll"])


def pagina(*, slug, title, description, h1, hero_sub, hero_img, hero_alt,
           hero_pills, corpo, faq, breadcrumb):
    faq_html = "\n".join(
        f'        <div class="faq-item"><button class="faq-q" onclick="toggleFaq(this)">{q}'
        f'<span class="faq-icon">+</span></button><div class="faq-a"><div class="faq-a-in">{a}</div></div></div>'
        for q, a in faq)
    faq_ld = ",\n".join(
        '    {"@type":"Question","name":%s,"acceptedAnswer":{"@type":"Answer","text":%s}}'
        % (jsonstr(q), jsonstr(re.sub(r"<[^>]+>", "", a))) for q, a in faq)
    pills = "\n".join(f"          <li>{p}</li>" for p in hero_pills)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />

{P['analytics']}

<title>{title}</title>
<meta name="description" content="{description}" />
<link rel="canonical" href="https://flaviaslittlesprouts.com/{slug}/" />

<!-- Favicon -->
<link rel="icon" href="logo.webp" type="image/webp" />

<meta property="og:type" content="website" />
<meta property="og:title" content="{title}" />
<meta property="og:description" content="{description}" />
<meta property="og:url" content="https://flaviaslittlesprouts.com/{slug}/" />
<meta property="og:image" content="https://flaviaslittlesprouts.com/hero.jpg" />

{P['estilo']}

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
{faq_ld}
  ]
}}
</script>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {{"@type":"ListItem","position":1,"name":"Home","item":"https://flaviaslittlesprouts.com/"}},
    {{"@type":"ListItem","position":2,"name":{jsonstr(breadcrumb)},"item":"https://flaviaslittlesprouts.com/{slug}/"}}
  ]
}}
</script>
</head>
<body>

{NAV}

<!-- HERO -->
<section id="hero">
  <div class="container">
    <div class="hero-in">
      <div>
        <div class="hero-logo-wrap">
          <img src="/logo.webp" alt="Flavia's Little Sprouts" />
        </div>
        <span class="hero-avail"><span class="hero-avail-dot"></span>Now enrolling &middot; Openings for infants &amp; toddlers</span>
        <span class="label">Novato &middot; Marin County</span>
        <h1>{h1}</h1>
        <p>{hero_sub}</p>
        <div class="hero-ctas">
          <a href="#enrollment" class="btn">Schedule a Tour &rarr;</a>
          <a href="tel:4152460309" class="btn-ghost">Call (415) 246-0309 &rarr;</a>
        </div>
        <ul class="hero-trust">
{pills}
        </ul>
      </div>
      <div class="hero-img-wrap">
        <div class="hero-img">
          <img src="/{hero_img}" fetchpriority="high" decoding="async" alt="{hero_alt}" style="width:100%;height:100%;object-fit:cover" />
        </div>
        <div class="hero-badge">
          <div class="hero-badge-icon">&#127793;</div>
          <div>
            <strong>In-Home Daycare</strong>
            <span>Novato &middot; Marin County, CA</span>
          </div>
        </div>
        <div class="hero-stat">
          <strong>2</strong>
          <span>Full-Time Caregivers</span>
        </div>
      </div>
    </div>
  </div>
</section>

{corpo}

<!-- FAQ -->
<section id="faq">
  <div class="container">
    <div class="faq-in">
      <div class="sec-head" style="margin:0 0 44px">
        <span class="label">FAQ</span>
        <h2>Common Questions</h2>
        <p>The questions parents ask us most about {breadcrumb.lower()}.</p>
      </div>
      <div class="faq-list">
{faq_html}
      </div>
    </div>
  </div>
</section>

{P['enroll']}

{FOOTER}

{P['scripts']}
</body>
</html>
"""


def jsonstr(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


# ─────────────────────────── /infant-care/ ───────────────────────────
INFANT_CORPO = """
<!-- WHY -->
<section id="why">
  <div class="container">
    <div class="sec-head">
      <span class="label">Infant Care</span>
      <h2>Caring for Babies from 4 Months</h2>
      <p>Leaving your baby for the first time is hard. Here is exactly what happens to your infant during the day, so there are no surprises.</p>
    </div>
    <div class="grid-3">
      <div class="card"><div class="card-icon">&#128155;</div><h3>Your Baby's Own Schedule</h3><p>Infants do not follow the group routine. Your baby eats and sleeps on their own schedule, the one you already use at home, and we write it down with you before day one.</p></div>
      <div class="card"><div class="card-icon">&#128118;</div><h3>Two Caregivers, Always</h3><p>Two experienced adults are here full time. While one is feeding or changing your baby, the other is with the group — your infant is never left waiting for attention.</p></div>
      <div class="card"><div class="card-icon">&#128564;</div><h3>Safe Sleep Practices</h3><p>Babies are placed on their backs in a crib or pack-and-play, with no loose bedding, blankets, or soft toys. Naps happen in a quiet, supervised space.</p></div>
      <div class="card"><div class="card-icon">&#127868;</div><h3>Breast Milk &amp; Formula</h3><p>Send breast milk or formula labeled with your baby's name and we follow your feeding amounts and times exactly. We log every bottle, so you know what they took and when.</p></div>
      <div class="card"><div class="card-icon">&#128241;</div><h3>Photos &amp; Daily Updates</h3><p>You get updates with photos through the day — bottles, diapers, naps, and the small firsts. You should not have to wonder how your baby is doing at 10 a.m.</p></div>
      <div class="card"><div class="card-icon">&#127968;</div><h3>A Home, Not a Center</h3><p>A small group in a real house means fewer children, fewer germs, and the same familiar faces every single day — which matters most at this age.</p></div>
    </div>
  </div>
</section>

<!-- SAFETY -->
<section id="safety">
  <div class="container">
    <div class="safety-in">
      <div class="safety-img-wrap">
        <div class="safety-img">
          <img src="/flavia-babies.webp" loading="lazy" decoding="async" alt="Flávia holding two babies at her infant daycare in Novato" style="width:100%;height:100%;object-fit:cover" />
        </div>
      </div>
      <div class="safety-content">
        <span class="label">Your Peace of Mind</span>
        <h2>Starting Infant Daycare</h2>
        <p>Most families start with a short first week — a couple of half days so your baby can meet us while you are still nearby. There is no extra charge for that, and it makes the transition much gentler for everyone.</p>
        <ul class="safety-list">
          <li class="saf-item"><span class="saf-check">&#10003;</span><div><h4>We accept babies from 4 months</h4><p>Infants through 3 years old, all in one small group</p></div></li>
          <li class="saf-item"><span class="saf-check">&#10003;</span><div><h4>CPR &amp; First Aid certified</h4><p>Both caregivers, with background verification</p></div></li>
          <li class="saf-item"><span class="saf-check">&#10003;</span><div><h4>You bring diapers, wipes and milk</h4><p>We provide the meals once your baby starts solids</p></div></li>
          <li class="saf-item"><span class="saf-check">&#10003;</span><div><h4>Open 7:30 AM &ndash; 5:30 PM</h4><p>Monday through Friday, with part-time options</p></div></li>
        </ul>
      </div>
    </div>
  </div>
</section>
"""

INFANT_FAQ = [
    ("I'm searching for infant care near me — where are you?",
     "We are an in-home daycare at <strong>412 Wood Hollow Dr, Novato, CA 94945</strong>, serving families across Novato and nearby Marin County. If you are searching for infant or baby daycare near you, the honest answer is that photos only tell you so much — schedule a tour and come see where your baby would actually spend the day."),
    ("What is the youngest age you accept?",
     "We accept babies from <strong>4 months old</strong>, and care for children up to 3 years. If your baby is not quite 4 months yet, reach out anyway — spots are limited and families often reserve a place a couple of months ahead."),
    ("Do you follow my baby's nap and feeding schedule?",
     "Yes. Infants do not follow the group routine — your baby keeps their own eating and sleeping schedule. We write it down with you before the first day and adjust with you as your baby grows."),
    ("Can I send breast milk?",
     "Absolutely. Send breast milk or formula labeled with your baby's name, along with bottles. We follow your instructions on amounts and timing, and we log every feeding so you know exactly what your baby took during the day."),
    ("How do you handle infant sleep safely?",
     "We follow safe-sleep practices: babies sleep on their backs in a crib or pack-and-play, with no loose bedding, pillows, or soft toys, in a quiet space where they are supervised at all times."),
    ("How many adults are with the children?",
     "There are <strong>two full-time caregivers</strong> here every day, both background-verified and CPR &amp; First Aid certified, with a small group of children. For a baby, that second pair of hands is the difference between waiting and being picked up."),
    ("What do I need to bring for my baby?",
     "Diapers and wipes, bottles with breast milk or formula, one or two changes of clothes, and a comfort item for naps if your baby uses one. Please label everything. Once your baby is on solids, we prepare the meals here."),
    ("How much does infant care cost?",
     "Full-time care (Monday to Friday, 7:30 AM to 5:30 PM) is $2,650 per month. Part-time is 3 flexible days per week, 7:30 AM to 3:00 PM, at $2,200 per month. A deposit of half a month reserves your baby's spot."),
    ("Can we visit before deciding?",
     "Please do — we would rather you see the space than take our word for it. Schedule a tour and you can meet Flávia, see where your baby would sleep and play, and ask anything you want."),
]

# ─────────────────────── /home-daycare-novato/ ───────────────────────
HOME_CORPO = """
<!-- WHY -->
<section id="why">
  <div class="container">
    <div class="sec-head">
      <span class="label">In-Home Daycare</span>
      <h2>What a Home Daycare Actually Means</h2>
      <p>A family daycare is not a smaller version of a center. It is a different thing entirely, and for children under three the difference is the whole point.</p>
    </div>
    <div class="grid-3">
      <div class="card"><div class="card-icon">&#127968;</div><h3>A Real House</h3><p>Your child spends the day in a home — a kitchen where lunch is actually cooked, a living room, a yard. Not a classroom wing with fluorescent lights and a rotating schedule.</p></div>
      <div class="card"><div class="card-icon">&#128106;</div><h3>The Same Faces Every Day</h3><p>Centers have staff turnover and shift changes. Here, your child is greeted by the same two people every morning, all year. At this age, that attachment is what makes them feel safe.</p></div>
      <div class="card"><div class="card-icon">&#128101;</div><h3>A Small Group</h3><p>A handful of children instead of a room full. Less noise, fewer germs, and enough quiet for a caregiver to notice that your child is having an off day.</p></div>
      <div class="card"><div class="card-icon">&#127859;</div><h3>Homemade Meals</h3><p>Morning snack, lunch, and afternoon snack are prepared fresh in the kitchen — not delivered in trays. We work around allergies and preferences.</p></div>
      <div class="card"><div class="card-icon">&#128064;</div><h3>Two Full-Time Caregivers</h3><p>The usual worry about home daycare is one adult doing everything alone. There are two of us here full time, so there is always a second pair of eyes on your child.</p></div>
      <div class="card"><div class="card-icon">&#128172;</div><h3>You Talk to the Owner</h3><p>No front desk, no director to schedule a meeting with. If something is on your mind, you say it to Flávia at pickup and it is handled that day.</p></div>
    </div>
  </div>
</section>

<!-- SCHEDULE -->
<section id="schedule">
  <div class="container">
    <div class="sec-head">
      <span class="label">Daily Routine</span>
      <h2>A Day in Our Home</h2>
      <p>Predictable enough that children feel secure, flexible enough to follow the day where it goes.</p>
    </div>
    <div class="sched-grid">
      <div class="sched-item"><div class="sched-time">7:30 &ndash; 8:30</div><h4>Arrival</h4><p>Warm welcome, free play, settling in</p></div>
      <div class="sched-item"><div class="sched-time">8:30 &ndash; 9:00</div><h4>Morning Snack</h4><p>Fresh fruit and whole grains</p></div>
      <div class="sched-item"><div class="sched-time">9:00 &ndash; 9:30</div><h4>Circle Time</h4><p>Songs, stories, and the plan for the day</p></div>
      <div class="sched-item"><div class="sched-time">9:30 &ndash; 10:30</div><h4>Learning Centers</h4><p>Rotating hands-on activities</p></div>
      <div class="sched-item"><div class="sched-time">11:00 &ndash; 12:00</div><h4>Outdoor Play</h4><p>Yard time and nature exploration</p></div>
      <div class="sched-item"><div class="sched-time">12:00 &ndash; 12:30</div><h4>Lunch</h4><p>Homemade meal, together at the table</p></div>
      <div class="sched-item"><div class="sched-time">12:30 &ndash; 2:30</div><h4>Nap &amp; Rest</h4><p>One nap a day, adjusted to each child</p></div>
      <div class="sched-item"><div class="sched-time">3:00 &ndash; 4:30</div><h4>Afternoon Play</h4><p>Child-led activities and exploration</p></div>
    </div>
  </div>
</section>

<!-- SAFETY -->
<section id="safety">
  <div class="container">
    <div class="safety-in">
      <div class="safety-img-wrap">
        <div class="safety-img">
          <img src="/care.webp" loading="lazy" decoding="async" alt="Children playing together at Flávia's in-home family daycare in Novato" style="width:100%;height:100%;object-fit:cover" />
        </div>
      </div>
      <div class="safety-content">
        <span class="label">Practical Details</span>
        <h2>Serving Novato &amp; Marin County</h2>
        <p>We are at 412 Wood Hollow Dr in Novato, CA 94945 — an in-home family daycare for children 4 months to 3 years old, open Monday through Friday.</p>
        <ul class="safety-list">
          <li class="saf-item"><span class="saf-check">&#10003;</span><div><h4>Full-Time &mdash; $2,650/month</h4><p>Monday to Friday, 7:30 AM &ndash; 5:30 PM</p></div></li>
          <li class="saf-item"><span class="saf-check">&#10003;</span><div><h4>Part-Time &mdash; $2,200/month</h4><p>3 flexible days, 7:30 AM &ndash; 3:00 PM</p></div></li>
          <li class="saf-item"><span class="saf-check">&#10003;</span><div><h4>Ages 4 months to 3 years</h4><p>Infants and toddlers in one small group</p></div></li>
          <li class="saf-item"><span class="saf-check">&#10003;</span><div><h4>Both caregivers certified</h4><p>CPR &amp; First Aid, background verified</p></div></li>
        </ul>
      </div>
    </div>
  </div>
</section>
"""

HOME_FAQ = [
    ("What is the difference between a home daycare and a daycare center?",
     "A center is a commercial facility with classrooms, larger groups, and staff who work in shifts. An in-home family daycare like ours is a small group of children in an actual house, with the same caregivers every day. For children under three, that consistency and the smaller group usually matter more than the size of the building."),
    ("I'm looking for a home daycare near me — where are you located?",
     "We are at <strong>412 Wood Hollow Dr, Novato, CA 94945</strong>, and we welcome families from Novato and the nearby Marin County communities. If you are searching for in-home childcare near you, the best way to know if it is the right fit is to come see the house in person."),
    ("Is only one person watching the children?",
     "No — and this is the question we get most. There are <strong>two full-time caregivers</strong> here every day, both background-verified and CPR &amp; First Aid certified. So even when one is changing a diaper or serving lunch, your child still has attentive eyes on them."),
    ("How many children are in the group?",
     "We keep the group deliberately small so each child gets real, personal attention. That also means spots are limited — families usually reserve a place ahead of the start date."),
    ("What ages do you take?",
     "Children from 4 months to 3 years old, infants and toddlers together in one small mixed-age group. Younger children learn a great deal from the older ones, and the older ones grow into little helpers."),
    ("Do you provide meals?",
     "Yes. A morning snack, a homemade lunch, and an afternoon snack, all prepared fresh in the kitchen. Please tell us about allergies or dietary restrictions in writing. Diapers, wipes, and formula are brought by the family."),
    ("What are your hours and rates?",
     "Full-time is Monday to Friday, 7:30 AM to 5:30 PM, at $2,650 per month. Part-time is 3 flexible days per week, 7:30 AM to 3:00 PM, at $2,200 per month. If you need to pick up earlier on a given day, just send us a text."),
    ("Can I come see the house before enrolling?",
     "Please do. Schedule a tour and Flávia will show you the play areas, the yard, where the children nap and eat, and answer whatever you want to ask. No one should hand over their child to a place they have only seen in photos."),
]

PAGINAS = [
    dict(
        slug="infant-care",
        title="Infant Care in Novato, CA · Daycare for Babies 4 Months &amp; Up — Flavia's Little Sprouts",
        description="Looking for infant care near you in Novato, CA? A small in-home daycare for babies from 4 months, with two full-time caregivers, safe sleep, and your baby's own feeding and nap schedule. Schedule a tour.",
        h1="Infant Care in Novato, CA &mdash; <em>Daycare for Babies from 4 Months</em>",
        hero_sub="A small, in-home daycare near you where your baby keeps their own feeding and nap schedule, sleeps safely, and is cared for by two full-time caregivers &mdash; Monday through Friday, 7:30 AM to 5:30 PM.",
        hero_img="flavia-babies.webp",
        hero_alt="Flávia holding two smiling babies at her infant daycare in Novato, CA",
        hero_pills=["Babies from 4 Months", "Two Full-Time Caregivers", "Safe Sleep Practices", "Daily Photo Updates"],
        corpo=INFANT_CORPO,
        faq=INFANT_FAQ,
        breadcrumb="Infant Care",
    ),
    dict(
        slug="home-daycare-novato",
        title="Home Daycare in Novato, CA · In-Home Family Childcare — Flavia's Little Sprouts",
        description="A home daycare near you in Novato, CA — in-home family childcare for ages 4 months to 3 years, with a small group, two full-time caregivers, and homemade meals. Schedule a tour.",
        h1="In-Home Daycare in Novato, CA &mdash; <em>A Real Home, Not a Center</em>",
        hero_sub="A family daycare near you in Novato, where a small group of children spends the day in an actual house &mdash; same two caregivers every morning, homemade meals, and a yard to play in.",
        hero_img="care.webp",
        hero_alt="Children playing together at an in-home family daycare in Novato, CA",
        hero_pills=["Ages 4 Months – 3 Years", "Two Full-Time Caregivers", "Small Group", "Homemade Meals Daily"],
        corpo=HOME_CORPO,
        faq=HOME_FAQ,
        breadcrumb="Home Daycare in Novato",
    ),
]

for cfg in PAGINAS:
    os.makedirs(cfg["slug"], exist_ok=True)
    html = pagina(**cfg)
    caminho = os.path.join(cfg["slug"], "index.html")
    open(caminho, "w", encoding="utf-8").write(html)
    print(f"{caminho}: {len(html)//1024} KB")
