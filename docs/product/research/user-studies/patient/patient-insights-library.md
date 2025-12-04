# Patient Insights Library

**Purpose**: Centralized repository of key learnings from user research
**Last Updated**: November 23, 2025
**Owner**: UX Research Team
**Source Study**: Product Feedback Sessions (14 patients/caregivers, Sept-Oct 2025)

---

## How to Use This Library

This library captures:
- **Patterns** observed across multiple users/studies
- **Validated hypotheses** we can build on
- **Invalidated assumptions** we should avoid
- **Surprising findings** that change our thinking

**When to add**:
- After completing user research studies
- When usage data reveals patterns
- When customer feedback clusters around themes

**How to use**:
- Reference when writing PRDs
- Validate feature ideas against known user needs
- Share with new team members for context

---

## Quick Stats: Research Foundation

| Metric | Value |
|--------|-------|
| Total Participants | 14 |
| Participant Types | Patients (self-managing), Caregivers (family members) |
| Health Complexity | Simple (quarterly visits) to Complex (7-8 monthly appointments) |
| Geographic Coverage | BC, Alberta, Ontario (Canada); United States |
| Age Range | 30s to 80s |
| Technology Comfort | "Paper people" to daily AI users |

---

## Active Insights

Insights currently shaping our roadmap, organized by category.

---

# CATEGORY: USER NEEDS

---

### Insight 1: Users Want Aggregated Health Data, Not Another Portal

**Category**: User Need
**Confidence**: 🟢 High
**Validated**: Sept-Oct 2025 via patient/caregiver interviews (n=14)

**What We Learned**:
Users are overwhelmed by fragmented health data across multiple portals, apps, and paper records. They don't want another place to log in—they want one place that brings everything together automatically. The fragmentation operates at three levels: geographic (provincial/national borders), institutional (each provider's silo), and format (incompatible digital systems and paper).

**Evidence**:
- "You know, like you said, it's very scattered. There's some stuff I can find in Health Gateway, but it's very generic, you know, like it'll say I went for a hospital procedure, but it won't say that that was a colonoscopy or any of that kind of level of detail." — P07-CC
- "I don't have anything like I don't think they share any information once you sign up for like a new health care system in a new province. I don't think any records are shared interprovincially." — P05-MB
- "Like the information I mean you have access to hopefully most or all of your medical information. Maybe not. But even if you do, it's often spread out amongst [different places]." — P08-MK
- 14/14 participants mentioned data fragmentation as a pain point
- Source: Thematic Analysis Code 1.1 (Information Fragmentation)

**Implications**:
- **For Product**: Prioritize integrations over manual data entry; solve cross-border/interprovincial data challenges that competitors ignore
- **For Design**: Focus on unified views, not forms; make aggregation boundaries explicit (never create false confidence in completeness)
- **For Strategy**: Differentiate on aggregation capability—"complete picture platform" positioning

**Related Features**:
- PHR Integration Strategy
- Unified Health Timeline
- Cross-Border Data Migration Tools
- Document Upload & OCR Pipeline

---

### Insight 2: Caregivers Need Purpose-Built Coordination Tools, Not Adapted Patient Tools

**Category**: User Need
**Confidence**: 🟢 High
**Validated**: Sept-Oct 2025 via caregiver interviews (n=7)

**What We Learned**:
Caregivers managing healthcare for family members perform invisible labor that healthcare systems assume will occur but don't support: coordinating appointments across specialists, transporting information between providers, reconstructing histories from fragments. Current tools treat caregivers as "proxy patients" rather than users with distinct workflows.

**Evidence**:
- "So, um, he I think has two appointments this week alone along with the fact that every Monday he goes for blood tests and if his hemoglobin is low, he has a transfusion that week and that's been going on basically since May." — P07-CC (daughter managing father's care)
- "I do feel completely disorganized and overwhelmed... there's only one of me I can only do so much." — P10-MT
- "I get a lot of requests from my family, my relatives, my friends in helping them navigate the system... you shouldn't need a terminal degree to be able to navigate healthcare as a consumer." — P11-RM
- Caregivers described managing 7-8 monthly appointments for family members
- Source: Thematic Analysis Codes 2.1-2.4 (Caregiver Experience & Burden)

**Implications**:
- **For Product**: Build multi-patient dashboards, delegation features, care team coordination; recognize caregiver as primary user
- **For Design**: Clear visual separation between managed patients; responsibility assignment across family members; action item tracking
- **For Strategy**: Target "adult children caring for aging parents" as initial market segment (40-65 year olds, high coordination burden, willingness to pay)

**Related Features**:
- Multi-Patient Management
- Family Sharing Controls
- Care Team Coordination
- Caregiver Dashboard

---

### Insight 3: Users Want Timeline/Visual Organization of Health Information

**Category**: User Need
**Confidence**: 🟢 High
**Validated**: Sept-Oct 2025 via prototype feedback (n=14)

**What We Learned**:
Users responded enthusiastically to chronological/timeline representations showing "all the different things" on one page. Particular appreciation for seeing temporal density—when multiple health events cluster together. This aligns with how users naturally understand health: as stories with arcs, patterns, and causality over time, not isolated data points.

**Evidence**:
- "That's nice. I like I like that one... I like the fact that I can see it all on one page, all the different things... And the fact is is that you not just have the MCL tear left, you have fell rollerblading." — P06-OV
- "this is amazing... this really really like shows that visual of what's been going on. like when there's this frequency all of a sudden where a whole bunch of things are happening at the same time." — P07-CC
- "Um, yeah, I think the the trends, which like I said, I already find those helpful. Um, the timeline is helpful, too. I never haven't seen anything like that." — P05-MB
- "you look at the life lab and they do over the timeline right over your last five results and it kind of it gives you that of um where I've been and where I'm going." — P08-MK
- Source: Thematic Analysis Code 5.1 (Timeline & Visualization Preferences)

**Implications**:
- **For Product**: Timeline/feed view as primary navigation paradigm; temporal density visualization for pattern recognition
- **For Design**: Show events chronologically with visual clustering; include context and relationships, not just data points; support "zooming" from years to days
- **For Strategy**: "Health story" framing resonates; differentiate from category-based portals

**Related Features**:
- Unified Health Timeline
- Temporal Density Visualization
- Event Clustering
- Pattern Recognition Alerts

---

### Insight 4: Users Need Appointment Preparation Support

**Category**: User Need
**Confidence**: 🟡 Medium
**Validated**: Sept-Oct 2025 via interviews (n=14)

**What We Learned**:
Users arrive at appointments unprepared because no tools help them gather relevant history, formulate questions, or anticipate what providers need. The work of appointment preparation is self-directed and unsupported, leading to forgotten questions, missing information, and inefficient visits.

**Evidence**:
- "Yeah. Yeah. I don't exactly know the right questions to ask, of course. So, but uh yeah, I I it gives me ideas of what to ask him when we go." — P03-CM
- "I usually have another head with me that will hear things that I probably don't hear and vice versa." — P04-JC (bringing support person as workaround)
- "for example sometimes you have to do blood test before seeing a doctor and they send you a paper an envelope with the requisition and the meeting is with the doctor in three months from now where do I put this paper so I remember to have it." — P04-JC
- Multiple participants described creating personal question lists and bringing documentation as self-organized workarounds
- Source: Thematic Analysis Codes 3.1-3.4, 6.1 (Patient-Provider Communication, Self-Education)

**Implications**:
- **For Product**: Appointment-specific preparation tools; auto-extract relevant history based on appointment type; suggest questions
- **For Design**: "Upcoming appointment" cards with relevant context; checklist of what to bring/do before visit
- **For Strategy**: Position as tool that makes appointments more efficient for both patients AND providers

**Related Features**:
- Appointment Preparation Module
- Question Suggestion Engine
- Pre-Visit Summary Generator
- Appointment Reminder Integration

---

### Insight 5: Users Need Control Over What Information Shares With Whom

**Category**: User Need
**Confidence**: 🟢 High
**Validated**: Sept-Oct 2025 via interviews (n=14)

**What We Learned**:
Users want granular control over which health information shares in which contexts—not because they're hiding things inappropriately, but because they strategically manage disclosure to avoid bias, stigma, or being overwhelmed with a "complicated" patient label. Current all-or-nothing sharing models don't support this legitimate need.

**Evidence**:
- "Say I had HIV or some sort of like STD stigmatizing, you know, you know, condition like mental health that I don't want to share with a provider who I feel could be judgmental. I want to delete it out of this interface but not my main database." — P11-RM
- "if I had a complicated medical history and there are 15 diagnosis um and I'm a woman, one of my concerns would be would the physician think I'm a hypochondriac and refer me to psychiatry, which has happened to my um female friends who are patients." — P11-RM
- "Um, wonder if there would should be like like an option for things you want to show. Yeah, like a family member. Like you might not want to share everything." — P05-MB
- "I would even say things like that I don't really want to share with my doctor. For examp I'm going to be a little silly losing hair given all the other severity of the other symptoms." — P04-JC
- Source: Thematic Analysis Code 7.2 (Informational Triage & Selective Disclosure)

**Implications**:
- **For Product**: Provider-specific views; context-aware sharing permissions; "full record" vs. "shared view" separation
- **For Design**: Make sharing controls intuitive but not burdensome; show what's included/excluded in any shared summary
- **For Strategy**: Privacy/control features as competitive differentiator; address legitimate user safety concerns

**Related Features**:
- Granular Sharing Controls
- Provider-Specific Views
- Sharing Audit Logs
- Temporary Access Links

---

# CATEGORY: PAIN POINTS

---

### Insight 6: Repetitive Information Provision Causes Major Frustration

**Category**: Pain Point
**Confidence**: 🟢 High
**Validated**: Sept-Oct 2025 via interviews (n=14)

**What We Learned**:
Users are exhausted by repeatedly providing identical information to different providers—same intake forms, same medical history questions, same allergy lists. This repetition wastes time, signals system dysfunction, and creates errors when users forget details they've reported many times before.

**Evidence**:
- "I felt like when I especially when I was giving birth, every single provider would ask me like literally the same questions over and over again. Like it was just constantly like do you have allergies?" — P05-MB
- "every time you go for a scan you only have this little section and you have to write all your surgery and I'm having a scan almost every month and I have to write the same blurb all the time." — P04-JC
- "Like every time I went to go see a new professional, whether it was an acupuncturist or a massage therapy person, you had to spend 15 minutes actually telling your story." — P13-MM
- "I always had to repeat myself. Like it was unbelievable how I get questions and I'm like reread the text re I just said that." — P01-CH
- Source: Thematic Analysis Code 1.2 (Information Redundancy)

**Implications**:
- **For Product**: Auto-populate intake forms; generate shareable summaries for new providers; reduce redundant data entry
- **For Design**: "Copy to clipboard" for common info; pre-filled templates; QR code sharing
- **For Strategy**: Quantify time savings as value proposition ("save 15 minutes per new provider")

**Related Features**:
- Provider Summary Generator
- Intake Form Auto-Fill
- Shareable Health Summary Links
- QR Code Health Card

---

### Insight 7: Accessing Own Medical Records Is Difficult and Delayed

**Category**: Pain Point
**Confidence**: 🟢 High
**Validated**: Sept-Oct 2025 via interviews (n=14)

**What We Learned**:
Patients face significant barriers obtaining their own medical records: long wait times, physical queuing, delayed results, and information that goes to providers but not patients. This creates information asymmetry where providers know more about the patient's health than the patient does.

**Evidence**:
- "I had to line up. Line up and wait and hopefully get the paper ready. In some at the cancer agency, we don't, but at the general hospital in Vancouver, you do. It's kind of crazy... and sometimes it's not timely either." — P04-JC
- "First of all the results may be available today but I'll receive the results when I have my next meeting with the doctor which could be three weeks from the date." — P04-JC
- "Yeah, I don't get the lab reports though. So I don't see those things. they go to the doctor." — P02-HS
- "when I was in the states and that was 3 years from the beginning of ago... I was doing the scans there and the next morning they were available on my screen. It was amazing." — P04-JC (contrast with Canadian experience)
- Source: Thematic Analysis Code 1.3 (Difficulty Accessing Records)

**Implications**:
- **For Product**: Real-time or near-real-time results access; concierge records request service; integration with labs/imaging
- **For Design**: "Results pending" status indicators; notification when new results available
- **For Strategy**: Speed-to-access as differentiator; address Canadian system delays specifically

**Related Features**:
- Lab Results Integration
- Results Notification System
- Concierge Records Request Service
- Real-Time Data Sync

---

### Insight 8: Medical Information Overload Prevents Processing and Action

**Category**: Pain Point
**Confidence**: 🟢 High
**Validated**: Sept-Oct 2025 via interviews (n=14)

**What We Learned**:
When presented with complex medical information (test results, treatment options, diagnoses), users feel overwhelmed and unable to process or act on it. They want verbal summaries and plain language explanations, not data dumps. This is especially acute during high-stress moments like diagnosis delivery.

**Evidence**:
- "It was just flabbergasting and the way it was given to me was rather casually. I was stunned. I could not hear anything... I heard nothing for five minutes as that doctor spoke to me." — P15-GB (on receiving pacemaker diagnosis)
- "I was told to research it on the internet to choose between a pacemaker or... just got so as I tried to research this and understand it, I went back to the doctor and I just said, 'Do whatever is easiest, safest, and quickest.'" — P15-GB (surrendering decision-making due to overwhelm)
- "are you smart enough to read your own results? This is where I'm getting a little frustrated because sure I want to have all good news, but if this is bad news, I still need to understand them." — P04-JC
- 3 of 4 early participants described situations where they asked providers to simplify/summarize
- Source: Thematic Analysis Codes 3.5, 7.3 (Catastrophic Diagnosis Communication, Patient Abdication)

**Implications**:
- **For Product**: AI summaries with plain language; progressive disclosure (summary first, details on demand); decision support tools
- **For Design**: Layered information architecture; "explain like I'm 10" option; visual explanations alongside text
- **For Strategy**: Balance between complete data access and digestible insights; trauma-aware design

**Related Features**:
- AI Health Summaries
- Plain Language Results Translator
- Progressive Disclosure UI
- Decision Support Module

---

### Insight 9: ⚠️ CRITICAL: Providers Don't Communicate With Each Other

**Category**: Pain Point
**Confidence**: 🟢 High
**Validated**: Sept-Oct 2025 via interviews (n=14)

**What We Learned**:
Specialists, primary care physicians, and other providers operate in silos, often completely unaware of each other's diagnoses, treatments, or recommendations. Patients become information couriers, manually transporting context between providers who make critical decisions based on incomplete pictures. This creates diagnostic delays, conflicting treatments, and safety risks.

**Evidence**:
- "I need my rheumatologist and my hypertension person to be able to see each other because I'm trying to get one of them to reduce the medications I'm on because they feel overdubbed." — P06-OV
- "he's been coughing up blood every day since May... he has been to I don't even remember how many specialists... and no one seems to be able out of all of these specialists that to me just keep passing the buck." — P07-CC
- "I feel like the health care professionals don't always talk to each other. Um, you know, and then when there does seem to be a problem, they're pointing fingers at each other." — P13-MM
- "And some of that is due to systems not talking to each other. Others are due to access to their own electronic medical records." — P11-RM
- Source: Thematic Analysis Code 6.2 (Provider Interoperability Gaps)

**Implications**:
- **For Product**: Cross-provider summary generation; medication reconciliation across sources; care team visibility
- **For Design**: "Share with provider" workflows; specialist-specific summary formats; care team map showing all providers involved
- **For Strategy**: Position patient as "system integrator" and build tools to support that essential role

**Related Features**:
- Provider Communication Tools
- Care Team Dashboard
- Medication Reconciliation
- Cross-Provider Summary Generator

---

### Insight 10: ⚠️ CRITICAL: Time Constraints Lead to Dismissiveness and Missed Concerns

**Category**: Pain Point
**Confidence**: 🟢 High
**Validated**: Sept-Oct 2025 via interviews (n=14)

**What We Learned**:
Rushed appointments leave patients feeling unheard, with concerns dismissed or not documented. Providers operating under time pressure may minimize patient-raised issues, particularly for women and those with complex histories. This creates adversarial dynamics where patients feel they must "fight" to be taken seriously.

**Evidence**:
- "He'll he'll answer questions, but they're it's not a it doesn't give a lot of us a lot of time, I guess, is what I would say." — P03-CM
- "And it was really like to the point where it was so quick. He was like chicken scratching notes and okay you want to have surgery tomorrow." — P04-JC
- "Because I get dismissed... They usually will dismiss me quite quickly, but if I insist, then they will clarify." — P04-JC
- "I feel that I'm patronized by the doctors because what do I know, right? What do I know about me?... it's almost like that just can't be true what you're saying." — P08-MK
- "Because the time of the appointment was up and I was in shock. Yeah. And there was no they're under a time schedule." — P15-GB
- Source: Thematic Analysis Code 3.2 (Time Constraints & Clinical Dismissiveness)

**Implications**:
- **For Product**: Pre-visit summaries that reduce provider's "catch-up" time; post-visit documentation comparison; concern prioritization tools
- **For Design**: Professional, credibility-establishing format for patient-generated summaries; clear concern flagging
- **For Strategy**: Frame as efficiency tool for providers AND empowerment tool for patients (dual value proposition)

**Related Features**:
- Pre-Visit Summary Generator
- Concern Prioritization Interface
- Visit Note Comparison Tool
- Provider-Ready Documentation

---

### Insight 11: ⚠️ CRITICAL: Diagnostic Journeys Without Resolution Cause Exhaustion

**Category**: Pain Point
**Confidence**: 🟡 Medium
**Validated**: Sept-Oct 2025 via interviews (n=5)

**What We Learned**:
Patients with unexplained symptoms may see multiple specialists over months or years without diagnosis, experiencing "specialist buck-passing" where each rules out their domain without taking ownership of the whole patient. This creates documentation burden (patient must maintain master narrative), emotional exhaustion, and healthcare system distrust.

**Evidence**:
- "he's been coughing up blood every day since May... he has been to I don't even remember how many specialists... and no one seems to be able out of all of these specialists that to me just keep passing the buck." — P07-CC
- "one of my friends has taken her 15 years to get the correct diagnosis and that disease is still not well managed." — P11-RM
- "once I actually saw the doctor, got on the list to get an MRI, it took me over a year to get actually an MRI done before they could actually refer me to a neurosurgeon." — P13-MM
- "during that time I was hearing all of these different things like it's not a slip disc, it might be a slip disc, but we didn't know because we didn't have the MRI." — P13-MM
- Source: Thematic Analysis Code 6.4 (Diagnostic Odyssey Experience)

**Implications**:
- **For Product**: Diagnostic journey tracking (specialists consulted, tests done, hypotheses, what's been ruled out); timeline flagging when investigation stalls
- **For Design**: "Investigation status" distinct from "diagnosed conditions"; hypothesis tracking interface
- **For Strategy**: Serve complex/undiagnosed patients as underserved segment; build loyalty through difficult periods

**Related Features**:
- Diagnostic Journey Tracker
- Specialist Consultation Log
- Hypothesis & Rule-Out Tracking
- Investigation Stall Alerts

---

### Insight 12: ⚠️ SAFETY CRITICAL: Medication Errors Occur Between Provider Handoffs

**Category**: Pain Point
**Confidence**: 🟡 Medium
**Validated**: Sept-Oct 2025 via interviews (n=3)

**What We Learned**:
Medication errors occur at handoff points—between prescriber and dispenser, between care settings, between provinces—with blame-shifting between parties and patients bearing the consequences. One participant described a medication error causing week-long psychosis in her mother-in-law, with pharmacist and doctor blaming each other.

**Evidence**:
- "recently we just had a situation where we were in France and so we weren't around and um the pharmacist actually who was doing the bubble packs they put two of the wrong medications together and she had some really severe reactions to it and was like in psychosis for like a week." — P13-MM
- "the pharmacist was blaming the doctor and the doctor was blaming the pharmacist. So, I just feel like I feel like we have a very inefficient system that we need to fix." — P13-MM
- "we're trying to be proactive rather than reactive and kind of take the situation to our own hands." — P13-MM (family creating own medication verification system)
- Source: Thematic Analysis Code 9.1 (Medication Error Cascades)

**Implications**:
- **For Product**: Medication reconciliation across all sources; interaction checking; change alerts when medications modified
- **For Design**: Visual medication timeline showing changes; alerts for concerning patterns; verification workflows
- **For Strategy**: Patient safety positioning; build trust through demonstrable safety features

**Related Features**:
- Medication Reconciliation Engine
- Drug Interaction Checker
- Medication Change Alerts
- Multi-Source Medication Aggregation

---

### Insight 13: ⚠️ SAFETY CRITICAL: Post-Diagnosis Support Is Often Absent

**Category**: Pain Point
**Confidence**: 🟡 Medium
**Validated**: Sept-Oct 2025 via interviews (n=3)

**What We Learned**:
After receiving major diagnoses or procedures, patients may experience complete absence of follow-up support, education, or care coordination. They are left to figure out medication impacts, lifestyle changes, and ongoing management without guidance—leading to poor outcomes and lingering uncertainty about whether they received appropriate care.

**Evidence**:
- "There was no support afterward after I got this pacemaker." — P15-GB
- "Nobody told me that I'd be taking several medications per day. Nobody. And that was another shock." — P15-GB
- "I think I'm starting to feel a bit better now, but I was told on the internet it would just be fantastic. Everything normal. I found myself sleepy." — P15-GB
- "this meditation makes me feel dizzy. I love doing yoga and I get dizzy when I have to stand up to do a balancing. I'm dizzy. I never was dizzy before. and he says, you are 75." — P15-GB (concern dismissed)
- Source: Thematic Analysis Code 9.2 (Post-Diagnosis Support Abandonment)

**Implications**:
- **For Product**: Post-diagnosis education modules; symptom tracking for new conditions; "what to expect" content; follow-up question capture
- **For Design**: Condition-specific onboarding flows; "new diagnosis" mode with appropriate resources
- **For Strategy**: Fill care gaps that health systems leave; partnership opportunity with patient education organizations

**Related Features**:
- Post-Diagnosis Support Module
- Condition-Specific Education Content
- "What to Expect" Guides
- Symptom Tracking for New Conditions

---

# CATEGORY: BEHAVIORS & WORKAROUNDS

---

### Insight 14: Users Create Manual Tracking Systems to Fill Gaps

**Category**: Behavior
**Confidence**: 🟢 High
**Validated**: Sept-Oct 2025 via interviews (n=14)

**What We Learned**:
In absence of integrated tools, users create their own systems—paper lists, phone notes, Word documents, spreadsheets, filing cabinets—to track health information. This labor-intensive workaround demonstrates the real need and willingness to invest effort. Users with manual systems are prime adoption candidates if we reduce their work.

**Evidence**:
- "My dad also carries a little piece of paper around with him with all their medications on it. Um, just for when it's an emergency and he needs to know something right away, he has it. But it's a challenge when he can't find that piece of paper right away." — P03-CM
- "And then I personally have my own, you know, on my iPhone in my notes, I have my own list of like chronologically everything that I've had done." — P07-CC
- "I just keep a little hard cover journal type thing and I try to remember to write in a date of when I saw the doctor and what occurred." — P02-HS
- "Oh, I have a filing cabinet with very very you know extensive filings." — P06-OV
- "I now carry a book with me all the time." — P15-GB
- Source: Thematic Analysis Code 1.4 (Manual Tracking Methods)

**Implications**:
- **For Product**: Import/migration from existing systems; reduce manual work dramatically; make existing effort portable
- **For Design**: Low-friction data entry; voice notes; photo capture; seamless sync
- **For Strategy**: Target users already tracking—they feel the pain most acutely and will appreciate value immediately

**Related Features**:
- Document Upload & Auto-Extraction
- Voice Note Capture
- Photo-to-Record Pipeline
- Import from Apple Health/Google Fit

---

### Insight 15: Users Actively Use ChatGPT/AI for Healthcare Navigation

**Category**: Behavior
**Confidence**: 🟡 Medium
**Validated**: Sept-Oct 2025 via interviews (n=6)

**What We Learned**:
Multiple participants described actively using ChatGPT to translate medical terminology, interpret lab results, get "second opinions," prepare for appointments, and summarize complex documents. This demonstrates demand for AI assistance AND acceptance of AI in healthcare contexts—but with specific task boundaries.

**Evidence**:
- "I plugged all of the information into chat GPT. And it was like, you're in amazing health... I am familiar with putting it into chat GBT and at least just getting sort of like a second not medical opinion." — P08-MK
- "my doctor right away is like, 'Oh my god, you have to get your cholesterol down.' Well, I plugged all of the information into chat GPT." — P07-CC (validating provider advice)
- "I just got it to summarize this morning for me um a sort of like something I can give to my stepfather's family doctor." — P07-CC
- "I use AI multiple times a day at least." — P07-CC
- "what I find is I would usually ask JDP the chat GTP I find that if I keep asking the same question but different angles eventually she figures out the answer." — P04-JC
- Source: Thematic Analysis Code 4.7 (Consumer AI Tools in Healthcare Navigation)

**Implications**:
- **For Product**: Build AI features users are already getting elsewhere; make them integrated, trustworthy, and health-specific
- **For Design**: Task-specific AI (summarization, translation, trend analysis) not general chatbot; clear accuracy indicators
- **For Strategy**: Competitive threat if we don't offer AI; opportunity if we offer trusted, integrated alternative to generic ChatGPT

**Related Features**:
- AI Health Summaries
- Medical Terminology Translator
- Lab Results Interpreter
- Document Summarization

---

### Insight 16: Caregivers Reconstruct Health Histories From Diaries and Memory

**Category**: Behavior
**Confidence**: 🟡 Medium
**Validated**: Sept-Oct 2025 via caregiver interviews (n=5)

**What We Learned**:
When formal records are incomplete or inaccessible, caregivers engage in painstaking historical reconstruction—going back through personal diaries, texting family members, searching old calendars—to piece together medical histories. This "detective work" is invisible to providers and exhausting for families.

**Evidence**:
- "She always keeps a daily diary... she's actually going back in her diary that she writes for her own mental health to go back and see... that's crazy like to go back, you know, a year or two." — P07-CC
- "I had to go back and forth with her on the phone and text message as I was trying to like fill in the holes." — P07-CC
- "going back say five years, he's had I don't even remember how many ER visits. So all of that is missing." — P07-CC
- "I kind of had to play in synthesizing the information only to transmit it to others who would also be interested." — P01-CH
- Source: Thematic Analysis Code 2.3 (Care Coordination Detective Work)

**Implications**:
- **For Product**: Historical timeline reconstruction tools; "fill in the gaps" workflows; family member contribution features
- **For Design**: Support partial information entry ("approximately 2019"); collaborative editing for family members
- **For Strategy**: Reduce reconstruction labor as key value proposition for caregivers

**Related Features**:
- Historical Timeline Builder
- Family Contribution Workflow
- Gap Identification & Fill-In Tools
- Approximate Date Support

---

### Insight 17: Users Strategically Withhold Information From Providers

**Category**: Behavior
**Confidence**: 🟡 Medium
**Validated**: Sept-Oct 2025 via interviews (n=5)

**What We Learned**:
Patients—particularly women and those with complex histories—strategically manage what information they disclose to avoid bias, being labeled "hypochondriac," or inappropriate psychiatric referrals. This defensive behavior is a rational response to experienced dismissiveness but creates safety risks when relevant information is withheld.

**Evidence**:
- "Say I had HIV or some sort of like STD stigmatizing, you know, you know, condition like mental health that I don't want to share with a provider who I feel could be judgmental." — P11-RM
- "if I had a complicated medical history and there are 15 diagnosis um and I'm a woman, one of my concerns would be would the physician think I'm a hypochondriac and refer me to psychiatry, which has happened to my um female friends who are patients." — P11-RM
- "I would even say things like that I don't really want to share with my doctor." — P04-JC
- Source: Thematic Analysis Code 7.2 (Informational Triage & Selective Disclosure)

**Implications**:
- **For Product**: Support legitimate selective disclosure; don't force all-or-nothing sharing; respect user agency
- **For Design**: Clear distinction between "my complete record" and "what I'm sharing with this provider"
- **For Strategy**: Understand this as safety behavior, not deception; build trust by respecting information control

**Related Features**:
- Selective Sharing Controls
- Provider-Specific Views
- "Complete" vs. "Shared" Record Separation

---

### Insight 18: Users Bring Support People to Important Appointments

**Category**: Behavior
**Confidence**: 🟡 Medium
**Validated**: Sept-Oct 2025 via interviews (n=7)

**What We Learned**:
Users frequently bring family members or friends to medical appointments as "second ears"—someone who can hear things the patient misses, ask questions, take notes, and provide emotional support. This compensates for information overload, stress-impaired processing, and time-pressured appointments.

**Evidence**:
- "I usually have another head with me that will hear things that I probably don't hear and vice versa." — P04-JC
- "Her friends also assist her, with one friend notably taking notes during a cardiology appointment." — P06-OV (field notes)
- "I had no one else there. I had no pen and pencil." — P15-GB (describing appointment where she received shocking diagnosis alone)
- "I attend I try to attend his appointments because it doesn't go so well when he goes on by himself." — P10-MT
- Source: Thematic Analysis Code 2.2 (Emotional Labor & Support)

**Implications**:
- **For Product**: Support person involvement features; shared access for appointment notes; post-visit summary sharing
- **For Design**: "Share with support person" workflow; collaborative note-taking; family member notification options
- **For Strategy**: Design for care dyads/triads, not just individual patients

**Related Features**:
- Support Person Access
- Appointment Note Sharing
- Collaborative Notes
- Care Circle Features

---

# CATEGORY: MENTAL MODELS

---

### Insight 19: Users Think of Health as Stories, Not Data Points

**Category**: Mental Model
**Confidence**: 🟢 High
**Validated**: Sept-Oct 2025 via interview patterns (n=14)

**What We Learned**:
Users naturally describe their health in narrative form—what happened, why, what they did about it—rather than as isolated data points. The context, timeline, and causal connections matter as much as the facts themselves. This narrative framing should guide information architecture.

**Evidence**:
- Users told detailed stories including timeline, decisions, and consequences when describing health issues
- Users referenced related events when describing health issues ("after my surgery...", "when I was waiting for...")
- Temporal and causal connections were central to how participants understood their health
- "And because I I needed sort of a chronological longitudinal kind of commentary about the last five or six weeks so that he could begin to see, oh yeah, okay, I can see that's happening more." — P01-CH
- Source: Thematic Analysis Codes 1.6, 5.1 (Temporal Challenges, Timeline Preferences)

**Implications**:
- **For Product**: Timeline/feed view as primary paradigm; event linking; narrative export features
- **For Design**: Show context and relationships alongside data; support story-building not just data storage
- **For Strategy**: "Health story" positioning differentiates from clinical, data-dump competitors

**Related Features**:
- Health Timeline
- Event Linking & Context
- Narrative Summary Export
- Story-Based Onboarding

---

### Insight 20: Trust in Digital Health Is Multi-Dimensional

**Category**: Mental Model
**Confidence**: 🟢 High
**Validated**: Sept-Oct 2025 via interviews (n=14)

**What We Learned**:
Users don't have simple trust/distrust reactions to digital health tools. Trust operates across multiple dimensions: security (will my data be breached?), accuracy (is this information correct?), business model (are you selling my data?), algorithmic (can I trust AI decisions?), and relationship impact (will this help or hurt my provider relationship?). All must reach threshold for adoption.

**Evidence**:
- Security: "I'm hyper concerned about security but that's just who I am... I'm also perfectly aware that there's nothing that's secure... everything's been hacked and everything will continue to be hacked." — P06-OV
- Business model: "I would want to know like what is the value ad? Um, even as a user, I kind of want to understand what your business model is. Like, is your business model just taking information from me and training your AI like am I your content?" — P11-RM
- Data quality: "if if it did it reliably in the sense of uh like so I guess my question is if everything's not there but you think everything's there then it becomes more dangerous than useful." — P06-OV
- Relationship impact: "my fear might be is oh if I send this what if they just say okay that sounds good because the real richness of the conversation was the thing I hadn't thought to say." — P01-CH
- Source: Thematic Analysis Codes 4.1-4.6 (Technology Adoption & Trust)

**Implications**:
- **For Product**: Address all trust dimensions explicitly; build features that demonstrate trustworthiness
- **For Design**: Make security practices visible; show data sources; explain AI; clarify business model
- **For Strategy**: "Radically transparent" positioning; earn trust through practices, not marketing

**Related Features**:
- Security Transparency Dashboard
- Data Source Indicators
- AI Explainability Features
- Business Model Clarity Page

---

### Insight 21: Health Information Is a Credibility Tool in Power Dynamics

**Category**: Mental Model
**Confidence**: 🟡 Medium
**Validated**: Sept-Oct 2025 via interviews (n=6)

**What We Learned**:
Patients—especially women and marginalized groups—use comprehensive documentation strategically to establish credibility with dismissive providers. Information isn't just about knowing; it's about being believed. Well-organized health records serve as evidence that the patient "knows what they're talking about" and deserves to be taken seriously.

**Evidence**:
- "I feel that I'm patronized by the doctors because what do I know, right? What do I know about me?... it's it's just empowers me to be confident in going to my appointment... because it shows that I do know what I'm talking about and I think that's huge." — P08-MK
- "I worked with marginalized communities... multiple multiple um health related issues. And of course, their appearance was one of uh you know, one looked like a garden gnome. So, heaven forbid that we should treat him... unless that person had somebody to go in with them, they didn't get the care that they deserved." — P08-MK
- "I recognized that that was extremely helpful to me in being prepared for the kind of conversations I needed to be in." — P01-CH
- Source: Thematic Analysis Code 7.1 (Health Information as Credibility Tool)

**Implications**:
- **For Product**: Generate professional, credibility-establishing summaries; help users "look prepared"
- **For Design**: Provider-ready formatting (not patient-y); clear, concise, clinically-framed presentation
- **For Strategy**: Empowerment positioning for underserved groups; partnership with patient advocacy orgs

**Related Features**:
- Professional Summary Generator
- Provider-Ready Formatting
- Chief Concern Framing
- Clinical Presentation Templates

---

### Insight 22: AI Acceptance Is Task-Specific, Not General

**Category**: Mental Model
**Confidence**: 🟢 High
**Validated**: Sept-Oct 2025 via interviews (n=14)

**What We Learned**:
Users make nuanced, task-specific decisions about AI appropriateness. They're comfortable with AI for bounded tasks (summarization, literature search, trend visualization) but uncomfortable with AI for judgment tasks (diagnosis, treatment decisions, relationship mediation). "AI-assisted" is acceptable; "AI-automated" is not.

**Evidence**:
- "Because I would like to do the organization myself. It helps me think think things through. But if AI can dig into the biomedical literature that's peer-reviewed and offer me citations... but just having AI do a keyword search and like lumping my symptoms together um would not be useful." — P11-RM
- "I think that the challenge with AI is that it's garbage in garbage out." — P06-OV
- "Um, I probably wouldn't use the AI assistant just cuz I I don't know why I'm still sometimes like just not sure about it." — P05-MB
- "I use chat and VT every day for my own business... I think AI is definitely a a really great tool and we're just going to see more and more of it moving forward." — P13-MM
- Source: Thematic Analysis Code 4.1 (AI Skepticism & Concerns)

**Implications**:
- **For Product**: Task-specific AI deployment; never auto-act on AI recommendations; human-in-loop always
- **For Design**: Granular AI consent (accept for summarization, decline for recommendations); clear accuracy indicators; editable outputs
- **For Strategy**: Position as "AI-assisted" not "AI-powered"; focus AI on tasks with user acceptance

**Related Features**:
- Task-Specific AI Consent
- AI Accuracy Disclosure
- Editable AI Outputs
- AI Explanation Features

---

# CATEGORY: TECHNOLOGY ATTITUDES

---

### Insight 23: Security Concerns Are Real But Balanced With Pragmatic Resignation

**Category**: Technology Attitude
**Confidence**: 🟢 High
**Validated**: Sept-Oct 2025 via interviews (n=14)

**What We Learned**:
Nearly every participant expressed security concerns, from mild wariness to deep anxiety. However, most have reached pragmatic acceptance that "everything gets hacked" while still wanting protection and control. They want to see security efforts, not be told "trust us."

**Evidence**:
- "I'm hyper concerned about security but that's just who I am... I'm also perfectly aware that there's nothing that's secure... everything's been hacked and everything will continue to be hacked." — P06-OV
- "I am an actuary so I know what an insurance company would say about having my cases that would basically be off of their chart." — P04-JC (insurance discrimination concern)
- "it could be used against consumers in the future, right? to up your rates for health insurance, to reject you for life insurance." — P11-RM
- "I just worry about security and confidentiality... and you know and personal information." — P10-MT
- Source: Thematic Analysis Code 4.2 (Security & Privacy Concerns)

**Implications**:
- **For Product**: Visible security practices; audit logs; encryption indicators; breach notification commitment
- **For Design**: "Who accessed my data" dashboard; clear privacy controls; no hidden data sharing
- **For Strategy**: Security as table stakes AND differentiator; exceed HIPAA, don't just meet it

**Related Features**:
- Access Audit Log
- Encryption Transparency
- Privacy Control Dashboard
- Security Practices Page

---

### Insight 24: Users Question Platform Business Models and Data Use

**Category**: Technology Attitude
**Confidence**: 🟡 Medium
**Validated**: Sept-Oct 2025 via interviews (n=8)

**What We Learned**:
Users are savvy about data-as-product business models and explicitly question what happens to their health data. They want transparency about costs, data use, and long-term platform viability. "Free" makes them suspicious; clear value exchange makes them trust.

**Evidence**:
- "I would want to know like what is the value ad? Um, even as a user, I kind of want to understand what your business model is. Like, is your business model just taking information from me and training your AI like am I your content?" — P11-RM
- "I guess I'd wonder how much is it going to cost me? is there going to be a fee for this or is it going to be free?" — P09-JC
- "That would be my only concern. Um is just who has access to it other than myself, right?... I don't want to like know if that my health records are being sold to like you know pharmaceutical companies." — P14-PS
- "I've had several incidences in which the hospital system that I was using, they updated their electronic medical records and some of my previous test results could not be found." — P11-RM (platform migration anxiety)
- Source: Thematic Analysis Code 4.5 (Platform Trust & Business Model Concerns)

**Implications**:
- **For Product**: Transparent pricing; explicit data use policy; data portability guarantee
- **For Design**: Clear business model explanation in non-legal language; "how we make money" page
- **For Strategy**: Freemium with clear value tiers; "never sell your data" commitment

**Related Features**:
- Pricing Transparency Page
- Data Use Policy (Plain Language)
- Data Export Feature
- Business Model Explanation

---

### Insight 25: Elderly Users Need Radically Simplified Interfaces

**Category**: Technology Attitude
**Confidence**: 🟢 High
**Validated**: Sept-Oct 2025 via interviews (n=7 caring for elderly)

**What We Learned**:
Elderly users (and caregivers designing for them) need interfaces that go far beyond standard accessibility: plain language over clinical terms, "friendly" not "clinical" feel, pictures and symbols, drastically simplified navigation, and minimal authentication barriers. Many elderly users are capable but easily overwhelmed by complexity.

**Evidence**:
- "um easy uh as in um finding the information by maybe having it um very worded very easily for regular people. Um, and maybe even more specifically for the things that elderly people deal with." — P03-CM
- "But she's 84 and even though I think she's actually pretty good with an iPhone that it cuz I think it's asking her to um log in with her BC services card and then she's like I don't know what that is." — P07-CC
- "I think for a senior it would be really difficult... just from my experience with them, they find working on the computer quite difficult." — P13-MM
- "Well, like pictures, you know, that's always an interesting way to do it. I think for older people that might be a good idea." — P03-CM
- Source: Thematic Analysis Code 5.2 (Accessibility for Elderly Users)

**Implications**:
- **For Product**: Simple/standard/detailed mode options; elderly-specific onboarding; caregiver-assisted setup
- **For Design**: Large defaults; minimal steps; visual wayfinding; plain language everywhere
- **For Strategy**: Elderly users as distinct segment, not afterthought; caregiver-mediated adoption pathway

**Related Features**:
- Simplified Mode
- Large Text Default
- Plain Language Interface
- Caregiver Setup Assistance

---

### Insight 26: Device Preferences Are Heterogeneous and Context-Dependent

**Category**: Technology Attitude
**Confidence**: 🟡 Medium
**Validated**: Sept-Oct 2025 via interviews (n=14)

**What We Learned**:
Users have diverse device preferences—some want phone (portability, always available), some want desktop (larger screen, serious tasks), some want paper (cognitive preference, comfort). These preferences are also context-dependent: crisis situations favor phones; detailed review favors desktop; appointments may favor paper.

**Evidence**:
- "I I felt like I was just surviving... the phone was the thing I had reliably with me so that ability to kind interface on the phone would have been kind of critical." — P01-CH (crisis context)
- "I use it on my on my um desktop... Yeah. Mostly on your desktop is a preference versus on your on your phone." — P06-OV
- "I prefer things in paper... I think a binder would be much easier for me." — P15-GB
- "I do most of when I have to fill out the forms for physicians, I do them at home on my laptop. Screen is bigger." — P10-MT
- Source: Thematic Analysis Code 5.4 (Device & Access Preferences)

**Implications**:
- **For Product**: True multi-platform support; high-quality print outputs; context-appropriate feature parity
- **For Design**: Mobile-first for quick access; desktop optimization for complex tasks; printable views
- **For Strategy**: Multi-modal access as differentiator vs. mobile-only or desktop-only competitors

**Related Features**:
- Responsive Web Design
- High-Quality Print Outputs
- Mobile Quick-Access Mode
- Desktop Full-Feature Mode

---

# CATEGORY: POSITIVE SIGNALS

---

### Insight 27: Strong Positive Reception to Consolidated Health Record Concept

**Category**: Positive Signal
**Confidence**: 🟢 High
**Validated**: Sept-Oct 2025 via prototype feedback (n=14)

**What We Learned**:
Participants responded enthusiastically to the concept of a consolidated personal health record, with multiple expressing strong interest in adoption. This validates the core value proposition—users want this solution.

**Evidence**:
- "Perfect. I think you're on the right track. I would like to have a system like that." — P04-JC
- "Um, I'm I'm impressed. I I like it." — P03-CM
- "I think it's a brilliant idea... I can't see any... Oh, yeah. I definitely I [would use it]." — P08-MK
- "I think it's really I think it's really user friendly." — P13-MM
- "It's set up it's set up really nice. It's easy to use. It doesn't, you know, you even if you're not someone that's comfortable with computers, it seems very easy to use." — P14-PS
- Source: Thematic Analysis Code 5.3 (Positive Product Reception)

**Implications**:
- **For Product**: Core concept validated; focus on execution not concept pivot
- **For Design**: Current direction resonating; refine rather than reinvent
- **For Strategy**: Market exists and recognizes value; focus on differentiation and trust-building

**Related Features**: All core features

---

### Insight 28: Users Value Provider Relationships and Human Connection

**Category**: Positive Signal
**Confidence**: 🟢 High
**Validated**: Sept-Oct 2025 via interviews (n=14)

**What We Learned**:
Despite frustrations with healthcare systems, users deeply value human connection with providers. They want technology to support, never replace, these relationships. Tools that might degrade relationship quality face rejection; tools that enhance relationships face acceptance.

**Evidence**:
- "But I have to say, I also really value those conversations and I valued those conversations with my mom's providers. And honestly, I wouldn't do anything that would get in between me and those phone conversations with the providers." — P01-CH
- "Not emails... It's in person, but since co there was a little bit more telephone calls. but if it is more of a serious nature, I want to see their eyes." — P04-JC
- "I could just imagine feeling really more alone than anything filling this out... I just want to talk to somebody." — P01-CH
- "We want providers to be spending more of their time actually caring for the patient." — P08-MK
- Source: Thematic Analysis Code 3.1 (Value of Human Connection)

**Implications**:
- **For Product**: Never position as replacing provider conversations; always frame as enabling better conversations
- **For Design**: "Prepare for your appointment" not "skip your appointment"; human-centered language
- **For Strategy**: Provider partnership messaging; dual value proposition (helps patients AND providers)

**Related Features**:
- Appointment Preparation (not replacement)
- Provider Summary Sharing
- Communication Enhancement Tools

---

### Insight 29: Users With Healthcare Professional Experience Navigate Better

**Category**: Positive Signal (for design direction)
**Confidence**: 🟡 Medium
**Validated**: Sept-Oct 2025 via interviews (n=6 with healthcare experience)

**What We Learned**:
Participants with healthcare professional experience (former medical office staff, health informatics researchers, clinical scientists, senior care advocates) navigate healthcare systems more effectively. This validates that the core challenge is system complexity and literacy, not inherent difficulty—and that tools reducing complexity can help everyone.

**Evidence**:
- "I was a receptionist at a multi-physician family doctor's office for two different offices... I was aware of that issue with doctor's offices talking to each other." — P02-HS
- "having worked in healthcare definitely empowers me to advocate for myself more than the average patient... I was a scientist at NIH." — P11-RM
- "I am a retired faculty member from the Bey School of Business where my area of interest and teaching and research was information systems... my research topics were on in uh health informatics." — P06-OV
- "my business is I'm a a healthcare or I'm sorry, I'm a uh advocate for seniors to help them with uh life transitions." — P13-MM
- Source: Thematic Analysis Code 6.5 (Healthcare System Literacy)

**Implications**:
- **For Product**: Build tools that give everyone "insider knowledge"; democratize healthcare navigation
- **For Design**: Embed system literacy education in context; explain "why" behind recommendations
- **For Strategy**: Equity positioning—serve those without professional healthcare connections

**Related Features**:
- Healthcare System Education
- Contextual Navigation Guidance
- "Why This Matters" Explanations

---

## Archived Insights

*No insights archived yet. Insights will be moved here when invalidated, outdated, or fully incorporated.*

---

## Research Backlog

Questions requiring further investigation:

### High Priority
- [ ] **Provider reception to patient-generated summaries** — Will providers actually use them? Do they find them helpful or threatening? — Method: Provider interviews (n=10-15)
- [ ] **Caregiver willingness to pay** — What's actual WTP for coordination tools? — Method: Pricing study with caregiver segment
- [ ] **Elderly user independent adoption** — Can elderly users adopt without caregiver help? — Method: Usability testing with 70+ users without tech support

### Medium Priority
- [ ] **Cross-border data migration friction** — What are actual barriers to interprovincial/international records transfer? — Method: Process documentation with recent movers
- [ ] **Diagnostic odyssey patterns** — How common are multi-year diagnostic journeys? What triggers them? — Method: Quantitative survey with chronic illness community
- [ ] **AI feature usage patterns** — Which AI features actually get used? Which get disabled? — Method: Usage analytics post-launch

### Low Priority
- [ ] **Provider portal proliferation** — How many portals does average patient have? — Method: Survey
- [ ] **Paper-to-digital conversion barriers** — What stops users from digitizing historical records? — Method: Workflow observation

---

## Insight Changelog

| Date | Insight | Change | Reason |
|------|---------|--------|--------|
| Nov 23, 2025 | All | Initial population | Qualitative study completion |

---

## By Feature Area

Quick reference for finding relevant insights:

### Onboarding
- [Insight #14]: Users create manual tracking systems — import existing work
- [Insight #25]: Elderly users need simplified interfaces
- [Insight #19]: Users think of health as stories — story-based onboarding

### Data Aggregation & Integration
- [Insight #1]: Users want aggregated data, not another portal
- [Insight #7]: Accessing records is difficult and delayed
- [Insight #9]: Providers don't communicate with each other
- [Insight #14]: Users create manual tracking systems

### Timeline & Visualization
- [Insight #3]: Users want timeline/visual organization
- [Insight #19]: Users think of health as stories
- [Insight #11]: Diagnostic journeys need tracking

### Caregiver Features
- [Insight #2]: Caregivers need purpose-built coordination tools
- [Insight #16]: Caregivers reconstruct histories from fragments
- [Insight #18]: Users bring support people to appointments

### AI Features
- [Insight #8]: Information overload prevents action — AI summaries valuable
- [Insight #15]: Users actively use ChatGPT for healthcare
- [Insight #22]: AI acceptance is task-specific
- [Insight #27]: Users want AI with human verification

### Privacy & Sharing
- [Insight #5]: Users need control over what shares with whom
- [Insight #17]: Users strategically withhold information
- [Insight #23]: Security concerns balanced with pragmatism
- [Insight #24]: Users question business models

### Provider Communication
- [Insight #4]: Users need appointment preparation support
- [Insight #6]: Repetitive information provision causes frustration
- [Insight #10]: Time constraints lead to dismissiveness
- [Insight #21]: Health information as credibility tool
- [Insight #28]: Users value human connection with providers

### Safety Features
- [Insight #12]: ⚠️ Medication errors occur at handoffs
- [Insight #13]: ⚠️ Post-diagnosis support is absent
- [Insight #10]: ⚠️ Time constraints lead to dismissiveness

### Trust & Adoption
- [Insight #20]: Trust is multi-dimensional
- [Insight #23]: Security concerns are real but pragmatic
- [Insight #24]: Users question business models
- [Insight #27]: Strong positive reception to concept

### Accessibility
- [Insight #25]: Elderly users need radically simplified interfaces
- [Insight #26]: Device preferences are heterogeneous

---

## Insight Validation Framework

How we determine confidence levels:

### 🟢 High Confidence
- Observed across 8+ participants (>50% of sample)
- Consistent pattern across different participant types
- Low contradictory evidence
- Low risk if we act on it

### 🟡 Medium Confidence
- Observed in 3-7 participants (20-50% of sample)
- Some supporting patterns but also variation
- May need more validation before major investment

### 🔴 Low Confidence
- Observed in 1-2 participants
- Contradictory evidence exists
- Hypothesis stage—needs testing before acting

---

## Related Resources

- [Research Codebook](/research/thrive_codebook_v1_final.md): Full thematic analysis codebook
- [Narrative Synthesis](/research/thrive_research_narrative_synthesis.md): Qualitative analysis report
- [Product Strategy](/strategy/product-strategy.md): How insights inform strategy
- [Feature Docs](/features/): PRDs that reference these insights
