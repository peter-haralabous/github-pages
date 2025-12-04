# NARRATIVE SYNTHESIS: PROVIDER PERSPECTIVES ON AI-ENABLED HEALTHCARE DATA TOOLS
## A Qualitative Analysis of Healthcare Provider Interviews

---

# 1. INTRODUCTION / CONTEXT

## 1.1 Study Background

The healthcare industry faces an enduring paradox: despite decades of investment in electronic health records (EHRs) and digital infrastructure, clinicians continue to report significant friction in accessing, consolidating, and utilizing patient information. Administrative burden remains a leading contributor to physician burnout, with studies suggesting that for every hour of direct patient care, physicians spend nearly two additional hours on documentation and desk work (Sinsky et al., 2016). The emergence of artificial intelligence—particularly large language models and conversational AI—presents both an opportunity and a challenge: these technologies promise to alleviate documentation burden and improve information synthesis, yet they introduce new concerns about accuracy, trust, and workflow integration.

This qualitative study sought to understand healthcare providers' experiences, pain points, and perspectives on AI-enabled data collection and summarization tools. The research aimed to surface the nuanced, contextual factors that shape technology adoption in clinical settings—factors that quantitative surveys often miss.

## 1.2 Participants

Twenty-two healthcare providers participated in semi-structured interviews. The sample was purposively selected to represent diversity across:

- **Specialty:** Family medicine, emergency medicine, urology, plastic surgery, internal medicine, anesthesiology, cardiology
- **Practice Model:** Team-based primary care, solo private practice, hospital-based, preventive health clinics
- **Professional Role:** Physicians (n=18), allied health professionals including physiotherapists (n=4)
- **Setting:** Urban academic medical centers, community practices, integrated health systems
- **Experience with AI:** Ranging from early adopters actively experimenting with AI scribes to those with limited exposure

Participants ranged from early-career to senior clinicians with 20+ years of experience. All practiced in British Columbia, Canada, though findings have broader applicability given the universal challenges of healthcare fragmentation and documentation burden.

## 1.3 Thematic Focus

Analysis revealed nine overarching themes that collectively illuminate the complex ecosystem in which healthcare AI tools must operate:

1. **Workflow Efficiency & Time Management** — The temporal economics of clinical work
2. **Data Quality & Trust** — Verification requirements and conditional confidence
3. **Technology Integration & Adoption** — Multi-tool ecosystems and implementation realities
4. **Data Consolidation & Interoperability** — The fragmentation problem
5. **Customization & Flexibility** — Rejecting one-size-fits-all solutions
6. **Business Model & Implementation** — Economic structures shaping adoption
7. **Clinical Information Needs** — Specific data types and clinical reasoning requirements
8. **Care Delivery Context** — How settings shape information needs
9. **Patient Experience & Accessibility** — The patient-facing dimension

These themes are not discrete categories but rather interconnected aspects of a complex sociotechnical system. The following sections present each theme with analytic interpretation and illustrative participant voices, followed by a cross-theme narrative that surfaces tensions, dependencies, and design implications.

---

# 2. PRESENTATION OF THEMES

## THEME 1: Workflow Efficiency & Time Management

### Analytic Summary

Healthcare providers operate within severe temporal constraints. The theme of workflow efficiency emerged not merely as a desire for convenience but as a fundamental determinant of care quality, provider wellbeing, and economic sustainability. Participants described a constant calculus—evaluating whether any given task merited the time investment against competing demands. This temporal pressure creates a paradox for new technologies: tools must demonstrably save time, yet providers expressed skepticism that promised efficiencies materialize once verification and learning curves are factored in.

Pre-visit preparation emerged as a particularly variable and often invisible time sink. Simple cases might require two minutes of review; complex patients with cancer histories or multiple comorbidities could demand thirty minutes or more of chart archaeology—opening and closing multiple systems, synthesizing fragmented information, and mentally constructing a patient narrative before the encounter begins.

The referral system emerged as a significant source of inefficiency, with family physicians sometimes sending four or five referrals before one is accepted by a specialist with capacity. The limited communication channels between primary care and specialists compound this inefficiency, creating a system where information is repeatedly gathered, lost, and re-gathered as patients move through the healthcare system.

### Illustrative Quotes

**P1 (Emergency Medicine):**
> "I usually look at their past medical history and their medications first, the triage note and their vital signs, and then I'll go into the room. Most part, less than five minutes. A couple of minutes if it's very complicated... if they're a cancer patient and I want to see what they've had so far for their cancer treatment, then I'm pulling up old notes, the chemo notes, the radiation notes... so that one, maybe 10 minutes."

**P2 (Family Medicine):**
> "The nurse will spend an hour or so on that. I will have the encounter time which will be 30 to 40 minutes with the patient plus I might do 20 minutes of prep. So I could easily round that up to an hour... That's the one where I would love more support because that's just busy work. It's poor use of my and the nursing team's skill set really."

**P3 (Anesthesiology):**
> "That's not a favorite position for anesthesiologists, and I enjoy the pre-mission clinic but I wouldn't want to do that every single day because there's a lot of stress to get through 12 patients in a short period of time. And you end up spending a lot of time doing that, the night before looking through quickly the patient list for the following day."

**P4 (Internal Medicine):**
> "Pre-prescribed, I probably spent sometimes 10 to 15 minutes for a complex case. If it's here in the hospital, it can be as long as half an hour sometimes. That's probably the extreme end—clicking on Cerner and clicking on Care Connect, opening, closing, opening, closing, opening, closing. Writing down important information."

**P5 (Allied Health - Physiotherapy):**
> "Because to me, me reading through this will also cut into any minimal time that's saved, right? There might still be gaps where we still have to probe."

**P6 (Emergency Medicine):**
> "The family doctor has to send like four or five referrals until one gets accepted by a specialist... You wait until the specialist will fax you back saying rejected. My waitlist is too long. Family doctors can't really call a specialist to get a same day answer. That really only happens in the hospital system."

### Interpretation

The time management theme reveals a sophisticated cost-benefit analysis that providers continuously perform. Time is not merely a resource but a moral consideration—time spent on administrative tasks is time not spent with patients. This creates emotional labor beyond the mechanical burden of documentation.

The extreme variability in preparation time (2-30+ minutes) suggests that effective solutions must be context-sensitive, adapting to patient complexity rather than offering uniform approaches. The "chart archaeology" metaphor that emerged from interviews—clicking through multiple systems, opening and closing windows—points to the cognitive load of information fragmentation beyond mere time cost.

Crucially, providers expressed skepticism about whether new tools actually save time once verification requirements are considered. This "time efficiency skepticism" represents a significant adoption barrier that must be addressed through transparent demonstration of net time savings rather than theoretical efficiency gains.

---

## THEME 2: Data Quality & Trust

### Analytic Summary

Trust emerged as perhaps the most complex and nuanced theme in the analysis. Providers do not approach data with binary trust/distrust but rather with sophisticated conditional frameworks. A striking pattern emerged: providers tend to trust the presence of information (if a system says a patient has diabetes, they accept this) but do not trust the absence of information (if a system shows no allergies, they still ask the patient). This asymmetric trust has profound implications for system design.

The verification imperative was universal. Every participant, regardless of specialty or AI experience, emphasized the need to review and verify AI-generated content. This was not presented as optional due diligence but as professional obligation. Several participants recounted experiences of being "caught out" by errors in auto-generated content, reinforcing the necessity of verification.

Patient-reported data occupied an interesting middle ground. Providers generally trusted patients' self-identification of disease entities ("I have diabetes") but were skeptical of specific values ("My PSA was 2.0") and recognized that patients often misunderstand or misrepresent their conditions due to health literacy limitations rather than intentional deception.

### Illustrative Quotes

**P7 (Urology):**
> "So I mean, I wouldn't—I don't accept any data from the patient. So if they say, 'Oh yeah, my PSA last year was two,' I'll write it down that patient reported PSA of two, but I will follow up on that and get the information myself to confirm it. I don't trust the patient for the direct data, but if they said they had a PSA done last year, then I will take that information and search it out."

**P8 (Surgeon):**
> "If there is pertinent positive information in Care Connect and it's fed to me, that's useful. Yes, I would use that. However, if it was absent, I wouldn't rely upon that being the truth... If it's fed to me and it's there, then I consider that the truth. But if it's not there, I don't assume it not to be there."

**P9 (Plastic Surgery):**
> "It definitely needs to be checked though. I definitely have to read through that consult note to make sure that it's accurate."

**P10 (Internal Medicine):**
> "You start to develop a bit of complacency as a physician because you assume the AI has captured everything and it's presented it correctly and you don't read through the note as carefully and things can get missed."

**P11 (Rehabilitation Medicine):**
> "A patient might not even understand their diagnosis. They might put in, you know, if they have numbness in their legs, we know that's because they have a radiculopathy in their back. They have pinched nerve in their back. So we would put it in as radiculopathy. The patient would put it in as pain in the legs, which is like two different things that you would then go down a very different path for."

**P12 (Preventive Health):**
> "Basically everything is almost annotated where you could hover over it, right click on it, and say like where did this come from and it will link you to the initial PDF... Clinicians will really, really want that, or they'll want to know—was this self-reported on an intake Q&A or was this from a referral letter?"

### Interpretation

The trust theme illuminates a fundamental tension in AI-assisted healthcare: the efficiency gains from AI summarization depend on providers accepting AI output, yet professional responsibility and patient safety demand verification. This creates a "trust tax"—the time cost of checking AI work that may partially or fully offset efficiency gains.

The conditional trust pattern (believing presence, not absence) has important design implications. Systems that confidently assert the absence of conditions ("No known allergies") may be more dangerous than systems that acknowledge uncertainty ("No allergies documented in available records"). The epistemological status of AI-generated claims must be transparent.

Source attribution emerged as a critical trust-building mechanism. Providers expressed greater confidence when they could trace claims to original sources, whether human-authored (like UpToDate guidelines) or documentary (like referral letters). This suggests that AI systems should maintain and expose provenance information rather than presenting synthesized information as authoritative assertions.

---

## THEME 3: Technology Integration & Adoption

### Analytic Summary

Healthcare providers do not adopt technologies in isolation; they integrate them into complex, pre-existing ecosystems of tools, workflows, and relationships. The theme of technology integration revealed a landscape of interconnected systems—EMRs, AI scribes, booking platforms, form systems, imaging archives—each requiring its own login, interface conventions, and mental model. Providers described sophisticated choreographies of copying and pasting between systems, uploading documents to AI tools, and manually transferring information across platforms.

AI scribe adoption emerged as a bright spot in this otherwise fragmented landscape. Participants using tools like Heidi, Empathia, and the BC Scribe project reported enthusiastic adoption and meaningful efficiency gains in documentation. However, even these successes were tempered by integration limitations—most scribes required copy-paste workflows into EMRs rather than direct integration.

Voice interface experimentation represented an emerging frontier. Several participants had begun experimenting with voice-based AI using platforms like ChatGPT, training these systems on their own clinical interviewing patterns. These experiments revealed both the promise of natural language interaction and its current limitations: lag, mid-conversation stops, and unnatural prompting behaviors.

Change management resistance was evident but nuanced. Providers were not technophobic; many were active experimenters. Rather, resistance stemmed from rational evaluation of implementation costs against uncertain benefits, particularly given the history of technology promises that failed to materialize in practice.

### Illustrative Quotes

**P13 (Family Medicine):**
> "So actually since we met, a few things have happened. On the AI scribe, we've got the BC Scribe project going now. A number of us have tried the AI scribes and it's going very well. I think quite a few people are going to adopt those... It's amazing. You cue up the AI scribe at the beginning of the appointment and you just talk to the patient. At the end it generates a transcript that you edit. There isn't yet a direct link into our EMR, so we have to copy and paste it, but that is not hard."

**P14 (Plastic Surgery):**
> "My MOA sets up an encounter, uploads the referral letter, and then also uploads any other stuff that's come along with that, like investigations, but then also the PDF that the Thrive produces, and then the AI program sort of scans that stuff."

**P15 (Urology):**
> "I started to tap on the new natural language in ChatGPT and what I did was I took 10 interviews that I did with patients, removed the patient demographics, and I uploaded the voice files to chat. And I asked it to sort of learn from that... It lagged a bit and that was frustrating because it didn't have the same tempo that I would have with a patient. Sometimes it would require a prompt to continue midway through a history taking, sometimes it would lag, sometimes just stop doing it."

**P16 (Allied Health):**
> "I just don't know if it would be worth an implementation process for cost, and now there's another portal to be a part of, there's another place to look for information... I can see where it's nice and consolidates everything. But for me personally, I just don't see where I feel that I would need to implement it versus just the verbal."

**P17 (Emergency Medicine):**
> "I make every single effort not to access that data because that just slows me down. That's not efficient. Every extra step I have to—every time I actually click on one of these, it opens up another window, right? Slows down my process, slows down the system... So you know that takes like 17 minutes of my time."

**P18 (Rheumatology):**
> "So it's weird because sometimes it does it perfectly and then other times it'll output with asterisks and dash lines in places that I don't even know and I've got to physically correct so it doesn't output the way I always want necessarily. What would be ideal is it should have a final transcript I can just copy and paste."

### Interpretation

The technology integration theme reveals that successful AI tools must be designed not as standalone solutions but as members of an ecosystem. The copy-paste workflow, while imperfect, persists because it allows providers to maintain their existing systems while gaining benefits from new tools. Direct integration, while theoretically superior, faces significant barriers including EMR vendor cooperation, security requirements, and the sheer diversity of existing systems.

The enthusiasm for AI scribes—despite their integration limitations—suggests that providers will adopt tools that deliver clear, immediate value even when integration is imperfect. The key appears to be demonstrable efficiency gains in specific, high-frequency tasks (like documentation) rather than comprehensive but complicated workflow transformation.

Voice interface experimentation signals an emerging modality that may become increasingly important. Providers' attempts to "train" general-purpose AI on their own clinical patterns reveals a desire for personalization that current purpose-built tools may not satisfy. This experimentation also highlights the gap between consumer AI capabilities and healthcare-specific requirements.

---

## THEME 4: Data Consolidation & Interoperability

### Analytic Summary

The fragmentation of patient information across disconnected systems emerged as one of the most deeply felt pain points. Providers described a healthcare landscape where patient data exists in silos—family doctor EMRs, specialist practices, hospital systems, community radiology, allied health platforms—each invisible to the others. The result is a system where patients become the primary information carriers, bringing their medical histories in memory (or through family members) because digital systems cannot communicate.

The vision of patient-owned, portable health records resonated strongly with participants. Several described an ideal state where patients carry comprehensive health data that accumulates across touchpoints, accessible to any provider with patient consent. This vision stands in stark contrast to current reality, where even providers within the same health authority may struggle to access each other's records.

System access disparities between professional groups added another dimension to fragmentation. Allied health professionals described being excluded from hospital EMR systems that physicians could access, forcing reliance on patient-mediated information transfer or informal workarounds.

### Illustrative Quotes

**P19 (Emergency Medicine):**
> "Obviously, we don't have access to their family doctor's office. We don't know what their rheumatologist told them last time because these are all in private offices. But they're very complex and they end up in hospital every six weeks. Every time they come to hospital, it goes by their memory or their son-in-law who took them there and they're not here today. So having this information available to healthcare workers who are not part of your medical home—that is probably even better added value because there is a lot of lost data."

**P20 (Family Medicine):**
> "This is one of the biggest bug bears in medicine—access to information, efficient use of medical information, communicating. It's where a lot of mistakes happen."

**P21 (Preventive Health):**
> "I feel like the optimal area to start with is just like helping people get it all in one place. That's it... If everybody was using the system and everybody was pulling data from their different sources and that's always being compiled and consolidated and built in this knowledge graph on that patient, then that goes everywhere that patient goes."

**P22 (Rheumatology):**
> "Once we've got a patient, we can continue to add data over time when the new stuff comes in and just dump it in, let AI look at it, say 'hey, this is what I think it is,' I'm going to apply it to the patient. And you can see that if this continues to happen from one clinic to another clinic, different specialists, that profile starts getting bigger and bigger and bigger about that patient. That's the vision anyways."

**P5 (Allied Health):**
> "I don't need the full health history. I just literally need access to this singular image, which EMRs in the hospitals—docs can just log into that EMR and pull that report out. If I could just have that ability, like from an allied health standpoint, I think if we could just get access to imaging reports, that would make us a lot happier."

### Interpretation

The fragmentation theme reveals a fundamental infrastructure deficit that individual tools cannot solve but must navigate. The "patient as courier" pattern—where patients physically or verbally transport their medical histories—represents a workaround for system failures that creates burden for patients and introduces error risk.

The allied health access disparity illuminates how digital infrastructure can encode professional hierarchies. Physiotherapists and other allied professionals may need specific pieces of information (like imaging reports) but lack the system access that physicians enjoy, creating inefficiencies that affect patient care.

The patient-owned record vision articulates an alternative architecture where data follows patients rather than residing in provider-controlled silos. This vision aligns with emerging patient data rights frameworks but faces significant technical, legal, and commercial barriers to implementation.

---

## THEME 5: Customization & Flexibility

### Analytic Summary

Healthcare is not monolithic, and providers emphatically rejected one-size-fits-all solutions. The customization theme revealed profound diversity in information needs across specialties, practice models, and individual preferences. An orthopedic surgeon may care primarily about bleeding and clotting risk; a cardiologist needs cardiovascular history in depth; a physiotherapist may need only imaging reports. These differences are not minor variations but fundamental distinctions in what constitutes relevant information.

Beyond specialty differences, individual providers described idiosyncratic workflows and preferences developed over years of practice. Some wanted tabular data presentations; others preferred narrative summaries. Some prioritized medications; others led with vital signs. These preferences were not arbitrary but reflected each provider's mental model of clinical reasoning.

Template customization emerged as a concrete expression of these needs. Providers described wanting multiple summary types—simple summaries, comprehensive summaries, consultation requests, transfer summaries—each serving different purposes and audiences.

### Illustrative Quotes

**P8 (Surgeon):**
> "An orthopedic surgeon might want to know only about whether this person has a bleeding or clotting problem, right? But a cardiologist is going to want to know something very different."

**P15 (Urology):**
> "In certain areas I asked it to go deeper with second-order questions. In certain areas like the past psychiatric history, I wasn't that keen on knowing that much information on the patient, so I had it say, 'Look, limit your questioning around the past psychiatric to one minute at the most.' And you don't need to go into second-order questions. So I did kind of tailor it more."

**P23 (Specialist):**
> "And the ones that I would have there would be like a simple summary, an everything summary, a consultation request summary, and probably like a transfer summary."

**P24 (Preventive Health):**
> "This obviously becomes more useful. And I think something that you're highlighting is that actually what this exactly looks like changes depending on the user... The template configuration—you might want this organized in a different way or prioritize certain things up top or formatted in a different way. That's completely in your control."

**P5 (Allied Health):**
> "I don't need the full health history. I just literally need access to this singular image."

### Interpretation

The customization theme challenges the assumption that healthcare AI can be designed for a generic "provider" user. The variation across specialties, practice models, and individuals suggests that successful tools must be fundamentally configurable—not merely offering a few display options but allowing users to shape what information is collected, how it is organized, and what level of detail is presented.

This finding aligns with research on expert cognition showing that experts develop domain-specific schemas that organize information in personally meaningful ways. Forcing experts into standardized interfaces may actually impair their reasoning by conflicting with these internalized structures.

The allied health perspective is particularly illuminating: sometimes less is more. A tool that provides comprehensive information may be less useful than one that provides exactly the right information for a specific clinical role.

---

## THEME 6: Business Model & Implementation

### Analytic Summary

Healthcare operates within economic structures that profoundly shape what is possible. The business model theme revealed how payment systems—particularly fee-for-service models—create barriers to certain workflows while enabling others. Providers cannot bill for reviewing patient forms, answering emails, or preparing for visits; they can only bill for direct patient encounters. This creates a structural disincentive for asynchronous care activities, regardless of their value to patients.

Allied health professionals faced particularly severe billing constraints, with insurance often covering only face-to-face time. Virtual care billing codes, expanded during COVID-19, were described as under threat as payers sought to reduce pandemic-era accommodations.

Cost-value calculations were sophisticated. Providers expressed willingness to pay $50-100/month for tools that demonstrably improved efficiency—a threshold informed by comparison to current costs (e.g., transcription services that previously cost $10/consultation now available for under $1/consultation through AI scribes).

Regulatory requirements added another constraint layer. Professional college mandates for in-person assessment limited the potential for fully remote intake, while documentation standards varied widely, creating uncertainty about what level of record-keeping would satisfy regulatory scrutiny.

### Illustrative Quotes

**P13 (Family Medicine):**
> "I think the other practical consideration—how do you bill for that in a fee-for-service environment? There isn't really a fee code for reviewing emails from patients. For phone calls and direct interaction with patients, it's easier to figure that out in terms of fee-for-service, but I don't know how you would do forms."

**P5 (Allied Health):**
> "A lot of insurers are only paying for one-on-one client time, one-on-one face time. They're not paying for—even if I was to use an assistant. It's just one-on-one face time... We only have billing codes for actual direct 101 care. From a MSP standpoint, we only have one billing code for MSP. That's $23 per visit."

**P19 (Emergency Medicine):**
> "A lot of these things are driven by compensation models. Obviously, I want the best for my patient, but if their potassium is perfectly fine and I have another 50 lab workups to review and four ultrasounds and three x-rays, I want to spend the least amount of time to get as much information and move on to the next task because reviewing patient information one by one doesn't actually pay me."

**P25 (Rheumatology):**
> "The cost used to be much higher when you had typists. The costs have come down substantially but it typically used to cost me about $10 for each consultation. And now if I'm paying $30 a month for hundreds of consultations, we're looking at less than a dollar per consult letter. So I think I'd be happy to pay $50 to $100 a month if it improved my efficiency there."

**P23 (Specialist):**
> "There's also a revenue opportunity in there because you cycle once in an asynchronous way with the doc who says, 'Yes, I'd like to see these tests.' They then order those tests and it all sort of happens with clicks of buttons. They now get to bill for that interaction."

### Interpretation

The business model theme reveals that technology adoption cannot be divorced from economics. Tools that create value for patients but cannot be monetized by providers face structural adoption barriers. Conversely, tools that align efficiency gains with billing opportunities—like the asynchronous care model described by P23—may achieve rapid adoption.

The fee-for-service/face-time constraint is particularly significant for AI-enabled intake and data collection. If providers cannot bill for reviewing AI-gathered information, the economic case for adoption weakens regardless of clinical value. This suggests that advocacy for billing code changes may be as important as technology development for market success.

The price sensitivity data ($50-100/month acceptable threshold) provides useful guidance for positioning but should be interpreted cautiously—willingness to pay varies with demonstrated value and competitive alternatives.

---

## THEME 7: Clinical Information Needs

### Analytic Summary

Beyond general information management, providers articulated specific clinical data requirements that shape what AI systems must capture and present. Medication reconciliation emerged as particularly challenging—providers needed complete medication lists including prescriptions, over-the-counter remedies, naturopathic treatments, and even "street-provided" substances. The temporal dimension of medications (when started, when stopped) added complexity.

Social determinants of health received variable attention. Some providers—particularly those serving marginalized populations—emphasized the importance of social history (housing, finances, support systems) as determinants of health outcomes. Others, focused on specific clinical problems, deprioritized social information.

Clinical decision support needs highlighted the distinction between patient-specific data and general clinical knowledge. Providers used tools like UpToDate for evidence-based guidelines, expressing trust in human-curated content that they did not extend to AI-generated clinical recommendations.

The theme of clinical nuance captured the challenge of precise symptom characterization. Patients might say they have symptoms "all the time" when they actually mean "most of the time with some relief"—a distinction with diagnostic significance. This nuance requires follow-up questioning that adapts based on initial responses, a capability that distinguishes clinical interviewing from simple form completion.

### Illustrative Quotes

**P19 (Emergency Medicine):**
> "I would like to know their medications—obviously what medications they're taking—and that's all of the medications: pharmacy provided, street provided, naturopath provided, wherever they come from."

**P19 (Emergency Medicine):**
> "I would like to know a fair bit about their social history... I am actually a believer in the social aspect of medicine and how it impacts patients' wellbeing and health and outcome and their needs. Social history has personal history built into it essentially. Do you drink? Who do you live with? How do you support yourself? Who do you support? And how are the finances?"

**P9 (Plastic Surgery):**
> "Like, you know, do you actually have symptoms all the time or do they come and go? Because people say, 'Oh, I have symptoms all the time,' but 'Oh, I have about two hours during the day where I don't have symptoms.' So there's a little bit of that... the extra nuance."

**P13 (Family Medicine):**
> "Most of us will trust UpToDate because it's put together by people. They probably do use some AI, but at least you've got the name of the person that wrote the article on what to do."

**P15 (Urology):**
> "I fed it some more second-order and tertiary-order questions. So for example, if you ask the patient, 'Have you had any heart disease?' and they say yes, then you're prompted to ask further questions. If they say they've had atrial fibrillation, then I want you to ask further about anticoagulation and rate control."

### Interpretation

The clinical information needs theme reveals that healthcare data collection is not simply about capturing information but about capturing the right information in the right form for clinical reasoning. The branching logic of clinical questioning—where initial answers determine follow-up questions—represents a fundamentally different paradigm from static form completion.

The medication reconciliation challenge illustrates the gap between institutional data (pharmacy records) and complete patient reality (including non-prescription substances). AI systems that rely solely on institutional data sources will miss clinically relevant information.

The trust distinction between patient-specific AI summarization and clinical decision support AI suggests different design approaches may be needed for different use cases. Providers may accept AI synthesis of patient information while remaining skeptical of AI clinical recommendations.

---

## THEME 8: Care Delivery Context

### Analytic Summary

The same provider may have fundamentally different information needs depending on the care context. The care delivery context theme illuminated how settings—emergency versus scheduled, first visit versus follow-up, specialist consultation versus primary care—shape what information is needed and how quickly it must be accessed.

Emergency settings presented the most acute information access challenges. Providers described seeing patients with complex histories who arrived without records, with only patient memory (often incomplete) as information source. The time pressure of emergency care meant that extensive pre-visit preparation was impossible; information needed to be immediately accessible and scannable.

Follow-up care had different requirements—verifying that ordered tests were completed, reviewing results, and efficiently updating treatment plans. The time allocated for follow-ups (often 10-15 minutes, sometimes by phone) demanded even greater efficiency than initial consultations.

First visits emphasized relationship building. Several providers stressed that initial encounters should be in-person to establish trust, even if subsequent follow-ups could be virtual. This had implications for how much data collection could appropriately occur before versus during the first visit.

Team-based care models introduced coordination challenges. When multiple professionals (nurse, physician, dietitian, physiotherapist) touched a patient in a single assessment day, information needed to flow between them without requiring the patient to repeat their history.

### Illustrative Quotes

**P7 (Urology):**
> "When you do get called out or when you do see someone in emerg, gaining access to all of their data can be a real challenge in an emergency setting. So I have quick access to what's available on Cerner... but let's say the patient has traveled. This very commonly happens to me."

**P25 (Rheumatology):**
> "A follow-up visit is typically 10 or 15 minutes. It's often on the phone. And you have to in that time get the history, sort out what they've done, go through the results, formulate a plan, send them prescriptions or new investigations, and dictate a report—all in about 10 or 15 minutes."

**P19 (Emergency Medicine):**
> "If I'm building a relationship with someone, the first few sessions need to be the impactful sessions, need to be in person. Again, it's a matter of taste or philosophy, but this is—we're thinking of essentially taking over this patient's provision of care."

**P2 (Family Medicine):**
> "With me being under Vancouver Coastal Health, the way it works at our clinic is it's very team-based, which is a way that a lot of primary care is going and should be going."

**P26 (Surgical Coordinator):**
> "It's primarily related to the multiple handovers between care providers. So it has to touch a lot of people... surgeon, pack nurse, booking clerks, booking nurse, anesthesiologist."

### Interpretation

The care delivery context theme reveals that information tools must be context-aware, adapting not only to specialty but to the specific type of encounter. A comprehensive intake appropriate for a preventive health assessment would be excessive for an emergency visit; a brief summary adequate for follow-up would be insufficient for initial consultation.

The emergency care challenge is particularly significant because it represents highest-stakes, lowest-information scenarios. Patients in emergency settings often have the most complex histories and the least access to records. Solutions that bridge this gap—perhaps through patient-portable records or rapid health authority-wide lookups—could have disproportionate impact on care quality.

The team-based care coordination challenge suggests that information systems should be designed not for dyadic (patient-provider) interactions but for many-to-one (multiple providers to single patient) relationships. Information captured by one team member should be immediately available to others.

---

## THEME 9: Patient Experience & Accessibility

### Analytic Summary

While the study focused on provider perspectives, a significant theme emerged around the patient experience of data collection tools. Providers served as proxies for patient voices, reporting on patient frustrations and preferences observed in practice.

Form burden was universally acknowledged. Patients "hate" spending 20 minutes on intake forms, and this burden occurs at a moment of vulnerability—when seeking care. The opportunity to pre-fill forms from existing data, reducing redundant entry, was seen as both efficiency gain and patient experience improvement.

Interface modality preferences remained uncertain. Providers wondered whether patients would prefer conversational AI to traditional forms, voice input to typing, but acknowledged they didn't know the answer. Early experiments with conversational intake were described as "cool" by providers, but patient reception remained to be validated.

Language and accessibility needs were raised by providers serving diverse populations. The ability to conduct intake in patients' preferred languages, with AI translation to English, was identified as a significant opportunity. Similarly, voice interfaces were suggested as accommodations for patients with literacy challenges.

Patient-mediated data transfer—patients physically carrying their records between providers—emerged as a current workaround for system fragmentation. This burden falls on patients (or their family members) and introduces error risk when medical histories are transmitted through memory rather than documentation.

### Illustrative Quotes

**P25 (Rheumatology):**
> "Patients hate sitting down and spending 20 minutes doing an intake form... It's the only time they'll do the intake form until maybe a few years later there's another consult for something else—they'll do another intake form."

**P27 (Surgery):**
> "I wonder—I don't know the answer to this—but is this easier for a patient to fill out than a form or not?"

**P7 (Urology):**
> "I'm just thinking about people who may not be as literate, right? To have that information or to be able to respond with a voice back and forth, have the option to do that would be nice."

**P2 (Family Medicine):**
> "Language barriers are a common problem. If this could be sent in that patient's preferred language, now this chatbot's asking those questions in that preferred language and getting more hopefully accurate answers back. And because it's AI, that translation back to English could also happen on the other end."

**P19 (Emergency Medicine):**
> "Every time they come to hospital, it goes by their memory or their son-in-law who took them there and they're not here today."

### Interpretation

The patient experience theme, though secondary to provider perspectives in this study, reveals an important stakeholder whose needs must be balanced against provider efficiency goals. Reducing form burden benefits both patients (less frustration) and providers (better completion rates, more accurate data from engaged patients).

The uncertainty about patient interface preferences suggests an opportunity for user research directly with patients. Provider assumptions about what patients want may not align with actual patient preferences, particularly across demographic groups with varying technology comfort levels.

The language accessibility opportunity is significant. AI translation capabilities could transform access for non-English-speaking patients who currently face barriers to complete, accurate communication of their health histories. This represents both an equity imperative and a quality improvement opportunity.

---

# 3. CROSS-THEME NARRATIVE

## 3.1 The Trust-Efficiency Tension

The most fundamental tension across themes is between trust requirements and efficiency aspirations. Providers want AI tools that save time (Theme 1), but trust requirements demand verification (Theme 2), which consumes time. This creates a potential zero-sum dynamic where verification time offsets efficiency gains.

However, the analysis suggests pathways through this tension. Source attribution and traceability (Theme 2) may reduce verification burden by allowing providers to quickly assess the reliability of specific claims rather than reviewing entire summaries. Customization (Theme 5) may allow providers to configure systems to present only information they trust, reducing the scope of verification. And the conditional trust pattern—trusting presence but not absence—suggests that verification can be targeted rather than comprehensive.

The key insight is that trust is not binary but graduated and contextual. Systems designed around this nuanced trust model, rather than assuming either complete trust or complete skepticism, may navigate the tension more effectively.

## 3.2 The Fragmentation-Integration Paradox

Themes 3 (Technology Integration) and 4 (Data Consolidation) reveal a paradox: the healthcare system suffers from fragmentation, yet providers resist adding "another portal" to their already complex tool ecosystems. Solutions that address fragmentation by introducing new platforms may exacerbate the very problem they seek to solve.

The successful adoption of AI scribes (Theme 3) suggests a resolution: tools that integrate into existing workflows through lightweight mechanisms (copy-paste) rather than demanding workflow transformation. The vision of patient-portable records (Theme 4) suggests another approach: rather than integrating provider systems, create a patient-centered layer that sits between systems.

The challenge is that truly solving fragmentation requires system-level change that individual tools cannot achieve. The practical path may be incrementalism—tools that make fragmentation more manageable rather than eliminating it, while larger infrastructure efforts proceed on longer timelines.

## 3.3 The Customization-Standardization Balance

Theme 5 (Customization) emphasizes the diversity of provider needs, while Theme 7 (Clinical Information Needs) reveals certain universal requirements (medication reconciliation, vital signs). This creates a design challenge: systems must be configurable enough to accommodate individual preferences while maintaining sufficient standardization to ensure clinical completeness.

The clinical nuance sub-theme (Theme 7) offers a model: branching logic that adapts to patient responses while ensuring critical questions are always asked. Applied to customization, this suggests "configurable defaults"—systems that follow specialty-specific templates but allow individual modification, with guardrails ensuring clinical essentials are not omitted.

## 3.4 The Business-Clinical Value Gap

Theme 6 (Business Model) reveals that clinical value does not automatically translate to economic value. Tools that benefit patients and providers may still face adoption barriers if they cannot be monetized within existing payment structures. This gap creates a market failure where valuable innovations struggle to achieve adoption.

The asynchronous care billing opportunity (Theme 6) suggests that economic constraints are not fixed but evolving. Advocacy for billing code changes, demonstration of downstream cost savings, and innovative pricing models may bridge the business-clinical gap. The COVID-era expansion of virtual care billing demonstrates that payment systems can change when circumstances demand.

## 3.5 Context-Sensitivity as Unifying Principle

Across themes, a unifying principle emerges: context matters. Information needs vary by specialty (Theme 5), care setting (Theme 8), patient complexity (Theme 1), and encounter type (Theme 8). Trust requirements vary by data source (Theme 2). Adoption barriers vary by practice model (Theme 6). Patient preferences vary by language and literacy (Theme 9).

This pervasive context-sensitivity suggests that successful healthcare AI tools must be fundamentally adaptive—not offering a single solution but providing a platform that configures itself to context. Machine learning may enable such adaptation, learning from provider corrections (Theme 3) to personalize over time.

---

# 4. DISCUSSION / IMPLICATIONS FOR UNDERSTANDING

## 4.1 Answering the Research Questions

This qualitative analysis set out to understand healthcare providers' perspectives on AI-enabled data collection and summarization tools. The thematic analysis reveals several key findings:

**How do providers currently manage patient information, and what are the pain points?**

Providers operate in a fragmented landscape where patient information is scattered across disconnected systems. They spend significant time—from minutes to half an hour per patient—on "chart archaeology," gathering and synthesizing information before encounters. The referral system compounds inefficiency through rejections, limited communication, and information loss at transitions. Time spent on administrative tasks is experienced not merely as burden but as moral injury—time taken from patient care.

**What are providers' requirements for trusting AI-generated information?**

Trust requirements are nuanced and conditional. Providers trust the presence of information but not its absence. They require source attribution to assess reliability. They recognize a professional obligation to verify AI output regardless of its apparent quality. The "trust tax"—time spent verifying—partially offsets efficiency gains. Trust-building requires transparency about information provenance and epistemological status.

**What factors shape adoption of new healthcare AI tools?**

Adoption is shaped by demonstrable efficiency gains, integration with existing workflows, economic viability within billing structures, and regulatory compliance. Tools that require dramatic workflow transformation face greater resistance than those that enhance existing practices. The success of AI scribes demonstrates that tools delivering clear, immediate value can achieve adoption despite integration limitations.

**How do specialty, practice model, and care context shape information needs?**

Information needs vary profoundly across specialties (different relevant data), practice models (team-based vs. solo, preventive vs. acute), and care contexts (emergency vs. scheduled, first visit vs. follow-up). One-size-fits-all solutions are rejected; customization is essential. Context-sensitivity—adapting to situation rather than offering uniform experience—emerges as a design imperative.

## 4.2 Contribution to Broader Knowledge

These findings contribute to several broader knowledge domains:

**Healthcare informatics:** The study extends understanding of EHR usability challenges into the AI era, showing that new technologies face similar barriers (fragmentation, trust, integration) as their predecessors while introducing new challenges (AI-specific accuracy concerns, complacency risks).

**Technology adoption in healthcare:** The findings complicate technology acceptance models by showing that adoption is not primarily about individual attitudes but about system-level factors: economic structures, regulatory requirements, and ecosystem complexity. The rational evaluation of implementation costs against uncertain benefits suggests that healthcare technology adoption follows different dynamics than consumer technology.

**AI trust and verification:** The conditional trust pattern (believing presence, not absence) and the trust-efficiency tension contribute to growing literature on human-AI teaming. Healthcare providers offer a case study of expert users who cannot simply accept AI output but must maintain professional accountability.

**Patient-centered care:** The patient experience theme reveals that provider-facing tools have patient-facing implications. Form burden, accessibility, and the patient-as-courier phenomenon all affect patient experience even when patients are not direct users of provider tools.

## 4.3 Limitations

This study is limited by its geographic focus (British Columbia, Canada), which affects generalizability to other healthcare systems. The sample, while diverse across specialties, may not capture perspectives of providers in smaller communities or different organizational contexts. As with all qualitative research, findings represent thematic patterns rather than statistical prevalence; the relative importance of themes cannot be quantified from this data.

The study relied on provider reports of patient preferences rather than direct patient voice. Future research should include patient perspectives to validate or complicate provider assumptions about patient experience.

---

# 5. DESIGN IMPLICATIONS

The following section translates research findings into actionable guidance for product development, policy, and practice. For each theme cluster, we present the underlying user need, a design principle for addressing it, current landscape context, identified gaps and opportunities, and specific implications for product strategy.

---

## 5.1 Theme Cluster: Workflow Efficiency & Time Management

### User Need → Design Principle

**Need:** Providers need to minimize time spent on administrative tasks, particularly pre-visit data review and information synthesis, while maintaining care quality. Time is experienced as a moral resource—time spent on administration is time taken from patients.

**Principle:** *Design for net time savings, accounting for the full workflow including verification.* Efficiency claims must be validated against real-world usage that includes the "trust tax" of verification. Surface-level time savings that shift burden (e.g., from data entry to data verification) do not create value.

### Current Landscape

**AI Scribes (Heidi, Abridge, Nuance DAX, Suki):** The most successful category in healthcare AI, achieving genuine adoption. These tools record clinical conversations and generate documentation, saving 5-10 minutes per encounter. Limitations include lack of direct EMR integration (requiring copy-paste), inconsistent formatting, and no support for pre-visit preparation.

**EHR Vendors (Epic, Cerner, MEDITECH):** Incumbents offer pre-visit summaries and chart preparation tools, but these are typically rule-based rather than AI-powered and require information to be in the EHR system—they cannot synthesize external information.

**Health Information Exchanges (Carequality, CommonWell):** These initiatives aim to enable cross-system data sharing but adoption remains limited, and providers report that even available data is difficult to access efficiently.

### Gap / Opportunity

**Gaps:**
- Pre-visit preparation remains largely unaddressed by current AI tools; scribes help with documentation but not with the "chart archaeology" that precedes encounters
- Complex patients (cancer histories, multiple comorbidities) who require 15-30 minutes of preparation receive no more support than simple cases
- Information from outside the health system (community radiology, private specialists, allied health) remains inaccessible

**Opportunity:** AI-powered pre-visit synthesis that aggregates information from multiple sources, adapts depth to patient complexity, and presents information in scannable format optimized for rapid review. This addresses the highest-burden scenarios (complex patients) where current tools provide least support.

### Implication for Product Strategy

**Differentiation opportunity:** While competitors focus on documentation (post-visit), position on preparation (pre-visit). The "chart archaeology" problem is acknowledged but unaddressed. A tool that saves 15 minutes on a complex patient's preparation—documented through time-motion studies—offers defensible value proposition.

**Key features:**
- Complexity-adaptive summarization: Brief summaries for simple cases, comprehensive synthesis for complex histories
- Multi-source aggregation: Ability to ingest documents from diverse sources (uploaded PDFs, faxes, patient-provided records) rather than requiring EMR integration
- Rapid scanning format: Design for eye movement and quick comprehension rather than reading; layered detail that expands on demand

**Trade-off to manage:** Thoroughness vs. speed. More comprehensive summaries require more generation time and more verification time. Design should expose this trade-off to users, allowing them to choose depth based on available time and patient complexity.

---

## 5.2 Theme Cluster: Data Quality & Trust

### User Need → Design Principle

**Need:** Providers must maintain professional accountability for clinical decisions even when using AI tools. They need to verify AI output efficiently and understand the provenance and reliability of information claims.

**Principle:** *Design for calibrated trust through transparency, not for blind acceptance.* Expose uncertainty, attribute sources, and support efficient targeted verification rather than requiring comprehensive review.

### Current Landscape

**AI Scribes:** Generally present output as authoritative text without uncertainty indicators or source attribution. Verification is an all-or-nothing proposition—providers must review entire notes rather than focusing on uncertain claims.

**Clinical Decision Support (UpToDate, DynaMed):** These human-curated resources enjoy high trust precisely because they are not AI-generated. They represent the gold standard for clinical reference but do not address patient-specific data synthesis.

**EHR Problem Lists and Summaries:** Often outdated, incomplete, and unreliable. Providers have learned to distrust these system-generated views, creating skepticism that transfers to AI tools.

### Gap / Opportunity

**Gaps:**
- No current tools implement the conditional trust model (distinguishing presence vs. absence claims)
- Source attribution is rare; when present, it typically links to documents rather than specific passages
- Uncertainty quantification in clinical AI remains primitive; most systems present all output with equal confidence

**Opportunity:** Trust-calibrated interfaces that distinguish claim types (present/absent/uncertain), expose sources at the claim level, and enable efficient targeted verification. This could transform the trust-efficiency relationship by allowing providers to trust confidently where warranted and verify efficiently where needed.

### Implication for Product Strategy

**Differentiation opportunity:** Position on trust through transparency rather than competing on accuracy claims that providers will not believe. The unique selling proposition is not "more accurate AI" but "AI that helps you know what to trust."

**Key features:**
- Claim-level source attribution: Every synthesized claim links to its source (original document, patient statement, inference)
- Presence/absence/uncertainty distinction: Visually differentiate "Patient has diabetes" (documented) from "No allergies recorded" (absence of documentation, not documented absence) from "Possibly has hypertension" (uncertain inference)
- Verification workflows: Enable providers to mark claims as verified, building a trust layer over time
- Correction feedback: When providers correct errors, use this to improve future output (the feedback loop participants requested)

**Trade-off to manage:** Transparency vs. cognitive load. Exposing uncertainty and sources adds visual complexity. Design must balance transparency with scannability, perhaps through progressive disclosure (summary view with detail available on hover/click).

---

## 5.3 Theme Cluster: Technology Integration & Multi-Tool Ecosystems

### User Need → Design Principle

**Need:** Providers work within complex ecosystems of existing tools. New technologies must integrate into these ecosystems without demanding wholesale workflow transformation.

**Principle:** *Design for ecosystem membership, not ecosystem replacement.* Accept copy-paste workflows as valid integration patterns. Optimize for interoperability with existing tools rather than requiring direct integration.

### Current Landscape

**AI Scribes:** Successfully adopted through copy-paste integration with EMRs. This "lightweight integration" proves that providers will accept friction if value is clear.

**Practice Management Systems (Jane, OSCAR, Accuro):** Highly fragmented market with hundreds of systems. Direct integration with each is economically impractical; most third-party tools resort to copy-paste or document exchange.

**Health Authority Systems (Cerner, Epic deployments):** Large institutional deployments have integration capabilities but lengthy approval processes, security requirements, and vendor gatekeeping that limit third-party access.

### Gap / Opportunity

**Gaps:**
- Voice AI is emerging as a modality but healthcare-specific implementations remain primitive (lag, interruptions, unnatural interaction patterns)
- Multi-tool workflow orchestration is manual; providers mentally coordinate between tools with no systematic support
- Output formatting remains inconsistent, creating friction in copy-paste workflows

**Opportunity:** Best-in-class copy-paste experience with consistent, EMR-friendly formatting, combined with emerging voice interface that addresses tempo and natural interaction concerns raised by early experimenters.

### Implication for Product Strategy

**Differentiation opportunity:** While competitors pursue EMR integration (slow, expensive, limited), optimize the copy-paste experience that will remain dominant for foreseeable future. Simultaneously invest in voice as the next major modality shift.

**Key features:**
- Format-aware output: Detect target EMR from user settings and generate output optimized for that system's formatting conventions
- One-click copy: Eliminate multi-step copy processes; generate clean text ready for immediate paste
- Voice interface (emerging): Build on early experimenter learnings—match clinical conversation tempo, handle interruptions gracefully, avoid meta-commentary ("I'm going to ask you a second-order question")
- Workflow awareness: Understand multi-tool context (user is preparing for visit in EMR, uploading documents from email, generating summary for scribe)

**Trade-off to manage:** Integration depth vs. breadth. Deep integration with one EMR limits market reach; shallow integration across many preserves market access but limits functionality. The copy-paste optimization strategy maximizes breadth while maintaining functionality.

---

## 5.4 Theme Cluster: Data Consolidation & Interoperability

### User Need → Design Principle

**Need:** Patient information is fragmented across disconnected systems, creating burden for providers and errors for patients. Providers need unified views of patient data regardless of where it was generated.

**Principle:** *Design as a aggregation layer, not a replacement system.* Accept that source systems will not be replaced; create value by synthesizing across them.

### Current Landscape

**Health Information Exchanges:** Technically capable of cross-system sharing but adoption and usability challenges limit practical impact. Providers report that even when data is theoretically available, accessing it efficiently remains difficult.

**Patient Portals (MyChart, others):** Give patients access to their data but in siloed views tied to specific health systems. Patients cannot easily aggregate their own records across providers.

**Personal Health Record attempts:** Multiple efforts (Google Health, Microsoft HealthVault) have failed, though newer entrants (Apple Health Records) show promise in limited contexts.

### Gap / Opportunity

**Gaps:**
- Patient-owned, patient-portable records remain aspirational; no mainstream solution enables patients to carry comprehensive records across providers
- Allied health professionals lack access to hospital systems, creating systematic information gaps
- Community services (radiology, labs, private specialists) remain disconnected islands

**Opportunity:** Patient-mediated aggregation that positions the patient as the data hub. Rather than solving provider-to-provider interoperability (a system-level problem requiring industry coordination), enable patients to aggregate and share their own data, with AI synthesis making the aggregated data clinically useful.

### Implication for Product Strategy

**Differentiation opportunity:** While competitors focus on provider-side integration, build on the patient-mediated transfer that already occurs (patients bringing records, family members relaying information). Formalize and enhance this pattern rather than replacing it.

**Key features:**
- Patient upload and aggregation: Enable patients to upload documents from any source (PDFs, photos of records, lab results)
- AI extraction and synthesis: Transform uploaded documents into structured, searchable, synthesizable data
- Provider access with consent: Allow providers to access patient-aggregated data with appropriate consent mechanisms
- Progressive enrichment: As more touchpoints contribute data, the patient record becomes increasingly comprehensive (the "network effect" participants envisioned)

**Trade-off to manage:** Patient burden vs. provider convenience. Patient-mediated aggregation requires patient effort. Design must minimize this burden through easy upload, OCR of photos, and intelligent extraction that doesn't require patient categorization or annotation.

---

## 5.5 Theme Cluster: Customization & Specialty Variation

### User Need → Design Principle

**Need:** Healthcare is not monolithic; information needs vary dramatically across specialties, practice models, and individual preferences. One-size-fits-all solutions fail to serve diverse users.

**Principle:** *Design for configurable defaults with specialty-specific starting points.* Provide templates optimized for common contexts while enabling full customization.

### Current Landscape

**EHR Templates:** Offer specialty-specific note templates but these are typically static forms rather than adaptive systems. Customization requires IT support and is rarely performed.

**AI Scribes:** Generally offer one-size-fits-all transcription with limited specialty awareness. Some (Nuance, Abridge) offer specialty modules but these are typically add-ons rather than fundamental architecture.

**Clinical Forms (Ocean, Phreesia):** Offer specialty-specific intake forms but without AI adaptation or synthesis.

### Gap / Opportunity

**Gaps:**
- No current tool offers the depth of customization providers described (second-order questions in some areas, minimal in others; specialty-specific information prioritization)
- Allied health needs are systematically underserved; most tools assume physician workflows
- The learning/adaptation capability providers experimented with (training ChatGPT on their own interview patterns) is not available in purpose-built healthcare tools

**Opportunity:** Deeply customizable system with AI learning that adapts to individual provider patterns over time. This addresses both initial fit (through specialty templates) and ongoing refinement (through learning from corrections).

### Implication for Product Strategy

**Differentiation opportunity:** Customization depth as competitive moat. While competitors offer surface-level configuration, build fundamentally configurable architecture that allows providers to shape every aspect of information collection and presentation.

**Key features:**
- Specialty templates: Out-of-box configurations for major specialties (family medicine, surgery, internal medicine, allied health)
- Provider learning: System learns from corrections over time, adapting output to individual preferences
- Branching question logic: Configurable conversation flows with mandatory questions, optional exploration, and depth limits by topic area
- Role-specific views: Different summaries for different team members seeing the same patient (surgeon vs. anesthesiologist vs. nurse)

**Trade-off to manage:** Customization power vs. usability. Deep customization can create complexity that deters adoption. Design should offer powerful customization to those who want it while maintaining usable defaults for those who don't.

---

## 5.6 Theme Cluster: Business Model & Economic Structures

### User Need → Design Principle

**Need:** Providers operate within economic structures that shape what activities are viable. Tools must deliver value that can be captured within existing (or achievable) payment models.

**Principle:** *Design for economic alignment, creating value that providers can monetize.* Understand billing codes and payment structures; optimize for activities that generate revenue or reduce costs.

### Current Landscape

**AI Scribes:** Successfully monetized through subscription ($50-150/month) justified by time savings that translate to additional patient volume (fee-for-service) or reduced overtime (salaried). Clear ROI calculation.

**Practice Management Tools:** Subscription models tied to practice size. Value proposition typically around revenue cycle management (billing optimization) rather than clinical efficiency.

**Health Authority Deployments:** Enterprise sales to health systems, often tied to quality improvement or cost reduction metrics. Longer sales cycles, larger deals.

### Gap / Opportunity

**Gaps:**
- Pre-visit preparation has unclear monetization path in fee-for-service models (providers can't bill for preparation time)
- Allied health billing constraints ($23/visit MSP) create severe price sensitivity
- Asynchronous care billing opportunities exist but are underutilized; tools could facilitate billing for currently un-billed activities

**Opportunity:** Design features that enable providers to capture value from previously un-billed activities. The asynchronous care model described by participants—where reviewing wait-list patients creates billable interactions—represents an untapped revenue stream that the right tool could unlock.

### Implication for Product Strategy

**Differentiation opportunity:** Revenue enablement rather than just efficiency. Position not only as time-saving tool but as revenue-generating tool by facilitating billable activities.

**Key features:**
- Asynchronous care workflows: Support for reviewing patient information, ordering tests, and communicating with patients—all billable activities—outside of scheduled appointments
- Billing code awareness: Understand which activities are billable; prompt providers when billable actions are available
- ROI documentation: Provide practices with data on time saved, additional patients seen, or billable activities enabled for budget justification
- Tiered pricing: Price sensitivity varies (physician vs. allied health, solo vs. group, fee-for-service vs. salaried); offer pricing tiers that capture value appropriately

**Trade-off to manage:** Revenue focus vs. care focus. Optimizing for billable activities could distort care toward what's reimbursable rather than what's needed. Design should enable revenue capture without incentivizing inappropriate care.

---

## 5.7 Theme Cluster: Clinical Information Needs & Nuance

### User Need → Design Principle

**Need:** Clinical data collection requires precise symptom characterization, adaptive follow-up questioning, and capture of specific data types (medications, social history, surgical history) that are frequently incomplete or inaccurate.

**Principle:** *Design for clinical conversation, not form completion.* Implement branching logic that adapts to patient responses, pursues clinical nuance, and ensures completeness of critical data elements.

### Current Landscape

**Digital Intake Forms (Phreesia, Klara):** Collect structured data but with static questions that cannot adapt based on responses. Miss the clinical nuance that conversational assessment captures.

**Conversational AI (general-purpose):** ChatGPT and similar tools can conduct adaptive conversations but lack healthcare-specific knowledge, HIPAA compliance, and clinical validation.

**Emerging Healthcare Conversational AI:** Early-stage companies building healthcare-specific conversational intake, but most remain limited to simple question sequences.

### Gap / Opportunity

**Gaps:**
- True clinical conversation with branching logic remains unavailable in production healthcare tools
- Medication reconciliation from diverse sources (pharmacy, OTC, naturopathic) is not systematically supported
- Social determinants of health are rarely collected in structured, usable formats
- Symptom specificity ("all the time" vs. "most of the time") is lost in form-based collection

**Opportunity:** Clinically-intelligent conversational intake that implements the second-order and third-order questioning logic that expert clinicians use. This captures nuance that forms miss while reducing patient burden compared to comprehensive written questionnaires.

### Implication for Product Strategy

**Differentiation opportunity:** Clinical depth that competitors lack. While others offer conversational interfaces, build true clinical conversation capability with specialty-specific question trees, branching logic, and nuance detection.

**Key features:**
- Branching conversation trees: When patient indicates heart disease history, automatically probe for specifics (type, treatment, anticoagulation)
- Nuance detection: Recognize and clarify imprecise answers ("all the time" → "Can you tell me more about when symptoms are worst or best?")
- Multi-source medication reconciliation: Prompt for all medication sources, not just prescriptions
- Social determinants capture: Systematically collect housing, finances, support system in clinically useful structure
- Clinical validation: Validate conversation logic with clinical experts; demonstrate equivalence or superiority to clinician interviewing

**Trade-off to manage:** Comprehensiveness vs. burden. More thorough questioning improves clinical value but increases patient time. Implement adaptive depth—go deep where responses indicate complexity, stay brief where everything is normal.

---

## 5.8 Theme Cluster: Care Context & Setting Variation

### User Need → Design Principle

**Need:** Information needs vary dramatically by care setting (emergency vs. scheduled), encounter type (first visit vs. follow-up), and provider role (specialist vs. primary care). The same tool must serve different contexts differently.

**Principle:** *Design for context-awareness, adapting presentation and depth to the specific care scenario.* Don't force users to manually configure for each encounter; infer context and adapt automatically.

### Current Landscape

**EHR Views:** Typically offer one standard view regardless of encounter context. Some systems offer "shortcuts" or "favorites" but these require manual configuration.

**Specialty-Specific Tools:** Anesthesia systems, emergency department systems, and others offer context-specific views but are siloed—emergency providers can't access the anesthesia view for a patient who recently had surgery.

**AI Tools:** Generally context-blind, offering the same output regardless of whether it's an emergency visit or scheduled follow-up.

### Gap / Opportunity

**Gaps:**
- No tool offers context-adaptive presentation that automatically adjusts based on encounter type
- Emergency settings have the most acute information needs but the least tool support
- Team-based care coordination (multiple providers seeing patient same day) lacks systematic support

**Opportunity:** Context-aware AI that recognizes the care scenario and adapts accordingly. Emergency visit triggers rapid-scan summary; first consultation provides comprehensive history; follow-up highlights changes since last visit.

### Implication for Product Strategy

**Differentiation opportunity:** Context intelligence that competitors lack. While others require manual configuration, automatically adapt to care context.

**Key features:**
- Encounter type detection: Infer from scheduling system, user selection, or explicit query whether this is emergency, follow-up, new consult, etc.
- Context-adaptive summarization: Different summary depths and structures for different contexts
- Change highlighting for follow-ups: Show what's changed since last visit rather than repeating stable history
- Team view coordination: When multiple providers access same patient same day, show what each has already reviewed/documented

**Trade-off to manage:** Automation vs. control. Automatic context detection may be wrong; provide easy override when the system's inference doesn't match the actual situation.

---

## 5.9 Theme Cluster: Patient Experience & Accessibility

### User Need → Design Principle

**Need:** Patients are the ultimate source of much health information, yet data collection processes often burden rather than support them. Diverse patient populations require accessible, multilingual, multimodal interfaces.

**Principle:** *Design for patient respect and accessibility.* Reduce burden, accommodate diversity, and treat data collection as a care experience, not an administrative extraction.

### Current Landscape

**Patient Portals:** Primarily designed for information access rather than input. Intake forms are typically afterthoughts, not optimized experiences.

**Digital Intake (Phreesia):** Focuses on administrative efficiency (insurance verification, demographics) more than clinical data quality.

**Multilingual Support:** Generally limited to static form translation; adaptive conversation in non-English languages is rare.

### Gap / Opportunity

**Gaps:**
- Conversational intake in patient's preferred language with AI translation for provider is not available
- Voice interfaces for patients with literacy challenges remain unexplored in healthcare intake
- Pre-filling from known information is limited; patients re-enter the same information repeatedly

**Opportunity:** Patient-centered intake that treats data collection as the first touchpoint of care—accessible, respectful, and efficient. This improves both patient experience and data quality (engaged patients provide better information).

### Implication for Product Strategy

**Differentiation opportunity:** Patient experience as provider selling point. While competitors focus on provider efficiency, demonstrate that better patient experience yields better data and better outcomes—making patient-centricity a provider-facing value proposition.

**Key features:**
- Multilingual AI conversation: Conduct intake in patient's preferred language; provide provider summary in English
- Voice option: Allow patients to speak responses rather than type, improving accessibility and reducing burden
- Smart pre-filling: Automatically populate known information; ask only for updates and new information
- Progress indication: Show patients how much remains, reducing anxiety and abandonment
- Respect and acknowledgment: Conversational elements that acknowledge patient concerns and validate their experience

**Trade-off to manage:** Accessibility features vs. implementation complexity. Multilingual and voice capabilities require significant investment. Prioritize based on patient population needs—practices serving diverse populations will value these highly; homogeneous populations may not justify the complexity.

---

# 6. CONCLUSION

This qualitative analysis of healthcare provider perspectives on AI-enabled data tools reveals a complex landscape where technology must navigate economic structures, professional accountability requirements, fragmented systems, and profound variation in user needs. The nine themes identified—from workflow efficiency to patient experience—collectively describe an ecosystem that resists simple solutions.

The path to successful healthcare AI is not through revolutionary transformation but through thoughtful integration: tools that enhance rather than replace existing workflows, build trust through transparency rather than demanding blind acceptance, and adapt to context rather than imposing uniformity. The providers in this study are not resistant to technology; they are sophisticated evaluators who will adopt tools that demonstrably improve their work and their patients' care.

The design implications outlined above provide a roadmap for building such tools. By grounding product decisions in the authentic voices and needs of healthcare providers, development can proceed with confidence that resulting solutions will create genuine value—for providers, for patients, and for the healthcare system that serves them both.

---

## References

Sinsky, C., Colligan, L., Li, L., Prgomet, M., Reynolds, S., Goeders, L., Westbrook, J., Tutty, M., & Blike, G. (2016). Allocation of Physician Time in Ambulatory Practice: A Time and Motion Study in 4 Specialties. *Annals of Internal Medicine*, 165(11), 753-760.

---

*Document prepared based on thematic analysis of 22 provider interview transcripts. All participant quotes are anonymized. Analysis conducted November 2024.*
