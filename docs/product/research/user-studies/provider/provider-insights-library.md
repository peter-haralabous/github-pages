# Provider Insights Library

**Purpose**: Centralized repository of key learnings from healthcare provider research
**Last Updated**: November 2024
**Owner**: UX Research Team
**Primary Source**: Provider Interview Study (n=22)

---

## How to Use This Library

This library captures:
- **Patterns** observed across multiple providers/specialties
- **Validated hypotheses** we can build on
- **Invalidated assumptions** we should avoid
- **Surprising findings** that change our thinking

**When to add**:
- After completing provider or patient research studies
- When usage data reveals patterns
- When customer feedback clusters around themes

**How to use**:
- Reference when writing PRDs
- Validate feature ideas against known provider needs
- Share with new team members for context
- Ground product decisions in authentic user voices

---

## Active Insights

Insights currently shaping our roadmap, organized by category.

---

# Category: User Needs

---

### Insight 1: Providers need pre-visit data synthesis, not just documentation help

**Category**: User Need
**Confidence**: 🟢 High
**Validated**: November 2024 via provider interviews (n=22)

**What We Learned**:
Providers spend 2-30+ minutes per patient on "chart archaeology"—clicking through multiple systems, opening and closing windows, synthesizing fragmented information—before they even see the patient. Current AI tools (scribes) help with post-visit documentation but don't address this pre-visit preparation burden, which is where complex patients create the most time pressure.

**Evidence**:
- "Pre-prescribed, I probably spent sometimes 10 to 15 minutes for a complex case. If it's here in the hospital, it can be as long as half an hour sometimes—clicking on Cerner and clicking on Care Connect, opening, closing, opening, closing." - P4, Internal Medicine
- "The nurse will spend an hour or so on that. I will have the encounter time which will be 30 to 40 minutes with the patient plus I might do 20 minutes of prep. So I could easily round that up to an hour." - P2, Family Medicine
- "If they're a cancer patient and I want to see what they've had so far for their cancer treatment, then I'm pulling up old notes, the chemo notes, the radiation notes... so that one, maybe 10 minutes." - P1, Emergency Medicine
- 18 of 22 participants described significant pre-visit preparation time
- Source: Provider Interview Study, Codebook Theme 1.1

**Implications**:
- **For Product**: Pre-visit synthesis is unaddressed market opportunity; AI scribes focus on post-visit
- **For Design**: Complexity-adaptive summaries that scale depth to patient complexity
- **For Strategy**: Differentiate on preparation (pre-visit) rather than documentation (post-visit)

**Related Features**:
- [Pre-Visit Summary Generation]
- [Multi-Source Data Aggregation]
- [Complexity-Adaptive Views]

---

### Insight 2: Providers require source attribution to trust AI-generated content

**Category**: User Need
**Confidence**: 🟢 High
**Validated**: November 2024 via provider interviews (n=22)

**What We Learned**:
Providers will not accept AI summaries as authoritative. They need to trace every claim back to its source document to verify accuracy and maintain professional accountability. The ability to hover/click and see "where did this come from" is described as essential, not optional.

**Evidence**:
- "Basically everything is almost annotated where you could hover over it, right click on it, and say 'where did this come from' and it will link you to the initial PDF... Clinicians will really, really want that." - P12, Preventive Health
- "People for the majority like it when I use Open Evidence—I do feel reassured that it cites its sources at the bottom." - P1, Emergency Medicine
- "Clinicians will want to know—was this self-reported on an intake Q&A or was this from a referral letter?" - P12, Preventive Health
- All 22 participants expressed verification requirements; source attribution cited as trust-builder
- Source: Provider Interview Study, Codebook Theme 2.4

**Implications**:
- **For Product**: Source attribution is table stakes, not a differentiator—but depth of attribution can differentiate
- **For Design**: Claim-level attribution (not just document-level); progressive disclosure from summary to source
- **For Strategy**: Position as "AI that helps you know what to trust" rather than "accurate AI"

**Related Features**:
- [Claim-Level Source Attribution]
- [Hover-to-Verify Interface]
- [Provenance Tracking]

---

### Insight 3: Providers need deep customization by specialty, practice model, and personal preference

**Category**: User Need
**Confidence**: 🟢 High
**Validated**: November 2024 via provider interviews (n=22)

**What We Learned**:
Healthcare is not monolithic. An orthopedic surgeon needs bleeding/clotting risk; a cardiologist needs cardiovascular depth; a physiotherapist needs only imaging reports. Beyond specialty, individual providers have idiosyncratic preferences developed over years. One-size-fits-all solutions are explicitly rejected.

**Evidence**:
- "An orthopedic surgeon might want to know only about whether this person has a bleeding or clotting problem, right? But a cardiologist is going to want to know something very different." - P8, Urology
- "I don't need the full health history. I just literally need access to this singular image." - P5, Allied Health
- "In certain areas I asked it to go deeper with second-order questions. In certain areas like the past psychiatric history, I wasn't that keen on knowing that much information." - P15, Urology
- "The ones that I would have there would be like a simple summary, an everything summary, a consultation request summary, and probably like a transfer summary." - P23, Specialist
- 19 of 22 participants described specialty-specific or personal customization needs
- Source: Provider Interview Study, Codebook Theme 5

**Implications**:
- **For Product**: Build fundamentally configurable architecture; specialty templates as starting points
- **For Design**: Configurable question depth, information priority, and output format per user
- **For Strategy**: Customization depth as competitive moat against generic solutions

**Related Features**:
- [Specialty Templates]
- [Configurable Question Trees]
- [Custom Summary Formats]
- [Provider Learning/Adaptation]

---

### Insight 4: Providers want AI that learns from their corrections over time

**Category**: User Need
**Confidence**: 🟡 Medium
**Validated**: November 2024 via provider interviews (n=8 who discussed AI learning)

**What We Learned**:
Several providers described experimenting with training AI on their own clinical patterns (uploading voice files, correcting outputs). They want a feedback loop where corrections improve future performance—"if I then take the corrected transcript and put it back in and say this is more correct, learn from it."

**Evidence**:
- "What would be useful is that last feedback loop... if I were to then take the corrected transcript and put it back in and say this is more correct than what you gave me, learn from it. And then it would modify the next time it puts out outputs." - P15, Urology
- "I started to tap on the new natural language in ChatGPT and what I did was I took 10 interviews that I did with patients, removed the patient demographics, and I uploaded the voice files to chat. And I asked it to sort of learn from that." - P15, Urology
- "I want the agent to learn that in meet and greet, Alli cares about these things." - P19, Emergency Medicine
- Source: Provider Interview Study, Codebook Theme 3.5

**Implications**:
- **For Product**: Build correction capture and model personalization infrastructure
- **For Design**: Make corrections easy; show when system has learned from feedback
- **For Strategy**: Personalization through use creates switching costs and defensibility

**Related Features**:
- [Correction Feedback Loop]
- [Provider-Specific Model Tuning]
- [Learning Indicators]

---

### Insight 5: Providers need unified access to fragmented patient data across systems

**Category**: User Need
**Confidence**: 🟢 High
**Validated**: November 2024 via provider interviews (n=22)

**What We Learned**:
Patient information exists in silos—family doctor EMRs, specialist practices, hospital systems, community radiology, allied health platforms. Providers describe a vision where patient data accumulates across touchpoints and follows the patient, accessible to any provider with consent. Current reality falls far short.

**Evidence**:
- "I feel like the optimal area to start with is just like helping people get it all in one place. That's it." - P21, Preventive Health
- "Once we've got a patient, we can continue to add data over time... that profile starts getting bigger and bigger about that patient. That's the vision anyways." - P22, Rheumatology
- "This is one of the biggest bug bears in medicine—access to information, efficient use of medical information, communicating. It's where a lot of mistakes happen." - P20, Family Medicine
- "Obviously, we don't have access to their family doctor's office. We don't know what their rheumatologist told them last time because these are all in private offices." - P19, Emergency Medicine
- 20 of 22 participants described data fragmentation challenges
- Source: Provider Interview Study, Codebook Theme 4

**Implications**:
- **For Product**: Position as aggregation layer, not replacement system; accept documents from any source
- **For Design**: Unified views that synthesize across sources; clear source labeling
- **For Strategy**: Patient-mediated aggregation may be faster path than provider-system integration

**Related Features**:
- [Multi-Source Document Upload]
- [AI Extraction and Synthesis]
- [Patient-Portable Records]

---

# Category: Pain Points

---

### Insight 6: Verification time may negate AI efficiency gains ("trust tax")

**Category**: Pain Point
**Confidence**: 🟢 High
**Validated**: November 2024 via provider interviews (n=22)

**What We Learned**:
Providers are skeptical that AI tools actually save time once verification requirements are accounted for. They must review AI output to maintain professional accountability, and this "trust tax" may partially or fully offset efficiency gains. This skepticism is a significant adoption barrier.

**Evidence**:
- "Because to me, me reading through this will also cut into any minimal time that's saved, right?" - P5, Allied Health
- "It definitely needs to be checked though. I definitely have to read through that consult note to make sure that it's accurate." - P9, Plastic Surgery
- "You start to develop a bit of complacency as a physician because you assume the AI has captured everything and it's presented it correctly and you don't read through the note as carefully and things can get missed." - P10, Internal Medicine
- "There might still be gaps where we still have to probe." - P5, Allied Health
- 17 of 22 participants expressed verification requirements or time skepticism
- Source: Provider Interview Study, Codebook Themes 1.7, 2.2

**Implications**:
- **For Product**: Design for efficient targeted verification, not comprehensive review
- **For Design**: Highlight uncertain claims; enable quick verification of specific elements
- **For Strategy**: Demonstrate NET time savings including verification; transparent ROI calculation

**Related Features**:
- [Uncertainty Indicators]
- [Quick-Verify Workflows]
- [Time Savings Dashboard]

---

### Insight 7: Copy-paste workflows persist despite friction because integration is worse

**Category**: Pain Point
**Confidence**: 🟢 High
**Validated**: November 2024 via provider interviews (n=22)

**What We Learned**:
Providers accept copy-paste between AI tools and EMRs as "good enough" integration. Direct EMR integration would be better in theory, but the barriers (vendor cooperation, security, approval processes) make copy-paste the practical reality. Successful tools optimize for this workflow rather than fighting it.

**Evidence**:
- "There isn't yet a direct link into our EMR, so we have to copy and paste it, but that is not hard." - P13, Family Medicine
- "What would be ideal is it should have a final transcript I can just copy and paste." - P15, Urology
- "So it's weird because sometimes it does it perfectly and then other times it'll output with asterisks and dash lines in places that I don't even know and I've got to physically correct." - P18, Rheumatology
- AI scribe adoption is high despite copy-paste requirement; value outweighs friction
- Source: Provider Interview Study, Codebook Theme 3.2, 3.7

**Implications**:
- **For Product**: Optimize copy-paste experience; don't gate value on EMR integration
- **For Design**: Format-aware output optimized for target EMR; one-click clean copy
- **For Strategy**: Copy-paste optimization is faster path to value than integration partnerships

**Related Features**:
- [EMR-Aware Formatting]
- [One-Click Copy]
- [Format Consistency]

---

### Insight 8: Referral system inefficiencies create cascading delays and information loss

**Category**: Pain Point
**Confidence**: 🟢 High
**Validated**: November 2024 via provider interviews (n=14 who discussed referrals)

**What We Learned**:
Family physicians often send 4-5 referrals before one is accepted by a specialist with capacity. There's no feedback loop, limited GP-specialist communication, and information is lost at each handover. Patients wait months without knowing if they're even on a waitlist.

**Evidence**:
- "The family doctor has to send like four or five referrals until one gets accepted by a specialist... You wait until the specialist will fax you back saying rejected. My waitlist is too long." - P6, Emergency Medicine
- "Family doctors can't really call a specialist to get a same day answer. That really only happens in the hospital system." - P6, Emergency Medicine
- "Patients now get nothing. You don't even know if you're on a wait list. Someone will say, 'I've referred you to someone.' And you literally have no idea if the referral went through." - P23, Specialist
- Wait times mentioned: 9 months, "booking into late October"
- Source: Provider Interview Study, Codebook Theme 1.6

**Implications**:
- **For Product**: Waitlist engagement is high-value opportunity; communicate with patients while waiting
- **For Design**: Status visibility for patients; triage support for specialists
- **For Strategy**: "While you wait" engagement creates value in broken referral system

**Related Features**:
- [Waitlist Patient Engagement]
- [Referral Status Tracking]
- [Pre-Appointment Data Collection]

---

### Insight 9: Allied health professionals face systematic access barriers to hospital systems

**Category**: Pain Point
**Confidence**: 🟡 Medium
**Validated**: November 2024 via allied health interviews (n=4)

**What We Learned**:
Physiotherapists and other allied health professionals cannot access hospital EMRs that physicians can access. They need specific pieces of information (like imaging reports) but lack system access, forcing reliance on patient-mediated information transfer.

**Evidence**:
- "I don't need the full health history. I just literally need access to this singular image, which EMRs in the hospitals—docs can just log into that EMR and pull that report out. If I could just have that ability, like from an allied health standpoint, I think if we could just get access to imaging reports, that would make us a lot happier." - P5, Allied Health
- "For a physician, they can get paid for referring for an X-ray. There's a billing code for that. We only have billing codes for actual direct 1:1 care." - P5, Allied Health
- Allied health relies on patients bringing records or informal workarounds
- Source: Provider Interview Study, Codebook Theme 4.5

**Implications**:
- **For Product**: Allied health is underserved market segment with specific, narrower needs
- **For Design**: Role-specific views showing only relevant information (imaging for physio)
- **For Strategy**: Allied health may be easier adoption path than physicians (less resistance, clearer pain)

**Related Features**:
- [Allied Health Specialty Views]
- [Imaging Report Access]
- [Role-Based Information Filtering]

---

### Insight 10: Fee-for-service billing doesn't compensate for AI-enabled workflow activities

**Category**: Pain Point
**Confidence**: 🟢 High
**Validated**: November 2024 via provider interviews (n=22)

**What We Learned**:
Providers cannot bill for reviewing patient forms, preparing for visits, or asynchronous communication. Fee-for-service pays only for face-to-face encounters. This creates structural disincentives for AI-enabled preparation and asynchronous care, regardless of clinical value.

**Evidence**:
- "I think the other practical consideration—how do you bill for that in a fee-for-service environment? There isn't really a fee code for reviewing emails from patients." - P13, Family Medicine
- "A lot of insurers are only paying for one-on-one client time, one-on-one face time... We only have billing codes for actual direct 1:1 care. From a MSP standpoint, we only have one billing code. That's $23 per visit." - P5, Allied Health
- "A lot of these things are driven by compensation models. Obviously, I want the best for my patient, but if their potassium is perfectly fine and I have another 50 lab workups to review... I want to spend the least amount of time because reviewing patient information one by one doesn't actually pay me." - P19, Emergency Medicine
- Source: Provider Interview Study, Codebook Theme 6.1

**Implications**:
- **For Product**: Design features that enable billing (asynchronous care codes) not just efficiency
- **For Design**: Integrate billing prompts; document billable activities automatically
- **For Strategy**: Revenue enablement is stronger value prop than time savings for some users

**Related Features**:
- [Asynchronous Care Workflows]
- [Billable Activity Documentation]
- [ROI Calculator]

---

# Category: Behaviors & Workarounds

---

### Insight 11: Patients serve as information couriers between disconnected providers

**Category**: Behavior / Workaround
**Confidence**: 🟢 High
**Validated**: November 2024 via provider interviews (n=22)

**What We Learned**:
Because provider systems don't communicate, patients physically carry their medical histories between appointments—through memory, family members, or paper documents. This is error-prone and burdens patients at vulnerable moments, but it's the practical workaround for system fragmentation.

**Evidence**:
- "Every time they come to hospital, it goes by their memory or their son-in-law who took them there and they're not here today." - P19, Emergency Medicine
- "If she had that where it was already done and ready and she could provide that information directly to her new doctor and take that everywhere she goes, that's fantastic." - P2, Family Medicine
- "From the end user side—the patient side—the incentive would be like hey you can upload basically all your data from this report and then if you're going to your next provider it's there." - P21, Preventive Health
- Patients bringing records mentioned by 15 of 22 participants
- Source: Provider Interview Study, Codebook Theme 9.4

**Implications**:
- **For Product**: Patient-mediated aggregation is existing behavior to enhance, not replace
- **For Design**: Easy patient upload (photos, PDFs); AI extraction that doesn't require patient categorization
- **For Strategy**: Build on existing patient behavior rather than requiring system-level change

**Related Features**:
- [Patient Document Upload]
- [Photo-to-Record OCR]
- [Patient-Controlled Sharing]

---

### Insight 12: Providers experiment with consumer AI to fill gaps in healthcare tools

**Category**: Behavior / Workaround
**Confidence**: 🟡 Medium
**Validated**: November 2024 via provider interviews (n=6 who described experiments)

**What We Learned**:
Several providers described using ChatGPT for clinical tasks—training it on their interview patterns, using voice features for patient conversations, looking up guidelines. This reveals both the gap in current healthcare tools and the risk of providers using non-compliant consumer tools for clinical work.

**Evidence**:
- "I started to tap on the new natural language in ChatGPT and what I did was I took 10 interviews that I did with patients, removed the patient demographics, and I uploaded the voice files to chat. And I asked it to sort of learn from that." - P15, Urology
- "It was really cool to toy around with it and the natural language selection was just kind of cool way to integrate that into my history taking." - P15, Urology
- "I had a dog bite the other day in the emerge. So I couldn't quite remember the rabies guidelines... so I used it to look up guidelines." - P1, Emergency Medicine
- Source: Provider Interview Study, Codebook Themes 3.5, 3.9

**Implications**:
- **For Product**: Healthcare tools must match or exceed consumer AI capabilities to prevent workarounds
- **For Design**: Voice interfaces, learning/personalization, clinical knowledge—features providers seek in ChatGPT
- **For Strategy**: Compliance + consumer-grade experience is the winning combination

**Related Features**:
- [Voice Interface]
- [Clinical Guideline Integration]
- [Provider Learning/Personalization]

---

### Insight 13: Multi-tool orchestration is manual and cognitively demanding

**Category**: Behavior / Workaround
**Confidence**: 🟢 High
**Validated**: November 2024 via provider interviews (n=22)

**What We Learned**:
Providers juggle multiple tools (EMR, AI scribe, booking system, forms platform, imaging archives) with no coordination between them. They mentally track what information is in which system and manually transfer between them. This creates cognitive load beyond the mechanical burden of data entry.

**Evidence**:
- "My MOA sets up an encounter, uploads the referral letter, and then also uploads any other stuff that's come along with that, like investigations, but then also the PDF that the Thrive produces, and then the AI program sort of scans that stuff." - P14, Plastic Surgery
- "For me to have access to outpatient reports and imaging, I have to actually separately log into every single one of their PACs. Sometimes they're like, 'I had an X-ray, where was it?' It was in Coquitlam. Well, there's three of them in Coquitlam. So you know that takes like 17 minutes of my time." - P17, Emergency Medicine
- "If they're booking online, we use the Jane app software... we are very much a Jane facilitated clinic." - P5, Allied Health
- Source: Provider Interview Study, Codebook Theme 3.8

**Implications**:
- **For Product**: Workflow awareness—understand the multi-tool context, not just single-tool tasks
- **For Design**: Reduce context-switching; aggregate information from multiple sources in one view
- **For Strategy**: "Orchestration layer" positioning that coordinates existing tools

**Related Features**:
- [Multi-Source Aggregation]
- [Workflow Context Awareness]
- [Unified Dashboard]

---

# Category: Mental Models

---

### Insight 14: Providers trust presence of information but not its absence ("conditional trust")

**Category**: Mental Model
**Confidence**: 🟢 High
**Validated**: November 2024 via provider interviews (n=22)

**What We Learned**:
Providers apply asymmetric trust to health data. If a system says a patient has diabetes, they accept this. But if a system shows no allergies, they still ask the patient—absence of documentation doesn't mean documented absence. This conditional trust pattern has profound implications for how AI should present information.

**Evidence**:
- "If there is pertinent positive information in Care Connect and it's fed to me, that's useful. Yes, I would use that. However, if it was absent, I wouldn't rely upon that being the truth... If it's fed to me and it's there, then I consider that the truth. But if it's not there, I don't assume it not to be there." - P8, Urology
- "I don't trust the patient for the direct data, but if they said they had a PSA done last year, then I will take that information and search it out." - P7, Urology
- "If they on history say, 'I have diabetes.' Yeah, I take that for face value that they have diabetes." - P7, Urology
- Source: Provider Interview Study, Codebook Theme 2.6

**Implications**:
- **For Product**: Distinguish between "documented" and "not documented" rather than asserting presence/absence
- **For Design**: Visual differentiation: confirmed present, confirmed absent, not documented (unknown)
- **For Strategy**: Epistemological precision is trust-builder; confident assertions of absence are dangerous

**Related Features**:
- [Three-State Data Display]
- [Uncertainty Visualization]
- [Documentation Status Indicators]

---

### Insight 15: Clinical information needs are context-dependent, not static

**Category**: Mental Model
**Confidence**: 🟢 High
**Validated**: November 2024 via provider interviews (n=22)

**What We Learned**:
The same provider needs different information depending on the care context. Emergency visits need rapid-scan summaries; first consultations need comprehensive history; follow-ups need change highlights. Providers don't think in terms of "complete patient record" but "what do I need for THIS encounter."

**Evidence**:
- "When you do get called out or when you do see someone in emerg, gaining access to all of their data can be a real challenge in an emergency setting." - P7, Urology
- "A follow-up visit is typically 10 or 15 minutes. It's often on the phone. And you have to in that time get the history, sort out what they've done, go through the results, formulate a plan." - P25, Rheumatology
- "If I'm building a relationship with someone, the first few sessions need to be the impactful sessions, need to be in person." - P19, Emergency Medicine
- Different time pressures: emergency (minutes), follow-up (10-15 min), initial consult (30-60 min)
- Source: Provider Interview Study, Codebook Theme 8

**Implications**:
- **For Product**: Context-adaptive views that automatically adjust to encounter type
- **For Design**: Emergency mode vs. comprehensive mode vs. follow-up mode
- **For Strategy**: Context-awareness as differentiator against static-view competitors

**Related Features**:
- [Encounter Type Detection]
- [Context-Adaptive Summaries]
- [Follow-Up Change Highlighting]

---

### Insight 16: Clinical conversation follows branching logic, not linear form completion

**Category**: Mental Model
**Confidence**: 🟡 Medium
**Validated**: November 2024 via provider interviews (n=12 who discussed clinical questioning)

**What We Learned**:
Providers don't ask standardized questions in fixed order. They follow branching logic—if a patient says "yes" to heart disease, they probe for type, treatment, anticoagulation. This clinical reasoning is lost in static forms, which capture answers but not the adaptive depth that reveals clinical nuance.

**Evidence**:
- "I fed it some more second-order and tertiary-order questions. So for example, if you ask the patient, 'Have you had any heart disease?' and they say yes, then you're prompted to ask further questions. If they say they've had atrial fibrillation, then I want you to ask further about anticoagulation and rate control." - P15, Urology
- "Like I don't ask all these questions to a patient. I take a whole bunch of information and then like go down paths, right?" - P27, Surgery
- "Do you actually have symptoms all the time or do they come and go? Because people say, 'Oh, I have symptoms all the time,' but 'Oh, I have about two hours during the day where I don't have symptoms.' So there's a little bit of that... the extra nuance." - P9, Plastic Surgery
- Source: Provider Interview Study, Codebook Theme 7.7

**Implications**:
- **For Product**: Conversational AI intake with configurable branching logic, not static forms
- **For Design**: Visual representation of conversation depth; configurable "go deep" vs. "stay shallow" areas
- **For Strategy**: True clinical conversation capability is rare in market; major differentiator

**Related Features**:
- [Branching Conversation Trees]
- [Configurable Question Depth]
- [Nuance Detection]

---

# Category: Feature Preferences

---

### Insight 17: Voice interfaces are promising but current implementations frustrate

**Category**: Feature Preference
**Confidence**: 🟡 Medium
**Validated**: November 2024 via provider interviews (n=6 who discussed voice AI)

**What We Learned**:
Providers experimenting with voice AI are enthusiastic about the modality but frustrated by current implementations—lag, mid-conversation stops, unnatural prompting ("I'm going to ask you a second-order question now"), tempo mismatches. The potential is clear but execution must improve.

**Evidence**:
- "It lagged a bit and that was frustrating because it didn't have the same tempo that I would have with a patient. Sometimes it would require a prompt to continue midway through a history taking, sometimes it would lag, sometimes just stop doing it." - P15, Urology
- "If I corrected it and I said 'okay ask a second order question' it would say 'okay I'm going to ask you a second order question now'—things like that. Normally as a physician you would just naturally do it." - P15, Urology
- "It was kind of cool and it sounded very realistic because it's natural language." - P15, Urology (enthusiasm despite frustrations)
- Source: Provider Interview Study, Codebook Theme 3.9

**Implications**:
- **For Product**: Voice is emerging modality worth investment; tempo and naturalness are critical
- **For Design**: Match clinical conversation rhythm; avoid meta-commentary; handle interruptions gracefully
- **For Strategy**: Healthcare-grade voice AI is a significant technical and UX challenge; potential differentiator

**Related Features**:
- [Voice Interface]
- [Natural Conversation Flow]
- [Tempo Matching]

---

### Insight 18: Providers want multiple summary formats for different purposes

**Category**: Feature Preference
**Confidence**: 🟢 High
**Validated**: November 2024 via provider interviews (n=22)

**What We Learned**:
No single summary format serves all needs. Providers described wanting simple summaries (brief overview), comprehensive summaries (everything), consultation request summaries (for referrals), and transfer summaries (for care transitions). The same underlying data needs different presentations for different audiences and purposes.

**Evidence**:
- "The ones that I would have there would be like a simple summary, an everything summary, a consultation request summary, and probably like a transfer summary." - P23, Specialist
- "I actually want better than intake form. I want your AI agent to summarize it and give me the important stuff." - P19, Emergency Medicine
- "This obviously becomes more useful. And what this exactly looks like changes depending on the user... The template configuration—you might want this organized in a different way." - P24, Preventive Health
- Source: Provider Interview Study, Codebook Theme 5.1

**Implications**:
- **For Product**: Multiple output templates from same underlying data
- **For Design**: Template selection interface; preview before generation
- **For Strategy**: Template library as product asset; potentially user-contributed templates

**Related Features**:
- [Summary Template Library]
- [Custom Template Builder]
- [One-Click Format Switching]

---

### Insight 19: Providers have clear price sensitivity thresholds ($50-100/month acceptable)

**Category**: Feature Preference
**Confidence**: 🟡 Medium
**Validated**: November 2024 via provider interviews (n=8 who discussed pricing)

**What We Learned**:
Providers who discussed pricing expressed willingness to pay $50-100/month for tools that demonstrably improve efficiency. This threshold is informed by comparison to current costs (transcription services dropped from $10/consult to <$1/consult with AI scribes) and perceived value.

**Evidence**:
- "The cost used to be much higher when you had typists. It typically used to cost me about $10 for each consultation. And now if I'm paying $30 a month for hundreds of consultations, we're looking at less than a dollar per consult letter. So I think I'd be happy to pay $50 to $100 a month if it improved my efficiency there." - P25, Rheumatology
- "That was the upper end but still acceptable." - P25, Rheumatology (on $100/month)
- "Yeah. Well, good luck and let me know when I can buy it." - P21, Preventive Health (expression of purchase intent)
- Source: Provider Interview Study, Codebook Theme 6.3

**Implications**:
- **For Product**: $50-100/month price point for physician users; lower for allied health
- **For Design**: ROI calculator to justify subscription; show value in time/money saved
- **For Strategy**: Freemium or trial essential to demonstrate value before purchase decision

**Related Features**:
- [Time Savings Dashboard]
- [ROI Calculator]
- [Trial/Freemium Offering]

---

# Category: Surprising Findings

---

### Insight 20: AI scribe adoption is enthusiastic despite imperfect integration

**Category**: Surprising Finding
**Confidence**: 🟢 High
**Validated**: November 2024 via provider interviews (n=22)

**What We Learned**:
Despite requiring copy-paste workflows, lacking direct EMR integration, and occasional formatting issues, AI scribes (Heidi, Empathia, BC Scribe) have achieved enthusiastic adoption. Providers describe them as "amazing" and adoption is spreading organically. This contradicts assumptions that perfect integration is required for adoption.

**Evidence**:
- "It's amazing. You cue up the AI scribe at the beginning of the appointment and you just talk to the patient. At the end it generates a transcript that you edit. There isn't yet a direct link into our EMR, so we have to copy and paste it, but that is not hard." - P13, Family Medicine
- "There are six AI scribes that are being trialed. Some of my colleagues are on the second or third one. The feedback and everything has been overwhelmingly positive." - P13, Family Medicine
- "I I mean, these are the kind of questions I would be going down. Damn thing's going to take my job." - P7, Urology (enthusiastic hyperbole about conversational AI)
- Source: Provider Interview Study, Codebook Theme 3.1

**Implications**:
- **For Product**: Value delivery trumps perfect integration; don't gate launch on EMR partnerships
- **For Design**: Optimize the imperfect workflow (copy-paste) rather than waiting for perfect workflow
- **For Strategy**: Learn from scribe success; identify analogous high-value, focused use cases

**Related Features**:
- [Optimized Copy-Paste]
- [Focused Value Delivery]
- [Organic Adoption Features]

---

### Insight 21: Providers resist new tools not from technophobia but from rational burden assessment

**Category**: Surprising Finding
**Confidence**: 🟢 High
**Validated**: November 2024 via provider interviews (n=22)

**What We Learned**:
Provider resistance to new tools is not technological conservatism. Providers are actively experimenting with AI, training their own models, and adopting scribes. Resistance comes from rational assessment of implementation burden against uncertain benefits—"another portal to be a part of, another place to look for information." Benefits must clearly outweigh costs.

**Evidence**:
- "I just don't know if it would be worth an implementation process for cost, and now there's another portal to be a part of, there's another place to look for information." - P16, Allied Health
- "There's just so much that we're constantly being asked to take on... even as we know it's going to make our lives better... we still are not willing to take it on." - P2, Family Medicine
- Same providers who expressed resistance also described active AI experimentation
- Source: Provider Interview Study, Codebook Themes 1.5, 3.4

**Implications**:
- **For Product**: Minimize implementation burden; value must be obvious and immediate
- **For Design**: Zero-configuration start; gradual complexity; no forced workflow changes
- **For Strategy**: "Try before you buy" essential; demonstrate value before asking for investment

**Related Features**:
- [Zero-Config Onboarding]
- [Immediate Value Demonstration]
- [Gradual Feature Discovery]

---

### Insight 22: Asynchronous care creates billing opportunities currently untapped

**Category**: Surprising Finding
**Confidence**: 🟡 Medium
**Validated**: November 2024 via provider interviews (n=4 who discussed billing opportunities)

**What We Learned**:
While fee-for-service limits compensation for preparation, there ARE billing codes for asynchronous patient communication and test ordering. A tool that facilitates reviewing waitlist patients, ordering pre-tests, and communicating results could enable $1000+ in additional monthly billing—and providers don't fully utilize these codes currently.

**Evidence**:
- "There's also a revenue opportunity in there because you cycle once in an asynchronous way with the doc who says, 'Yes, I'd like to see these tests.' They then order those tests. They now get to bill for that interaction." - P23, Specialist
- "So if you do it every two days, and remember, you're billing for it—if you have a list of 50 and you get 20 bucks per and you sit in your bed from 9 to 9:30 before you go to sleep, you just made $1000 and you help your patients." - P23, Specialist
- "When you communicate to the patient, you can bill for that and when you communicate to another physician, you can bill for that. And they're different billables." - P23, Specialist
- Source: Provider Interview Study, Codebook Theme 6.2

**Implications**:
- **For Product**: Build asynchronous care workflows that generate billable events
- **For Design**: Surface billing opportunities; integrate with billing capture
- **For Strategy**: Revenue enablement is potentially stronger value proposition than efficiency

**Related Features**:
- [Asynchronous Care Workflows]
- [Billing Opportunity Alerts]
- [Waitlist Patient Management]

---

## Archived Insights

*No insights archived yet. This section will capture insights that are invalidated, outdated, or fully incorporated into product.*

---

## Insight Validation Framework

### 🟢 High Confidence
- Observed across 10+ providers in this study (n=22)
- Consistent across specialties and practice types
- Multiple supporting quotes from different participants
- Aligns with external research/industry knowledge

### 🟡 Medium Confidence
- Observed in 4-9 providers
- May be specialty-specific or practice-type specific
- Supporting quotes available but limited diversity
- Needs validation with larger/different sample

### 🔴 Low Confidence
- Observed in 1-3 providers
- May be individual preference not pattern
- Contradictory evidence may exist
- Hypothesis stage—needs testing

---

## Research Backlog

Questions requiring further investigation:

### High Priority
- [ ] **Patient preferences for intake modality** (conversational vs. form vs. voice) — Providers uncertain; direct patient research needed — Method: Patient interviews/surveys
- [ ] **Allied health adoption patterns** — Only 4 allied health in sample; may have distinct needs — Method: Focused allied health study
- [ ] **Net time savings validation** — Providers skeptical; need quantitative measurement — Method: Time-motion study with tool usage

### Medium Priority
- [ ] **Price sensitivity by practice type** — Solo vs. group vs. health authority may differ — Method: Conjoint analysis
- [ ] **EMR-specific formatting requirements** — Different EMRs have different conventions — Method: Technical audit + user testing
- [ ] **Patient accuracy in self-reported data** — Providers skeptical; what's actual error rate? — Method: Data validation study

### Low Priority
- [ ] **Voice AI tempo optimization** — What conversation speed feels natural? — Method: A/B testing
- [ ] **Template sharing behaviors** — Would providers share custom templates? — Method: Feature usage analytics
- [ ] **Billing code utilization barriers** — Why aren't providers using async codes? — Method: Focused billing interviews

---

## Insight Changelog

| Date | Insight | Change | Reason |
|------|---------|--------|--------|
| Nov 2024 | All | Initial population | Provider Interview Study complete |

---

## By Feature Area

Quick reference for finding relevant insights:

### Onboarding & Adoption
- [Insight #20]: AI scribe adoption succeeds despite imperfect integration
- [Insight #21]: Resistance is rational burden assessment, not technophobia

### Pre-Visit Preparation
- [Insight #1]: Providers need pre-visit data synthesis, not just documentation help
- [Insight #6]: Verification time may negate AI efficiency gains

### Data Collection & Intake
- [Insight #16]: Clinical conversation follows branching logic, not linear forms
- [Insight #17]: Voice interfaces are promising but current implementations frustrate

### Trust & Verification
- [Insight #2]: Providers require source attribution to trust AI-generated content
- [Insight #14]: Providers trust presence but not absence of information
- [Insight #6]: Verification time may negate AI efficiency gains

### Customization & Personalization
- [Insight #3]: Deep customization needed by specialty and individual
- [Insight #4]: Providers want AI that learns from corrections
- [Insight #18]: Multiple summary formats needed for different purposes

### Data Aggregation & Interoperability
- [Insight #5]: Unified access to fragmented data is critical need
- [Insight #11]: Patients serve as information couriers between providers
- [Insight #13]: Multi-tool orchestration is manual and demanding

### Context & Care Settings
- [Insight #15]: Information needs are context-dependent
- [Insight #8]: Referral inefficiencies create cascading problems
- [Insight #9]: Allied health faces systematic access barriers

### Business Model & Economics
- [Insight #10]: Fee-for-service doesn't compensate AI-enabled activities
- [Insight #19]: Price sensitivity threshold is $50-100/month
- [Insight #22]: Asynchronous care creates untapped billing opportunities

### Integration & Workflows
- [Insight #7]: Copy-paste workflows persist; optimize rather than replace
- [Insight #12]: Providers experiment with consumer AI to fill gaps
- [Insight #13]: Multi-tool orchestration is manual and demanding

---

## Related Resources

- [Comprehensive Codebook v3.0](/research/codebook-v3-final.md): Full coding framework
- [Narrative Synthesis](/research/narrative-synthesis.md): Qualitative research report
- [Provider Personas](/research/provider-personas.md): Persona development from this study
- [Product Strategy](/strategy/product-strategy.md): How insights inform strategy
- [Feature Roadmap](/features/roadmap.md): PRDs influenced by these insights
