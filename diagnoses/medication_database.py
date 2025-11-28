"""
Comprehensive Evidence-Based Medication Database
Based on WHO Guidelines, Uganda Clinical Guidelines, and International Standards
"""

MEDICATION_DATABASE = {
    "Malaria": {
        "uncomplicated": [
            {
                "name": "Artemether-Lumefantrine (Coartem)",
                "dosage": "Adult: 4 tablets (80mg/480mg) at 0, 8, 24, 36, 48, 60 hours | Child: Weight-based - 5-14kg: 1 tablet per dose, 15-24kg: 2 tablets, 25-34kg: 3 tablets",
                "duration": "3 days (6 doses total)",
                "instructions": "Take with fatty food or milk to enhance absorption. Complete full course even if symptoms improve. Avoid grapefruit juice.",
                "contraindications": "First trimester pregnancy, severe hepatic impairment, QT prolongation",
                "monitoring": "Monitor for headache, dizziness, palpitations. Check parasitemia on Day 3.",
                "source": "WHO Malaria Treatment Guidelines 2023, Uganda Essential Medicines List"
            },
            {
                "name": "Artesunate-Amodiaquine (ASAQ)",
                "dosage": "Adult: AS 200mg + AQ 540mg once daily | Child: Weight-based dosing",
                "duration": "3 days",
                "instructions": "Take with water, preferably after food. Avoid antacids within 2 hours.",
                "contraindications": "Severe malaria, known hypersensitivity",
                "source": "WHO ACT Policy 2023"
            },
            {
                "name": "Dihydroartemisinin-Piperaquine",
                "dosage": "Once daily for 3 days, weight-based tablets",
                "duration": "3 days",
                "instructions": "Take without food (at least 3 hours after last meal). Effective for areas with AL resistance.",
                "source": "WHO Alternative ACT Recommendation"
            }
        ],
        "severe": [
            {
                "name": "Artesunate IV/IM",
                "dosage": "2.4 mg/kg IV or IM at 0, 12, 24 hours, then once daily",
                "duration": "Minimum 24 hours IV, then complete 3 days with oral ACT",
                "instructions": "EMERGENCY - Immediate hospitalization required. Reconstitute with 5% sodium bicarbonate. Monitor glucose every 4-6 hours (risk of hypoglycemia).",
                "monitoring": "Blood glucose, hemoglobin, renal function, parasitemia",
                "complications": "Watch for delayed hemolysis (7-14 days post-treatment)",
                "source": "WHO Guidelines for Severe Malaria 2023"
            },
            {
                "name": "Quinine IV (if artesunate unavailable)",
                "dosage": "Loading: 20mg/kg over 4 hours, then 10mg/kg every 8 hours",
                "duration": "Until oral therapy possible, complete 7 days total",
                "instructions": "Dilute in normal saline or 5% dextrose. Monitor for hypoglycemia and cinchonism.",
                "contraindications": "Myasthenia gravis, optic neuritis",
                "source": "WHO Alternative for Severe Malaria"
            }
        ],
        "supportive": [
            "Paracetamol 15mg/kg every 6 hours for fever (max 4g/day adults)",
            "Oral Rehydration Solution or IV fluids if unable to drink",
            "Tepid sponging for high fever",
            "Anticonvulsants (diazepam) if seizures occur"
        ],
        "prevention": [
            "Sulfadoxine-Pyrimethamine for pregnant women (IPTp)",
            "Insecticide-treated bed nets",
            "Indoor residual spraying"
        ]
    },

    "Pneumonia": {
        "mild_community": [
            {
                "name": "Amoxicillin",
                "dosage": "Adult: 500-1000mg TID | Child: 40-50mg/kg/day divided TID (max 3g/day)",
                "duration": "5-7 days",
                "instructions": "Can take with or without food. Complete full course to prevent resistance.",
                "contraindications": "Penicillin allergy, infectious mononucleosis",
                "source": "WHO Pneumonia Guidelines, IDSA CAP Guidelines"
            },
            {
                "name": "Azithromycin (if atypical suspected)",
                "dosage": "Adult: 500mg Day 1, then 250mg Days 2-5 | Child: 10mg/kg Day 1, then 5mg/kg Days 2-5",
                "duration": "5 days",
                "instructions": "Take on empty stomach (1 hour before or 2 hours after meals). Good for Mycoplasma/Chlamydia.",
                "source": "IDSA Atypical Pneumonia Guidelines"
            }
        ],
        "moderate": [
            {
                "name": "Amoxicillin-Clavulanate",
                "dosage": "Adult: 875mg/125mg BID or 500mg/125mg TID | Child: 45mg/kg/day divided BID",
                "duration": "7-10 days",
                "instructions": "Take with food to reduce GI upset. Better gram-negative and β-lactamase coverage.",
                "monitoring": "Liver function if prolonged use",
                "source": "WHO Hospital Care for Children"
            },
            {
                "name": "Cefuroxime",
                "dosage": "Adult: 500mg BID | Child: 20-30mg/kg/day divided BID",
                "duration": "7-10 days",
                "instructions": "Second-generation cephalosporin. Good alternative if penicillin allergy.",
                "source": "Uganda Clinical Guidelines"
            }
        ],
        "severe": [
            {
                "name": "Ceftriaxone IV",
                "dosage": "Adult: 1-2g once daily | Child: 50-75mg/kg/day (max 2g/day)",
                "duration": "7-14 days",
                "instructions": "IV administration. Hospitalization required. Can switch to oral after clinical improvement (48-72 hours afebrile).",
                "monitoring": "Respiratory rate, oxygen saturation, chest X-ray",
                "source": "WHO Severe Pneumonia Protocol"
            },
            {
                "name": "Ceftriaxone + Azithromycin (severe CAP)",
                "dosage": "Ceftriaxone 1-2g daily IV + Azithromycin 500mg daily",
                "duration": "7-10 days",
                "instructions": "Combination for severe community-acquired pneumonia. Covers typical and atypical pathogens.",
                "source": "IDSA/ATS Severe CAP Guidelines"
            }
        ],
        "aspiration": [
            {
                "name": "Ampicillin-Sulbactam or Amoxicillin-Clavulanate",
                "dosage": "Ampicillin-Sulbactam 1.5-3g IV every 6 hours",
                "duration": "10-14 days",
                "instructions": "Covers anaerobes and gram-negatives. For witnessed aspiration or risk factors.",
                "source": "Aspiration Pneumonia Guidelines"
            }
        ],
        "supportive": [
            "Oxygen therapy if SpO2 <90%",
            "IV fluids if dehydrated",
            "Chest physiotherapy",
            "Paracetamol for fever and pain"
        ]
    },

    "Upper Respiratory Tract Infection": {
        "viral": [
            {
                "name": "Supportive Care Only (NO Antibiotics)",
                "dosage": "N/A",
                "duration": "Symptomatic relief, 5-7 days recovery",
                "instructions": "REST is essential. Antibiotics NOT effective for viral infections and promote resistance. Symptoms typically resolve in 7-10 days.",
                "red_flags": "Seek immediate care if: fever >39°C for >3 days, difficulty breathing, severe headache, rash, confusion",
                "source": "WHO Antimicrobial Stewardship Guidelines, CDC"
            },
            {
                "name": "Paracetamol (Acetaminophen)",
                "dosage": "Adult: 500-1000mg every 4-6 hours (max 4g/day) | Child: 10-15mg/kg every 4-6 hours (max 5 doses/day)",
                "duration": "3-5 days as needed",
                "instructions": "For fever and sore throat pain. Take with food if stomach upset. Do NOT exceed maximum dose.",
                "contraindications": "Severe liver disease",
                "source": "WHO Pain Management Guidelines"
            },
            {
                "name": "Ibuprofen",
                "dosage": "Adult: 400mg every 6-8 hours (max 1200mg/day) | Child >6 months: 5-10mg/kg every 6-8 hours",
                "duration": "3-5 days",
                "instructions": "Take with food. Better anti-inflammatory than paracetamol. Avoid in asthma, peptic ulcer.",
                "contraindications": "Peptic ulcer, severe kidney disease, pregnancy (3rd trimester)",
                "source": "Standard Practice"
            }
        ],
        "bacterial_pharyngitis": [
            {
                "name": "Amoxicillin (for Strep throat)",
                "dosage": "Adult: 500mg TID or 1000mg BID | Child: 50mg/kg/day divided BID-TID (max 1g/day)",
                "duration": "10 days (important to complete)",
                "instructions": "Only if rapid strep test positive or strong clinical suspicion. Complete 10 days to prevent rheumatic fever.",
                "indication": "Centor criteria ≥3: fever, tonsillar exudate, tender lymph nodes, no cough",
                "source": "IDSA Group A Streptococcal Pharyngitis Guidelines"
            },
            {
                "name": "Azithromycin (if penicillin allergy)",
                "dosage": "Adult: 500mg Day 1, then 250mg Days 2-5 | Child: 12mg/kg once daily",
                "duration": "5 days",
                "instructions": "Alternative for penicillin-allergic patients.",
                "source": "IDSA Guidelines"
            }
        ],
        "sinusitis": [
            {
                "name": "Amoxicillin-Clavulanate (if bacterial sinusitis)",
                "dosage": "Adult: 875/125mg BID | Child: 45mg/kg/day divided BID",
                "duration": "7-10 days",
                "instructions": "Only prescribe if symptoms >10 days or severe (fever >39°C, purulent discharge, facial pain). Most sinusitis is viral.",
                "indication": "Symptoms >10 days without improvement OR severe symptoms OR worsening after initial improvement",
                "source": "IDSA Sinusitis Guidelines"
            }
        ],
        "home_remedies": [
            "Warm salt water gargling (1/2 tsp salt in warm water, 3-4 times daily)",
            "Steam inhalation with eucalyptus oil",
            "Honey and lemon in warm water for cough",
            "Adequate hydration (8-10 glasses water/day)",
            "Humidifier in bedroom",
            "Throat lozenges for sore throat"
        ]
    },

    "Typhoid Fever": {
        "first_line": [
            {
                "name": "Ceftriaxone",
                "dosage": "Adult: 2g once daily IV/IM | Child: 75mg/kg once daily (max 2g)",
                "duration": "7-14 days depending on severity",
                "instructions": "First-line for MDR (multi-drug resistant) typhoid. IV or IM administration. Most effective in endemic areas.",
                "monitoring": "Blood culture, temperature chart, abdominal examination",
                "source": "WHO Typhoid Treatment Guidelines 2023"
            },
            {
                "name": "Azithromycin",
                "dosage": "Adult: 500mg-1g once daily | Child: 10-20mg/kg once daily (max 1g)",
                "duration": "5-7 days",
                "instructions": "Effective for uncomplicated typhoid. Take on empty stomach. Good compliance with shorter duration.",
                "advantages": "Oral administration, shorter course, fewer side effects",
                "source": "WHO Guidelines for Endemic Areas"
            }
        ],
        "alternative": [
            {
                "name": "Ciprofloxacin",
                "dosage": "Adult: 500mg BID | NOT recommended for children <18 years",
                "duration": "7-10 days",
                "instructions": "Check local resistance patterns before use. Increasing resistance in South Asia and East Africa.",
                "contraindications": "Pregnancy, breastfeeding, children <18 years (affects cartilage)",
                "resistance_warning": "High resistance in many endemic areas - sensitivity testing recommended",
                "source": "Uganda Clinical Guidelines (use with caution)"
            },
            {
                "name": "Cefixime (oral)",
                "dosage": "Adult: 400mg BID | Child: 20mg/kg/day divided BID",
                "duration": "7-14 days",
                "instructions": "Oral cephalosporin alternative. Good for step-down therapy after IV ceftriaxone.",
                "source": "WHO Alternative Regimen"
            }
        ],
        "severe_complicated": [
            {
                "name": "Ceftriaxone + Azithromycin (combination)",
                "dosage": "Standard doses for each",
                "duration": "14 days",
                "instructions": "For severe typhoid with complications (intestinal perforation, hemorrhage, encephalopathy). ICU care may be needed.",
                "complications": "Monitor for perforation, GI bleeding, encephalopathy",
                "source": "WHO Severe Typhoid Protocol"
            }
        ],
        "supportive": [
            "IV fluids for dehydration",
            "Paracetamol for fever (avoid NSAIDs - bleeding risk)",
            "Nutritional support (soft diet)",
            "Bed rest",
            "Monitor for complications: perforation, bleeding"
        ],
        "prevention": [
            "Typhoid conjugate vaccine (TCV)",
            "Hygiene: handwashing, safe water",
            "Food safety practices"
        ]
    },

    "Meningitis": {
        "bacterial_suspected": [
            {
                "name": "Ceftriaxone IV",
                "dosage": "Adult: 2g every 12 hours | Child: 100mg/kg/day divided every 12 hours (max 4g/day)",
                "duration": "10-14 days (varies by organism)",
                "instructions": "EMERGENCY - Immediate hospitalization and ICU care required. Start antibiotics within 30 minutes of presentation. Do lumbar puncture before antibiotics if possible, but DO NOT delay treatment.",
                "monitoring": "Neurological status every hour, Glasgow Coma Scale, signs of increased intracranial pressure",
                "source": "WHO Meningitis Guidelines 2023, IDSA Bacterial Meningitis"
            },
            {
                "name": "Ceftriaxone + Vancomycin (if drug-resistant pneumococcus)",
                "dosage": "Ceftriaxone 2g IV Q12H + Vancomycin 15-20mg/kg IV Q8-12H",
                "duration": "10-14 days",
                "instructions": "For suspected drug-resistant Streptococcus pneumoniae. Requires therapeutic drug monitoring for vancomycin.",
                "monitoring": "Vancomycin trough levels, renal function",
                "source": "IDSA Meningitis Guidelines for Drug-Resistant Organisms"
            },
            {
                "name": "Ampicillin (add if Listeria suspected - elderly/immunocompromised)",
                "dosage": "Adult: 2g IV every 4 hours | Child: 200-400mg/kg/day divided Q6H",
                "duration": "14-21 days",
                "instructions": "Add to ceftriaxone if age >50 years, immunocompromised, or pregnant. Listeria not covered by cephalosporins.",
                "source": "WHO Listeria Meningitis Protocol"
            }
        ],
        "viral_meningitis": [
            {
                "name": "Supportive Care (NO Antibiotics for Viral)",
                "dosage": "N/A",
                "duration": "7-14 days recovery",
                "instructions": "Most viral meningitis resolves spontaneously. Hospitalization for observation and symptom management. Antibiotics NOT effective for viral infections.",
                "supportive_measures": "IV fluids, pain control, fever management, quiet dark room",
                "source": "WHO Viral Meningitis Management"
            },
            {
                "name": "Acyclovir IV (if Herpes Simplex Virus suspected)",
                "dosage": "Adult: 10mg/kg IV every 8 hours | Child: 20mg/kg IV every 8 hours",
                "duration": "14-21 days",
                "instructions": "Start immediately if HSV meningitis/encephalitis suspected. Critical for preventing brain damage.",
                "monitoring": "Renal function (nephrotoxic), adequate hydration",
                "source": "IDSA HSV Encephalitis Guidelines"
            }
        ],
        "emergency_treatment": [
            "IMMEDIATE: Airway, Breathing, Circulation (ABC)",
            "Blood cultures BEFORE antibiotics (if possible, but don't delay)",
            "Lumbar puncture for CSF analysis (if no contraindications)",
            "IV Dexamethasone 0.15mg/kg Q6H for 2-4 days (given before or with first antibiotic dose)",
            "Manage increased intracranial pressure (elevate head 30°, hyperventilation if needed)",
            "IV fluids for resuscitation",
            "Isolate patient (droplet precautions for first 24 hours of antibiotics)"
        ],
        "supportive": [
            "IV fluids to maintain euvolemia",
            "Paracetamol for fever and headache",
            "Anticonvulsants if seizures (Lorazepam, Phenytoin)",
            "Quiet, dark environment",
            "Frequent neurological assessments",
            "Contact tracing and prophylaxis for close contacts (Rifampin or Ciprofloxacin)"
        ],
        "prevention": [
            "Meningococcal vaccine (MenACWY, MenB)",
            "Pneumococcal vaccine (PCV13, PPSV23)",
            "Hib vaccine (Haemophilus influenzae type b)",
            "Avoid sharing drinks, utensils, close contact with infected persons"
        ],
        "monitoring": [
            "Neurological examination every 1-2 hours initially",
            "Glasgow Coma Scale",
            "Signs of increased ICP: headache, vomiting, altered consciousness, papilledema",
            "Seizure activity",
            "Hearing assessment (post-recovery - common complication)"
        ]
    },

    "Gastroenteritis": {
        "viral": [
            {
                "name": "Oral Rehydration Solution (ORS)",
                "dosage": "Adults: 200-400ml after each loose stool | Children: 50-100ml/kg over 4 hours",
                "duration": "Until symptoms resolve (typically 3-5 days)",
                "instructions": "PRIMARY TREATMENT. Most gastroenteritis is viral and self-limiting. Antibiotics NOT needed. Mix ORS sachet in 1 liter clean water.",
                "source": "WHO Gastroenteritis Management Guidelines 2023"
            },
            {
                "name": "Zinc Sulfate (Children <5 years)",
                "dosage": "Infants <6 months: 10mg daily | Children 6mo-5yr: 20mg daily",
                "duration": "10-14 days",
                "instructions": "Reduces duration and severity. Continue for full 14 days even after diarrhea stops.",
                "source": "WHO/UNICEF Diarrhea Treatment"
            },
            {
                "name": "Probiotics (optional)",
                "dosage": "Lactobacillus rhamnosus or Saccharomyces boulardii - as per product label",
                "duration": "5-7 days",
                "instructions": "May reduce duration of symptoms by 1 day. Not essential but can be beneficial.",
                "source": "Cochrane Review on Probiotics for Acute Gastroenteritis"
            }
        ],
        "bacterial_dysentery": [
            {
                "name": "Ciprofloxacin (if blood in stool)",
                "dosage": "Adult: 500mg BID | Child: 15mg/kg BID (max 500mg)",
                "duration": "3-5 days",
                "instructions": "Only for BLOODY diarrhea (dysentery). Indicates bacterial infection (Shigella, Campylobacter, Salmonella). Continue ORS therapy.",
                "source": "WHO Dysentery Guidelines"
            },
            {
                "name": "Azithromycin (alternative or if ciprofloxacin resistance)",
                "dosage": "Adult: 500mg once daily | Child: 10mg/kg once daily",
                "duration": "3 days",
                "instructions": "Alternative for dysentery. Safer in children. Effective for Shigella and Campylobacter.",
                "source": "WHO Alternative Dysentery Treatment"
            }
        ],
        "supportive": [
            "Oral rehydration is PRIMARY treatment",
            "IV fluids only if severe dehydration or unable to drink",
            "Continue breastfeeding (infants)",
            "BRAT diet not recommended - continue age-appropriate foods",
            "Paracetamol for fever if needed",
            "Avoid anti-diarrheal medications (loperamide) in children or bloody diarrhea"
        ],
        "prevention": [
            "Handwashing with soap and water",
            "Safe food preparation and storage",
            "Clean drinking water",
            "Rotavirus vaccine for infants",
            "Proper sanitation and hygiene"
        ],
        "red_flags": [
            "Blood in stool → May need antibiotics",
            "Severe dehydration (sunken eyes, no tears, dry mouth) → IV fluids",
            "High fever >39°C persisting >3 days → Investigate for other causes",
            "Severe abdominal pain → Rule out appendicitis, intussusception",
            "No urine for 6-8 hours → Severe dehydration"
        ]
    },

    "Diarrhea": {
        "acute_watery": [
            {
                "name": "Oral Rehydration Solution (ORS)",
                "dosage": "Adults: 200-400ml after each loose stool | Children: Plan A (50-100ml/kg over 4 hours), Plan B (75ml/kg over 4 hours)",
                "duration": "Until diarrhea stops",
                "instructions": "PRIMARY TREATMENT. Mix 1 sachet in 1 liter clean water. Sip frequently. Continue normal feeding. Most diarrhea needs ONLY ORS.",
                "preparation": "WHO ORS formula: Low osmolarity (Sodium 75 mEq/L, Glucose 75 mmol/L)",
                "source": "WHO Diarrhea Treatment Guidelines 2023"
            },
            {
                "name": "Zinc Sulfate (Children <5 years)",
                "dosage": "Infants <6 months: 10mg daily | Children 6mo-5yr: 20mg daily",
                "duration": "10-14 days (continue even after diarrhea stops)",
                "instructions": "Reduces severity and duration by 25%. Prevents recurrence for 2-3 months. Dispersible tablet in water or breastmilk.",
                "evidence": "Reduces mortality by 50% in developing countries",
                "source": "WHO/UNICEF Joint Statement on Zinc Supplementation"
            }
        ],
        "persistent": [
            {
                "name": "Continue ORS + Zinc",
                "dosage": "Same as acute",
                "duration": "Zinc for full 14 days",
                "instructions": "Diarrhea >14 days needs investigation. Check for: parasites (Giardia), lactose intolerance, malabsorption.",
                "investigation": "Stool microscopy, culture, HIV testing if applicable",
                "source": "WHO Persistent Diarrhea Protocol"
            }
        ],
        "dysentery": [
            {
                "name": "Ciprofloxacin",
                "dosage": "Adult: 500mg BID | Child: 15mg/kg BID (max 500mg)",
                "duration": "3-5 days",
                "instructions": "Only for BLOODY diarrhea (dysentery). Indicates bacterial infection (Shigella). Still give ORS + Zinc.",
                "indication": "Blood in stool, high fever, severe abdominal pain",
                "source": "WHO Guidelines for Shigellosis"
            },
            {
                "name": "Azithromycin (alternative)",
                "dosage": "Adult: 500mg once daily | Child: 10mg/kg once daily",
                "duration": "3 days",
                "instructions": "Alternative for ciprofloxacin-resistant Shigella. Safer in children.",
                "source": "WHO Alternative for Dysentery"
            }
        ],
        "cholera": [
            {
                "name": "Ringer's Lactate IV or ORS (severe)",
                "dosage": "Plan C: IV 100ml/kg over 3-6 hours (divided: infants 30ml/kg in 1hr, then 70ml/kg in 5hrs)",
                "duration": "Until rehydrated",
                "instructions": "EMERGENCY - Rapid rehydration critical. Can lose 10-20L/day. Death from shock within hours if untreated.",
                "antibiotics": "Add doxycycline 300mg single dose (adult) or azithromycin (children) to reduce duration",
                "source": "WHO Cholera Treatment Guidelines"
            }
        ],
        "NOT_recommended": [
            "Antidiarrheals (loperamide) - dangerous in children, can worsen bacterial diarrhea",
            "Antibiotics for viral diarrhea - ineffective and promote resistance",
            "Carbonated drinks - high sugar worsens diarrhea",
            "Sports drinks - incorrect electrolyte ratio"
        ],
        "diet": [
            "Continue breastfeeding (infants)",
            "Age-appropriate foods (bananas, rice, toast)",
            "Avoid high-sugar foods and drinks",
            "Small frequent meals"
        ]
    },

    "Snake Bite": {
        "immediate_emergency": [
            {
                "name": "Polyvalent Anti-Snake Venom (ASV)",
                "dosage": "Initial: 10 vials diluted in 200-500ml normal saline over 1 hour | Repeat 5-10 vials every 6 hours if needed",
                "duration": "Continue until symptoms controlled (bleeding stops, neurotoxicity reverses)",
                "instructions": "EMERGENCY - Time critical. Start within 4 hours for best outcome. Premedicate with adrenaline 0.25mg SC and antihistamine. Monitor for anaphylaxis (keep adrenaline ready).",
                "monitoring": "20-minute whole blood clotting test, ptosis, respiratory distress, urine output",
                "types": "Use region-specific ASV: SAIMR (South African), VINS (Indian), or local equivalent",
                "source": "WHO Guidelines for Snake Bite Management 2023"
            }
        ],
        "pre_hospital": [
            "Keep patient calm and still - movement spreads venom",
            "Immobilize bitten limb with splint",
            "Remove rings, watches, tight clothing",
            "Mark bite site and leading edge of swelling with pen (time)",
            "Transport to hospital immediately - do NOT wait for symptoms",
            "DO NOT: cut wound, suck venom, apply tourniquet, ice, traditional remedies"
        ],
        "supportive": [
            {
                "name": "IV Fluids",
                "dosage": "Normal Saline or Ringer's Lactate - maintain urine output >30ml/hour",
                "duration": "Until stable",
                "instructions": "Prevent shock and maintain renal perfusion. Monitor for acute kidney injury.",
                "source": "Emergency Resuscitation Protocol"
            },
            {
                "name": "Fresh Frozen Plasma (if coagulopathy)",
                "dosage": "10-15ml/kg",
                "duration": "As needed until clotting normalized",
                "instructions": "For viper bites with severe bleeding and failed clotting. Check PT/INR.",
                "source": "WHO Coagulopathy Management"
            },
            {
                "name": "Blood Transfusion (if severe bleeding/anemia)",
                "dosage": "Packed RBC based on hemoglobin",
                "instructions": "For hemotoxic snake bites with significant blood loss.",
                "source": "Transfusion Medicine Guidelines"
            }
        ],
        "infection_prevention": [
            {
                "name": "Tetanus Prophylaxis",
                "dosage": "Tetanus Toxoid 0.5ml IM | If >5 years since last dose or unknown status, give Tetanus Immunoglobulin 250-500 IU IM",
                "duration": "Single dose",
                "instructions": "All snake bites are tetanus-prone wounds. Update immunization status.",
                "source": "WHO Tetanus Prevention"
            },
            {
                "name": "Antibiotics (wound infection prevention)",
                "dosage": "Amoxicillin-Clavulanate 875/125mg BID or Ceftriaxone 1-2g daily",
                "duration": "5-7 days",
                "instructions": "Start after stabilization. Snake mouths harbor multiple bacteria. Clean wound thoroughly.",
                "coverage": "Gram-positive, gram-negative, anaerobes",
                "source": "Wound Management Guidelines"
            }
        ],
        "neurotoxicity": [
            {
                "name": "Neostigmine (for neurotoxic envenoming)",
                "dosage": "Adult: 0.5-2.5mg IV (with atropine 0.6mg) | Child: 0.05-0.08mg/kg",
                "duration": "May repeat every 30 minutes",
                "instructions": "For cobra/krait bites with ptosis, paralysis. Gives temporary improvement but ASV still needed. Have atropine ready for cholinergic effects.",
                "source": "WHO Neurotoxic Snake Bite Protocol"
            }
        ],
        "respiratory_support": [
            "Intubation and mechanical ventilation if respiratory paralysis",
            "Bag-valve-mask ventilation as bridge",
            "May need prolonged ventilation (48-72 hours) until venom metabolized"
        ],
        "specific_antivenoms": [
            "Carpet Viper (Echis): SAIMR polyvalent",
            "Puff Adder (Bitis): SAIMR polyvalent",
            "Black Mamba (Dendroaspis): SAIMR polyvalent",
            "Cobra (Naja): Region-specific ASV",
            "Consult toxicology center for rare species"
        ]
    },

    "Hypertension": {
        "first_line": [
            {
                "name": "Amlodipine (Calcium Channel Blocker)",
                "dosage": "Initial: 5mg once daily | Maintenance: 5-10mg once daily",
                "duration": "Long-term (lifelong)",
                "instructions": "Take same time daily, with or without food. Effective as monotherapy in African populations. May cause ankle swelling.",
                "monitoring": "BP every 2 weeks until controlled, then monthly",
                "source": "WHO HEARTS Package, Uganda HTN Guidelines"
            },
            {
                "name": "Hydrochlorothiazide (Thiazide Diuretic)",
                "dosage": "12.5-25mg once daily in morning",
                "duration": "Long-term",
                "instructions": "Take in morning to avoid night-time urination. Increases urination initially. Effective and inexpensive.",
                "monitoring": "Potassium, creatinine, glucose (can worsen diabetes)",
                "contraindications": "Gout, severe hypokalemia",
                "source": "WHO Essential Medicines List"
            }
        ],
        "combination": [
            {
                "name": "Amlodipine + Hydrochlorothiazide",
                "dosage": "Amlodipine 5mg + HCTZ 12.5mg once daily",
                "duration": "Long-term",
                "instructions": "If BP not controlled on single agent. Better than high-dose monotherapy.",
                "source": "WHO Combination Therapy Recommendation"
            },
            {
                "name": "ACE Inhibitor (e.g., Enalapril) + HCTZ",
                "dosage": "Enalapril 5-10mg + HCTZ 12.5-25mg once daily",
                "duration": "Long-term",
                "instructions": "Preferred if diabetes or kidney disease. Check creatinine before starting.",
                "contraindications": "Pregnancy, bilateral renal artery stenosis, hyperkalemia",
                "source": "JNC 8 Guidelines"
            }
        ],
        "resistant_hypertension": [
            {
                "name": "Spironolactone (add as 4th agent)",
                "dosage": "25-50mg once daily",
                "duration": "Long-term",
                "instructions": "For resistant HTN (not controlled on 3 agents). Monitor potassium closely.",
                "monitoring": "Potassium, creatinine every 1-2 weeks initially",
                "source": "PATHWAY-2 Trial"
            }
        ],
        "hypertensive_emergency": [
            {
                "name": "Labetalol IV or Hydralazine IV",
                "dosage": "Labetalol 20mg slow IV push, repeat/increase as needed | Hydralazine 10-20mg IV",
                "duration": "Until BP controlled, then oral therapy",
                "instructions": "Emergency - BP >180/120 with organ damage. ICU monitoring. Lower BP gradually (25% in first hour).",
                "target": "Reduce MAP by 20-25% in first hour, avoid sudden drops",
                "source": "Hypertensive Emergency Protocol"
            }
        ],
        "lifestyle": [
            "Reduce salt intake (<5g/day = 1 teaspoon)",
            "DASH diet (fruits, vegetables, low-fat dairy)",
            "Exercise 150 minutes/week",
            "Weight loss if overweight (each 1kg = 1mmHg reduction)",
            "Limit alcohol",
            "Stress management"
        ]
    },

    "Diabetes Mellitus Type 2": {
        "first_line": [
            {
                "name": "Metformin",
                "dosage": "Start: 500mg BID with meals | Titrate to 1000mg BID (max 2550mg/day)",
                "duration": "Long-term (lifelong)",
                "instructions": "First-line for all Type 2 DM unless contraindicated. Take with food to reduce GI upset. Start low, go slow to improve tolerance.",
                "benefits": "Reduces cardiovascular risk, weight neutral, inexpensive",
                "contraindications": "eGFR <30ml/min, severe liver disease, alcohol abuse, acute illness",
                "monitoring": "HbA1c every 3 months, renal function annually, B12 levels (long-term use)",
                "source": "ADA Standards of Care 2023, WHO Essential Medicines"
            }
        ],
        "second_line": [
            {
                "name": "Glimepiride (Sulfonylurea)",
                "dosage": "Start: 1mg once daily with breakfast | Max: 6mg daily",
                "duration": "Long-term",
                "instructions": "Add if HbA1c >7% on metformin. Take with first meal. Risk of hypoglycemia - educate patient on symptoms.",
                "side_effects": "Weight gain (2-3kg), hypoglycemia",
                "monitoring": "Blood glucose, HbA1c, weight",
                "source": "Uganda DM Guidelines"
            },
            {
                "name": "Insulin NPH (if oral agents insufficient)",
                "dosage": "Start: 10 units or 0.1-0.2 units/kg at bedtime | Titrate by 2 units every 3 days",
                "duration": "Long-term",
                "instructions": "Inject subcutaneously in abdomen, thighs, or arms. Rotate injection sites. Store in refrigerator. Don't shake, roll gently.",
                "target": "Fasting glucose 4-7 mmol/L (70-130 mg/dL)",
                "hypoglycemia_management": "15-20g fast-acting carbs (3-4 glucose tablets, juice)",
                "source": "WHO Insulin Guidelines"
            }
        ],
        "intensive": [
            {
                "name": "Basal-Bolus Insulin (NPH + Regular)",
                "dosage": "NPH BID (2/3 morning, 1/3 evening) + Regular insulin before meals",
                "duration": "Long-term",
                "instructions": "For poorly controlled DM or insulin-dependent. Requires glucose monitoring 4x daily.",
                "source": "ADA Insulin Therapy Guidelines"
            }
        ],
        "complications_management": [
            "ACE inhibitor for kidney protection (if microalbuminuria)",
            "Statin for cardiovascular risk (Atorvastatin 10-20mg)",
            "Aspirin 75-150mg if cardiovascular disease",
            "Foot care and annual screening"
        ],
        "monitoring": [
            "HbA1c every 3 months (target <7%)",
            "Fasting glucose target: 4-7 mmol/L",
            "Blood pressure <140/90 (or <130/80 if high CV risk)",
            "Annual: eye exam, foot exam, microalbumin, lipids"
        ],
        "lifestyle": [
            "Medical nutrition therapy (carb counting)",
            "150 minutes moderate exercise/week",
            "Weight loss 5-10% if overweight",
            "No smoking",
            "Limit alcohol"
        ]
    },

    "Urinary Tract Infection": {
        "uncomplicated_cystitis": [
            {
                "name": "Nitrofurantoin",
                "dosage": "100mg BID",
                "duration": "5-7 days",
                "instructions": "Take with food. Best for lower UTI (cystitis). Minimal resistance. Turns urine dark yellow/brown (normal).",
                "contraindications": "eGFR <30ml/min, G6PD deficiency, pregnancy at term",
                "source": "IDSA UTI Guidelines 2023"
            },
            {
                "name": "Trimethoprim-Sulfamethoxazole (Co-trimoxazole)",
                "dosage": "160/800mg (DS) BID",
                "duration": "3 days",
                "instructions": "Only if local resistance <20%. Drink plenty of water. Check allergy to sulfa drugs.",
                "resistance": "High resistance in many areas - check local antibiogram",
                "source": "WHO UTI Treatment"
            },
            {
                "name": "Amoxicillin-Clavulanate",
                "dosage": "500/125mg TID or 875/125mg BID",
                "duration": "5-7 days",
                "instructions": "Alternative if others unsuitable. Take with food.",
                "source": "IDSA Alternative Regimen"
            }
        ],
        "pyelonephritis": [
            {
                "name": "Ciprofloxacin",
                "dosage": "500mg BID (oral) or 400mg BID (IV if severe)",
                "duration": "7-14 days",
                "instructions": "For upper UTI/kidney infection. Hospitalize if severe (high fever, vomiting, sepsis). Switch to oral after 48 hours afebrile.",
                "monitoring": "Temperature, flank pain, urine culture",
                "source": "IDSA Pyelonephritis Guidelines"
            },
            {
                "name": "Ceftriaxone IV (severe)",
                "dosage": "1-2g once daily",
                "duration": "7-14 days",
                "instructions": "For severe pyelonephritis or sepsis. Hospitalization required. Can step down to oral after improvement.",
                "source": "WHO Hospital Guidelines"
            }
        ],
        "pregnancy": [
            {
                "name": "Nitrofurantoin (avoid near term)",
                "dosage": "100mg BID",
                "duration": "7 days",
                "instructions": "Safe in pregnancy except near delivery. Screen all pregnant women for asymptomatic bacteriuria.",
                "source": "IDSA Pregnancy UTI Guidelines"
            },
            {
                "name": "Amoxicillin-Clavulanate",
                "dosage": "500/125mg TID",
                "duration": "7 days",
                "instructions": "Safe throughout pregnancy.",
                "source": "Pregnancy Safety Guidelines"
            }
        ],
        "recurrent_uti": [
            {
                "name": "Continuous Prophylaxis (if ≥2 UTIs in 6 months)",
                "dosage": "Nitrofurantoin 50-100mg at bedtime OR TMP-SMX 40/200mg daily",
                "duration": "6 months",
                "instructions": "For frequent recurrent UTIs. Address modifiable risk factors (post-coital, constipation, incomplete voiding).",
                "source": "IDSA Recurrent UTI Prevention"
            }
        ],
        "prevention": [
            "Hydration (8-10 glasses water/day)",
            "Void after intercourse",
            "Avoid douches, feminine sprays",
            "Cranberry products (some evidence)",
            "Proper wiping (front to back)"
        ]
    }
}


def get_medication_by_diagnosis(diagnosis_name, severity="mild", age_group="adult", special_conditions=None):
    """
    Get evidence-based medication recommendations for a diagnosis.
    
    Args:
        diagnosis_name (str): Primary diagnosis
        severity (str): 'mild', 'moderate', 'severe', 'uncomplicated', 'complicated'
        age_group (str): 'adult', 'child', 'infant', 'elderly'
        special_conditions (list): ['pregnancy', 'diabetes', 'kidney_disease', etc.]
    
    Returns:
        dict: Medication recommendations with dosage, duration, instructions
    """
    # Normalize diagnosis name
    diagnosis_key = None
    for key in MEDICATION_DATABASE.keys():
        if key.lower() in diagnosis_name.lower() or diagnosis_name.lower() in key.lower():
            diagnosis_key = key
            break
    
    if not diagnosis_key:
        return get_default_supportive_care()
    
    medications_data = MEDICATION_DATABASE[diagnosis_key]
    
    # Select appropriate medication category based on severity
    severity_map = {
        'mild': ['first_line', 'mild', 'uncomplicated', 'mild_community', 'viral'],
        'moderate': ['moderate', 'second_line', 'combination'],
        'severe': ['severe', 'intensive', 'complicated', 'severe_complicated'],
        'uncomplicated': ['uncomplicated', 'first_line', 'mild'],
        'emergency': ['immediate_emergency', 'severe', 'hypertensive_emergency']
    }
    
    possible_keys = severity_map.get(severity.lower(), ['first_line'])
    
    selected_medications = None
    for key in possible_keys:
        if key in medications_data:
            selected_medications = medications_data[key]
            break
    
    if not selected_medications and 'first_line' in medications_data:
        selected_medications = medications_data['first_line']
    elif not selected_medications:
        selected_medications = list(medications_data.values())[0]
    
    # Include supportive care if available
    result = {
        'primary_medications': selected_medications,
        'supportive_care': medications_data.get('supportive', []),
        'monitoring': medications_data.get('monitoring', []),
        'lifestyle': medications_data.get('lifestyle', []),
        'prevention': medications_data.get('prevention', [])
    }
    
    return result


def get_default_supportive_care():
    """Default recommendations when specific diagnosis not found."""
    return {
        'primary_medications': [
            {
                "name": "Symptomatic Treatment",
                "dosage": "As per clinical assessment",
                "duration": "As needed",
                "instructions": "Specific diagnosis required for targeted treatment. Consult healthcare provider. Avoid self-medication with antibiotics.",
                "source": "WHO Antimicrobial Stewardship"
            }
        ],
        'supportive_care': [
            "Adequate rest and hydration",
            "Paracetamol for fever/pain (10-15mg/kg every 6 hours)",
            "Oral rehydration if needed",
            "Monitor vital signs",
            "Seek immediate care if condition worsens"
        ],
        'monitoring': [
            "Temperature every 4-6 hours",
            "Hydration status",
            "Symptoms progression"
        ]
    }


# Severity determination helper
def determine_severity_from_vitals(vital_signs, symptoms):
    """
    Determine severity based on vital signs and symptoms.
    
    Returns: 'mild', 'moderate', 'severe'
    """
    if not vital_signs:
        return 'mild'
    
    temp = float(vital_signs.get('temperature', 37))
    respiratory_rate = vital_signs.get('respiratory_rate', 0)
    heart_rate = vital_signs.get('heart_rate', 0)
    
    # Fever severity
    severe_fever = temp >= 39.5
    high_fever = temp >= 38.5
    
    # Respiratory distress indicators
    tachypnea = respiratory_rate > 30 if respiratory_rate else False
    
    # Check for danger signs in symptoms
    danger_keywords = ['unconscious', 'seizure', 'bleeding', 'unable to drink', 
                       'severe pain', 'difficulty breathing', 'confusion']
    has_danger_sign = any(keyword in symptoms.lower() for keyword in danger_keywords)
    
    if severe_fever or tachypnea or has_danger_sign:
        return 'severe'
    elif high_fever:
        return 'moderate'
    else:
        return 'mild'
