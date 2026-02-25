# app_1/management/commands/setup_dev_data.py
import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app_1.models import (
    Company, StructureLevel, OrgNode, UserDashboard, TeamData, 
    UserPsycoProcessedData, UserPsycoProcessedDataHistory
)
from app_1.tasks import generate_drill_down_lists
UserDashboard.objects.all().delete()
TeamData.objects.all().delete()
OrgNode.objects.all().delete()
User.objects.exclude(is_superuser=True).delete()
Company.objects.all().delete()
class Command(BaseCommand):
    help = 'Generates comprehensive company hierarchy with Indian employees and detailed mental health data'

    def create_user_and_node(self, username, name, company, structure_level, parent=None):
        """Helper to create user and node"""
        u, _ = User.objects.get_or_create(username=username)
        u.set_password("password123")
        u.save()
        node = OrgNode.objects.create(
            user=u, 
            name=name, 
            company=company,
            structure_level=structure_level,  
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

    def generate_mock_psycho_data(self):
        """Generates a randomized block of psychometric data following the exact JSON structure"""
        def gen_items(questions, max_val):
            return {q: random.randint(0, max_val) for q in questions}

        dep_q = [
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
        
        anx_q = [
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

        # Process Depression Mock Data
        dep_items = gen_items(dep_q, 4) 
        dep_score = sum(dep_items.values())
        if dep_score <= 13: dep_sev = "Normal"
        elif dep_score <= 19: dep_sev = "Mild Depression"
        elif dep_score <= 28: dep_sev = "Moderate Depression"
        elif dep_score <= 35: dep_sev = "Severe Depression"
        else: dep_sev = "Very Severe Depression"

        # Process Anxiety Mock Data
        anx_items = gen_items(anx_q, 4)
        anx_score = sum(anx_items.values())
        if anx_score <= 14: anx_sev = "Normal"
        elif anx_score <= 25: anx_sev = "Moderate Anxiety"
        elif anx_score <= 35: anx_sev = "Severe Anxiety"
        else: anx_sev = "Very Severe Anxiety"

        # Process Burnout
        ee = random.randint(5, 30)
        dp = random.randint(0, 20)
        pa = random.randint(15, 36)

        overall_burnout = "Burnout Risk (partial)" if (ee > 20 or dp > 10) else "Low Risk"
        risk_level = "High" if "Severe" in dep_sev or "Severe" in anx_sev else "Moderate" if "Moderate" in dep_sev else "Low"
        
        flags = []
        if "Normal" not in dep_sev: flags.append(f"Depression: {dep_sev}")
        if "Normal" not in anx_sev: flags.append(f"Anxiety: {anx_sev}")
        if overall_burnout != "Low Risk": flags.append(f"Burnout: {overall_burnout}")

        return {
            "big_five": {
                "Neuroticism": {
                    "raw_score": round(random.uniform(1.0, 5.0), 2),
                    "max_possible": 5.0,
                    "level": random.choice(["low", "average", "high"]),
                    "items_scored": 10,
                    "interpretation": "Moderate emotional reactivity; occasional stress or worry."
                },
                "Extraversion": {
                    "raw_score": round(random.uniform(1.0, 5.0), 2),
                    "max_possible": 5.0,
                    "level": random.choice(["low", "average", "high"]),
                    "items_scored": 9,
                    "interpretation": "Moderately social; comfortable both alone and with others."
                },
                "Openness to Experience": {
                    "raw_score": round(random.uniform(2.0, 5.0), 2),
                    "max_possible": 5.0,
                    "level": random.choice(["average", "high"]),
                    "items_scored": 9,
                    "interpretation": "Highly curious, creative, imaginative, and open to new ideas."
                },
                "Agreeableness": {
                    "raw_score": round(random.uniform(2.5, 5.0), 2),
                    "max_possible": 5.0,
                    "level": random.choice(["average", "high"]),
                    "items_scored": 10,
                    "interpretation": "Cooperative, trusting, empathetic, and eager to help others."
                },
                "Conscientiousness": {
                    "raw_score": round(random.uniform(2.5, 5.0), 2),
                    "max_possible": 5.0,
                    "level": random.choice(["average", "high"]),
                    "items_scored": 11,
                    "interpretation": "Highly disciplined, organized, reliable, and achievement-oriented."
                }
            },
            "burnout": {
                "Emotional Exhaustion": {
                    "score": ee, "max_possible": 36, "level": "High" if ee > 20 else "Low",
                    "interpretation": f"EE score {ee} \u2192 {'High' if ee > 20 else 'Low'} emotional exhaustion."
                },
                "Depersonalization": {
                    "score": dp, "max_possible": 30, "level": "High" if dp > 10 else "Low",
                    "interpretation": f"DP score {dp} \u2192 {'High' if dp > 10 else 'Low'} depersonalization."
                },
                "Personal Accomplishment": {
                    "score": pa, "max_possible": 36, "level": "Low" if pa < 25 else "High",
                    "interpretation": f"PA score {pa} \u2192 {'Low' if pa < 25 else 'High'} sense of accomplishment."
                },
                "overall_burnout": overall_burnout
            },
            "depression": {
                "total_score": dep_score,
                "max_possible": 52,
                "severity": dep_sev,
                "interpretation": f"{dep_sev} detected based on psychometric scores.",
                "item_scores": dep_items
            },
            "anxiety": {
                "total_score": anx_score,
                "max_possible": 56,
                "severity": anx_sev,
                "interpretation": f"{anx_sev} detected based on somatic and psychic evaluation.",
                "psychic_subscale_score": sum(list(anx_items.values())[:6]),
                "somatic_subscale_score": sum(list(anx_items.values())[6:]),
                "item_scores": anx_items
            },
            "clinical_summary": {
                "overall_risk_level": risk_level,
                "active_clinical_flags": flags,
                "comorbidity_note": "Co-occurring conditions detected and analyzed." if len(flags) > 1 else "No significant comorbidities.",
                "recommendation": "Urgent clinical referral recommended." if risk_level == "High" else "Monitor and provide resources."
            }
        }

    def create_psyco_data(self, user):
        """Creates the PsychoData and PsychoDataHistory for the provided user"""
        current_data = self.generate_mock_psycho_data()
        
        # 1. UserPsycoProcessedData (Try exact fields first, fallback to JSON "content" field)
        try:
            UserPsycoProcessedData.objects.update_or_create(
                user=user,
                defaults={
                    "big_five": current_data["big_five"],
                    "burnout": current_data["burnout"],
                    "depression": current_data["depression"],
                    "anxiety": current_data["anxiety"],
                    "clinical_summary": current_data["clinical_summary"]
                }
            )
        except Exception:
            try:
                UserPsycoProcessedData.objects.update_or_create(user=user, defaults={"content": current_data})
            except Exception as e:
                pass # Silently pass if model schema differs to avoid breaking the script
        
        # 2. UserPsycoProcessedDataHistory
        history_records = []
        for i in range(2):
            past_data = self.generate_mock_psycho_data()
            date_str = f"{random.randint(1,12):02d}-{random.randint(1,28):02d}-26"
            history_records.append({
                "content": past_data,
                "date": date_str
            })

        try:
            UserPsycoProcessedDataHistory.objects.update_or_create(
                user=user,
                defaults={"content": history_records}
            )
        except Exception:
            pass

    def handle(self, *args, **kwargs):
        self.stdout.write("Cleaning old data...")
        UserDashboard.objects.all().delete()
        TeamData.objects.all().delete()
        OrgNode.objects.all().delete()
        
        # Also clean up the new psychometric data modules
        try:
            UserPsycoProcessedData.objects.all().delete()
            UserPsycoProcessedDataHistory.objects.all().delete()
        except Exception:
            pass

        User.objects.exclude(is_superuser=True).delete()
        Company.objects.all().delete()

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
                {"recommendation": "Schedule quarterly leadership retreats to reconnect with personal values and long-term vision"}
            ]
        )
        self.create_psyco_data(u_rajesh)

        # 3. LEVEL 2: VP Engineering
        u_priya, node_priya = self.create_user_and_node(
            "priya.sharma", "Priya Sharma (VP Engineering)", comp, lvl_2, node_rajesh
        )
        self.create_user_dashboard(
            u_priya,
            positive=[
                {"positive": "Exceptional technical leadership with strong ability to mentor and develop engineering talent"},
                {"positive": "Maintains composure during production incidents and models calm problem-solving for team"},
                {"positive": "Proactively addresses burnout in team through workload monitoring and resource allocation"}
            ],
            problems=[
                {"problem": "Constant Context Switching", "description": "Jumping between technical reviews, people management, and strategic planning causes mental fragmentation and reduced effectiveness"},
                {"problem": "On-Call Anxiety", "description": "Even when not on-call, experiences hypervigilance about production systems affecting relaxation"},
                {"problem": "Perfectionism", "description": "Setting unrealistically high standards for self and team, leading to delayed releases and team stress"}
            ],
            recommendations=[
                {"recommendation": "Implement time-blocking with dedicated focus hours for deep technical work vs meetings"},
                {"recommendation": "Establish clearer on-call rotation and escalation procedures to reduce personal responsibility burden"}
            ]
        )
        self.create_psyco_data(u_priya)

        # VP Sales
        u_vikram, node_vikram = self.create_user_and_node(
            "vikram.patel", "Vikram Patel (VP Sales)", comp, lvl_2, node_rajesh
        )
        self.create_user_dashboard(
            u_vikram,
            positive=[
                {"positive": "Charismatic leadership style that motivates sales team and drives strong revenue performance"},
                {"positive": "Resilient in face of rejection and maintains optimistic outlook even during tough quarters"}
            ],
            problems=[
                {"problem": "Performance Pressure", "description": "Quarterly targets create intense stress cycles with anxiety peaking in final month of each quarter"},
                {"problem": "Client Entertainment Fatigue", "description": "Regular evening dinners and weekend golf with clients leaving minimal personal time and affecting physical health"}
            ],
            recommendations=[
                {"recommendation": "Work with CEO to establish more realistic quarterly targets with longer evaluation cycles"},
                {"recommendation": "Limit client entertainment to 2 evenings per week and explore daytime networking alternatives"}
            ]
        )
        self.create_psyco_data(u_vikram)

        # Director HR
        u_anjali, node_anjali = self.create_user_and_node(
            "anjali.reddy", "Anjali Reddy (Director HR)", comp, lvl_2, node_rajesh
        )
        self.create_user_dashboard(
            u_anjali,
            positive=[
                {"positive": "Deeply compassionate approach to employee welfare with genuine care for organizational wellbeing"},
                {"positive": "Strong conflict resolution skills helping de-escalate tense workplace situations"}
            ],
            problems=[
                {"problem": "Vicarious Trauma", "description": "Absorbing emotional distress from employees sharing mental health struggles, harassment cases, and personal crises"},
                {"problem": "Compassion Fatigue", "description": "Emotional exhaustion from continuous caregiving role reducing capacity for empathy"}
            ],
            recommendations=[
                {"recommendation": "Engage personal therapist to process vicarious trauma and maintain emotional wellbeing"},
                {"recommendation": "Establish clear role boundaries about what HR can/cannot address regarding mental health"}
            ]
        )
        self.create_psyco_data(u_anjali)

        # LEVEL 3: MANAGERS
        u_arjun, node_arjun = self.create_user_and_node("arjun.singh", "Arjun Singh (Engineering Manager - Backend)", comp, lvl_3, node_priya)
        self.create_user_dashboard(u_arjun, positive=[{"positive": "Patient and supportive management style helps junior developers grow confidence"}], problems=[{"problem": "Meeting Overload", "description": "Back-to-back meetings from 9 AM to 6 PM"}], recommendations=[{"recommendation": "Implement 'No Meeting Fridays'"}])
        self.create_psyco_data(u_arjun)

        u_meera, node_meera = self.create_user_and_node("meera.iyer", "Meera Iyer (Engineering Manager - Frontend)", comp, lvl_3, node_priya)
        self.create_user_dashboard(u_meera, positive=[{"positive": "Advocates effectively for team needs in resource allocation discussions"}], problems=[{"problem": "Design-Engineering Conflict", "description": "Mediating constant tensions"}], recommendations=[{"recommendation": "Facilitate regular design-engineering alignment sessions"}])
        self.create_psyco_data(u_meera)

        u_karthik, node_karthik = self.create_user_and_node("karthik.nair", "Karthik Nair (Sales Manager - Enterprise)", comp, lvl_3, node_vikram)
        self.create_user_dashboard(u_karthik, positive=[{"positive": "Exceptional relationship builder who maintains long-term client partnerships"}], problems=[{"problem": "Travel Exhaustion", "description": "15-20 days monthly travel disrupting sleep"}], recommendations=[{"recommendation": "Negotiate travel reduction by clustering client visits"}])
        self.create_psyco_data(u_karthik)

        u_divya, node_divya = self.create_user_and_node("divya.menon", "Divya Menon (Sales Manager - SMB)", comp, lvl_3, node_vikram)
        self.create_user_dashboard(u_divya, positive=[{"positive": "Adaptable and quickly adjusts sales approach based on market feedback"}], problems=[{"problem": "Volume Pressure", "description": "Managing 40+ small accounts simultaneously"}], recommendations=[{"recommendation": "Implement CRM automation and templates"}])
        self.create_psyco_data(u_divya)

        u_rahul, node_rahul = self.create_user_and_node("rahul.gupta", "Rahul Gupta (HR Manager - Talent Acquisition)", comp, lvl_3, node_anjali)
        self.create_user_dashboard(u_rahul, positive=[{"positive": "Builds genuine connections with candidates creating positive candidate experience"}], problems=[{"problem": "Requisition Overload", "description": "15+ open positions with aggressive timelines"}], recommendations=[{"recommendation": "Work with leadership to prioritize requisitions"}])
        self.create_psyco_data(u_rahul)

        # LEVEL 4: TEAM LEADS
        u_sanjay, node_sanjay = self.create_user_and_node("sanjay.reddy", "Sanjay Reddy (Team Lead - Microservices)", comp, lvl_4, node_arjun)
        self.create_user_dashboard(u_sanjay, positive=[{"positive": "Deep technical expertise"}], problems=[{"problem": "On-Call Burnout", "description": "Responding to production alerts"}], recommendations=[{"recommendation": "Advocate for better monitoring"}])
        self.create_psyco_data(u_sanjay)

        u_pooja, node_pooja = self.create_user_and_node("pooja.desai", "Pooja Desai (Team Lead - API Gateway)", comp, lvl_4, node_arjun)
        self.create_user_dashboard(u_pooja, positive=[{"positive": "Proactive in identifying potential issues"}], problems=[{"problem": "Gateway Dependency Stress", "description": "Being critical path"}], recommendations=[{"recommendation": "Build redundancy in gateway architecture"}])
        self.create_psyco_data(u_pooja)

        u_aditya, node_aditya = self.create_user_and_node("aditya.krishnan", "Aditya Krishnan (Team Lead - Web App)", comp, lvl_4, node_meera)
        self.create_user_dashboard(u_aditya, positive=[{"positive": "User-centric mindset"}], problems=[{"problem": "Framework Fatigue", "description": "Constant evolution of JS ecosystem"}], recommendations=[{"recommendation": "Establish technology evaluation framework"}])
        self.create_psyco_data(u_aditya)

        u_neha, node_neha = self.create_user_and_node("neha.kapoor", "Neha Kapoor (Team Lead - Mobile App)", comp, lvl_4, node_meera)
        self.create_user_dashboard(u_neha, positive=[{"positive": "Detail-oriented approach"}], problems=[{"problem": "App Store Anxiety", "description": "Fear of app rejection"}], recommendations=[{"recommendation": "Develop comprehensive pre-submission checklist"}])
        self.create_psyco_data(u_neha)

        u_manish, node_manish = self.create_user_and_node("manish.joshi", "Manish Joshi (Team Lead - Enterprise Sales)", comp, lvl_4, node_karthik)
        self.create_user_dashboard(u_manish, positive=[{"positive": "Natural relationship builder"}], problems=[{"problem": "Long Sales Cycle Stress", "description": "9-12 month enterprise deals"}], recommendations=[{"recommendation": "Build larger pipeline"}])
        self.create_psyco_data(u_manish)

        u_sneha, node_sneha = self.create_user_and_node("sneha.shah", "Sneha Shah (Team Lead - SMB Sales)", comp, lvl_4, node_divya)
        self.create_user_dashboard(u_sneha, positive=[{"positive": "High activity level"}], problems=[{"problem": "Activity Metrics Pressure", "description": "Constant monitoring"}], recommendations=[{"recommendation": "Reframe metrics as personal game"}])
        self.create_psyco_data(u_sneha)

        u_rohit, node_rohit = self.create_user_and_node("rohit.malhotra", "Rohit Malhotra (Team Lead - Campus Hiring)", comp, lvl_4, node_rahul)
        self.create_user_dashboard(u_rohit, positive=[{"positive": "Passionate about developing fresh talent"}], problems=[{"problem": "Campus Season Burnout", "description": "3-month recruitment blitz"}], recommendations=[{"recommendation": "Negotiate additional team support"}])
        self.create_psyco_data(u_rohit)

        # LEVEL 5: EMPLOYEES
        self.stdout.write("Creating Level 5 employees...")
        
        backend_employees_sanjay = [
            ("amit.verma", "Amit Verma (Sr. Backend Engineer)", [{"positive": "Writes clean, well-tested code"}], [{"problem": "Code Review Anxiety", "description": "Fear of judgment during code reviews"}], [{"recommendation": "Shift mindset to view code reviews as collaborative"}]),
            ("kavya.pillai", "Kavya Pillai (Backend Engineer)", [{"positive": "Quick learner"}], [{"problem": "Impostor Syndrome", "description": "Constant comparison to senior engineers"}], [{"recommendation": "Keep achievement log"}]),
            ("vishal.bhatt", "Vishal Bhatt (Backend Engineer)", [{"positive": "Strong debugging skills"}], [{"problem": "Scope Creep Frustration", "description": "Requirements changing mid-sprint"}], [{"recommendation": "Advocate for requirement freeze"}])
        ]
        for username, name, positive, problems, recommendations in backend_employees_sanjay:
            u, node = self.create_user_and_node(username, name, comp, lvl_5, node_sanjay)
            self.create_user_dashboard(u, positive, problems, recommendations)
            self.create_psyco_data(u)

        backend_employees_pooja = [
            ("deepak.saxena", "Deepak Saxena (API Engineer)", [{"positive": "Meticulous attention to API design"}], [{"problem": "Breaking Change Anxiety", "description": "Fear of breaking external integrations"}], [{"recommendation": "Implement comprehensive API testing"}]),
            ("priyanka.choudhary", "Priyanka Choudhary (API Engineer)", [{"positive": "Excellent communicator"}], [{"problem": "Stakeholder Expectation Management", "description": "Difficulty saying no to unrealistic API requests"}], [{"recommendation": "Practice negotiation skills"}])
        ]
        for username, name, positive, problems, recommendations in backend_employees_pooja:
            u, node = self.create_user_and_node(username, name, comp, lvl_5, node_pooja)
            self.create_user_dashboard(u, positive, problems, recommendations)
            self.create_psyco_data(u)

        frontend_employees_aditya = [
            ("ravi.kumar", "Ravi Kumar (Frontend Engineer)", [{"positive": "Strong sense of visual design"}], [{"problem": "Design-Dev Handoff Friction", "description": "Receiving incomplete designs"}], [{"recommendation": "Establish design acceptance criteria"}]),
            ("ishita.malhotra", "Ishita Malhotra (Frontend Engineer)", [{"positive": "Strong accessibility advocate"}], [{"problem": "Accessibility vs Timeline Conflict", "description": "Wanting to build accessible features"}], [{"recommendation": "Build accessibility into definition of done"}]),
            ("gaurav.singh", "Gaurav Singh (Frontend Engineer)", [{"positive": "Excellent problem solver"}], [{"problem": "State Management Complexity", "description": "Global state growing unwieldy"}], [{"recommendation": "Refactor to use local state by default"}])
        ]
        for username, name, positive, problems, recommendations in frontend_employees_aditya:
            u, node = self.create_user_and_node(username, name, comp, lvl_5, node_aditya)
            self.create_user_dashboard(u, positive, problems, recommendations)
            self.create_psyco_data(u)

        mobile_employees_neha = [
            ("akash.jain", "Akash Jain (Mobile Engineer - iOS)", [{"positive": "Passionate about creating delightful user experiences"}], [{"problem": "App Review Rejection Stress", "description": "Fear of Apple rejection"}], [{"recommendation": "Build comprehensive pre-submission checklist"}]),
            ("shweta.rao", "Shweta Rao (Mobile Engineer - Android)", [{"positive": "Adept at handling Android device fragmentation"}], [{"problem": "Device Fragmentation Nightmare", "description": "Testing across hundreds of Android device combinations"}], [{"recommendation": "Focus testing on top 80% devices"}])
        ]
        for username, name, positive, problems, recommendations in mobile_employees_neha:
            u, node = self.create_user_and_node(username, name, comp, lvl_5, node_neha)
            self.create_user_dashboard(u, positive, problems, recommendations)
            self.create_psyco_data(u)

        enterprise_sales_employees = [
            ("ankit.agarwal", "Ankit Agarwal (Enterprise Sales Rep)", [{"positive": "Builds genuine relationships"}], [{"problem": "Deal Loss Devastation", "description": "Months of work lost to competitor"}], [{"recommendation": "Conduct post-loss analysis"}]),
            ("nidhi.bansal", "Nidhi Bansal (Enterprise Sales Rep)", [{"positive": "Strategic thinker"}], [{"problem": "Work-Life Integration Struggle", "description": "Client demands bleeding into personal time"}], [{"recommendation": "Set explicit availability windows"}])
        ]
        for username, name, positive, problems, recommendations in enterprise_sales_employees:
            u, node = self.create_user_and_node(username, name, comp, lvl_5, node_manish)
            self.create_user_dashboard(u, positive, problems, recommendations)
            self.create_psyco_data(u)

        smb_sales_employees = [
            ("rajat.khanna", "Rajat Khanna (SMB Sales Rep)", [{"positive": "High energy and enthusiasm"}], [{"problem": "Call Reluctance", "description": "Building anxiety before cold calling sessions"}], [{"recommendation": "Develop pre-call warm-up routine"}]),
            ("swati.kulkarni", "Swati Kulkarni (SMB Sales Rep)", [{"positive": "Empathetic approach"}], [{"problem": "Emotional Labor Exhaustion", "description": "Constantly maintaining upbeat persona"}], [{"recommendation": "Allow moments of authentic emotion"}]),
            ("varun.prasad", "Varun Prasad (SMB Sales Rep)", [{"positive": "Natural storyteller"}], [{"problem": "Financial Stress", "description": "Variable commission structure"}], [{"recommendation": "Negotiate higher base salary or budget conservatively"}])
        ]
        for username, name, positive, problems, recommendations in smb_sales_employees:
            u, node = self.create_user_and_node(username, name, comp, lvl_5, node_sneha)
            self.create_user_dashboard(u, positive, problems, recommendations)
            self.create_psyco_data(u)

        recruiter_employees = [
            ("pallavi.deshmukh", "Pallavi Deshmukh (Campus Recruiter)", [{"positive": "Genuine passion"}], [{"problem": "Campus Season Overwhelm", "description": "Managing 1000+ applicants"}], [{"recommendation": "Request additional recruiter support"}]),
            ("siddharth.yadav", "Siddharth Yadav (Technical Recruiter)", [{"positive": "Strong technical understanding"}], [{"problem": "Talent Shortage Stress", "description": "Unable to find qualified candidates"}], [{"recommendation": "Educate hiring managers on market realities"}])
        ]
        for username, name, positive, problems, recommendations in recruiter_employees:
            u, node = self.create_user_and_node(username, name, comp, lvl_5, node_rohit)
            self.create_user_dashboard(u, positive, problems, recommendations)
            self.create_psyco_data(u)

        # Generate drill-down lists for all nodes
        self.stdout.write("Generating drill down lists for all nodes...")
        all_nodes = OrgNode.objects.filter(company=comp).order_by('structure_level')
        for node in all_nodes:
            generate_drill_down_lists(node)

        # Create Team Dashboards for all non-leaf nodes
        self.stdout.write("Creating team dashboards...")
        
        TeamData.objects.create(
            node=node_rajesh,
            content=[{
                "common_problems": [
                    {"problem": "Cross-Department Silos", "description": "Engineering, Sales, and HR operating independently leading to misalignment"}
                ],
                "recommendations": [
                    {"recommendation": "Establish quarterly cross-functional town halls to improve transparency"}
                ],
                "policy_changes": [
                    {"title": "Mental Health Days Policy", "description": "Provide 4 dedicated mental health days per year"}
                ]
            }]
        )
        
        TeamData.objects.create(
            node=node_priya,
            content=[{
                "common_problems": [{"problem": "On-Call Burnout", "description": "Engineers experiencing sleep disruption"}],
                "recommendations": [{"recommendation": "Implement follow-the-sun on-call rotation"}],
                "policy_changes": [{"title": "On-Call Compensation", "description": "Provide additional PTO days"}]
            }]
        )
        
        TeamData.objects.create(
            node=node_vikram,
            content=[{
                "common_problems": [{"problem": "Quota Pressure Culture", "description": "Intense quarterly pressure"}],
                "recommendations": [{"recommendation": "Shift to rolling quarterly targets"}],
                "policy_changes": [{"title": "Client Entertainment Limits", "description": "Cap client entertainment"}]
            }]
        )

        TeamData.objects.create(
            node=node_anjali,
            content=[{
                "common_problems": [{"problem": "Vicarious Trauma Exposure", "description": "HR team absorbing emotional distress"}],
                "recommendations": [{"recommendation": "Provide regular supervision with external HR consultant"}],
                "policy_changes": [{"title": "HR Wellness Program", "description": "Provide dedicated wellness support for HR team"}]
            }]
        )

        # Final summary
        self.stdout.write(self.style.SUCCESS('\n✅ Successfully created comprehensive test data!'))
        self.stdout.write(self.style.SUCCESS(f'Company: {comp.name}'))
        self.stdout.write(self.style.SUCCESS(f'Total Users: {User.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Total Nodes: {OrgNode.objects.filter(company=comp).count()}'))
        self.stdout.write(self.style.SUCCESS(f'User Dashboards: {UserDashboard.objects.count()}'))
        try:
            self.stdout.write(self.style.SUCCESS(f'User Psychometric Datasets: {UserPsycoProcessedData.objects.count()}'))
        except Exception:
            pass
        self.stdout.write(self.style.SUCCESS(f'Team Dashboards: {TeamData.objects.count()}'))
        self.stdout.write(self.style.SUCCESS('\n🔐 All passwords: password123'))