import factory.random
from faker.providers import BaseProvider


class ConditionProvider(BaseProvider):
    __provider__ = "condition_name"

    def condition_name(self):
        return factory.random.randgen.choice(condition_names)


condition_names = [
    "Osteoarthritis",
    "Hyperlipidemia (High cholesterol)",
    "Influenza (Flu)",
    "Essential hypertension (High blood pressure)",
    "Hypothyroidism",
    "Alzheimer's disease",
    "Type 2 diabetes mellitus",
    "Cataract",
    "Allergy to pollen",
    "Chronic kidney disease (Stage 3)",
    "Bipolar disorder",
    "Coronary heart disease",
    "Major depressive disorder",
    "Anemia",
    "Carotid artery stenosis",
    "Benign prostatic hyperplasia (BPH)",
    "Attention deficit hyperactivity disorder (ADHD)",
    "Acute bronchitis",
    "Migraine",
    "Eczema (Atopic dermatitis)",
    "Generalized anxiety disorder (GAD)",
    "Thyroid nodule",
    "Iron deficiency anemia",
    "Chronic hepatitis C",
    "Acute otitis media (Middle ear infection)",
    "Irritable bowel syndrome (IBS)",
    "Post-traumatic stress disorder (PTSD)",
    "Chronic lower back pain",
    "Chronic pain",
    "Pneumonia",
    "Acute pharyngitis (Strep throat/Sore throat)",
    "Fibromyalgia",
    "Chronic obstructive pulmonary disease (COPD)",
    "Allergic rhinitis (Hay fever)",
    "Urinary tract infection (UTI)",
    "Obesity",
    "Vertigo (Vestibular disorder)",
    "Asthma",
    "Gout",
    "Gastroesophageal reflux disease (GERD)",
]
