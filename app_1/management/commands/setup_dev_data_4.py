# app_1/management/commands/setup_dev_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app_1.models import Company, StructureLevel, OrgNode, UserDashboard, TeamData, UserPsycoProcessedData, UserPsycoProcessedDataHistory
from app_1.tasks import generate_drill_down_lists
import random
from datetime import datetime

UserDashboard.objects.all().delete()
TeamData.objects.all().delete()
OrgNode.objects.all().delete()
User.objects.exclude(is_superuser=True).delete()
Company.objects.all().delete()
UserPsycoProcessedData.objects.all().delete()
UserPsycoProcessedDataHistory.objects.all().delete()

class Command(BaseCommand):
    help = 'Generates comprehensive company hierarchy with Indian employees and detailed mental health data including psycho processed data'

    def generate_big_five(self):
        traits = {
            "Neuroticism": {
                "interpretations": {
                    "low": "Low emotional reactivity; remains calm under stress.",
                    "average": "Moderate emotional reactivity; occasional stress or worry.",
                    "high": "High emotional reactivity; frequent stress or worry."
                }
            },
            "Extraversion": {
                "interpretations": {
                    "low": "Introverted; prefers solitude or small groups.",
                    "average": "Moderately social; comfortable both alone and with others.",
                    "high": "Highly social; energized by interactions with others."
                }
            },
            "Openness to Experience": {
                "interpretations": {
                    "low": "Practical and conventional; prefers routine.",
                    "average": "Moderately curious and open to new ideas.",
                    "high": "Highly curious, creative, imaginative, and open to new ideas."
                }
            },
            "Agreeableness": {
                "interpretations": {
                    "low": "Competitive and skeptical; prioritizes self-interest.",
                    "average": "Moderately cooperative and trusting.",
                    "high": "Cooperative, trusting, empathetic, and eager to help others."
                }
            },
            "Conscientiousness": {
                "interpretations": {
                    "low": "Flexible and spontaneous; may struggle with organization.",
                    "average": "Moderately disciplined and organized.",
                    "high": "Highly disciplined, organized, reliable, and achievement-oriented."
                }
            }
        }
        data = {}
        for trait, info in traits.items():
            items_scored = random.randint(8, 12)
            raw_score = round(random.uniform(1.0, 5.0), 2)
            if raw_score < 2.5:
                level = "low"
            elif raw_score < 3.5:
                level = "average"
            else:
                level = "high"
            interpretation = info["interpretations"][level]
            data[trait] = {
                "raw_score": raw_score,
                "max_possible": 5.0,
                "level": level,
                "items_scored": items_scored,
                "interpretation": interpretation
            }
        return data

    def generate_burnout(self):
        subscales = {
            "Emotional Exhaustion": {"max": 36, "interpretations": {"Low": "Low emotional exhaustion.", "Moderate": "Moderate emotional exhaustion.", "High": "High emotional exhaustion."}},
            "Depersonalization": {"max": 30, "interpretations": {"Low": "Low depersonalization.", "Moderate": "Moderate depersonalization.", "High": "High depersonalization."}},
            "Personal Accomplishment": {"max": 36, "interpretations": {"Low": "Low sense of accomplishment. (Concerning — low PA contributes to burnout.) ", "Moderate": "Moderate sense of accomplishment.", "High": "High sense of accomplishment."}}
        }
        data = {}
        total_levels = []
        for subscale, info in subscales.items():
            score = random.randint(0, info["max"])
            if score < info["max"] / 3:
                level = "Low"
            elif score < 2 * info["max"] / 3:
                level = "Moderate"
            else:
                level = "High"
            interpretation = f"{subscale[:2]} score {score} → {info['interpretations'][level]}"
            data[subscale] = {"score": score, "max_possible": info["max"], "level": level, "interpretation": interpretation}
            total_levels.append(level)
        overall = "No Burnout" if all(l == "Low" for l in total_levels) else "Partial Risk" if any(l == "Low" for l in total_levels) else "High Risk"
        data["overall_burnout"] = overall
        return data

    def generate_depression(self):
        items = [
            "Does the user experience a depressed mood such as sadness or hopelessness?",
            "Does the user experience feelings of guilt?",
            "Does the user experience suicidal thoughts or behaviors?",
            "Does the user have difficulty falling asleep?",
            "Does the user experience disturbed sleep during the night?",
            "Does the user wake up early due to sleep disturbance?",
            "Has the user's interest in work or activities decreased?",
            "Does the user show psychomotor slowing?",
            "Does the user experience agitation or restlessness?",
            "Does the user experience psychological anxiety?",
            "Does the user experience physical anxiety symptoms?",
            "Does the user experience gastrointestinal symptoms?",
            "Does the user experience general physical symptoms?",
            "Does the user experience sexual or genital symptoms?",
            "Does the user show excessive concern about health?"
        ]
        item_scores = {item: random.randint(0, 4) for item in items}
        total_score = sum(item_scores.values())
        max_possible = 60  # Adjusted for 15 items * 4
        if total_score < 10:
            severity = "Minimal Depression"
            interpretation = "Minimal depression; monitor if symptoms persist."
        elif total_score < 20:
            severity = "Mild Depression"
            interpretation = "Mild depression; consider lifestyle changes or counseling."
        elif total_score < 30:
            severity = "Moderate Depression"
            interpretation = "Moderate depression; professional help recommended."
        elif total_score < 40:
            severity = "Severe Depression"
            interpretation = "Severe depression; clinical intervention advised."
        else:
            severity = "Very Severe Depression"
            interpretation = "Very severe depression; urgent clinical intervention required."
        return {
            "total_score": total_score,
            "max_possible": max_possible,
            "severity": severity,
            "interpretation": interpretation,
            "item_scores": item_scores
        }

    def generate_anxiety(self):
        items = [
            "Does the user experience an anxious mood?",
            "Does the user experience tension or nervousness?",
            "Does the user experience fears?",
            "Does the user experience insomnia related to anxiety?",
            "Does the user have difficulty concentrating due to anxiety?",
            "Does the user experience depressed mood related to anxiety?",
            "Does the user experience muscular symptoms?",
            "Does the user experience sensory symptoms?",
            "Does the user experience cardiovascular symptoms?",
            "Does the user experience respiratory symptoms?",
            "Does the user experience gastrointestinal symptoms related to anxiety?",
            "Does the user experience genitourinary symptoms related to anxiety?",
            "Does the user experience autonomic symptoms?"
        ]
        item_scores = {item: random.randint(0, 4) for item in items}
        total_score = sum(item_scores.values())
        max_possible = 52  # 13 items * 4
        psychic_subscale_score = sum(list(item_scores.values())[:6])  # Approximate
        somatic_subscale_score = sum(list(item_scores.values())[6:])
        if total_score < 10:
            severity = "Minimal Anxiety"
        elif total_score < 20:
            severity = "Mild Anxiety"
        elif total_score < 30:
            severity = "Moderate Anxiety"
        elif total_score < 40:
            severity = "Severe Anxiety"
        else:
            severity = "Very Severe Anxiety"
        interpretation = f"{severity}; {'monitor' if total_score < 20 else 'clinical attention recommended' if total_score < 40 else 'urgent clinical attention warranted'}."
        return {
            "total_score": total_score,
            "max_possible": max_possible,
            "severity": severity,
            "interpretation": interpretation,
            "psychic_subscale_score": psychic_subscale_score,
            "somatic_subscale_score": somatic_subscale_score,
            "item_scores": item_scores
        }

    def generate_stress(self):
        items = [
            "Does the user experience work-related stress?",
            "Does the user feel overwhelmed by daily tasks?",
            "Does the user have trouble relaxing after work?",
            "Does the user experience physical symptoms like headaches from stress?",
            "Does the user feel irritable due to stress?",
            "Does the user have difficulty making decisions under stress?",
            "Does the user experience appetite changes due to stress?",
            "Does the user feel a sense of dread about upcoming events?",
            "Does the user experience muscle tension from stress?",
            "Does the user have trouble concentrating due to stress?"
        ]
        item_scores = {item: random.randint(0, 5) for item in items}
        total_score = sum(item_scores.values())
        max_possible = 50
        if total_score < 15:
            severity = "Low Stress"
            interpretation = "Low stress levels; maintain current coping strategies."
        elif total_score < 25:
            severity = "Moderate Stress"
            interpretation = "Moderate stress; consider stress management techniques."
        else:
            severity = "High Stress"
            interpretation = "High stress; professional intervention recommended."
        return {
            "total_score": total_score,
            "max_possible": max_possible,
            "severity": severity,
            "interpretation": interpretation,
            "item_scores": item_scores
        }

    def generate_resilience(self):
        items = [
            "Does the user bounce back quickly after setbacks?",
            "Does the user adapt well to change?",
            "Does the user maintain optimism in difficult situations?",
            "Does the user seek support when needed?",
            "Does the user have a strong sense of purpose?",
            "Does the user manage emotions effectively?",
            "Does the user learn from past experiences?",
            "Does the user maintain healthy relationships?",
            "Does the user take care of physical health?",
            "Does the user have problem-solving skills?"
        ]
        item_scores = {item: random.randint(0, 5) for item in items}
        total_score = sum(item_scores.values())
        max_possible = 50
        if total_score > 35:
            level = "High Resilience"
            interpretation = "High resilience; strong ability to cope with adversity."
        elif total_score > 20:
            level = "Moderate Resilience"
            interpretation = "Moderate resilience; room for improvement in coping strategies."
        else:
            level = "Low Resilience"
            interpretation = "Low resilience; may benefit from resilience-building exercises."
        return {
            "total_score": total_score,
            "max_possible": max_possible,
            "level": level,
            "interpretation": interpretation,
            "item_scores": item_scores
        }

    def generate_clinical_summary(self, depression, anxiety, burnout, stress, resilience):
        risk_levels = []
        if depression["severity"] in ["Severe Depression", "Very Severe Depression"]:
            risk_levels.append(f"Depression: {depression['severity']}")
        if anxiety["severity"] in ["Severe Anxiety", "Very Severe Anxiety"]:
            risk_levels.append(f"Anxiety: {anxiety['severity']}")
        if burnout["overall_burnout"] != "No Burnout":
            risk_levels.append(f"Burnout: {burnout['overall_burnout']}")
        if stress["severity"] == "High Stress":
            risk_levels.append(f"Stress: {stress['severity']}")
        if resilience["level"] == "Low Resilience":
            risk_levels.append(f"Resilience: {resilience['level']}")

        overall_risk_level = "Low" if not risk_levels else "Moderate" if len(risk_levels) < 3 else "High"
        comorbidity_note = "Co-occurring depression and anxiety detected. This combination is clinically significant and associated with greater functional impairment." if "Depression" in str(risk_levels) and "Anxiety" in str(risk_levels) else "No significant comorbidity detected."
        recommendation = "Monitor regularly." if overall_risk_level == "Low" else "Consider counseling." if overall_risk_level == "Moderate" else "Urgent clinical referral recommended."
        return {
            "overall_risk_level": overall_risk_level,
            "active_clinical_flags": risk_levels,
            "comorbidity_note": comorbidity_note,
            "recommendation": recommendation
        }

    def generate_psycho_data(self):
        big_five = self.generate_big_five()
        burnout = self.generate_burnout()
        depression = self.generate_depression()
        anxiety = self.generate_anxiety()
        stress = self.generate_stress()
        resilience = self.generate_resilience()
        clinical_summary = self.generate_clinical_summary(depression, anxiety, burnout, stress, resilience)
        return {
            "big_five": big_five,
            "burnout": burnout,
            "depression": depression,
            "anxiety": anxiety,
            "stress": stress,
            "resilience": resilience,
            "clinical_summary": clinical_summary
        }

    def generate_psycho_history(self):
        num_entries = random.randint(2, 5)
        history = {"content": []}
        current_year = datetime.now().year % 100
        for _ in range(num_entries):
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            date_str = f"{month:02d}-{day:02d}-{current_year:02d}"
            content = self.generate_psycho_data()
            history["content"].append({"content": content, "date": date_str})
        # Sort by date for chronological order
        history["content"].sort(key=lambda x: datetime.strptime(x["date"], "%m-%d-%y"))
        return history

    def create_user_and_node(self, username, name, company, structure_level, parent=None):
        """Helper to create user and node"""
        u, _ = User.objects.get_or_create(username=username)
        u.set_password("password123")
        u.save()
        node = OrgNode.objects.create(
            user=u, 
            name=name, 
            company=company,
            structure_level=structure_level,  # Pass the StructureLevel instance
            parent=parent
        )
        return u, node

    def create_user_dashboard(self, user, positive, problems, recommendations):
        """Helper to create user dashboard"""
        UserDashboard.objects.update_or_create(
            owner=user,
            defaults={'content': {
                "_personal_dashboard_data": {
                    "positive": positive,
                    "common_problems": problems,
                    "recommendation": recommendations
                }
            }}
        )

    def create_user_psycho_data(self, user):
        """Helper to create psycho processed data"""
        UserPsycoProcessedData.objects.update_or_create(
            owner=user,
            defaults={'content': self.generate_psycho_data()}
        )

    def create_user_psycho_history(self, user):
        """Helper to create psycho processed data history"""
        UserPsycoProcessedDataHistory.objects.update_or_create(
            owner=user,
            defaults={'content': self.generate_psycho_history()}
        )

    def handle(self, *args, **kwargs):
        self.stdout.write("Setting up comprehensive test data with Indian employees...")
        # 1. Company & Structure Levels
        comp = Company.objects.create(name="TechVista Solutions Pvt Ltd")
        lvl_1 = StructureLevel.objects.create(company=comp, name="CEO", level_rank=1)
        lvl_2 = StructureLevel.objects.create(company=comp, name="VP/Director", level_rank=2)
        lvl_3 = StructureLevel.objects.create(company=comp, name="Manager", level_rank=3)
        lvl_4 = StructureLevel.objects.create(company=comp, name="Team Lead", level_rank=4)
        lvl_5 = StructureLevel.objects.create(company=comp, name="Employee", level_rank=5)
        # 2. LEVEL 1: CEO
        u_rajesh, node_rajesh = self.create_user_and_node(
            "rajesh.kumar", "Rajesh Kumar (CEO)", comp, lvl_1, None
        )
        self.create_user_dashboard(
            u_rajesh,
            positive=[
                {"positive": "Demonstrates exceptional strategic vision and has successfully steered company through market volatility"},
                {"positive": "Maintains excellent work-life boundaries despite demanding role, setting good example for organization"},
                {"positive": "Shows genuine empathy in leadership interactions and actively listens to employee concerns"},
                {"positive": "Effectively manages stress through regular meditation and exercise routines"}
            ],
            problems=[
                {"problem": "Decision Fatigue", "description": "Making 40-50 critical decisions daily is leading to mental exhaustion by end of week, affecting weekend recovery"},
                {"problem": "Isolation at the Top", "description": "Limited peer support network within organization leading to feelings of loneliness in decision-making"},
                {"problem": "Sleep Disruption", "description": "Averaging 5.5 hours sleep due to late-night international calls and early morning reviews"},
                {"problem": "Impostor Syndrome", "description": "Despite success, occasionally experiences self-doubt about capabilities during challenging board meetings"},
                {"problem": "Work-Life Guilt", "description": "Feeling torn between family commitments and organizational responsibilities, especially during crisis periods"}
            ],
            recommendations=[
                {"recommendation": "Implement a structured decision-making framework to reduce cognitive load and delegate routine decisions"},
                {"recommendation": "Join CEO peer group or executive coaching program for emotional support and perspective"},
                {"recommendation": "Establish strict 11 PM digital cutoff and morning exercise routine to improve sleep quality"},
                {"recommendation": "Schedule quarterly leadership retreats to reconnect with personal values and long-term vision"},
                {"recommendation": "Delegate more operational oversight to VPs and focus on strategic initiatives only"},
                {"recommendation": "Block out dedicated family time in calendar as non-negotiable appointments"},
                {"recommendation": "Practice mindfulness exercises during transitions between meetings to reset mental state"},
                {"recommendation": "Consider executive assistant to filter and prioritize communications more effectively"}
            ]
        )
        self.create_user_psycho_data(u_rajesh)
        self.create_user_psycho_history(u_rajesh)
        # 3. LEVEL 2: VP Engineering
        u_priya, node_priya = self.create_user_and_node(
            "priya.sharma", "Priya Sharma (VP Engineering)", comp, lvl_2, node_rajesh
        )
        self.create_user_dashboard(
            u_priya,
            positive=[
                {"positive": "Exceptional technical leadership with strong ability to mentor and develop engineering talent"},
                {"positive": "Maintains composure during production incidents and models calm problem-solving for team"},
                {"positive": "Proactively addresses burnout in team through workload monitoring and resource allocation"},
                {"positive": "Successfully advocates for engineering needs while balancing business priorities"}
            ],
            problems=[
                {"problem": "Constant Context Switching", "description": "Jumping between technical reviews, people management, and strategic planning causes mental fragmentation and reduced effectiveness"},
                {"problem": "On-Call Anxiety", "description": "Even when not on-call, experiences hypervigilance about production systems affecting relaxation"},
                {"problem": "Gender Bias Stress", "description": "Navigating occasional microaggressions and having to repeatedly prove technical competence in male-dominated meetings"},
                {"problem": "Perfectionism", "description": "Setting unrealistically high standards for self and team, leading to delayed releases and team stress"},
                {"problem": "Boundary Erosion", "description": "Team members reaching out at all hours due to timezone differences with US clients"}
            ],
            recommendations=[
                {"recommendation": "Implement time-blocking with dedicated focus hours for deep technical work vs meetings"},
                {"recommendation": "Establish clearer on-call rotation and escalation procedures to reduce personal responsibility burden"},
                {"recommendation": "Seek support from women in tech networks and consider formal sponsorship for career advancement"},
                {"recommendation": "Adopt 'progress over perfection' mindset and celebrate incremental improvements with team"},
                {"recommendation": "Set clear communication hours policy and model healthy boundaries for team"},
                {"recommendation": "Schedule regular one-on-ones with CEO to discuss systemic challenges and get executive support"},
                {"recommendation": "Take quarterly mental health days for complete disconnection and personal renewal"},
                {"recommendation": "Engage in technical hobby projects outside work to maintain passion without pressure"}
            ]
        )
        self.create_user_psycho_data(u_priya)
        self.create_user_psycho_history(u_priya)
        # VP Sales
        u_vikram, node_vikram = self.create_user_and_node(
            "vikram.patel", "Vikram Patel (VP Sales)", comp, lvl_2, node_rajesh
        )
        self.create_user_dashboard(
            u_vikram,
            positive=[
                {"positive": "Charismatic leadership style that motivates sales team and drives strong revenue performance"},
                {"positive": "Resilient in face of rejection and maintains optimistic outlook even during tough quarters"},
                {"positive": "Strong emotional intelligence helps navigate complex client relationships effectively"},
                {"positive": "Celebrates team wins generously and shares credit for successes"}
            ],
            problems=[
                {"problem": "Performance Pressure", "description": "Quarterly targets create intense stress cycles with anxiety peaking in final month of each quarter"},
                {"problem": "Client Entertainment Fatigue", "description": "Regular evening dinners and weekend golf with clients leaving minimal personal time and affecting physical health"},
                {"problem": "Team Attrition Stress", "description": "High turnover in sales creating constant recruitment burden and guilt about team development failures"},
                {"problem": "Mood Volatility", "description": "Emotional state heavily tied to deal pipeline, causing mood swings that affect team morale"},
                {"problem": "Substance Use Concerns", "description": "Increased alcohol consumption during client entertainment raising personal health concerns"}
            ],
            recommendations=[
                {"recommendation": "Work with CEO to establish more realistic quarterly targets with longer evaluation cycles"},
                {"recommendation": "Limit client entertainment to 2 evenings per week and explore daytime networking alternatives"},
                {"recommendation": "Implement structured onboarding and mentorship program to reduce attrition and guilt"},
                {"recommendation": "Practice emotional regulation techniques to separate self-worth from deal outcomes"},
                {"recommendation": "Set personal limits on alcohol consumption and explore non-drinking entertainment options"},
                {"recommendation": "Engage executive coach specialized in sales leadership stress management"},
                {"recommendation": "Schedule regular health check-ups and commit to fitness routine for stress management"},
                {"recommendation": "Build peer support network with other sales leaders facing similar challenges"}
            ]
        )
        self.create_user_psycho_data(u_vikram)
        self.create_user_psycho_history(u_vikram)
        # Director HR
        u_anjali, node_anjali = self.create_user_and_node(
            "anjali.reddy", "Anjali Reddy (Director HR)", comp, lvl_2, node_rajesh
        )
        self.create_user_dashboard(
            u_anjali,
            positive=[
                {"positive": "Deeply compassionate approach to employee welfare with genuine care for organizational wellbeing"},
                {"positive": "Strong advocate for mental health initiatives and has championed EAP program implementation"},
                {"positive": "Excellent conflict resolution skills helping de-escalate tense workplace situations"},
                {"positive": "Maintains strict confidentiality and trustworthiness in sensitive employee matters"}
            ],
            problems=[
                {"problem": "Vicarious Trauma", "description": "Absorbing emotional distress from employees sharing mental health struggles, harassment cases, and personal crises"},
                {"problem": "Ethical Dilemmas", "description": "Caught between employee advocacy and business needs, causing moral distress and identity conflict"},
                {"problem": "Compassion Fatigue", "description": "Emotional exhaustion from continuous caregiving role reducing capacity for empathy"},
                {"problem": "Confidentiality Burden", "description": "Carrying heavy knowledge of organizational problems without outlet for processing creates isolation"},
                {"problem": "Impostor Feelings", "description": "Questioning qualifications when dealing with complex mental health cases beyond HR training"}
            ],
            recommendations=[
                {"recommendation": "Engage personal therapist to process vicarious trauma and maintain emotional wellbeing"},
                {"recommendation": "Establish clear role boundaries about what HR can/cannot address regarding mental health"},
                {"recommendation": "Schedule regular supervision sessions with external HR consultant for case consultation"},
                {"recommendation": "Take mental health days proactively rather than waiting for burnout symptoms"},
                {"recommendation": "Join HR professional community for peer support and ethical guidance"},
                {"recommendation": "Develop partnerships with mental health professionals for complex cases requiring specialized support"},
                {"recommendation": "Practice self-compassion and recognize limitations of HR role in solving all problems"},
                {"recommendation": "Implement rotating on-call system for employee emergencies to distribute emotional load"}
            ]
        )
        self.create_user_psycho_data(u_anjali)
        self.create_user_psycho_history(u_anjali)
        # LEVEL 3: MANAGERS
        # Engineering Manager - Backend
        u_arjun, node_arjun = self.create_user_and_node(
            "arjun.singh", "Arjun Singh (Engineering Manager - Backend)", comp, lvl_3, node_priya
        )
        self.create_user_dashboard(
            u_arjun,
            positive=[
                {"positive": "Strong technical background enables effective technical guidance and credibility with team"},
                {"positive": "Patient and supportive management style helps junior developers grow confidence"},
                {"positive": "Transparent communication about challenges builds trust within team"},
                {"positive": "Regularly seeks feedback and demonstrates growth mindset"}
            ],
            problems=[
                {"problem": "Identity Crisis", "description": "Struggling with transition from individual contributor to manager, missing hands-on coding and feeling less valuable"},
                {"problem": "Meeting Overload", "description": "Back-to-back meetings from 9 AM to 6 PM leaving no time for focused work or personal breaks"},
                {"problem": "People Pleasing", "description": "Difficulty saying no to requests from team and leadership, leading to overcommitment and stress"},
                {"problem": "Technical Skill Anxiety", "description": "Fear of skills becoming outdated while in management reducing confidence in technical discussions"},
                {"problem": "Feedback Avoidance", "description": "Avoiding difficult performance conversations with underperforming team members due to conflict aversion"}
            ],
            recommendations=[
                {"recommendation": "Block 20% time for hands-on technical work to maintain skills and satisfy creative needs"},
                {"recommendation": "Implement 'No Meeting Fridays' for team and personal focus time"},
                {"recommendation": "Practice assertiveness training and learn to negotiate priorities with stakeholders"},
                {"recommendation": "Dedicate time for technical learning through online courses and staying current with backend trends"},
                {"recommendation": "Role-play difficult conversations with HR or mentor to build confidence in feedback delivery"},
                {"recommendation": "Join engineering management community for peer learning and validation"},
                {"recommendation": "Reframe management as technical work with people as the system to optimize"},
                {"recommendation": "Set up weekly one-on-ones with VP to discuss management challenges and get coaching"}
            ]
        )
        self.create_user_psycho_data(u_arjun)
        self.create_user_psycho_history(u_arjun)
        # Engineering Manager - Frontend
        u_meera, node_meera = self.create_user_and_node(
            "meera.iyer", "Meera Iyer (Engineering Manager - Frontend)", comp, lvl_3, node_priya
        )
        self.create_user_dashboard(
            u_meera,
            positive=[
                {"positive": "Creative problem-solver who brings innovative solutions to user experience challenges"},
                {"positive": "Builds psychologically safe environment where team feels comfortable sharing concerns"},
                {"positive": "Advocates effectively for team needs in resource allocation discussions"},
                {"positive": "Demonstrates work-life balance by leaving on time and encouraging team to do same"}
            ],
            problems=[
                {"problem": "Design-Engineering Conflict", "description": "Mediating constant tensions between design and engineering creating emotional exhaustion"},
                {"problem": "Caregiver Burden", "description": "Managing elderly parent care alongside demanding job causing extreme stress and guilt"},
                {"problem": "Recognition Gap", "description": "Frontend work seen as less complex than backend leading to feelings of being undervalued"},
                {"problem": "Aesthetic Perfectionism", "description": "Obsessing over pixel-perfect implementations causing delays and team frustration"},
                {"problem": "Browser Compatibility Stress", "description": "Anxiety about supporting diverse devices and browsers creating quality assurance overwhelm"}
            ],
            recommendations=[
                {"recommendation": "Facilitate regular design-engineering alignment sessions with clear decision-making frameworks"},
                {"recommendation": "Explore elder care services and family medical leave options to reduce caregiver burden"},
                {"recommendation": "Document and communicate frontend complexity to leadership for better recognition"},
                {"recommendation": "Establish 'good enough' criteria and timebox aesthetic refinements to prevent perfectionism"},
                {"recommendation": "Implement automated testing across browsers to reduce manual verification anxiety"},
                {"recommendation": "Build support network of other working caregivers for practical and emotional support"},
                {"recommendation": "Negotiate flexible working hours to accommodate caregiving responsibilities"},
                {"recommendation": "Prioritize self-care through respite care services and personal time boundaries"}
            ]
        )
        self.create_user_psycho_data(u_meera)
        self.create_user_psycho_history(u_meera)
        # Sales Manager - Enterprise
        u_karthik, node_karthik = self.create_user_and_node(
            "karthik.nair", "Karthik Nair (Sales Manager - Enterprise)", comp, lvl_3, node_vikram
        )
        self.create_user_dashboard(
            u_karthik,
            positive=[
                {"positive": "Exceptional relationship builder who maintains long-term client partnerships"},
                {"positive": "Resilient and bounces back quickly from lost deals"},
                {"positive": "Mentors junior sales reps generously with time and knowledge"},
                {"positive": "Maintains ethical standards even under pressure to close deals"}
            ],
            problems=[
                {"problem": "Travel Exhaustion", "description": "15-20 days monthly travel disrupting sleep, diet, and family life causing physical and mental fatigue"},
                {"problem": "Rejection Sensitivity", "description": "Despite resilience, cumulative effect of client rejections affecting self-esteem and motivation"},
                {"problem": "Financial Anxiety", "description": "Commission-based income creating stress during slow sales months affecting family security feelings"},
                {"problem": "Always-On Culture", "description": "Expected to respond to client messages 24/7 preventing true disconnection and recovery"},
                {"problem": "Relationship Strain", "description": "Frequent absences and work stress creating distance with spouse and children"}
            ],
            recommendations=[
                {"recommendation": "Negotiate travel reduction by clustering client visits regionally and using video calls strategically"},
                {"recommendation": "Develop pre-call rituals and post-rejection processing techniques to manage emotional impact"},
                {"recommendation": "Work with finance team to explore base salary increase to reduce variable income anxiety"},
                {"recommendation": "Establish clear communication windows with clients and educate them on response time expectations"},
                {"recommendation": "Schedule dedicated family time and quality activities during non-travel weeks"},
                {"recommendation": "Practice mindfulness during travel downtime to process emotions and reduce stress accumulation"},
                {"recommendation": "Explore couples counseling to address relationship strain proactively"},
                {"recommendation": "Build emergency fund to buffer against commission fluctuations and reduce financial stress"}
            ]
        )
        self.create_user_psycho_data(u_karthik)
        self.create_user_psycho_history(u_karthik)
        # Sales Manager - SMB
        u_divya, node_divya = self.create_user_and_node(
            "divya.menon", "Divya Menon (Sales Manager - SMB)", comp, lvl_3, node_vikram
        )
        self.create_user_dashboard(
            u_divya,
            positive=[
                {"positive": "High energy and enthusiasm that energizes team and motivates consistent performance"},
                {"positive": "Excellent at breaking down complex products into simple value propositions"},
                {"positive": "Celebrates small wins with team creating positive momentum"},
                {"positive": "Adaptable and quickly adjusts sales approach based on market feedback"}
            ],
            problems=[
                {"problem": "Volume Pressure", "description": "Managing 40+ small accounts simultaneously creating organizational chaos and constant urgency"},
                {"problem": "Undervalued Work", "description": "SMB deals seen as less prestigious than enterprise causing feelings of being second-tier"},
                {"problem": "Churn Anxiety", "description": "High SMB customer churn rates causing constant stress about maintaining revenue numbers"},
                {"problem": "Multitasking Burnout", "description": "Juggling too many small tasks and conversations leading to cognitive overload"},
                {"problem": "Career Progression Concerns", "description": "Unclear path forward from SMB role creating existential anxiety about future"}
            ],
            recommendations=[
                {"recommendation": "Implement CRM automation and templates to reduce manual work in managing high volume"},
                {"recommendation": "Reframe SMB role as training ground for efficiency and process optimization skills"},
                {"recommendation": "Analyze churn patterns and work with product team on retention initiatives to feel more in control"},
                {"recommendation": "Practice single-tasking and time-blocking to reduce cognitive fragmentation"},
                {"recommendation": "Have career development conversation with VP about path to enterprise or management"},
                {"recommendation": "Celebrate expertise in velocity sales as valuable specialization"},
                {"recommendation": "Build peer support group with other SMB managers across industry"},
                {"recommendation": "Set healthy boundaries on account volume and advocate for additional team members"}
            ]
        )
        self.create_user_psycho_data(u_divya)
        self.create_user_psycho_history(u_divya)
        # HR Manager - Talent Acquisition
        u_rahul, node_rahul = self.create_user_and_node(
            "rahul.gupta", "Rahul Gupta (HR Manager - Talent Acquisition)", comp, lvl_3, node_anjali
        )
        self.create_user_dashboard(
            u_rahul,
            positive=[
                {"positive": "Excellent judge of character and cultural fit leading to strong hiring success rate"},
                {"positive": "Builds genuine connections with candidates creating positive candidate experience"},
                {"positive": "Process-oriented approach brings structure to chaotic hiring environment"},
                {"positive": "Maintains composure during high-pressure hiring sprints"}
            ],
            problems=[
                {"problem": "Requisition Overload", "description": "15+ open positions with aggressive timelines creating impossible workload expectations"},
                {"problem": "Hiring Manager Conflict", "description": "Dealing with unrealistic expectations and constant changing requirements causing frustration"},
                {"problem": "Candidate Ghosting Impact", "description": "Emotional investment in candidates who ghost at offer stage leading to disappointment"},
                {"problem": "Market Competition Stress", "description": "Losing top candidates to competitors with better offers creating feelings of failure"},
                {"problem": "Quality vs Speed Tension", "description": "Pressure to fill roles quickly while maintaining quality standards causing ethical stress"}
            ],
            recommendations=[
                {"recommendation": "Work with leadership to prioritize requisitions and establish realistic hiring timelines"},
                {"recommendation": "Implement structured intake process with hiring managers to align expectations upfront"},
                {"recommendation": "Develop emotional detachment strategies and view ghosting as market reality not personal failure"},
                {"recommendation": "Build compelling employer value proposition to compete better for top talent"},
                {"recommendation": "Establish quality metrics and educate leadership on long-term cost of bad hires"},
                {"recommendation": "Create recruiter peer support group for sharing challenges and best practices"},
                {"recommendation": "Automate repetitive tasks like interview scheduling to focus on relationship building"},
                {"recommendation": "Take breaks between major hiring sprints to recover and prevent burnout"}
            ]
        )
        self.create_user_psycho_data(u_rahul)
        self.create_user_psycho_history(u_rahul)
        # LEVEL 4: TEAM LEADS
        # Backend Team Lead - Microservices
        u_sanjay, node_sanjay = self.create_user_and_node(
            "sanjay.reddy", "Sanjay Reddy (Team Lead - Microservices)", comp, lvl_4, node_arjun
        )
        self.create_user_dashboard(
            u_sanjay,
            positive=[
                {"positive": "Deep technical expertise in distributed systems earns respect from team and peers"},
                {"positive": "Calm demeanor during incidents helps team stay focused under pressure"},
                {"positive": "Actively shares knowledge through documentation and brown bag sessions"},
                {"positive": "Provides constructive code review feedback that helps developers improve"}
            ],
            problems=[
                {"problem": "On-Call Burnout", "description": "Responding to production alerts 2-3 times per night during on-call weeks destroying sleep quality"},
                {"problem": "Technical Debt Guilt", "description": "Knowing architectural shortcuts taken under pressure will cause future problems creating chronic worry"},
                {"problem": "Scope Creep Stress", "description": "Requirements changing mid-sprint causing frustration and team morale issues"},
                {"problem": "Impostor Syndrome", "description": "Despite expertise, feeling inadequate when comparing to tech influencers and open source maintainers"},
                {"problem": "Work-Life Imbalance", "description": "Passion for coding leading to working evenings and weekends affecting personal relationships"}
            ],
            recommendations=[
                {"recommendation": "Advocate for better monitoring and auto-remediation to reduce on-call burden"},
                {"recommendation": "Schedule dedicated sprints for technical debt reduction to address guilt and improve system health"},
                {"recommendation": "Implement requirement freeze policy after sprint planning to reduce scope creep"},
                {"recommendation": "Reframe comparison as inspiration and recognize unique value of domain expertise"},
                {"recommendation": "Set strict work hours and create separation rituals to improve work-life boundaries"},
                {"recommendation": "Rotate on-call duties more frequently to prevent single-person burnout"},
                {"recommendation": "Practice self-compassion and recognize impossibility of knowing all technologies"},
                {"recommendation": "Engage in non-technical hobbies to create identity beyond work"}
            ]
        )
        self.create_user_psycho_data(u_sanjay)
        self.create_user_psycho_history(u_sanjay)
        # Backend Team Lead - API Gateway  
        u_pooja, node_pooja = self.create_user_and_node(
            "pooja.desai", "Pooja Desai (Team Lead - API Gateway)", comp, lvl_4, node_arjun
        )
        self.create_user_dashboard(
            u_pooja,
            positive=[
                {"positive": "Proactive in identifying potential issues before they become critical problems"},
                {"positive": "Strong collaboration skills facilitate smooth cross-team API integrations"},
                {"positive": "Maintains detailed documentation making knowledge transfer efficient"},
                {"positive": "Supportive of team members taking time off and encourages work-life balance"}
            ],
            problems=[
                {"problem": "Gateway Dependency Stress", "description": "Being critical path for all services creates pressure to never fail and constant anxiety"},
                {"problem": "Performance Obsession", "description": "Spending excessive time micro-optimizing latency causing diminishing returns and stress"},
                {"problem": "Communication Overload", "description": "Required in every integration discussion leading to meeting fatigue and fragmented focus"},
                {"problem": "Single Point of Knowledge", "description": "Being only person who understands certain legacy components creating fear of taking vacation"},
                {"problem": "Pregnancy-Related Anxiety", "description": "Concerns about maintaining performance during pregnancy and career impact of maternity leave"}
            ],
            recommendations=[
                {"recommendation": "Build redundancy in gateway architecture to reduce single point of failure pressure"},
                {"recommendation": "Establish performance budgets and stop optimizing once thresholds are met"},
                {"recommendation": "Delegate representation in integration meetings to team members for knowledge sharing"},
                {"recommendation": "Document and cross-train team on legacy components to distribute knowledge burden"},
                {"recommendation": "Have open conversation with manager about pregnancy support and transition planning"},
                {"recommendation": "Connect with working mothers network for advice on managing career and motherhood"},
                {"recommendation": "Set realistic expectations with stakeholders about availability during pregnancy"},
                {"recommendation": "Practice letting go of control and trusting team to handle issues independently"}
            ]
        )
        self.create_user_psycho_data(u_pooja)
        self.create_user_psycho_history(u_pooja)
        # Frontend Team Lead - Web App
        u_aditya, node_aditya = self.create_user_and_node(
            "aditya.krishnan", "Aditya Krishnan (Team Lead - Web App)", comp, lvl_4, node_meera
        )
        self.create_user_dashboard(
            u_aditya,
            positive=[
                {"positive": "Creative problem solver who finds elegant solutions to complex UI challenges"},
                {"positive": "User-centric mindset ensures products are intuitive and accessible"},
                {"positive": "Encourages experimentation and learning from failures within team"},
                {"positive": "Stays current with frontend trends and evaluates new technologies objectively"}
            ],
            problems=[
                {"problem": "Framework Fatigue", "description": "Constant evolution of JavaScript ecosystem creating pressure to continuously learn and rewrite"},
                {"problem": "Design Handoff Friction", "description": "Receiving incomplete or changing designs mid-development causing rework frustration"},
                {"problem": "Browser Bug Exhaustion", "description": "Debugging obscure browser-specific issues consuming disproportionate time and mental energy"},
                {"problem": "Accessibility Guilt", "description": "Knowing accessibility standards but compromising due to time pressure creating ethical discomfort"},
                {"problem": "Creative Drought", "description": "Repetitive nature of CRUD interfaces leading to feeling creatively unfulfilled"}
            ],
            recommendations=[
                {"recommendation": "Establish technology evaluation framework to make informed choices without FOMO"},
                {"recommendation": "Implement design system and component library to reduce custom development needs"},
                {"recommendation": "Use browser testing automation tools to catch compatibility issues earlier"},
                {"recommendation": "Allocate dedicated time for accessibility improvements in each sprint as non-negotiable"},
                {"recommendation": "Take on side projects or contribute to open source for creative outlet"},
                {"recommendation": "Establish clear design handoff process with acceptance criteria for completeness"},
                {"recommendation": "Create browser support policy to limit testing scope to manageable set"},
                {"recommendation": "Rotate team members through different types of work to prevent monotony"}
            ]
        )
        self.create_user_psycho_data(u_aditya)
        self.create_user_psycho_history(u_aditya)
        # Frontend Team Lead - Mobile App
        u_neha, node_neha = self.create_user_and_node(
            "neha.kapoor", "Neha Kapoor (Team Lead - Mobile App)", comp, lvl_4, node_meera
        )
        self.create_user_dashboard(
            u_neha,
            positive=[
                {"positive": "Detail-oriented approach catches potential issues before they reach production"},
                {"positive": "Empathetic leadership creates supportive environment where team feels valued"},
                {"positive": "Strong problem-solving under app store review constraints"},
                {"positive": "Builds inclusive team culture that celebrates diverse perspectives"}
            ],
            problems=[
                {"problem": "App Store Anxiety", "description": "Fear of app rejection causing excessive pre-submission stress and over-testing"},
                {"problem": "Platform Fragmentation", "description": "Supporting iOS and Android with different UI paradigms creating mental context switching"},
                {"problem": "Release Day Panic", "description": "Cannot quickly fix production bugs due to app review delays causing helplessness"},
                {"problem": "Offline Functionality Complexity", "description": "Managing data synchronization edge cases creating overwhelming cognitive load"},
                {"problem": "Work Martyrdom", "description": "Taking on too much to protect team leading to personal burnout"}
            ],
            recommendations=[
                {"recommendation": "Develop comprehensive pre-submission checklist to reduce last-minute anxiety"},
                {"recommendation": "Invest in shared component library to reduce platform-specific development burden"},
                {"recommendation": "Implement robust beta testing program to catch issues before production release"},
                {"recommendation": "Create systematic approach to offline sync using established patterns and libraries"},
                {"recommendation": "Practice delegation and trust team to handle challenging work independently"},
                {"recommendation": "Build buffer time in release schedules to account for review delays"},
                {"recommendation": "Join mobile development communities for support and validation"},
                {"recommendation": "Set boundaries on heroic efforts and communicate limitations to stakeholders"}
            ]
        )
        self.create_user_psycho_data(u_neha)
        self.create_user_psycho_history(u_neha)
        # Enterprise Sales Team Lead
        u_manish, node_manish = self.create_user_and_node(
            "manish.joshi", "Manish Joshi (Team Lead - Enterprise Sales)", comp, lvl_4, node_karthik
        )
        self.create_user_dashboard(
            u_manish,
            positive=[
                {"positive": "Natural relationship builder who creates genuine connections with enterprise clients"},
                {"positive": "Analytical approach to sales helps identify best opportunities and optimize efforts"},
                {"positive": "Coaches team members effectively on enterprise sales techniques"},
                {"positive": "Maintains integrity in sales process even under pressure"}
            ],
            problems=[
                {"problem": "Long Sales Cycle Stress", "description": "9-12 month enterprise deals creating sustained uncertainty and difficulty forecasting"},
                {"problem": "Executive Presence Anxiety", "description": "Presenting to C-suite buyers causing impostor feelings despite proven track record"},
                {"problem": "Deal Dependency", "description": "Heavy reliance on 2-3 large deals for quarterly target creating all-or-nothing pressure"},
                {"problem": "Competitive Intelligence Obsession", "description": "Constantly monitoring competitors leading to anxiety and reactive positioning"},
                {"problem": "Personal Life Sacrifice", "description": "Prioritizing clients over family events creating relationship strain and guilt"}
            ],
            recommendations=[
                {"recommendation": "Build larger pipeline to reduce dependency on individual deals"},
                {"recommendation": "Invest in executive presence coaching to build confidence in C-suite interactions"},
                {"recommendation": "Work with leadership to adjust quota structure accounting for deal cycle length"},
                {"recommendation": "Focus on differentiation rather than competition to reduce reactive anxiety"},
                {"recommendation": "Block out family time as protected and communicate boundaries to clients"},
                {"recommendation": "Practice mindfulness to stay present rather than catastrophizing about deal outcomes"},
                {"recommendation": "Build support network with other enterprise sellers for shared experiences"},
                {"recommendation": "Celebrate small milestones in long sales cycles to maintain motivation"}
            ]
        )
        self.create_user_psycho_data(u_manish)
        self.create_user_psycho_history(u_manish)
        # SMB Sales Team Lead
        u_sneha, node_sneha = self.create_user_and_node(
            "sneha.shah", "Sneha Shah (Team Lead - SMB Sales)", comp, lvl_4, node_divya
        )
        self.create_user_dashboard(
            u_sneha,
            positive=[
                {"positive": "High activity level and efficiency creates strong results in volume-based sales"},
                {"positive": "Positive attitude is infectious and motivates team through challenging periods"},
                {"positive": "Quick learner who rapidly adapts to product changes and market shifts"},
                {"positive": "Celebrates team successes and maintains competitive spirit"}
            ],
            problems=[
                {"problem": "Activity Metrics Pressure", "description": "Constant monitoring of call volume and email metrics creating surveillance anxiety"},
                {"problem": "Rejection Accumulation", "description": "Hearing 'no' 50+ times daily taking emotional toll despite individual resilience"},
                {"problem": "Script Fatigue", "description": "Repetitive sales conversations feeling robotic and unfulfilling"},
                {"problem": "Value Perception", "description": "Feeling like sales machine rather than strategic partner in organization"},
                {"problem": "Screen Time Burnout", "description": "8+ hours daily on video calls and computer causing physical and mental exhaustion"}
            ],
            recommendations=[
                {"recommendation": "Reframe metrics as personal game with rewards rather than surveillance"},
                {"recommendation": "Develop daily reset ritual between morning and afternoon calling sessions"},
                {"recommendation": "Personalize script within guidelines to maintain authenticity and engagement"},
                {"recommendation": "Document SMB insights and share with product team to demonstrate strategic value"},
                {"recommendation": "Implement regular screen breaks and eye exercises to reduce physical strain"},
                {"recommendation": "Build variety into day by alternating between calls, emails, and planning"},
                {"recommendation": "Connect with sales team for mutual support and shared rejection processing"},
                {"recommendation": "Explore opportunities for account management or expansion sales for career growth"}
            ]
        )
        self.create_user_psycho_data(u_sneha)
        self.create_user_psycho_history(u_sneha)
        # Talent Acquisition Team Lead
        u_rohit, node_rohit = self.create_user_and_node(
            "rohit.malhotra", "Rohit Malhotra (Team Lead - Campus Hiring)", comp, lvl_4, node_rahul
        )
        self.create_user_dashboard(
            u_rohit,
            positive=[
                {"positive": "Passionate about developing fresh talent and shaping early careers"},
                {"positive": "Creates positive candidate experience that strengthens employer brand"},
                {"positive": "Organized and systematic approach manages campus recruitment complexity well"},
                {"positive": "Builds strong relationships with college placement officers"}
            ],
            problems=[
                {"problem": "Campus Season Burnout", "description": "3-month recruitment blitz with travel, events, and selection causing complete exhaustion"},
                {"problem": "Offer Decline Disappointment", "description": "Emotional investment in candidates who decline offers for higher packages elsewhere"},
                {"problem": "Seasonal Work Anxiety", "description": "Intense busy period followed by slow months creating job security concerns"},
                {"problem": "Young Talent Responsibility", "description": "Feeling pressure to make right choices that impact fresh graduates' career trajectories"},
                {"problem": "Event Exhaustion", "description": "Back-to-back college visits, pre-placement talks, and hackathons draining energy reserves"}
            ],
            recommendations=[
                {"recommendation": "Negotiate additional team support during peak campus season to distribute workload"},
                {"recommendation": "Develop emotional detachment by viewing offers as business transactions not personal"},
                {"recommendation": "Diversify responsibilities beyond campus to create year-round value and security"},
                {"recommendation": "Share selection decisions with panel to distribute responsibility burden"},
                {"recommendation": "Build recovery time into schedule after major campus events before next commitment"},
                {"recommendation": "Create sustainable campus engagement model that doesn't require constant travel"},
                {"recommendation": "Practice self-compassion recognizing impossibility of perfect hiring decisions"},
                {"recommendation": "Take mandatory break after campus season ends to fully recover"}
            ]
        )
        self.create_user_psycho_data(u_rohit)
        self.create_user_psycho_history(u_rohit)
        # LEVEL 5: EMPLOYEES
        self.stdout.write("Creating Level 5 employees...")
        
        # Employees under Sanjay (Backend - Microservices)
        backend_employees_sanjay = [
            ("amit.verma", "Amit Verma (Sr. Backend Engineer)", [
                {"positive": "Writes clean, well-tested code that rarely causes production issues"},
                {"positive": "Helpful mentor to junior team members without being condescending"},
                {"positive": "Takes ownership of complex problems and sees them through to resolution"},
                {"positive": "Maintains calm during incidents and thinks clearly under pressure"}
            ], [
                {"problem": "Code Review Anxiety", "description": "Fear of judgment during code reviews causing overthinking and delays in submitting PRs"},
                {"problem": "Perfectionism Paralysis", "description": "Spending excessive time refactoring before shipping causing missed deadlines"},
                {"problem": "Documentation Procrastination", "description": "Dreading writing documentation leading to knowledge silos"},
                {"problem": "Career Plateau Concerns", "description": "Uncertain about next career step causing existential anxiety about growth"}
            ], [
                {"recommendation": "Shift mindset to view code reviews as collaborative learning rather than judgment"},
                {"recommendation": "Adopt 'ship it, then improve it' approach with planned refactoring sprints"},
                {"recommendation": "Use documentation templates and AI tools to reduce writing friction"},
                {"recommendation": "Have career development conversation with manager about path to staff engineer"}
            ]),
            ("kavya.pillai", "Kavya Pillai (Backend Engineer)", [
                {"positive": "Quick learner who rapidly absorbs new technologies and patterns"},
                {"positive": "Asks thoughtful questions that often uncover edge cases"},
                {"positive": "Collaborative team player who helps colleagues debug issues"},
                {"positive": "Maintains good work-life balance and sets healthy example"}
            ], [
                {"problem": "Impostor Syndrome", "description": "Constant comparison to senior engineers creating feelings of inadequacy"},
                {"problem": "Speaking Up Anxiety", "description": "Hesitant to share ideas in technical discussions fearing they might be wrong"},
                {"problem": "On-Call Dread", "description": "Anxiety building up week before on-call rotation affecting sleep and focus"},
                {"problem": "Tech Stack Overwhelm", "description": "Feeling lost trying to understand entire microservices ecosystem"}
            ], [
                {"recommendation": "Keep achievement log to combat impostor feelings with concrete evidence of growth"},
                {"recommendation": "Practice 'stupid question' reframing - questions benefit everyone learning"},
                {"recommendation": "Pair with senior engineer during first on-call shifts to build confidence"},
                {"recommendation": "Focus on mastering one service deeply before breadth across all services"}
            ]),
            ("vishal.bhatt", "Vishal Bhatt (Backend Engineer)", [
                {"positive": "Strong debugging skills help team resolve production issues quickly"},
                {"positive": "Takes initiative on technical debt reduction without being asked"},
                {"positive": "Maintains positive attitude even during stressful sprint deadlines"},
                {"positive": "Open to feedback and implements suggestions constructively"}
            ], [
                {"problem": "Scope Creep Frustration", "description": "Requirements changing mid-sprint making completed work obsolete"},
                {"problem": "Meeting Interruption Stress", "description": "Frequent context switches preventing flow state and deep work"},
                {"problem": "Learning Time Scarcity", "description": "No time allocated for skill development causing stagnation anxiety"},
                {"problem": "Recognition Gap", "description": "Technical debt work going unnoticed while feature work gets celebrated"}
            ], [
                {"recommendation": "Advocate for requirement freeze after sprint planning to protect team focus"},
                {"recommendation": "Block 2-hour focus time slots and educate team on importance of uninterrupted time"},
                {"recommendation": "Negotiate 20% learning time or Friday afternoons for professional development"},
                {"recommendation": "Document and present technical debt impact in sprint reviews to increase visibility"}
            ])
        ]
        for username, name, positive, problems, recommendations in backend_employees_sanjay:
            u, node = self.create_user_and_node(username, name, comp, lvl_5, node_sanjay)
            self.create_user_dashboard(u, positive, problems, recommendations)
            self.create_user_psycho_data(u)
            self.create_user_psycho_history(u)
        # Employees under Pooja (Backend - API Gateway)
        backend_employees_pooja = [
            ("deepak.saxena", "Deepak Saxena (API Engineer)", [
                {"positive": "Meticulous attention to API design consistency and documentation"},
                {"positive": "Proactive about security considerations in API development"},
                {"positive": "Patient with external teams integrating with APIs"},
                {"positive": "Maintains backward compatibility carefully during changes"}
            ], [
                {"problem": "Breaking Change Anxiety", "description": "Fear of breaking external integrations causing excessive caution"},
                {"problem": "Support Request Overload", "description": "Constant API usage questions interrupting development flow"},
                {"problem": "Version Management Stress", "description": "Maintaining multiple API versions simultaneously creating maintenance burden"},
                {"problem": "Performance Pressure", "description": "Every millisecond of latency scrutinized creating optimization obsession"}
            ], [
                {"recommendation": "Implement comprehensive API testing and deprecation process to reduce fear"},
                {"recommendation": "Create self-service API documentation and examples to deflect routine questions"},
                {"recommendation": "Advocate for sunset policy on old API versions to reduce maintenance load"},
                {"recommendation": "Define acceptable performance SLAs and stop optimizing beyond targets"}
            ]),
            ("priyanka.choudhary", "Priyanka Choudhary (API Engineer)", [
                {"positive": "Excellent communicator who explains technical concepts clearly to non-technical stakeholders"},
                {"positive": "Detail-oriented approach catches potential issues in design phase"},
                {"positive": "Advocates for user experience in API design discussions"},
                {"positive": "Builds strong cross-functional relationships"}
            ], [
                {"problem": "Stakeholder Expectation Management", "description": "Difficulty saying no to unrealistic API requests causing overcommitment"},
                {"problem": "Technical vs Business Tension", "description": "Pressure to compromise on technical quality for business timelines"},
                {"problem": "Gender Dynamics Fatigue", "description": "Being only woman in technical meetings requiring extra effort to be heard"},
                {"problem": "Work-Life Boundary Blur", "description": "Global stakeholders reaching out across timezones blurring work hours"}
            ], [
                {"recommendation": "Practice negotiation skills to propose alternatives rather than accepting all requests"},
                {"recommendation": "Frame technical quality as business benefit to align goals"},
                {"recommendation": "Build alliances with other women in engineering for support and amplification"},
                {"recommendation": "Set clear communication hours and educate stakeholders on timezone boundaries"}
            ])
        ]
        for username, name, positive, problems, recommendations in backend_employees_pooja:
            u, node = self.create_user_and_node(username, name, comp, lvl_5, node_pooja)
            self.create_user_dashboard(u, positive, problems, recommendations)
            self.create_user_psycho_data(u)
            self.create_user_psycho_history(u)
        # Employees under Aditya (Frontend - Web)
        frontend_employees_aditya = [
            ("ravi.kumar", "Ravi Kumar (Frontend Engineer)", [
                {"positive": "Strong sense of visual design and user experience intuition"},
                {"positive": "Enjoys learning new frameworks and sharing knowledge with team"},
                {"positive": "Creates polished, professional UI components"},
                {"positive": "Good at translating design mockups to pixel-perfect implementations"}
            ], [
                {"problem": "Design-Dev Handoff Friction", "description": "Receiving incomplete designs mid-sprint causing rework and frustration"},
                {"problem": "CSS Specificity Nightmares", "description": "Debugging cascading style conflicts consuming excessive time"},
                {"problem": "Responsive Design Exhaustion", "description": "Testing across multiple screen sizes feeling endless"},
                {"problem": "Animation Perfectionism", "description": "Obsessing over micro-interactions while core features remain incomplete"}
            ], [
                {"recommendation": "Establish design acceptance criteria before starting implementation"},
                {"recommendation": "Adopt CSS-in-JS or utility classes to eliminate specificity debugging"},
                {"recommendation": "Define breakpoint strategy and limit testing to key sizes"},
                {"recommendation": "Timebox polish work and create separate backlog for nice-to-have enhancements"}
            ]),
            ("ishita.malhotra", "Ishita Malhotra (Frontend Engineer)", [
                {"positive": "Strong accessibility advocate ensuring inclusive user experiences"},
                {"positive": "Writes maintainable, well-structured component code"},
                {"positive": "Collaborative approach to pair programming and knowledge sharing"},
                {"positive": "Proactive about performance optimization"}
            ], [
                {"problem": "Accessibility vs Timeline Conflict", "description": "Wanting to build accessible features but facing pressure to ship quickly"},
                {"problem": "JavaScript Framework Churn", "description": "Fear of learning becoming obsolete with rapid frontend technology changes"},
                {"problem": "Testing Avoidance", "description": "Finding frontend testing complex and frustrating leading to procrastination"},
                {"problem": "Component Reusability Overthinking", "description": "Over-engineering components causing complexity and delays"}
            ], [
                {"recommendation": "Build accessibility into definition of done rather than optional enhancement"},
                {"recommendation": "Focus on mastering JavaScript fundamentals which transcend framework changes"},
                {"recommendation": "Start with simple snapshot tests and gradually build testing confidence"},
                {"recommendation": "Follow YAGNI principle - build for current needs not hypothetical future"}
            ]),
            ("gaurav.singh", "Gaurav Singh (Frontend Engineer)", [
                {"positive": "Excellent problem solver for complex state management challenges"},
                {"positive": "Takes pride in writing clean, readable code"},
                {"positive": "Helpful in onboarding new team members to codebase"},
                {"positive": "Stays calm during production bugs and methodically debugs"}
            ], [
                {"problem": "State Management Complexity", "description": "Global state growing unwieldy causing confusion about data flow"},
                {"problem": "Bundle Size Anxiety", "description": "Worrying about application performance with every dependency addition"},
                {"problem": "Cross-Browser Bug Fatigue", "description": "Obscure browser-specific issues consuming disproportionate debugging time"},
                {"problem": "Career Direction Uncertainty", "description": "Unsure whether to specialize in frontend or become full-stack"}
            ], [
                {"recommendation": "Refactor to use local state by default and lift to global only when necessary"},
                {"recommendation": "Set bundle size budgets and use automated monitoring"},
                {"recommendation": "Define browser support matrix to limit testing scope to business priorities"},
                {"recommendation": "Experiment with backend work through internal tools to inform decision"}
            ])
        ]
        for username, name, positive, problems, recommendations in frontend_employees_aditya:
            u, node = self.create_user_and_node(username, name, comp, lvl_5, node_aditya)
            self.create_user_dashboard(u, positive, problems, recommendations)
            self.create_user_psycho_data(u)
            self.create_user_psycho_history(u)
        # Employees under Neha (Frontend - Mobile)
        mobile_employees_neha = [
            ("akash.jain", "Akash Jain (Mobile Engineer - iOS)", [
                {"positive": "Passionate about creating delightful user experiences on mobile"},
                {"positive": "Detail-oriented ensuring apps feel native and polished"},
                {"positive": "Quick to adopt new iOS features and capabilities"},
                {"positive": "Maintains high code quality standards"}
            ], [
                {"problem": "App Review Rejection Stress", "description": "Fear of Apple rejection causing excessive testing and launch delays"},
                {"problem": "iOS Version Fragmentation", "description": "Supporting multiple iOS versions while wanting to use latest APIs"},
                {"problem": "Device Testing Overwhelm", "description": "Ensuring compatibility across iPhone, iPad models feeling impossible"},
                {"problem": "Swift Evolution Fatigue", "description": "Constant language changes requiring code updates and relearning"}
            ], [
                {"recommendation": "Build comprehensive pre-submission checklist following App Store guidelines"},
                {"recommendation": "Define minimum iOS version support policy based on user analytics"},
                {"recommendation": "Use cloud device testing services to expand coverage"},
                {"recommendation": "View Swift evolution as improvement and allocate time for migration"}
            ]),
            ("shweta.rao", "Shweta Rao (Mobile Engineer - Android)", [
                {"positive": "Adept at handling Android device fragmentation challenges"},
                {"positive": "Strong understanding of material design principles"},
                {"positive": "Proactive about battery and memory optimization"},
                {"positive": "Helpful contributor to team code reviews"}
            ], [
                {"problem": "Device Fragmentation Nightmare", "description": "Testing across hundreds of Android device combinations causing endless compatibility issues"},
                {"problem": "Permission Model Complexity", "description": "Managing evolving Android permissions across versions creating confusion"},
                {"problem": "Play Store Policy Anxiety", "description": "Frequent policy changes requiring rushed updates to avoid app suspension"},
                {"problem": "Kotlin Migration Pressure", "description": "Legacy Java code requiring gradual migration while maintaining features"}
            ], [
                {"recommendation": "Focus testing on top 80% devices by user base using analytics"},
                {"recommendation": "Create permission request wrapper to abstract version differences"},
                {"recommendation": "Subscribe to Play Store policy updates and proactively schedule compliance work"},
                {"recommendation": "Plan systematic Kotlin migration one module at a time"}
            ])
        ]
        for username, name, positive, problems, recommendations in mobile_employees_neha:
            u, node = self.create_user_and_node(username, name, comp, lvl_5, node_neha)
            self.create_user_dashboard(u, positive, problems, recommendations)
            self.create_user_psycho_data(u)
            self.create_user_psycho_history(u)
        # Employees under Manish (Enterprise Sales)
        enterprise_sales_employees = [
            ("ankit.agarwal", "Ankit Agarwal (Enterprise Sales Rep)", [
                {"positive": "Builds genuine relationships with clients based on trust"},
                {"positive": "Excellent listener who understands customer pain points deeply"},
                {"positive": "Persistent without being pushy in sales approach"},
                {"positive": "Strong presenter in executive stakeholder meetings"}
            ], [
                {"problem": "Deal Loss Devastation", "description": "Months of work lost to competitor causing emotional crash and motivation loss"},
                {"problem": "Quota Pressure", "description": "Constant stress about hitting numbers affecting sleep and mental health"},
                {"problem": "Relationship Fatigue", "description": "Exhaustion from constant networking and relationship maintenance"},
                {"problem": "Pipeline Anxiety", "description": "Obsessively checking CRM and worrying about deal progression"}
            ], [
                {"recommendation": "Conduct post-loss analysis to learn rather than dwell emotionally on defeats"},
                {"recommendation": "Focus on controllable activities rather than outcomes to reduce quota anxiety"},
                {"recommendation": "Schedule relationship-building activities sustainably"},
                {"recommendation": "Set specific CRM check times rather than compulsive monitoring"}
            ]),
            ("nidhi.bansal", "Nidhi Bansal (Enterprise Sales Rep)", [
                {"positive": "Strategic thinker who maps account relationships effectively"},
                {"positive": "Resilient and bounces back quickly from setbacks"},
                {"positive": "Collaborative with solutions engineering and product teams"},
                {"positive": "Maintains professional boundaries with clients"}
            ], [
                {"problem": "Work-Life Integration Struggle", "description": "Client demands bleeding into personal time causing resentment"},
                {"problem": "Negotiation Stress", "description": "High-stakes pricing discussions causing anxiety and self-doubt"},
                {"problem": "Internal Politics Frustration", "description": "Navigating cross-functional dependencies for deals causing conflict"},
                {"problem": "Commission Volatility Anxiety", "description": "Unpredictable income affecting financial planning"}
            ], [
                {"recommendation": "Set explicit availability windows and train clients on response expectations"},
                {"recommendation": "Role-play pricing negotiations with manager to build confidence"},
                {"recommendation": "Build strong relationships with internal stakeholders proactively"},
                {"recommendation": "Work with finance on commission advance or conservative budgeting"}
            ])
        ]
        for username, name, positive, problems, recommendations in enterprise_sales_employees:
            u, node = self.create_user_and_node(username, name, comp, lvl_5, node_manish)
            self.create_user_dashboard(u, positive, problems, recommendations)
            self.create_user_psycho_data(u)
            self.create_user_psycho_history(u)
        # Employees under Sneha (SMB Sales)
        smb_sales_employees = [
            ("rajat.khanna", "Rajat Khanna (SMB Sales Rep)", [
                {"positive": "High energy and enthusiasm that converts to strong close rates"},
                {"positive": "Efficient at managing high volume of smaller deals"},
                {"positive": "Quick rapport building with small business owners"},
                {"positive": "Adaptable pitch based on different industry verticals"}
            ], [
                {"problem": "Call Reluctance", "description": "Building anxiety before cold calling sessions affecting productivity"},
                {"problem": "Rejection Accumulation", "description": "Hearing 'no' 50+ times daily eroding confidence over time"},
                {"problem": "Metric Surveillance Stress", "description": "Constant monitoring of activity metrics creating performance anxiety"},
                {"problem": "Script Monotony", "description": "Repetitive conversations feeling soul-crushing and meaningless"}
            ], [
                {"recommendation": "Develop pre-call warm-up routine to build energy and reduce anxiety"},
                {"recommendation": "Reframe rejections as filtering for qualified prospects"},
                {"recommendation": "Focus on daily habits rather than metrics and let results follow"},
                {"recommendation": "Personalize script within guidelines to maintain authenticity"}
            ]),
            ("swati.kulkarni", "Swati Kulkarni (SMB Sales Rep)", [
                {"positive": "Empathetic approach resonates well with small business owners"},
                {"positive": "Organized system for managing multiple concurrent deals"},
                {"positive": "Strong follow-up discipline drives high conversion rates"},
                {"positive": "Collaborative teammate who shares winning strategies"}
            ], [
                {"problem": "Emotional Labor Exhaustion", "description": "Constantly maintaining upbeat persona causing authenticity fatigue"},
                {"problem": "Screen Time Strain", "description": "8 hours of video calls causing eye strain and headaches"},
                {"problem": "Competition Pressure", "description": "Internal leaderboards creating unhealthy comparison and rivalry"},
                {"problem": "Career Growth Concerns", "description": "Unclear progression path from SMB role causing future anxiety"}
            ], [
                {"recommendation": "Allow moments of authentic emotion rather than forced positivity"},
                {"recommendation": "Follow 20-20-20 rule and take regular breaks from screen"},
                {"recommendation": "Focus on personal best rather than comparing to top performers"},
                {"recommendation": "Discuss career path options with manager"}
            ]),
            ("varun.prasad", "Varun Prasad (SMB Sales Rep)", [
                {"positive": "Natural storyteller who makes product value compelling"},
                {"positive": "Resilient and maintains motivation through slumps"},
                {"positive": "Coachable and implements feedback quickly"},
                {"positive": "Celebrates small wins to maintain team morale"}
            ], [
                {"problem": "Financial Stress", "description": "Variable commission structure causing anxiety about meeting monthly expenses"},
                {"problem": "Ghosting Frustration", "description": "Prospects disappearing mid-deal causing confusion and wasted effort"},
                {"problem": "Product Knowledge Gaps", "description": "Struggling to answer technical questions causing credibility concerns"},
                {"problem": "Work Hours Guilt", "description": "Feeling obligated to work evenings to hit numbers"}
            ], [
                {"recommendation": "Negotiate higher base salary or budget conservatively"},
                {"recommendation": "Develop systematic follow-up process and accept ghosting as normal"},
                {"recommendation": "Schedule regular product training and shadow solutions engineers"},
                {"recommendation": "Set strict work hours and optimize efficiency rather than adding hours"}
            ])
        ]
        for username, name, positive, problems, recommendations in smb_sales_employees:
            u, node = self.create_user_and_node(username, name, comp, lvl_5, node_sneha)
            self.create_user_dashboard(u, positive, problems, recommendations)
            self.create_user_psycho_data(u)
            self.create_user_psycho_history(u)
        # Employees under Rohit (Campus Recruiting)
        recruiter_employees = [
            ("pallavi.deshmukh", "Pallavi Deshmukh (Campus Recruiter)", [
                {"positive": "Genuine passion for helping students start careers successfully"},
                {"positive": "Excellent at presenting company culture authentically"},
                {"positive": "Builds strong relationships with placement officers and professors"},
                {"positive": "Organized and manages high-volume campus recruitment well"}
            ], [
                {"problem": "Campus Season Overwhelm", "description": "Managing 1000+ applicants during peak season causing burnout"},
                {"problem": "Candidate Disappointment Burden", "description": "Rejecting hundreds of hopeful students causing emotional exhaustion"},
                {"problem": "Travel Fatigue", "description": "Constant college visits during recruitment season disrupting routine"},
                {"problem": "Offer Acceptance Anxiety", "description": "Worrying about offer declines affecting hiring targets"}
            ], [
                {"recommendation": "Request additional recruiter support during peak campus season"},
                {"recommendation": "Develop compassionate rejection templates and process emotions with peers"},
                {"recommendation": "Cluster college visits regionally to reduce travel burden"},
                {"recommendation": "Build buffer into hiring plans to account for expected declines"}
            ]),
            ("siddharth.yadav", "Siddharth Yadav (Technical Recruiter)", [
                {"positive": "Strong technical understanding helps evaluate engineering candidates effectively"},
                {"positive": "Persistent in sourcing hard-to-find specialized talent"},
                {"positive": "Builds authentic relationships with candidates beyond transactional recruiting"},
                {"positive": "Data-driven approach to optimizing recruiting metrics"}
            ], [
                {"problem": "Talent Shortage Stress", "description": "Unable to find qualified candidates for niche roles causing failure feelings"},
                {"problem": "Candidate Ghosting Impact", "description": "Investing time in candidates who disappear without explanation"},
                {"problem": "Hiring Manager Unrealistic Expectations", "description": "Purple squirrel job descriptions creating impossible search criteria"},
                {"problem": "Market Competition Anxiety", "description": "Losing candidates to bigger companies with better offers"}
            ], [
                {"recommendation": "Educate hiring managers on market realities and negotiate realistic requirements"},
                {"recommendation": "Develop multiple candidate pipelines to reduce dependency"},
                {"recommendation": "Conduct intake sessions to align on must-have vs nice-to-have qualifications"},
                {"recommendation": "Build strong employer brand and sell opportunity beyond compensation"}
            ])
        ]
        for username, name, positive, problems, recommendations in recruiter_employees:
            u, node = self.create_user_and_node(username, name, comp, lvl_5, node_rohit)
            self.create_user_dashboard(u, positive, problems, recommendations)
            self.create_user_psycho_data(u)
            self.create_user_psycho_history(u)
        # Generate drill-down lists for all nodes
        self.stdout.write("Generating drill down lists for all nodes...")
        all_nodes = OrgNode.objects.filter(company=comp).order_by('structure_level')
        for node in all_nodes:
            generate_drill_down_lists(node)
        # Create Team Dashboards for all non-leaf nodes
        self.stdout.write("Creating team dashboards...")
        # CEO Team Dashboard
        TeamData.objects.create(
            node=node_rajesh,
            content=[{
                "common_problems": [
                    {"problem": "Cross-Department Silos", "description": "Engineering, Sales, and HR operating independently leading to misalignment on priorities and duplicated efforts"},
                    {"problem": "Burnout Epidemic", "description": "60% of employees showing signs of emotional exhaustion with increasing sick leave and turnover intentions"},
                    {"problem": "Innovation Stagnation", "description": "Team members too overwhelmed with operational work to explore creative solutions or process improvements"},
                    {"problem": "Communication Breakdown", "description": "Important information not flowing effectively between levels causing confusion and rework"},
                    {"problem": "Mental Health Stigma", "description": "Employees hesitant to utilize EAP services due to fear of career impact and lack of psychological safety"},
                    {"problem": "Work-Life Balance Crisis", "description": "Always-on culture with expectation of 24/7 availability eroding personal boundaries across organization"}
                ],
                "recommendations": [
                    {"recommendation": "Establish quarterly cross-functional town halls to improve transparency and alignment on company direction"},
                    {"recommendation": "Implement mandatory no-meeting days company-wide to provide recovery time and focus periods"},
                    {"recommendation": "Launch comprehensive mental health awareness campaign with leadership participation to reduce stigma"},
                    {"recommendation": "Institute 4-day work week pilot program in one department to evaluate productivity and wellbeing impact"},
                    {"recommendation": "Create innovation time policy allowing 10% of work hours for exploratory projects"},
                    {"recommendation": "Implement manager mental health training to identify and support struggling team members"},
                    {"recommendation": "Establish clear right-to-disconnect policy with no expectation of after-hours responses"}
                ],
                "policy_changes": [
                    {"title": "Mental Health Days Policy", "description": "Provide 4 dedicated mental health days per year separate from PTO, no questions asked, to normalize mental health care"},
                    {"title": "Flexible Working Hours", "description": "Allow employees to choose core hours between 10 AM - 4 PM with flexibility on remaining hours to accommodate personal needs"},
                    {"title": "Therapy Coverage Enhancement", "description": "Increase EAP sessions from 6 to 12 per year and add specialized therapy coverage for burnout and workplace stress"},
                    {"title": "Meeting-Free Fridays", "description": "Designate Fridays as focus days with no internal meetings scheduled to enable deep work and weekly recovery"},
                    {"title": "Sabbatical Program", "description": "Offer 4-week paid sabbatical after 5 years of service for long-term employee renewal and retention"},
                    {"title": "Manager Support Ratio", "description": "Limit manager to direct report ratio to maximum 8:1 to ensure adequate time for people management and support"}
                ]
            }]
        )
        # VP Engineering Team Dashboard
        TeamData.objects.create(
            node=node_priya,
            content=[{
                "common_problems": [
                    {"problem": "On-Call Burnout", "description": "Engineers experiencing sleep disruption and constant hypervigilance due to 24/7 on-call rotation expectations"},
                    {"problem": "Technical Debt Overwhelm", "description": "Accumulating shortcuts and workarounds creating anxiety about system stability and future maintainability"},
                    {"problem": "Unrealistic Deadlines", "description": "Product and sales commitments made without engineering input causing chronic sprint overload and quality compromises"},
                    {"problem": "Meeting Overload", "description": "Engineers spending 50%+ time in meetings leaving insufficient focus time for complex problem-solving"},
                    {"problem": "Knowledge Silos", "description": "Critical system knowledge concentrated in few individuals creating single points of failure and vacation anxiety"},
                    {"problem": "Impostor Syndrome Culture", "description": "Competitive environment where engineers afraid to ask questions or admit knowledge gaps"}
                ],
                "recommendations": [
                    {"recommendation": "Implement follow-the-sun on-call rotation with offshore team to reduce individual burden"},
                    {"recommendation": "Allocate 20% of each sprint specifically for technical debt reduction and refactoring"},
                    {"recommendation": "Require engineering participation in roadmap planning before external commitments are made"},
                    {"recommendation": "Establish no-meeting blocks daily from 9-12 AM for focused engineering work"},
                    {"recommendation": "Create documentation sprints and pair programming rotations to spread knowledge"},
                    {"recommendation": "Launch engineering learning culture initiative celebrating questions and knowledge sharing"},
                    {"recommendation": "Provide mental health resources specifically for tech workers addressing industry-specific stressors"}
                ],
                "policy_changes": [
                    {"title": "On-Call Compensation", "description": "Provide additional PTO days and financial compensation for on-call weeks to acknowledge burden"},
                    {"title": "Code Freeze Windows", "description": "Institute monthly code freeze weeks to reduce production pressure and allow focus on stability"},
                    {"title": "20% Learning Time", "description": "Formalize Google-style 20% time for skill development, open source contribution, or innovation projects"},
                    {"title": "Pair Programming Standard", "description": "Require pairing on complex features to reduce knowledge silos and provide mutual support"},
                    {"title": "Post-Incident Recovery", "description": "Mandatory day off after major incidents for engineers who led troubleshooting and resolution"},
                    {"title": "Remote Work Flexibility", "description": "Allow permanent remote work option for engineering roles to improve work-life balance and reduce commute stress"}
                ]
            }]
        )
        # VP Sales Team Dashboard
        TeamData.objects.create(
            node=node_vikram,
            content=[{
                "common_problems": [
                    {"problem": "Quota Pressure Culture", "description": "Intense quarterly pressure creating boom-bust stress cycles and short-term thinking over sustainable performance"},
                    {"problem": "Client Entertainment Burnout", "description": "Expected evening and weekend client entertainment causing work-life boundary erosion and health impacts"},
                    {"problem": "Commission Volatility Anxiety", "description": "Variable compensation creating financial stress affecting focus and mental health, especially during slow periods"},
                    {"problem": "Travel Exhaustion", "description": "Extensive client travel disrupting sleep, nutrition, exercise routines and family relationships"},
                    {"problem": "Deal Loss Depression", "description": "Significant emotional investment in deals leading to disproportionate distress when losing to competitors"},
                    {"problem": "Always-On Expectations", "description": "Client responsiveness culture creating inability to truly disconnect and recover"}
                ],
                "recommendations": [
                    {"recommendation": "Shift to rolling quarterly targets to reduce end-of-quarter pressure spikes"},
                    {"recommendation": "Set limits on client entertainment frequency and explore daytime alternatives"},
                    {"recommendation": "Increase base salary component to reduce commission volatility anxiety"},
                    {"recommendation": "Implement travel reduction initiative using video calls for routine meetings"},
                    {"recommendation": "Create deal loss post-mortem process focused on learning not blame"},
                    {"recommendation": "Establish clear communication windows and educate clients on response expectations"},
                    {"recommendation": "Provide sales-specific stress management and resilience training"}
                ],
                "policy_changes": [
                    {"title": "Client Entertainment Limits", "description": "Cap client entertainment at 2 evenings per week to protect personal time and health"},
                    {"title": "Sales Compensation Restructure", "description": "Adjust commission structure to 60/40 base/variable split to reduce financial anxiety"},
                    {"title": "Travel Wellness Support", "description": "Provide gym memberships, healthy meal stipends, and travel wellness resources"},
                    {"title": "Mandatory Time Off Post-Quarter", "description": "Require 3-day break after quarter close for recovery before next cycle begins"},
                    {"title": "Right to Disconnect", "description": "No expectation of responses to client emails/calls between 8 PM - 8 AM or on weekends"},
                    {"title": "Sales Therapy Program", "description": "Provide access to therapists specializing in sales stress, rejection resilience, and performance anxiety"}
                ]
            }]
        )
        # Director HR Team Dashboard
        TeamData.objects.create(
            node=node_anjali,
            content=[{
                "common_problems": [
                    {"problem": "Vicarious Trauma Exposure", "description": "HR team absorbing emotional distress from employee crisis situations, harassment cases, and terminations without adequate support"},
                    {"problem": "Ethical Conflict Stress", "description": "Caught between employee advocacy and business priorities creating moral distress and role confusion"},
                    {"problem": "Compassion Fatigue", "description": "Continuous caregiving role depleting empathy reserves and affecting ability to provide quality support"},
                    {"problem": "Confidentiality Isolation", "description": "Carrying sensitive knowledge without outlet for processing creating profound loneliness"},
                    {"problem": "Boundary Challenges", "description": "Employees reaching out for support at all hours blurring professional boundaries"},
                    {"problem": "Scope Creep Overwhelm", "description": "HR expected to solve all people problems including those requiring clinical mental health expertise"}
                ],
                "recommendations": [
                    {"recommendation": "Provide regular supervision with external HR consultant for case debriefing and emotional processing"},
                    {"recommendation": "Establish clear boundaries about HR scope vs clinical mental health requiring specialist referral"},
                    {"recommendation": "Implement rotating on-call system for employee emergencies to distribute emotional burden"},
                    {"recommendation": "Create peer support group for HR professionals to share challenges confidentially"},
                    {"recommendation": "Mandate therapy for HR team members to process vicarious trauma proactively"},
                    {"recommendation": "Set communication hours policy and model healthy boundaries for organization"},
                    {"recommendation": "Bring in mental health professionals for complex cases beyond HR training"}
                ],
                "policy_changes": [
                    {"title": "HR Wellness Program", "description": "Provide dedicated wellness support for HR team including mandatory therapy and supervision sessions"},
                    {"title": "Mental Health Partnerships", "description": "Contract with mental health professionals for employee referrals and HR team consultation"},
                    {"title": "Vicarious Trauma Training", "description": "Train all HR staff on recognizing and managing vicarious trauma from employee cases"},
                    {"title": "Case Load Limits", "description": "Set maximum concurrent high-complexity employee cases per HR team member to prevent overwhelm"},
                    {"title": "HR Recovery Days", "description": "Provide additional PTO days specifically for HR team recovery from emotionally demanding periods"},
                    {"title": "Professional Development Budget", "description": "Increase budget for HR certifications, conferences, and mental health specialized training"}
                ]
            }]
        )
        # Manager Team Dashboards
        TeamData.objects.create(
            node=node_arjun,
            content=[{
                "common_problems": [
                    {"problem": "On-Call Alert Fatigue", "description": "Team members experiencing sleep deprivation from nighttime production alerts affecting health and performance"},
                    {"problem": "Context Switching Overhead", "description": "Engineers pulled into too many meetings and interruptions preventing deep focus work on complex problems"},
                    {"problem": "Technical Debt Anxiety", "description": "Growing awareness of system fragility from accumulated shortcuts causing chronic worry and risk aversion"}
                ],
                "recommendations": [
                    {"recommendation": "Invest in monitoring automation and alert tuning to reduce false positive on-call burden"},
                    {"recommendation": "Implement focus time blocks with no-meeting windows and communication protocols"},
                    {"recommendation": "Schedule monthly technical debt sprints to systematically address architectural concerns"}
                ],
                "policy_changes": [
                    {"title": "On-Call Rotation Reform", "description": "Limit on-call shifts to 1 week per month with mandatory recovery day after rotation"},
                    {"title": "No-Meeting Mornings", "description": "Block 9 AM - 12 PM daily for focused engineering work without meeting interruptions"},
                    {"title": "Technical Debt Sprints", "description": "Dedicate first sprint of each quarter exclusively to technical debt reduction and refactoring"}
                ]
            }]
        )
        TeamData.objects.create(
            node=node_meera,
            content=[{
                "common_problems": [
                    {"problem": "Design-Engineering Friction", "description": "Constant tension over feasibility, timelines, and quality standards causing team stress and conflict"},
                    {"problem": "Perfectionism Paralysis", "description": "Engineers spending excessive time on pixel-perfect implementation causing delays and diminishing returns"},
                    {"problem": "Framework Churn Anxiety", "description": "Rapid JavaScript ecosystem evolution creating fear of skill obsolescence and learning fatigue"}
                ],
                "recommendations": [
                    {"recommendation": "Establish design-engineering alignment process with clear acceptance criteria and feasibility reviews"},
                    {"recommendation": "Define 'good enough' quality standards and timebox aesthetic refinement work"},
                    {"recommendation": "Focus on JavaScript fundamentals and adopt stable frameworks to reduce churn impact"}
                ],
                "policy_changes": [
                    {"title": "Design Handoff Standards", "description": "Require complete, high-fidelity designs with annotations before implementation begins"},
                    {"title": "Polish Time Limits", "description": "Timebox visual refinement to maximum 20% of feature development time"},
                    {"title": "Framework Stability Policy", "description": "Evaluate new frameworks annually, not reactively, to reduce constant technology churn"}
                ]
            }]
        )
        TeamData.objects.create(
            node=node_karthik,
            content=[{
                "common_problems": [
                    {"problem": "Long Sales Cycle Uncertainty", "description": "9-12 month enterprise deals creating prolonged stress and difficulty with revenue forecasting"},
                    {"problem": "Travel Lifestyle Impact", "description": "15-20 days monthly travel disrupting health routines, sleep, and family relationships"},
                    {"problem": "Deal Loss Emotional Impact", "description": "Months of relationship building lost to competitors causing significant emotional distress"}
                ],
                "recommendations": [
                    {"recommendation": "Build deeper pipeline to reduce dependency on individual deals and smooth revenue"},
                    {"recommendation": "Cluster client visits regionally and increase strategic use of video calls to reduce travel"},
                    {"recommendation": "Implement deal loss retrospective process focused on learning not blame or punishment"}
                ],
                "policy_changes": [
                    {"title": "Travel Reduction Initiative", "description": "Require business case for in-person meetings vs video calls to minimize unnecessary travel"},
                    {"title": "Compensation Restructure", "description": "Shift to 65/35 base/commission split to reduce income volatility anxiety"},
                    {"title": "Deal Support System", "description": "Provide access to sports psychology or performance coaching for high-pressure situations"}
                ]
            }]
        )
        TeamData.objects.create(
            node=node_divya,
            content=[{
                "common_problems": [
                    {"problem": "Volume Overwhelm", "description": "Managing 40+ small accounts simultaneously creating constant urgency and organizational chaos"},
                    {"problem": "Call Rejection Accumulation", "description": "Hearing 'no' 50+ times daily eroding confidence and emotional resilience over time"},
                    {"problem": "Activity Metric Pressure", "description": "Constant monitoring of call volumes and email activity creating surveillance anxiety and burnout"}
                ],
                "recommendations": [
                    {"recommendation": "Implement CRM automation and templates to reduce manual overhead of high-volume management"},
                    {"recommendation": "Teach rejection reframing techniques and create peer support for processing cumulative impact"},
                    {"recommendation": "Focus on daily habits and process rather than outcome metrics to reduce pressure"}
                ],
                "policy_changes": [
                    {"title": "Account Load Limits", "description": "Cap maximum concurrent accounts at 35 to prevent overwhelming team members"},
                    {"title": "Screen Break Requirements", "description": "Mandate 10-minute break every 90 minutes away from screens for health protection"},
                    {"title": "Metric Focus Shift", "description": "Emphasize quality conversations and conversion rates over pure activity volume"}
                ]
            }]
        )
        TeamData.objects.create(
            node=node_rahul,
            content=[{
                "common_problems": [
                    {"problem": "Requisition Overload", "description": "15+ concurrent open positions with aggressive timelines creating impossible workload expectations"},
                    {"problem": "Candidate Ghosting Impact", "description": "Emotional investment in candidates who disappear at offer stage causing disappointment and frustration"},
                    {"problem": "Hiring Manager Conflict", "description": "Unrealistic expectations and constantly changing requirements causing professional friction"}
                ],
                "recommendations": [
                    {"recommendation": "Establish requisition prioritization framework to focus efforts on critical hires"},
                    {"recommendation": "Develop emotional detachment strategies viewing ghosting as market reality not personal"},
                    {"recommendation": "Implement structured intake process to align hiring manager expectations upfront"}
                ],
                "policy_changes": [
                    {"title": "Recruiter Load Limits", "description": "Cap maximum concurrent requisitions at 10 per recruiter to ensure quality focus"},
                    {"title": "Hiring Manager Alignment", "description": "Require completed intake questionnaire before opening requisitions to set clear expectations"},
                    {"title": "Recovery Time Policy", "description": "Provide 1-week break after major hiring campaigns for recruiter recovery"}
                ]
            }]
        )
        # Team Lead Team Dashboards
        TeamData.objects.create(
            node=node_sanjay,
            content=[{
                "common_problems": [
                    {"problem": "On-Call Sleep Disruption", "description": "Team responding to production alerts 2-3 times nightly during on-call weeks destroying sleep quality and recovery"},
                    {"problem": "Technical Debt Guilt", "description": "Team knowing architectural shortcuts will cause future problems creating chronic background worry"},
                    {"problem": "Scope Creep Frustration", "description": "Requirements changing mid-sprint invalidating completed work and demoralizing team"}
                ],
                "recommendations": [
                    {"recommendation": "Implement better monitoring and auto-remediation to reduce manual on-call interventions"},
                    {"recommendation": "Schedule dedicated technical debt sprints to address guilt and improve system health proactively"},
                    {"recommendation": "Enforce requirement freeze after sprint planning to protect team focus and morale"}
                ],
                "policy_changes": [
                    {"title": "On-Call Recovery", "description": "Mandatory day off after on-call week for sleep recovery and restoration"},
                    {"title": "Technical Debt Budget", "description": "Allocate minimum 20% of sprint capacity for addressing technical debt"},
                    {"title": "Requirement Stability", "description": "Freeze requirements 48 hours after sprint planning with formal change request process"}
                ]
            }]
        )
        TeamData.objects.create(
            node=node_pooja,
            content=[{
                "common_problems": [
                    {"problem": "Gateway Critical Path Pressure", "description": "Being dependency for all services creating constant pressure to never fail and high anxiety"},
                    {"problem": "Performance Micro-optimization", "description": "Team spending excessive time optimizing latency with diminishing returns and increasing stress"},
                    {"problem": "Knowledge Concentration", "description": "Legacy gateway components understood by only one person creating vacation anxiety and risk"}
                ],
                "recommendations": [
                    {"recommendation": "Build redundancy in gateway architecture to reduce single point of failure pressure"},
                    {"recommendation": "Establish performance budgets and stop optimizing once acceptable thresholds are met"},
                    {"recommendation": "Document and cross-train on legacy components to distribute knowledge burden across team"}
                ],
                "policy_changes": [
                    {"title": "Performance SLA Standards", "description": "Define acceptable latency ranges to prevent perfectionist over-optimization"},
                    {"title": "Knowledge Distribution", "description": "Require pairing and documentation for all critical system components"},
                    {"title": "Gateway Architecture Review", "description": "Quarterly architecture review to identify and eliminate single points of failure"}
                ]
            }]
        )
        TeamData.objects.create(
            node=node_aditya,
            content=[{
                "common_problems": [
                    {"problem": "Design Handoff Incompleteness", "description": "Receiving partial designs mid-development causing rework frustration and timeline slippage"},
                    {"problem": "Browser Compatibility Rabbit Holes", "description": "Obscure browser bugs consuming disproportionate debugging time and energy"},
                    {"problem": "Creative Fulfillment Gap", "description": "Repetitive CRUD interface work lacking creative challenge causing motivation decline"}
                ],
                "recommendations": [
                    {"recommendation": "Establish design completeness checklist before implementation begins"},
                    {"recommendation": "Use automated browser testing tools to catch compatibility issues earlier in cycle"},
                    {"recommendation": "Rotate team through different types of work and allocate time for creative side projects"}
                ],
                "policy_changes": [
                    {"title": "Design Acceptance Criteria", "description": "Require signed-off high-fidelity designs before sprint planning"},
                    {"title": "Browser Testing Automation", "description": "Invest in cloud testing services to reduce manual browser debugging burden"},
                    {"title": "Innovation Time", "description": "Allocate 10% time for exploring new frontend technologies and creative projects"}
                ]
            }]
        )
        TeamData.objects.create(
            node=node_neha,
            content=[{
                "common_problems": [
                    {"problem": "App Store Rejection Fear", "description": "Anxiety about Apple/Google rejection causing excessive pre-submission testing and delays"},
                    {"problem": "Platform Fragmentation Exhaustion", "description": "Supporting both iOS and Android with different paradigms causing mental context switching"},
                    {"problem": "Release Helplessness", "description": "Inability to quickly fix production bugs due to app review delays creating frustration"}
                ],
                "recommendations": [
                    {"recommendation": "Develop comprehensive pre-submission checklist following store guidelines to reduce anxiety"},
                    {"recommendation": "Invest in shared component library to reduce platform-specific development differences"},
                    {"recommendation": "Implement robust beta testing program to catch issues before production release"}
                ],
                "policy_changes": [
                    {"title": "App Store Preparation", "description": "Allocate 3 days pre-submission buffer for thorough testing and review"},
                    {"title": "Cross-Platform Strategy", "description": "Evaluate React Native or Flutter to reduce platform maintenance burden"},
                    {"title": "Beta Testing Requirements", "description": "Mandate minimum 2-week beta period before production releases"}
                ]
            }]
        )
        TeamData.objects.create(
            node=node_manish,
            content=[{
                "common_problems": [
                    {"problem": "Long Cycle Forecasting Difficulty", "description": "9-12 month deals making accurate revenue forecasting impossible and creating leadership tension"},
                    {"problem": "Executive Presentation Anxiety", "description": "High-stakes C-suite meetings causing significant pre-presentation stress and self-doubt"},
                    {"problem": "Deal Concentration Risk", "description": "Quarterly targets dependent on 2-3 large deals creating all-or-nothing pressure"}
                ],
                "recommendations": [
                    {"recommendation": "Build larger pipeline with more deals to distribute risk and smooth forecasting"},
                    {"recommendation": "Provide executive presence coaching to build confidence in senior stakeholder engagement"},
                    {"recommendation": "Work with leadership to adjust quota methodology accounting for deal cycle length"}
                ],
                "policy_changes": [
                    {"title": "Pipeline Development Focus", "description": "Protect 25% of time for new opportunity development vs servicing active deals"},
                    {"title": "Forecast Methodology", "description": "Implement multi-quarter rolling forecasts to account for long sales cycles"},
                    {"title": "Executive Skills Training", "description": "Provide annual executive presence and C-suite engagement training"}
                ]
            }]
        )
        TeamData.objects.create(
            node=node_sneha,
            content=[{
                "common_problems": [
                    {"problem": "High-Volume Rejection Fatigue", "description": "Team hearing 'no' hundreds of times daily accumulating emotional toll despite individual resilience"},
                    {"problem": "Metric Surveillance Anxiety", "description": "Constant activity monitoring creating performance pressure and sense of being watched"},
                    {"problem": "Repetitive Conversation Burnout", "description": "Same sales script dozens of times daily feeling robotic and soul-draining"}
                ],
                "recommendations": [
                    {"recommendation": "Implement daily rejection processing rituals and peer support groups"},
                    {"recommendation": "Shift focus from activity metrics to outcome metrics like conversion rate and deal quality"},
                    {"recommendation": "Allow script personalization within guidelines to maintain authenticity and prevent monotony"}
                ],
                "policy_changes": [
                    {"title": "Metric Rebalancing", "description": "Reduce emphasis on call volume in favor of conversation quality and conversion metrics"},
                    {"title": "Peer Support Sessions", "description": "Weekly team sessions for processing rejection and celebrating resilience"},
                    {"title": "Script Evolution", "description": "Quarterly script updates with team input to maintain freshness and engagement"}
                ]
            }]
        )
        TeamData.objects.create(
            node=node_rohit,
            content=[{
                "common_problems": [
                    {"problem": "Campus Season Intensity", "description": "3-month recruitment blitz with constant travel and events causing complete team exhaustion"},
                    {"problem": "Candidate Rejection Burden", "description": "Disappointing hundreds of hopeful students causing compassion fatigue and emotional drain"},
                    {"problem": "Seasonal Workload Imbalance", "description": "Extreme peaks and valleys in work creating job security anxiety during slow periods"}
                ],
                "recommendations": [
                    {"recommendation": "Request additional temporary recruiter support during peak campus season"},
                    {"recommendation": "Develop compassionate rejection templates and process emotions through peer debriefing"},
                    {"recommendation": "Diversify responsibilities beyond campus recruiting to create year-round value"}
                ],
                "policy_changes": [
                    {"title": "Campus Season Staffing", "description": "Hire contract recruiters for peak 3-month campus recruitment season"},
                    {"title": "Post-Season Recovery", "description": "Mandatory 1-week break after campus season completion for team recovery"},
                    {"title": "Role Diversification", "description": "Expand campus recruiter responsibilities to include employer branding and intern programs year-round"}
                ]
            }]
        )
        # Final summary
        self.stdout.write(self.style.SUCCESS('\n✅ Successfully created comprehensive test data!'))
        self.stdout.write(self.style.SUCCESS(f'Company: {comp.name}'))
        self.stdout.write(self.style.SUCCESS(f'Total Users: {User.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Total Nodes: {OrgNode.objects.filter(company=comp).count()}'))
        self.stdout.write(self.style.SUCCESS(f'User Dashboards: {UserDashboard.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Team Dashboards: {TeamData.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Psycho Data: {UserPsycoProcessedData.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Psycho History: {UserPsycoProcessedDataHistory.objects.count()}'))
        self.stdout.write(self.style.SUCCESS('\n📊 Hierarchy Structure:'))
        self.stdout.write(self.style.SUCCESS('Level 1 (CEO): 1 person'))
        self.stdout.write(self.style.SUCCESS('Level 2 (VPs/Directors): 3 people'))
        self.stdout.write(self.style.SUCCESS('Level 3 (Managers): 6 people'))
        self.stdout.write(self.style.SUCCESS('Level 4 (Team Leads): 9 people'))
        self.stdout.write(self.style.SUCCESS('Level 5 (Employees): 20 people'))
        self.stdout.write(self.style.SUCCESS('TOTAL: 39 employees'))
        self.stdout.write(self.style.SUCCESS('\n🔐 All passwords: password123'))
        self.stdout.write(self.style.SUCCESS('\n👥 Sample login accounts:'))
        self.stdout.write(self.style.SUCCESS('CEO: rajesh.kumar'))
        self.stdout.write(self.style.SUCCESS('VP Engineering: priya.sharma'))
        self.stdout.write(self.style.SUCCESS('VP Sales: vikram.patel'))
        self.stdout.write(self.style.SUCCESS('Director HR: anjali.reddy'))
        self.stdout.write(self.style.SUCCESS('Manager (Backend): arjun.singh'))
        self.stdout.write(self.style.SUCCESS('Team Lead (Microservices): sanjay.reddy'))
        self.stdout.write(self.style.SUCCESS('Engineer: amit.verma'))