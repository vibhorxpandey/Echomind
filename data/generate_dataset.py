"""
Deterministic synthetic dataset generator for Nexus Tech Club (2021-2025).

No LLM calls. random.seed(42) -> identical output every run.
Output: data/club_docs.json  (~300 docs)

Six storylines are planted across handcrafted docs (stable, readable IDs
prefixed s1..s6) so demo queries and the ablation harness can target them:
  1. HackNexus 2023 lost Rs.18,000 (venue double-booking + TechVerse pullout)
  2. TechVerse Solutions ghosted again in 2024; handover says never rely on them
  3. Prof. Mehra budget trick: submit before the 5th with a one-page summary
  4. Membership dropped 40% in 2024 after beginner workshops stopped
  5. The 2025 Cloudnine Devtools pitch that worked (Rs.50,000)
  6. Contradiction: fest in March (2022 doc) vs moved to September (2024 doc)
"""

import json
import random
from pathlib import Path

random.seed(42)

OUT_PATH = Path(__file__).parent / "club_docs.json"

FIRST = ["Aarav", "Diya", "Rohan", "Ananya", "Kabir", "Ishita", "Vikram", "Meera",
         "Arjun", "Sanya", "Dev", "Priya", "Nikhil", "Tara", "Rahul", "Zoya",
         "Aditya", "Naina", "Karan", "Riya", "Sameer", "Pooja", "Yash", "Lakshmi",
         "Farhan", "Shreya", "Manav", "Kavya", "Om", "Nidhi"]
LAST = ["Sharma", "Iyer", "Bose", "Reddy", "Khan", "Patel", "Nair", "Gupta",
        "Menon", "Kulkarni", "Das", "Chopra", "Rao", "Sethi", "Verma", "Joshi"]

def _names(n):
    combos = [(f, l) for f in FIRST for l in LAST]
    random.shuffle(combos)
    return [f"{f} {l}" for f, l in combos[:n]]

MEMBERS = _names(70)
YEARS = [2021, 2022, 2023, 2024, 2025]

ROLES = ["President", "Vice President", "Secretary", "Treasurer",
         "Events Lead", "Tech Lead", "Design Lead", "Outreach Lead"]
# officers[year][role] -> name (deterministic)
OFFICERS = {}
_pool = MEMBERS[:]
for y in YEARS:
    OFFICERS[y] = {}
    for r in ROLES:
        OFFICERS[y][r] = _pool[(y - 2021) * len(ROLES) + ROLES.index(r) % len(_pool)]

EVENTS = ["HackNexus", "CodeSprint", "TechTalks", "Intro to Git Workshop",
          "AI Study Jam", "Nexus Annual Fest", "Design-a-thon", "Open Source Week",
          "Alumni Connect", "Robotics Demo Day", "CTF Night", "Web Dev Bootcamp"]
SPONSORS = ["PixelForge Media", "ByteBasket", "Larkspur Systems", "Orbita Labs",
            "Chai Point Campus", "Vertex Print Co.", "NimbusHost", "Quanta Books"]
FACULTY = ["Prof. Mehra", "Prof. D'Souza", "Dr. Raghavan", "Prof. Bhattacharya"]
VENUES = ["Seminar Hall B", "Main Auditorium", "CS Block Lab 3", "Innovation Centre",
          "Open Air Theatre", "Library Conference Room"]
AGENDA = ["event planning", "budget review", "recruitment drive", "website revamp",
          "sponsor outreach", "workshop scheduling", "inventory check",
          "collab with the design club", "social media strategy", "alumni newsletter",
          "T-shirt printing quotes", "lab access permissions", "fest logistics",
          "photography team formation", "certificate distribution"]
INTERESTS = ["web development", "machine learning", "competitive programming",
             "UI/UX design", "cybersecurity", "robotics", "cloud computing",
             "game development", "open source", "data visualisation"]

def _date(year, month=None, day=None):
    m = month if month else random.randint(1, 12)
    d = day if day else random.randint(1, 28)
    return f"{year}-{m:02d}-{d:02d}"

DOCS = []

def add(doc_id, title, doc_type, year, date, author, content):
    words = len(content.split())
    assert 120 <= words <= 430, f"{doc_id}: {words} words"
    DOCS.append({"id": doc_id, "title": title, "doc_type": doc_type,
                 "year": year, "date": date, "author": author,
                 "content": " ".join(content.split())})

# ---------------------------------------------------------------------------
# STORYLINE 1 — HackNexus 2023 lost Rs.18,000
# ---------------------------------------------------------------------------
add("s1-budget-hacknexus-2023", "HackNexus 2023 — Final Budget Reconciliation",
    "event_budget", 2023, "2023-10-24", OFFICERS[2023]["Treasurer"], f"""
Final reconciliation for HackNexus 2023, prepared by {OFFICERS[2023]['Treasurer']} (Treasurer).
Projected income: Rs.65,000 (Rs.25,000 committed sponsorship from TechVerse Solutions,
Rs.20,000 college activity grant, Rs.20,000 participant registration at Rs.200 x 100 teams).
Actual income: Rs.40,000. The TechVerse Solutions sponsorship of Rs.25,000 was never received —
the company withdrew five days before the event, after banners with their logo had already
been printed. Registration closed at 98 teams (Rs.19,600) and the college grant of Rs.20,000
came through on time. Actual expenditure: Rs.58,000 against a planned Rs.52,000. Major
overruns: venue — the Main Auditorium booking was found to be double-booked with the
Cultural Society two weeks out, forcing a last-minute shift to the Innovation Centre plus
rented seating and generator, adding Rs.9,500 we had not budgeted; catering rose by
Rs.2,400 because the rescheduled venue had no canteen access; logistics and printing
reprints added Rs.1,900 (TechVerse-branded banners had to be redone without their logo).
Net position: Rs.40,000 income minus Rs.58,000 expenditure = a loss of Rs.18,000, covered
from the club reserve fund, which now stands at Rs.7,200. Recommendation for future
treasurers: never print sponsor-branded material before the money is in the account, get
written venue confirmation from the estate office (not verbal), and keep a 15% contingency
line. See the HackNexus 2023 post-mortem for the full cause analysis.
""")

add("s1-postmortem-hacknexus-2023", "HackNexus 2023 Post-Mortem",
    "post_mortem", 2023, "2023-10-30", OFFICERS[2023]["Events Lead"], f"""
Post-mortem for HackNexus 2023 (14-15 October), written by {OFFICERS[2023]['Events Lead']}
with input from the core team. What went well: 98 teams registered, our largest hackathon
turnout to date; judging ran on schedule; the problem statements from Orbita Labs were well
received; volunteers handled the overnight shift without incident. What went wrong: the
event lost Rs.18,000, and the causes were avoidable. Cause one: venue double-booking. Our
verbal booking of the Main Auditorium was overridden by the Cultural Society's written
booking. We discovered this only two weeks before the event and moved to the Innovation
Centre, paying Rs.9,500 extra for rented chairs, a generator, and cleaning. Lesson: get
written confirmation from the estate office with a receipt number. Cause two: sponsor
withdrawal. TechVerse Solutions, who had committed Rs.25,000 by email in July, pulled out
on 9 October — five days before the event — citing an internal budget freeze. We had
already printed banners and certificates with their logo and had planned prize money
against their money. Lesson: a sponsorship is not confirmed until the amount is in the club
account or an MoU is signed; always line up a backup sponsor for at least 50% of the
largest commitment. Cause three: no contingency line in the budget. Action items carried
to 2024: written venue confirmations, signed MoUs for any sponsorship above Rs.10,000, a
15% contingency line, and a shared sponsor-risk register so future teams know which
companies have burned us before.
""")

add("s1-minutes-venue-clash-2023", "Core Team Meeting Minutes — 30 September 2023",
    "meeting_minutes", 2023, "2023-09-30", OFFICERS[2023]["Secretary"], f"""
Minutes of the core team meeting held on 30 September 2023 in CS Block Lab 3, recorded by
{OFFICERS[2023]['Secretary']}. Present: all eight core members. Agenda item one: HackNexus
venue crisis. {OFFICERS[2023]['Events Lead']} reported that the estate office has allotted
the Main Auditorium to the Cultural Society for 14-15 October — the same weekend as
HackNexus. Our booking was made verbally with the previous estate clerk and no receipt
exists, so the Cultural Society's written booking takes precedence. Options discussed:
shift dates (rejected — sponsor commitments and exam calendar), negotiate a share
(rejected by Cultural Society), or move to the Innovation Centre. Resolved: move HackNexus
to the Innovation Centre. The hall is smaller, has no fixed seating and no backup power,
so we will rent 120 chairs and a generator; {OFFICERS[2023]['Treasurer']} estimates
Rs.9,000-10,000 in unplanned cost and flagged that the budget has no contingency line to
absorb it. Agenda item two: sponsorship status. TechVerse Solutions has still not
transferred the committed Rs.25,000; their SPOC has been "waiting on finance approval" for
three weeks. {OFFICERS[2023]['Outreach Lead']} will escalate to the marketing head this
week. Agenda item three: volunteer roster for the overnight shift was finalised, twelve
names confirmed. Next meeting scheduled for 7 October to lock logistics.
""")

add("s1-minutes-emergency-2023", "Emergency Core Meeting Minutes — 10 October 2023",
    "meeting_minutes", 2023, "2023-10-10", OFFICERS[2023]["Secretary"], f"""
Minutes of the emergency core meeting held on 10 October 2023 at 9 PM in the Innovation
Centre, recorded by {OFFICERS[2023]['Secretary']}. Called by {OFFICERS[2023]['President']}
after TechVerse Solutions emailed on 9 October withdrawing their Rs.25,000 sponsorship for
HackNexus, five days before the event, citing an internal budget freeze. Discussion: prize
pool of Rs.30,000 was announced publicly on the poster and cannot be reduced without
reputational damage. Banners, standees and certificates carrying the TechVerse logo have
already been printed (Rs.1,900 to reprint without the logo — resolved to reprint only the
stage banner and certificates). {OFFICERS[2023]['Treasurer']} presented revised numbers:
with the venue overrun already at Rs.9,500 and the sponsorship gone, the event will close
roughly Rs.18,000 in deficit, to be covered from the reserve fund. {OFFICERS[2023]['Outreach Lead']}
attempted same-week outreach to ByteBasket and NimbusHost; both declined on short notice,
ByteBasket indicating interest for next year instead. Resolved: proceed with the event at
full announced prize pool, absorb the deficit from reserves, and formally record TechVerse
Solutions in the sponsor register as high-risk. Resolved further: from 2024, no sponsor
logo goes to print before funds are received, and every sponsorship above Rs.10,000
requires a signed MoU. Meeting closed 10:40 PM.
""")

# ---------------------------------------------------------------------------
# STORYLINE 2 — TechVerse ghosts again in 2024
# ---------------------------------------------------------------------------
add("s2-email-techverse-thread-2024", "Email Thread: TechFest 2024 Sponsorship — TechVerse Solutions",
    "sponsor_email", 2024, "2024-07-18", OFFICERS[2024]["Outreach Lead"], f"""
Archived email thread between {OFFICERS[2024]['Outreach Lead']} (Outreach Lead) and Rohit
Malhotra, Marketing Manager, TechVerse Solutions, regarding TechFest 2024 sponsorship.
12 June: we proposed a Rs.20,000 silver tier. 14 June: TechVerse replied enthusiastically,
"count us in, paperwork by month end." 28 June: we sent the MoU draft as agreed at the
post-HackNexus review (signed MoU required before any commitment is treated as real).
5 July: no signature; Rohit wrote "finance team is reviewing, should be quick." 12 July:
follow-up sent, response "still with finance, don't worry, we are definitely on board."
18 July: follow-up sent, no reply. Note appended by {OFFICERS[2024]['Outreach Lead']} for
the record: this is the same pattern TechVerse showed in 2023 before withdrawing from
HackNexus five days out — enthusiastic verbal yes, then weeks of "finance is reviewing,"
then silence. Per the 2023 post-mortem policy, TechVerse money is not to be counted in any
budget projection until it is physically in the club account. I am keeping this thread in
the archive so the next outreach lead sees the pattern in their own words. Current
TechFest 2024 budget assumes zero from TechVerse; the gap is being pitched to ByteBasket
and Larkspur Systems instead, both of whom responded within three days.
""")

add("s2-email-techverse-silence-2024", "Follow-up #4: TechVerse MoU — no response (final note)",
    "sponsor_email", 2024, "2024-08-09", OFFICERS[2024]["Outreach Lead"], f"""
Final note on the TechVerse Solutions thread for TechFest 2024, filed by
{OFFICERS[2024]['Outreach Lead']}. Sent follow-up #4 on 2 August and a last courtesy note
on 9 August. No reply to either; the SPOC Rohit Malhotra has also stopped responding on
LinkedIn. Marking this outreach as DEAD. Total time invested: eight weeks, five emails,
two calls. Outcome: zero rupees, exactly as in 2023 when they withdrew Rs.25,000 from
HackNexus five days before the event. Pattern to remember, written plainly for whoever
reads this archive next year: TechVerse Solutions says yes fast and enthusiastically,
never signs anything, cites finance review, then goes silent. Two years, two ghostings.
Do not allocate their money in any projection, do not print their logo, and honestly, do
not spend outreach hours on them at all while better sponsors reply in days. For contrast,
in the same period ByteBasket confirmed Rs.12,000 with a signed MoU in nine days and
Larkspur Systems confirmed Rs.8,000 in six days — both amounts were in the club account
before poster printing. Recommendation recorded for the sponsor register: TechVerse
Solutions status = BLACKLISTED (two consecutive years of ghosting after verbal
commitment). If they ever approach us first with payment upfront, the core team can
revisit; otherwise this vendor should stay off the outreach list entirely.
""")

add("s2-handover-treasurer-2024", "Treasurer Handover Note 2024 → 2025",
    "handover_note", 2024, "2024-12-15", OFFICERS[2024]["Treasurer"], f"""
Handover from {OFFICERS[2024]['Treasurer']} (Treasurer 2024) to the incoming treasurer for
2025. Accounts: club account balance Rs.31,400; reserve fund rebuilt to Rs.15,000 after
the 2023 HackNexus loss drained it to Rs.7,200. Keys and ledgers are with the faculty
coordinator. Three things I need you to actually internalise. One: NEVER rely on TechVerse
Solutions. They committed Rs.25,000 to HackNexus 2023 and withdrew five days before the
event; in 2024 they verbally committed Rs.20,000 to TechFest, strung us along for eight
weeks of "finance is reviewing," and went silent. Two years, two ghostings. They are
blacklisted in the sponsor register — do not count their money, do not print their logo,
do not waste outreach hours. Two: the budget approval trick still works — Prof. Mehra
clears requisitions roughly three times faster if you submit before the 5th of the month
with a one-page summary on top (see the 2022 and 2023 secretary handovers; it has held
true for three years now). Submit on the 12th with a raw spreadsheet and you will wait a
month. Three: keep the 15% contingency line in every event budget; it is club policy since
the 2023 post-mortem and it saved Design-a-thon 2024 when the projector rental doubled.
Reliable sponsors as of today: ByteBasket, Larkspur Systems, and Cloudnine Devtools (see
the 2025 pitch preparation docs). Good luck — the books are clean, keep them that way.
""")

# ---------------------------------------------------------------------------
# STORYLINE 3 — Prof. Mehra budget trick (two handover notes)
# ---------------------------------------------------------------------------
add("s3-handover-secretary-2022", "Secretary Handover Note 2022 → 2023",
    "handover_note", 2022, "2022-12-18", OFFICERS[2022]["Secretary"], f"""
Handover from {OFFICERS[2022]['Secretary']} (Secretary 2022) to the incoming secretary.
Records: all meeting minutes for 2021 and 2022 are in the shared drive under /minutes,
named by date. The club register with the student affairs office must be renewed every
June — miss it and room bookings freeze. Templates for event proposals and requisition
forms are in /templates; use them, the office rejects free-form requests. The single most
useful thing I learned this year: how to get budgets approved fast. Prof. Mehra, our
faculty coordinator, processes requisitions in batches early in the month. If you submit
before the 5th of the month AND staple a one-page summary on top (total amount, purpose,
three bullet points of justification), approval comes back in three or four days. Submit
mid-month, or hand over a raw multi-tab spreadsheet with no summary, and the same request
sits for two to three weeks — I tested this the hard way with the TechTalks AV budget,
which took 19 days in August versus 4 days for the near-identical October request
submitted on the 3rd with a summary page. That is roughly three times faster, sometimes
better. Pass this on. Other notes: minute-taking template is in /templates/minutes.docx;
always record attendance count because the student affairs audit asks for it; the
Cultural Society books the Main Auditorium months ahead, so put our fest booking in
writing early (we hold the fest every March, so book by December). Reach me on the alumni
group if anything is unclear.
""")

add("s3-handover-treasurer-2023", "Treasurer Handover Note 2023 → 2024",
    "handover_note", 2023, "2023-12-20", OFFICERS[2023]["Treasurer"], f"""
Handover from {OFFICERS[2023]['Treasurer']} (Treasurer 2023) to the incoming treasurer.
It was a rough year financially: HackNexus 2023 closed Rs.18,000 in deficit (venue
double-booking plus the TechVerse Solutions pullout — read the post-mortem, it is
mandatory reading) and the reserve fund is down to Rs.7,200. Your first job is to rebuild
it to at least Rs.15,000 before committing to any large event. Practical things that will
save you weeks. First, the Prof. Mehra approval pattern is real: requisitions submitted
before the 5th of the month with a one-page summary sheet on top get cleared in about
3-4 working days; anything submitted later in the month or without the summary takes two
to three weeks. The previous secretary documented the same thing in their 2022 handover —
between us we have now seen it hold for two full years across a dozen requisitions.
Batch your purchases so requests land on the 1st-4th window. Second, new club policy from
the HackNexus post-mortem: every sponsorship above Rs.10,000 needs a signed MoU, no
sponsor logo goes to print before money is received, and every event budget carries a 15%
contingency line. Third, registration income via the college payment portal takes 12-15
days to reach our account — never plan to spend registration money on the event itself.
The ledgers are reconciled up to 20 December and Prof. Mehra has countersigned. Questions
welcome on the alumni group.
""")

# ---------------------------------------------------------------------------
# STORYLINE 4 — membership dropped 40% in 2024 after beginner workshops stopped
# ---------------------------------------------------------------------------
add("s4-minutes-workshops-cut-2024", "Core Team Meeting Minutes — 12 February 2024",
    "meeting_minutes", 2024, "2024-02-12", OFFICERS[2024]["Secretary"], f"""
Minutes of the core team meeting held on 12 February 2024 in Seminar Hall B, recorded by
{OFFICERS[2024]['Secretary']}. Present: seven of eight core members ({OFFICERS[2024]['Design Lead']}
absent, informed). Agenda item one: annual calendar. {OFFICERS[2024]['Tech Lead']} proposed
discontinuing the beginner workshop series (Intro to Git, Web Dev Bootcamp, AI Study Jam
basics track) for 2024. Reasons given: core members are stretched thin after the HackNexus
deficit recovery plan, senior members find teaching basics repetitive, and the view that
"people who are serious will learn on their own and come to the advanced events."
{OFFICERS[2024]['Outreach Lead']} objected, noting that the beginner workshops are where
most first-years first touch the club and that 60% of current members joined through one.
Vote: 5-2 in favour of discontinuing. Resolved: 2024 calendar will focus on advanced
events only — CTF Night, Open Source Week, Design-a-thon, TechFest, and competitive
programming sessions. Beginner series marked "on hold, revisit in 2025." Agenda item two:
budget recovery. Treasurer reported reserve fund at Rs.8,100, on track to Rs.15,000 by
year end. Agenda item three: TechFest sponsor shortlist approved (ByteBasket, Larkspur
Systems, TechVerse pending MoU per policy). Next meeting 26 February.
""")

add("s4-minutes-agm-2025", "Annual General Meeting Minutes — 20 January 2025",
    "meeting_minutes", 2025, "2025-01-20", OFFICERS[2025]["Secretary"], f"""
Minutes of the Annual General Meeting held on 20 January 2025 in the Main Auditorium,
recorded by {OFFICERS[2025]['Secretary']}. Attendance: 54. Agenda item one: membership
report. {OFFICERS[2025]['President']} presented the numbers: paid membership fell from 118
in January 2024 to 71 in December 2024 — a drop of exactly 40%. First-year sign-ups
collapsed from 52 (2023 intake) to 14 (2024 intake). The membership survey (see the 2024
Membership Review) attributes this overwhelmingly to the discontinuation of the beginner
workshop series in February 2024: first-years reported that every remaining event
"assumed you already knew things" and that there was no entry point into the club. The
advanced events themselves were well attended by existing members but recruited almost
nobody new. Resolved unanimously: reinstate the beginner workshop series from March 2025
with at least one beginner-track event per month (Intro to Git, Web Dev Bootcamp, AI
Study Jam basics), and pair every workshop with a mentorship sign-up sheet. Resolved
further: membership recovery target of 100 by December 2025. Agenda item two: accounts
summary presented and adopted; reserve fund stands at Rs.15,000. Agenda item three:
election of the 2025 core team was conducted by the outgoing president; results recorded
in the election register. Meeting closed with the president's note that "we learned an
expensive lesson: the pipeline matters more than the peak."
""")

add("s4-review-membership-2024", "Membership Review 2024 — Survey Findings",
    "project_doc", 2024, "2024-12-08", OFFICERS[2024]["Outreach Lead"], f"""
Membership Review 2024, compiled by {OFFICERS[2024]['Outreach Lead']} from the December
survey (61 responses: 44 current members, 17 lapsed members and first-years who chose not
to join). Headline numbers: paid membership stood at 118 in January 2024 and 71 in
December 2024, a 40% decline, the club's first drop since founding in 2021. First-year
sign-ups fell from 52 to 14 year over year. Survey findings: asked why they did not join
or renew, 71% of lapsed and prospective members selected "no beginner-friendly events" as
a top-two reason; free-text answers repeatedly mention that CTF Night and Open Source
Week "felt like they were for people who already knew everything." Several first-years
wrote that seniors were helpful when approached but that there was "no obvious first
event to attend." Correlation with the calendar: the beginner workshop series (Intro to
Git, Web Dev Bootcamp, AI Study Jam basics) was discontinued by core team vote in
February 2024; historically 60% of members joined the club through a beginner workshop.
Retention of existing advanced-track members remained healthy (82% renewed).
Recommendations: reinstate the beginner series with monthly cadence, assign a named
mentor to each workshop cohort, schedule beginner events in the first six weeks of each
semester when first-years are actively looking for clubs, and track "first event
attended" in the member register so this correlation is measurable next year.
""")

# ---------------------------------------------------------------------------
# STORYLINE 5 — Cloudnine Devtools 2025 pitch that worked
# ---------------------------------------------------------------------------
add("s5-postmortem-sponsor-2025", "Sponsor Outreach Post-Mortem 2025 — What Finally Worked",
    "post_mortem", 2025, "2025-04-22", OFFICERS[2025]["Outreach Lead"], f"""
Sponsor outreach post-mortem, April 2025, by {OFFICERS[2025]['Outreach Lead']}. Headline:
Cloudnine Devtools signed for Rs.50,000 — the largest sponsorship in club history — for
HackNexus 2025. This document records what we changed versus the 2023 approach, because
the difference was the pitch, not luck. What we did in 2023: a generic 14-slide deck about
the club, sent as cold email to 30 companies, asking for money against logo placement.
Result: one verbal yes (TechVerse Solutions) that evaporated five days before the event.
What we did in 2025: one-page pitch, tailored per company, metrics first. The Cloudnine
page led with numbers they cared about — 98 teams at HackNexus 2023, 340 unique attendees
across 2024 events, 71 paid members, 4,100 Instagram followers — then a specific offer:
their CLI tool as the official build tool of the hackathon, a 10-minute demo slot, a
dedicated API-prize track judged by their engineer, and winners interviewing for their
campus internship pool. Money asked: Rs.50,000 split as Rs.25,000 on MoU signing and
Rs.25,000 a week before the event — milestone payments, both received on time. We also
followed the post-2023 rules: signed MoU before any public announcement, no logo printing
until the first tranche cleared, and ByteBasket lined up as a Rs.15,000 backup in case
Cloudnine fell through. Lessons: sponsors buy outcomes, not goodwill; one tailored page
beats fourteen generic slides; milestone payments de-risk both sides; and a backup
sponsor means you never negotiate desperate.
""")

add("s5-email-cloudnine-2025", "Email: Cloudnine Devtools — Sponsorship Confirmed (Rs.50,000)",
    "sponsor_email", 2025, "2025-03-14", OFFICERS[2025]["Outreach Lead"], f"""
Archived confirmation email, filed by {OFFICERS[2025]['Outreach Lead']}. From: Ananya
Krishnan, Developer Relations Lead, Cloudnine Devtools. To: Nexus Tech Club outreach.
Subject: RE: HackNexus 2025 — partnership confirmed. Body (excerpt): "Loved the one-pager —
it answered in one page what most clubs take a call and a deck to not answer. The 98-team
turnout and the API-track proposal sold it internally in a day. Confirming Rs.50,000 as
discussed: Rs.25,000 released on MoU signature, Rs.25,000 released seven days before the
event. Our engineer Dhruv will judge the API track and we will ship 150 swag kits. Send
the MoU." Note by {OFFICERS[2025]['Outreach Lead']}: MoU signed 21 March, first tranche
of Rs.25,000 received 26 March, confirmation forwarded to the treasurer and logged in the
sponsor register with status = CONFIRMED-PAID. Second tranche received 2 April, a week
ahead of their own deadline. For contrast and for the record: this is what a real sponsor
looks like — fast internal approval, milestone payments offered without being pushed,
named point of contact who answers within a day. Compare the TechVerse Solutions threads
of 2023 and 2024 in this same archive before trusting any verbal commitment. The
Cloudnine one-page pitch template is saved in /templates/sponsor-onepager-2025 and the
full story of what changed versus 2023 is in the Sponsor Outreach Post-Mortem 2025.
""")

add("s5-minutes-hacknexus-win-2025", "Core Team Meeting Minutes — 28 April 2025",
    "meeting_minutes", 2025, "2025-04-28", OFFICERS[2025]["Secretary"], f"""
Minutes of the core team meeting held on 28 April 2025 in the Innovation Centre, recorded
by {OFFICERS[2025]['Secretary']}. Present: all eight core members. Agenda item one:
HackNexus 2025 wrap-up. {OFFICERS[2025]['Events Lead']} reported final numbers: 124 teams
(a club record, up from 98 in 2023), zero venue incidents (written estate-office
confirmation obtained in January, receipt number filed), and the event closed Rs.6,300 in
surplus — the first HackNexus to make money. {OFFICERS[2025]['Treasurer']} confirmed both
Cloudnine Devtools tranches (Rs.25,000 + Rs.25,000) were received before their respective
deadlines and the ByteBasket backup commitment was released with thanks, keeping the
relationship warm for TechFest. Agenda item two: what to institutionalise.
Resolved: the one-page tailored pitch replaces the slide deck as the club's default
sponsorship instrument; the milestone-payment structure (50% on MoU, 50% pre-event) is
club policy for all sponsorships above Rs.20,000; and the sponsor register review is now
a standing AGM agenda item. Agenda item three: beginner workshop series update — three
workshops held since March, 41 new sign-ups, membership at 89 and on track for the
100-member recovery target. Next meeting 12 May. Meeting closed 6:45 PM.
""")

# ---------------------------------------------------------------------------
# STORYLINE 6 — fest timing contradiction (March vs September)
# ---------------------------------------------------------------------------
add("s6-festplan-march-2022", "Nexus Annual Fest 2022 — Planning Document",
    "project_doc", 2022, "2022-01-10", OFFICERS[2022]["Events Lead"], f"""
Planning document for Nexus Annual Fest 2022, prepared by {OFFICERS[2022]['Events Lead']}.
The Nexus Annual Fest is held every March — it is the club's flagship event and closes
the academic year's activity calendar before end-semester exams begin in April. Fest 2022
is scheduled for 18-19 March in the Main Auditorium and Open Air Theatre (booking letter
submitted to the estate office in December, per standing practice; the Cultural Society
books months ahead so early written booking is essential). Planned segments: project expo
(20 stalls), the inter-college coding championship, two invited tech talks, the robotics
demo, and the closing awards ceremony where the year's best-member and best-project
trophies are presented. Budget envelope: Rs.45,000, of which Rs.15,000 from the college
cultural grant, Rs.18,000 from sponsors (PixelForge Media and Quanta Books confirmed),
and the balance from the club fund and stall fees. Committees: logistics under the Events
Lead, publicity under the Design Lead, judging under the Tech Lead, hospitality under the
Vice President. Timeline: posters by 20 February, registrations open 25 February, dry run
16 March. Standing rationale recorded for future teams: March slotting means first-years
have had two full semesters to build projects worth exhibiting, and the fest doubles as
the send-off for graduating seniors — keep the fest in March.
""")

add("s6-minutes-fest-moved-2024", "Core Team Meeting Minutes — 22 April 2024",
    "meeting_minutes", 2024, "2024-04-22", OFFICERS[2024]["Secretary"], f"""
Minutes of the core team meeting held on 22 April 2024 in Library Conference Room,
recorded by {OFFICERS[2024]['Secretary']}. Present: eight of eight. Agenda item one: fest
rescheduling decision. {OFFICERS[2024]['President']} presented the proposal to move the
Nexus Annual Fest permanently from March to September, effective this year (Fest 2024 will
be held 21-22 September). Reasons: the university's revised academic calendar has pulled
end-semester exams into mid-March, which gutted Fest 2024 planning (originally slotted for
March per club tradition) and would do so every year going forward; September gives
first-years an early flagship event in their first semester, which the Outreach Lead
argued is exactly the entry point the club has been missing; and the Main Auditorium is
demonstrably easier to book in September than in the crowded spring slot. Discussion:
{OFFICERS[2024]['Tech Lead']} noted the old March rationale (projects mature by spring,
senior send-off) and proposed a smaller "Farewell Demo Night" in March to preserve the
send-off tradition. Vote on moving the fest to September: 7-1 in favour. RESOLVED: from
2024 onward the Nexus Annual Fest is held in September, superseding the pre-2024 practice
of holding it in March; all planning templates and booking letters to be updated
accordingly. Agenda item two: fest committee formation for September deferred to next
meeting. Meeting closed 5:50 PM.
""")

# ---------------------------------------------------------------------------
# FILLER GENERATORS (template + seeded variation)
# ---------------------------------------------------------------------------

def slug(s):
    return "".join(c if c.isalnum() else "-" for c in s.lower()).strip("-").replace("--", "-")

def gen_meeting_minutes(year, idx):
    sec = OFFICERS[year]["Secretary"]
    date = _date(year)
    venue = random.choice(VENUES)
    items = random.sample(AGENDA, 4)
    attendees = random.randint(6, 14)
    event = random.choice(EVENTS)
    lead = random.choice(list(OFFICERS[year].values()))
    extra = random.choice([
        f"{lead} volunteered to draft the proposal and circulate it before the next meeting.",
        f"The team agreed to revisit this after the mid-semester exams.",
        f"{lead} raised concerns about volunteer availability and will prepare a duty roster.",
        f"A subcommittee of three was formed to follow up and report back in two weeks.",
        f"It was agreed to request a quotation from three vendors before deciding.",
    ])
    content = f"""
Minutes of the core team meeting held on {date} in {venue}, recorded by {sec}
(Secretary). Attendance: {attendees} members. Agenda item one: {items[0]}. The team
reviewed current status and open action items from the previous meeting; two of three
items were closed and one was carried forward. {extra} Agenda item two: {items[1]}.
{lead} presented a short update covering progress since last month, blockers, and the
plan for the coming fortnight. Discussion focused on timelines and who owns which
deliverable; owners were noted in the action register. Agenda item three: {items[2]}
with reference to the upcoming {event}. Preliminary dates were discussed and the events
team will confirm venue availability with the estate office in writing, per club policy.
Agenda item four: {items[3]}. Members were reminded to update the shared tracker by
Friday and to route all purchase requests through the treasurer using the standard
requisition template. Any other business: none recorded. The next meeting is scheduled
for a fortnight from the above date at the same venue; the secretary will circulate the
agenda three days in advance as usual.
"""
    add(f"minutes-{year}-{idx:02d}", f"Core Team Meeting Minutes — {date}",
        "meeting_minutes", year, date, sec, content)

def gen_event_budget(year, idx):
    treas = OFFICERS[year]["Treasurer"]
    event = random.choice([e for e in EVENTS if e not in ("HackNexus", "Nexus Annual Fest")])
    date = _date(year)
    total = random.randint(4, 30) * 500
    grant = int(total * random.choice([0.3, 0.4, 0.5]))
    sponsor = random.choice(SPONSORS)
    sp_amt = int(total * random.choice([0.1, 0.2, 0.25]))
    balance = total - grant - sp_amt
    ven = random.choice(VENUES)
    surplus = random.choice(["a small surplus", "break-even", "a minor overrun absorbed by the contingency line"])
    content = f"""
Budget sheet for {event} {year}, prepared by {treas} (Treasurer). Total planned
expenditure: Rs.{total:,}. Funding plan: Rs.{grant:,} from the college activity grant,
Rs.{sp_amt:,} sponsored by {sponsor}, and Rs.{balance:,} from the club fund and
participant fees. Expenditure heads: venue and AV setup at {ven} (projector, microphones,
extension boards), refreshments for participants and volunteers, printing (posters,
certificates, signage), speaker or judge honorarium where applicable, and miscellaneous
logistics including transport of equipment. A contingency line of 15% is included within
the total, per club policy adopted after the 2023 review. Approval: the requisition was
submitted to the faculty coordinator with a one-page summary sheet on top and cleared
without queries. Payment terms: all vendor payments by account transfer against invoice;
no cash advances above Rs.500. Reconciliation note: the event closed with {surplus};
final receipts are filed in the treasury folder for {year} and the ledger entry has been
countersigned by the faculty coordinator. Reminder recorded for future treasurers:
collect all vendor invoices on the day of the event itself — chasing invoices weeks later
delayed last quarter's reconciliation by ten days and holds up the audit trail required
by the student affairs office.
"""
    add(f"budget-{slug(event)}-{year}-{idx}", f"{event} {year} — Budget Sheet",
        "event_budget", year, date, treas, content)

def gen_sponsor_email(year, idx):
    out = OFFICERS[year]["Outreach Lead"]
    sponsor = random.choice(SPONSORS)
    event = random.choice(EVENTS)
    date = _date(year)
    amt = random.randint(3, 24) * 500
    outcome = random.choice([
        f"{sponsor} confirmed Rs.{amt:,} against logo placement and a stall; MoU signed and the amount was received before printing began",
        f"{sponsor} declined this cycle citing budget timing but asked to be contacted again next semester",
        f"{sponsor} offered in-kind support (goodies and vouchers worth roughly Rs.{amt:,}) instead of cash, which the core team accepted",
        f"{sponsor} confirmed Rs.{amt:,} split into two milestone payments per the club's standard terms",
    ])
    content = f"""
Archived sponsor correspondence, filed by {out} (Outreach Lead). Thread: {event} {year}
sponsorship discussion with {sponsor}. Summary of the exchange: the initial outreach email
introduced the club, shared audience numbers and the event plan, and proposed tiered
sponsorship options. {sponsor}'s marketing contact responded within the week requesting
details on footfall, social media reach, and deliverables. We shared the standard
deliverables sheet: logo on posters and certificates, a shout-out during the opening,
social media mentions before and after the event, and an optional stall or demo slot
depending on tier. Outcome: {outcome}. Follow-up actions recorded: deliverables were
tracked in the sponsor register, proof-of-delivery photos were shared with the sponsor
within one week of the event, and a thank-you note was sent from the club account.
Process note for future outreach leads: keep every commitment in writing in this archive,
update the sponsor register status field the same day anything changes, and remember that
per club policy no sponsor logo goes to print before the corresponding payment or signed
MoU is in hand. Relationship status after this cycle: warm; add them to the first-contact
list for next year's {event} planning.
"""
    add(f"sponsor-{slug(sponsor)}-{year}-{idx}", f"Sponsor Thread: {sponsor} — {event} {year}",
        "sponsor_email", year, date, out, content)

def gen_post_mortem(year, idx):
    lead = OFFICERS[year]["Events Lead"]
    event = random.choice([e for e in EVENTS if e != "HackNexus"])
    date = _date(year)
    attendance = random.randint(30, 220)
    good = random.sample([
        "registrations exceeded projections", "the volunteer roster held up with no gaps",
        "AV setup was tested the previous evening and ran without a hitch",
        "the feedback form response rate crossed 60%", "social media posts drove strong walk-in turnout",
        "judging finished on schedule", "the venue layout handled the crowd comfortably",
    ], 3)
    bad = random.sample([
        "certificate printing was left to the last two days and required a rush fee",
        "the registration desk was understaffed for the first hour",
        "speaker confirmation came late, compressing the publicity window",
        "refreshment counts were estimated too low and a top-up run was needed",
        "photography coverage of the first session was missed",
        "the feedback form went out two days late, reducing responses",
    ], 2)
    content = f"""
Post-mortem for {event} {year}, written by {lead} (Events Lead) with input from the
organising committee. Attendance: {attendance}. What went well: {good[0]}; {good[1]};
and {good[2]}. These reflect the checklist discipline introduced after earlier events and
should be retained in the standard operating procedure. What went wrong: {bad[0]}, and
{bad[1]}. Neither issue affected the outcome materially but both were avoidable with
earlier planning. Root causes discussed: task owners were assigned late in the cycle, and
the shared tracker was not updated in the final week, which hid the slippage until it was
urgent. Action items for the next edition: freeze the task-owner matrix at least three
weeks before the event date; add printing and speaker-confirmation deadlines to the
tracker as hard checkpoints with a named owner each; and have the secretary review the
tracker in the weekly core meeting during the final month. Budget note: the event closed
within its envelope and the reconciliation is filed by the treasurer; see the
corresponding budget sheet for the year. Overall assessment: a solid edition worth
repeating, with the fixes above expected to remove most of the friction observed this
time. This document is filed in the post-mortem archive for future organisers.
"""
    add(f"pm-{slug(event)}-{year}-{idx}", f"{event} {year} Post-Mortem",
        "post_mortem", year, date, lead, content)

def gen_handover(year, idx):
    role = random.choice([r for r in ROLES if r not in ("Secretary", "Treasurer")])
    person = OFFICERS[year][role]
    date = f"{year}-12-{random.randint(10, 22):02d}"
    tips = random.sample([
        "keep the shared drive folder structure exactly as it is — the audit depends on it",
        "confirm every venue booking in writing with the estate office and file the receipt number",
        "start sponsor outreach at least ten weeks before any event; late asks get in-kind offers at best",
        "the design templates in /templates save days — do not rebuild posters from scratch",
        "post event photos within 48 hours while the buzz is alive; engagement drops sharply after that",
        "maintain the equipment register every time anything leaves the club cupboard",
        "brief volunteers the evening before, never the morning of the event",
        "route every purchase through the treasurer's requisition template, however small",
    ], 4)
    content = f"""
Handover note from {person} ({role}, {year}) to the incoming {role.lower()}. Scope of the
role as practised this year: owning the {role.lower()} responsibilities across all club
events, coordinating with the rest of the core team in the weekly meeting, and keeping
the relevant sections of the shared tracker current. State of affairs at handover: all
open action items are closed or explicitly reassigned, the relevant folders in the shared
drive are organised by year and event, and contact lists (vendors, speakers, volunteers,
and counterparts in other clubs) are up to date as of this month. Things I wish someone
had told me at the start, in order of importance: first, {tips[0]}; second, {tips[1]};
third, {tips[2]}; and finally, {tips[3]}. Rhythm of the year: the recruitment push and
calendar planning dominate the first quarter, events cluster mid-year, and the last
quarter is about closing the books, documentation, and this handover. Expect the
unexpected during fest season and keep buffer days in every plan. I am reachable on the
alumni group for the first semester after graduation — ask early rather than rediscover
things the hard way. Best of luck; the club rewards the effort you put into it.
"""
    add(f"handover-{slug(role)}-{year}-{idx}", f"{role} Handover Note {year} → {year + 1}",
        "handover_note", year, date, person, content)

def gen_member_profile(name, year, idx):
    interest = random.sample(INTERESTS, 2)
    joined_via = random.choice(["Intro to Git Workshop", "Web Dev Bootcamp", "AI Study Jam",
                                "the recruitment drive", "Nexus Annual Fest", "a senior's referral"])
    proj = random.choice(["the club website revamp", "the attendance portal", "the fest registration app",
                          "the CTF challenge set", "the club Discord bot", "the equipment register app",
                          "the alumni newsletter pipeline", "the workshop content repo"])
    contribution = random.choice([
        "volunteered at three events and anchored the registration desk",
        "led a workshop session and mentored two first-year teams",
        "handled photography and social media coverage for the semester",
        "maintained the shared drive and the meeting-minutes archive",
        "represented the club at two inter-college competitions",
    ])
    date = _date(year)
    content = f"""
Member profile: {name}, on the rolls of Nexus Tech Club since {year}. Joined through
{joined_via}, which remains the story for a majority of the club's intake. Primary
interests: {interest[0]} and {interest[1]}. Contributions this year: {contribution};
additionally contributed to {proj} alongside senior members, picking up the club's
conventions for code review and documentation along the way. Participation record:
regular at the weekly meetings and present at most flagship events of the year, including
the fest and at least one hackathon or sprint. Skills and tools noted by the tech lead:
solid fundamentals, quick to pick up new tooling, and reliable on deadlines once
committed. Mentorship: paired with a senior mentor under the club's buddy system during
the first semester; now listed as available to mentor newer members in {interest[0]}.
Feedback from event leads describes {name.split()[0]} as dependable under pressure and
willing to take unglamorous tasks like inventory and desk duty, which the club values
highly. Recorded goals for next year: take ownership of one flagship event workstream,
deepen {interest[1]} through the project track, and contribute at least one reusable
template or document to the club's knowledge base so the next batch starts further ahead.
"""
    add(f"member-{slug(name)}-{idx}", f"Member Profile: {name}",
        "member_profile", year, date, OFFICERS[year]["Secretary"], content)

def gen_project_doc(year, idx):
    lead = random.choice(list(OFFICERS[year].values()))
    proj = random.choice(["Club Website Revamp", "Attendance Portal", "Fest Registration App",
                          "Discord Bot", "Equipment Register", "Alumni Newsletter Pipeline",
                          "Workshop Content Repository", "CTF Challenge Platform",
                          "Sponsor Register System", "Photo Archive Tooling"])
    stack = random.choice(["Next.js and Firebase", "Flask and SQLite", "React and Supabase",
                           "Django and Postgres", "FastAPI and MongoDB", "plain HTML with Sheets as backend"])
    status = random.choice(["shipped and in active use", "in beta with the core team",
                            "handed over to next year's maintainers with docs",
                            "paused pending volunteer bandwidth, codebase documented"])
    date = _date(year)
    n_contrib = random.randint(2, 6)
    content = f"""
Project document: {proj} ({year}), maintained by {lead}. Purpose: {proj.lower()} for the
club's internal operations, replacing the previous manual process that consumed volunteer
hours every week and was error-prone during peak event season. Tech stack: {stack},
chosen because members already knew it and hosting fits in the free tier. Team:
{n_contrib} contributors this cycle, coordinated through the club GitHub organisation
with pull-request review required from at least one senior member before merge. Current
status: {status}. Key design decisions recorded for future maintainers: keep secrets in
environment variables and never in the repository; prefer boring, well-documented
libraries over novel ones since maintainers change every year; and write the README as if
the reader has never seen the project, because next year they will not have. Operations:
deployment steps, admin credentials location (with the faculty coordinator, not in the
repo), and the backup schedule are documented in the project wiki. Known issues and
wishlist are tracked as GitHub issues labelled by priority; three are marked
good-first-issue to onboard juniors. Handover expectation: whoever takes this over should
read the wiki first, run the local setup end to end, and close one small issue before
touching anything large — that path has produced the smoothest maintainer transitions in
club history.
"""
    add(f"project-{slug(proj)}-{year}-{idx}", f"{proj} — Project Doc ({year})",
        "project_doc", year, date, lead, content)

# ---------------------------------------------------------------------------
# Generate filler to reach ~300 docs
# ---------------------------------------------------------------------------
mm_counts = {2021: 14, 2022: 15, 2023: 14, 2024: 15, 2025: 14}   # 72 filler minutes
for y, n in mm_counts.items():
    for i in range(n):
        gen_meeting_minutes(y, i)

for y in YEARS:
    for i in range(8):       # 40 filler budgets
        gen_event_budget(y, i)

for y in YEARS:
    for i in range(6):       # 30 filler sponsor emails
        gen_sponsor_email(y, i)

for y in YEARS:
    for i in range(5):       # 25 filler post-mortems
        gen_post_mortem(y, i)

for y in YEARS:
    for i in range(3):       # 15 filler handover notes
        gen_handover(y, i)

for i, name in enumerate(MEMBERS[:60]):   # 60 member profiles
    year = YEARS[i % 5]
    gen_member_profile(name, year, i)

for y in YEARS:
    for i in range(8):       # 40 project docs
        gen_project_doc(y, i)

# ---------------------------------------------------------------------------
random.shuffle(DOCS)  # deterministic shuffle so storyline docs aren't clustered

if __name__ == "__main__":
    OUT_PATH.write_text(json.dumps(DOCS, indent=1, ensure_ascii=False), encoding="utf-8")
    from collections import Counter
    types = Counter(d["doc_type"] for d in DOCS)
    print(f"Wrote {len(DOCS)} docs to {OUT_PATH}")
    for t, c in sorted(types.items()):
        print(f"  {t}: {c}")
