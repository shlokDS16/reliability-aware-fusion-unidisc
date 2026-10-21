"""Cover letter for Paper 1 in the format of the author's sample letter (Diffusion Model Audit/cover_letter.pdf).
Every number repeats the manuscript. Writes research/COVER-LETTER-paper1.docx.
    python research/make_cover_letter.py   (from the repository root)
"""
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Cm

OUT = Path(__file__).resolve().parent / "COVER-LETTER-paper1-ACM.docx"
d = Document()
for s in d.sections:
    s.top_margin = s.bottom_margin = Cm(1.5)
    s.left_margin = s.right_margin = Cm(2.0)
st = d.styles["Normal"]
st.font.name = "Times New Roman"
st.font.size = Pt(10.5)
st.paragraph_format.space_after = Pt(4)


def para(text="", bold=False, after=6, align=None):
    p = d.add_paragraph()
    p.paragraph_format.space_after = Pt(after)
    if align:
        p.alignment = align
    if text:
        r = p.add_run(text)
        r.bold = bold
    return p


def block(lines):
    for i, l in enumerate(lines):
        para(l, after=0 if i < len(lines) - 1 else 10)


block(["Prof. Subramaniyaswamy Vairavasundaram",
       "School of Computer Science and Engineering",
       "Vellore Institute of Technology, Vellore, Tamil Nadu 632014, India",
       "subramaniyaswamy.v@vit.ac.in"])
para("21 October 2026", after=10)
block(["The Editor-in-Chief", "ACM Computing Surveys"])
p = para(after=10)
p.add_run("Subject: ").bold = True
p.add_run("Submission of the manuscript \"Diffusion Language Models and Unified Multimodal Generation: A Critical "
          "Systematic Review of Discrete and Continuous Approaches\"")
para("Dear Editor-in-Chief,", after=4)
para("On behalf of all authors, I am pleased to submit this manuscript as a long survey paper to ACM Computing Surveys.",
     after=8)
para("Diffusion language models, and unified models that also generate images, are a fast-growing alternative to "
     "autoregressive generation, yet their reported results depend heavily on how they are decoded, and papers rarely "
     "state the decoding rule behind a headline number. Building on a systematic search of 79,963 records and 615 included "
     "studies, the survey makes the following technical contributions.")
para("Contributions and key findings:", bold=True, after=2)
items = [
    ("A design space that organises the field. ",
     "Every generator is described by five design choices, from the corruption channel to the commitment and revision "
     "rules; the design space places all 47 models tested, 36 fully and 11 with a stated extension."),
    ("A reporting gap with direct consequences. ",
     "A census of a random sample of papers finds that 147 of 153 report their headline result with a decoding rule "
     "other than plain sampling or do not state the rule, so many cross-paper comparisons are not like for like."),
    ("Evidence synthesis with explicit verdicts. ",
     "Comparisons with autoregressive models are split and only 1 of 25 is compute-matched, training gains are rarely "
     "isolated, and more inference compute helps most curves in 9 of 15 sweeping studies; each verdict is tested for "
     "robustness."),
    ("Practical guidance and open problems. ",
     "An error budget classifies methods by the error they change; a decision framework, a reporting checklist and open "
     "problems with the measurements that would settle them complete the review."),
]
for lead, rest in items:
    q = d.add_paragraph(style="List Bullet")
    q.paragraph_format.space_after = Pt(3)
    q.add_run(lead).bold = True
    q.add_run(rest)
para("We believe the work suits the broad readership of ACM Computing Surveys across natural language processing, "
     "generative modelling and multimodal learning, serving both researchers entering the area and practitioners "
     "choosing a model or decoder. The main paper is 34 pages including references in the ACM Surveys format, with a "
     "marked electronic supplement. The protocol, records, analysis scripts and manuscript sources are archived at "
     "https://doi.org/10.5281/zenodo.23524470, so every reported number can be reproduced.")
para("We confirm that this manuscript is original, has not been published previously, and is not under consideration "
     "for publication elsewhere; an earlier version of its sources is part of the data archive above, not of any "
     "journal, proceedings or preprint server. All authors have approved the manuscript and agree with its submission. "
     "The review analyses published literature only; no human participants were involved. The use of AI tools is "
     "described in the manuscript's Declaration on the use of AI. No funding was received; the article processing "
     "charge is covered by Vellore Institute of Technology, Vellore, India, and the authors declare no conflicts of "
     "interest.")
para("Thank you for considering our manuscript. We look forward to your response.", after=6)
para("Yours sincerely,", after=8)
para("Prof. Subramaniyaswamy Vairavasundaram (Corresponding Author)", after=0)
para("on behalf of Shlok Goenka and Balaji G N", after=0)
for p in d.paragraphs:
    if p.alignment is None:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY if len(p.text) > 120 else None
d.save(OUT)
print("wrote", OUT)
