# app_1/tasks.py
from datetime import date
from .models import ( OrgNode, UserChatSummary, UserDashboard, UserDashboard,
                    User, UserChatDB, UserDrillDown, TeamData, TeamDataHistory,
                    UserDashboardHistory,UserPersonalityData,UserPsycoData,
                    UserPsycoDataHistory,UserPersonalityDataHistoric,
                    UserPsycoProcessedDataHistory,UserPsycoProcessedData,
)
from django.shortcuts import get_object_or_404
from .problems_AI import TeamDashboard_data, UserDashboard_data
from .Ai import summarize_chat_history,assesment
import math
import json
import dataclasses
def generate_drill_down_lists(target):
   
    subordinates = target.children.all()
    
    drill_down_list, created = UserDrillDown.objects.get_or_create(
        owner=target.user,
        defaults={'content': []}
    )

    new_drill_down = []
    
    new_drill_down.append({
        "node_id": target.id,
        "name": target.name,
        "title": target.structure_level.name if target.structure_level else "No Title",
        "has_team": subordinates.exists() 
    })

    for child in subordinates:
        new_drill_down.append({
            "node_id": child.id,
            "name": child.name,
            "title": child.structure_level.name if child.structure_level else "No Title",
            "has_team": child.children.exists() 
        })

    drill_down_list.content = new_drill_down
    drill_down_list.save()
    
    return new_drill_down

def my_daily_function():
    #mid_night() # this will be uncomented in future
    #get_report()
    process_midnight_snapshots()


def get_direct_reports_ids(root_id, include_self=True):
    children_ids = list(OrgNode.objects.filter(parent_id=root_id).values_list('id', flat=True))
    
    if include_self:
        children_ids.append(root_id)
        
    return children_ids



def mid_night():# this is for chat summry--> but rn i am not to use it ,also i need to improve it for updated format of archit's ai 
    users = User.objects.all()
    for user in users:
        user_chats = UserChatDB.objects.filter(owner=user)
        for chat_session in user_chats:
                history_obj = get_object_or_404(UserChatDB, chat=chat_session, owner=user, to_be_summarized=True)
                # summarize the chat history
                summary = summarize_chat_history(history_obj.content)
                UserChatSummary.objects.clear(owner=user, chat=chat_session)
                UserChatSummary.objects.create(
                    owner=user,
                    chat=chat_session,
                    summary=summary
                )
                history_obj.to_be_summarized = False
                history_obj.save()

def get_report():
    users = User.objects.all()
    for user in users:
        User_data, created = UserPsycoData.objects.get_or_create(
            owner=user,
            defaults={'content': {
        "Personality": {
          "Does the user tend not to worry excessively?": "Neutral",
          "Does the user generally like most people they meet?": "Neutral",
          "Does the user have a very active imagination?": "Neutral",
          "Is the user known for prudence and common sense?": "Neutral",
          "Does the user often get angry about how people treat them?": "Neutral",
          "Does the user shy away from crowds of people?": "Neutral",
          "Are aesthetic and artistic concerns relatively unimportant to the user?": "Neutral",
          "Is the user not crafty or sly by nature?": "Neutral",
          "Does the user prefer keeping options open rather than planning everything in advance?": "Neutral",
          "Does the user rarely feel lonely or sad?": "Neutral",
          "Is the user dominant, forceful, and assertive?": "Neutral",
          "Does the user feel life would be uninteresting without strong emotions?": "Neutral",
          "Do some people perceive the user as selfish or egotistical?": "Neutral",
          "Does the user try to perform all assigned tasks conscientiously?": "Neutral",
          "Does the user dread making social blunders when interacting with others?": "Neutral",
          "Does the user have a leisurely style in work and play?": "Neutral",
          "Is the user fairly set in their ways?": "Neutral",
          "Does the user prefer cooperating with others rather than competing?": "Neutral",
          "Is the user easy-going and somewhat lackadaisical?": "Neutral",
          "Does the user rarely overindulge in anything?": "Neutral",
          "Does the user often crave excitement?": "Neutral",
          "Does the user enjoy playing with theories or abstract ideas?": "Neutral",
          "Does the user not mind bragging about talents and accomplishments?": "Neutral",
          "Is the user good at pacing themselves to complete tasks on time?": "Neutral",
          "Does the user often feel helpless and want others to solve their problems?": "Neutral",
          "Has the user never literally jumped for joy?": "Neutral",
          "Is the user often the life of the party?": "Neutral",
          "Does the user feel little concern for others?": "Neutral",
          "Is the user always prepared?": "Neutral",
          "Does the user get stressed out easily?": "Neutral",
          "Does the user have a rich vocabulary?": "Neutral",
          "Does the user tend not to talk much?": "Neutral",
          "Is the user interested in people?": "Neutral",
          "Does the user leave their belongings around?": "Neutral",
          "Is the user relaxed most of the time?": "Neutral",
          "Does the user have difficulty understanding abstract ideas?": "Neutral",
          "Does the user feel comfortable around people?": "Neutral",
          "Does the user insult people?": "Neutral",
          "Does the user pay attention to details?": "Neutral",
          "Does the user worry about things?": "Neutral",
          "Does the user have a vivid imagination?": "Neutral",
          "Does the user prefer to keep in the background?": "Neutral",
          "Is the user generally uninterested in others?": "Neutral",
          "Does the user like order?": "Neutral",
          "Is the user quiet around strangers?": "Neutral",
          "Does the user make people feel at ease?": "Neutral",
          "Is the user exacting or precise in their work?": "Neutral",
          "Does the user often feel sad or blue?": "Neutral",
          "Is the user full of ideas?": "Neutral"
        },
        "Burnout": {
          "Does the user feel emotionally exhausted because of their work?": "Neutral",
          "Does the user feel worn out at the end of a working day?": "Neutral",
          "Does the user feel tired upon waking and facing a new workday?": "Neutral",
          "Can the user easily understand the actions of colleagues or supervisors?": "Neutral",
          "Does the user feel they treat some colleagues impersonally, like objects?": "Neutral",
          "Does the user find working with people all day stressful?": "Neutral",
          "Is the user afraid their work is making them emotionally harder?": "Neutral",
          "Does the user feel full of energy?": "Neutral",
          "Does the user feel frustrated by their work?": "Neutral",
          "Does the user feel they work too hard?": "Neutral",
          "Is the user uninterested in what is going on with many colleagues?": "Neutral",
          "Does the user find direct contact with people at work too stressful?": "Neutral",
          "Does the user find it easy to create a relaxed work atmosphere?": "Neutral",
          "Does the user feel stimulated after working closely with colleagues?": "Neutral",
          "Has the user achieved many rewarding work objectives?": "Neutral",
          "Is the user relaxed when dealing with emotional problems at work?": "Neutral",
          "Does the user feel colleagues blame them for their problems?": "Neutral"
        },
        "Depression": {
          "Does the user experience a depressed mood such as sadness or hopelessness?": "Neutral",
          "Does the user experience feelings of guilt?": "Neutral",
          "Does the user experience suicidal thoughts or behaviors?": "Neutral",
          "Does the user have difficulty falling asleep?": "Neutral",
          "Does the user experience disturbed sleep during the night?": "Neutral",
          "Does the user wake up early due to sleep disturbance?": "Neutral",
          "Has the user's interest in work or activities decreased?": "Neutral",
          "Does the user show psychomotor slowing?": "Neutral",
          "Does the user experience agitation or restlessness?": "Neutral",
          "Does the user experience psychological anxiety?": "Neutral",
          "Does the user experience physical anxiety symptoms?": "Neutral",
          "Does the user experience gastrointestinal symptoms?": "Neutral",
          "Does the user experience general physical symptoms?": "Neutral",
          "Does the user experience sexual or genital symptoms?": "Neutral",
          "Does the user show excessive concern about health?": "Neutral"
        },
        "Anxiety": {
          "Does the user experience an anxious mood?": "Neutral",
          "Does the user experience tension or nervousness?": "Neutral",
          "Does the user experience fears?": "Neutral",
          "Does the user experience insomnia related to anxiety?": "Neutral",
          "Does the user have difficulty concentrating due to anxiety?": "Neutral",
          "Does the user experience depressed mood related to anxiety?": "Neutral",
          "Does the user experience muscular symptoms?": "Neutral",
          "Does the user experience sensory symptoms?": "Neutral",
          "Does the user experience cardiovascular symptoms?": "Neutral",
          "Does the user experience respiratory symptoms?": "Neutral",
          "Does the user experience gastrointestinal symptoms related to anxiety?": "Neutral",
          "Does the user experience genitourinary symptoms related to anxiety?": "Neutral",
          "Does the user experience autonomic symptoms?": "Neutral"
        }}}  
              )
        
        old_data_list = User_data.content if isinstance(User_data.content, dict) else {}
        b = []
        chats = []
        user_chats = UserChatDB.objects.filter(owner=user)
        total_words = 0
        for chat in user_chats:
            for item in chat.content:
                c = item.get("message","")
                words = c.split()
                total_words += len(words)
                estimated_tokens = math.ceil(total_words * 1.5)
                chats.append(chat)
                if estimated_tokens > 5000:
                    a = summarize_chat_history(chats)
                    chats = []
                    total_words = 0
                    b.append(a)

        b.append(chats)
        AI_data = assesment(old_data_list,b)
        AI_data = AI_data
        processed_data = {"content":AI_data,
                          "date": str(date.today())}
        history_doc, created = UserPsycoDataHistory.objects.get_or_create(
            owner=user,
            content= []
        )
        old_data_list = AI_data
        User_data.content = old_data_list
        User_data.save()
        history_list = history_doc.content if isinstance(history_doc.content, list) else {}
        history_list.append(processed_data)
        history_doc.content = history_list
        history_doc.save()
        # data processing 
        from dataclasses import dataclass, field
        from typing import Dict, Tuple
        import json

        def likert_5(response: str) -> int:
            """Disagree=1, Neutral=3, Agree=5 (standard 5-point Likert)"""
            return {"Disagree": 1, "Neutral": 3, "Agree": 5}.get(response, 3)

        def likert_5_reversed(response: str) -> int:
            """Reversed: Agree=1, Neutral=3, Disagree=5"""
            return {"Disagree": 5, "Neutral": 3, "Agree": 1}.get(response, 3)

        def mbi_score(response: str) -> float:
            """MBI frequency: Disagree~0, Neutral~3, Agree~6"""
            return {"Disagree": 0, "Neutral": 3, "Agree": 6}.get(response, 3)

        def mbi_score_reversed(response: str) -> float:
            return {"Disagree": 6, "Neutral": 3, "Agree": 0}.get(response, 3)

        def ham_score_0_2(response: str) -> int:
            """HAM-D/HAM-A items: 0=absent, 1=mild/doubtful, 2=clearly present"""
            return {"Disagree": 0, "Neutral": 1, "Agree": 2}.get(response, 1)

        def ham_score_0_4(response: str) -> int:
            """HAM-D/HAM-A items with 0-4 scale (more granular symptoms)"""
            return {"Disagree": 0, "Neutral": 2, "Agree": 4}.get(response, 2)

        # Factors: N=Neuroticism, E=Extraversion, O=Openness, A=Agreeableness, C=Conscientiousness
        BIG_FIVE_ITEMS: Dict[str, Tuple[str, bool]] = {
            "Does the user tend not to worry excessively?":                    ("N", True),   # low N
            "Does the user generally like most people they meet?":             ("A", False),
            "Does the user have a very active imagination?":                   ("O", False),
            "Is the user known for prudence and common sense?":                ("C", False),
            "Does the user often get angry about how people treat them?":      ("N", False),  # negative affect
            "Does the user shy away from crowds of people?":                   ("E", True),   # reverse E
            "Are aesthetic and artistic concerns relatively unimportant to the user?": ("O", True),  # reverse O
            "Is the user not crafty or sly by nature?":                        ("A", False),
            "Does the user prefer keeping options open rather than planning everything in advance?": ("C", True), # reverse C
            "Does the user rarely feel lonely or sad?":                        ("N", True),
            "Is the user dominant, forceful, and assertive?":                  ("E", False),
            "Does the user feel life would be uninteresting without strong emotions?": ("O", False),
            "Do some people perceive the user as selfish or egotistical?":     ("A", True),
            "Does the user try to perform all assigned tasks conscientiously?": ("C", False),
            "Does the user dread making social blunders when interacting with others?": ("N", False),
            "Does the user have a leisurely style in work and play?":          ("C", True),
            "Is the user fairly set in their ways?":                           ("O", True),
            "Does the user prefer cooperating with others rather than competing?": ("A", False),
            "Is the user easy-going and somewhat lackadaisical?":              ("C", True),
            "Does the user rarely overindulge in anything?":                   ("N", True),
            "Does the user often crave excitement?":                           ("E", False),
            "Does the user enjoy playing with theories or abstract ideas?":    ("O", False),
            "Does the user not mind bragging about talents and accomplishments?": ("A", True),
            "Is the user good at pacing themselves to complete tasks on time?": ("C", False),
            "Does the user often feel helpless and want others to solve their problems?": ("N", False),
            "Has the user never literally jumped for joy?":                    ("E", True),
            "Is the user often the life of the party?":                        ("E", False),
            "Does the user feel little concern for others?":                   ("A", True),
            "Is the user always prepared?":                                    ("C", False),
            "Does the user get stressed out easily?":                          ("N", False),
            "Does the user have a rich vocabulary?":                           ("O", False),
            "Does the user tend not to talk much?":                            ("E", True),
            "Is the user interested in people?":                               ("A", False),
            "Does the user leave their belongings around?":                    ("C", True),
            "Is the user relaxed most of the time?":                           ("N", True),
            "Does the user have difficulty understanding abstract ideas?":     ("O", True),
            "Does the user feel comfortable around people?":                   ("E", False),
            "Does the user insult people?":                                    ("A", True),
            "Does the user pay attention to details?":                         ("C", False),
            "Does the user worry about things?":                               ("N", False),
            "Does the user have a vivid imagination?":                         ("O", False),
            "Does the user prefer to keep in the background?":                 ("E", True),
            "Is the user generally uninterested in others?":                   ("A", True),
            "Does the user like order?":                                       ("C", False),
            "Is the user quiet around strangers?":                             ("E", True),
            "Does the user make people feel at ease?":                         ("A", False),
            "Is the user exacting or precise in their work?":                  ("C", False),
            "Does the user often feel sad or blue?":                           ("N", False),
            "Is the user full of ideas?":                                      ("O", False),
        }

        BIG_FIVE_NORMS = {
            "N": {"low": (1.0, 2.5), "average": (2.5, 3.5), "high": (3.5, 5.0)},
            "E": {"low": (1.0, 2.5), "average": (2.5, 3.5), "high": (3.5, 5.0)},
            "O": {"low": (1.0, 2.5), "average": (2.5, 3.5), "high": (3.5, 5.0)},
            "A": {"low": (1.0, 2.5), "average": (2.5, 3.5), "high": (3.5, 5.0)},
            "C": {"low": (1.0, 2.5), "average": (2.5, 3.5), "high": (3.5, 5.0)},
        }

        FACTOR_NAMES = {
            "N": "Neuroticism",
            "E": "Extraversion",
            "O": "Openness to Experience",
            "A": "Agreeableness",
            "C": "Conscientiousness",
        }

        FACTOR_DESCRIPTORS = {
            "N": {
                "low":     "Emotionally stable, calm, rarely experiences negative emotions.",
                "average": "Moderate emotional reactivity; occasional stress or worry.",
                "high":    "Prone to emotional instability, anxiety, moodiness, and stress.",
            },
            "E": {
                "low":     "Introverted, reserved, prefers solitude and quiet environments.",
                "average": "Moderately social; comfortable both alone and with others.",
                "high":    "Highly sociable, energetic, talkative, and assertive.",
            },
            "O": {
                "low":     "Conventional, practical, prefers routine over novelty.",
                "average": "Balanced curiosity; open to some new ideas and experiences.",
                "high":    "Highly curious, creative, imaginative, and open to new ideas.",
            },
            "A": {
                "low":     "Competitive, skeptical, may appear unfriendly or uncooperative.",
                "average": "Generally cooperative with occasional competitive tendencies.",
                "high":    "Cooperative, trusting, empathetic, and eager to help others.",
            },
            "C": {
                "low":     "Flexible or disorganized; may struggle with planning and follow-through.",
                "average": "Moderately organized; generally reliable but not overly rigid.",
                "high":    "Highly disciplined, organized, reliable, and achievement-oriented.",
            },
        }

        def score_big_five(data: dict) -> dict:
            factor_scores = {f: [] for f in ["N", "E", "O", "A", "C"]}

            for question, response in data.items():
                if question not in BIG_FIVE_ITEMS:
                    continue
                factor, is_reversed = BIG_FIVE_ITEMS[question]
                score = likert_5_reversed(response) if is_reversed else likert_5(response)
                factor_scores[factor].append(score)

            results = {}
            for factor, scores in factor_scores.items():
                if not scores:
                    continue
                mean = sum(scores) / len(scores)
                norms = BIG_FIVE_NORMS[factor]
                if mean <= norms["low"][1]:
                    level = "low"
                elif mean <= norms["average"][1]:
                    level = "average"
                else:
                    level = "high"

                results[FACTOR_NAMES[factor]] = {
                    "raw_score": round(mean, 2),
                    "max_possible": 5.0,
                    "level": level,
                    "items_scored": len(scores),
                    "interpretation": FACTOR_DESCRIPTORS[factor][level],
                }

            return results


        # EE = Emotional Exhaustion (high = burnout)
        # DP = Depersonalization (high = burnout)
        # PA = Personal Accomplishment (LOW = burnout — reverse indicator)
        MBI_ITEMS: Dict[str, Tuple[str, bool]] = {
            "Does the user feel emotionally exhausted because of their work?":       ("EE", False),
            "Does the user feel worn out at the end of a working day?":              ("EE", False),
            "Does the user feel tired upon waking and facing a new workday?":        ("EE", False),
            "Can the user easily understand the actions of colleagues or supervisors?": ("PA", False),
            "Does the user feel they treat some colleagues impersonally, like objects?": ("DP", False),
            "Does the user find working with people all day stressful?":             ("EE", False),
            "Is the user afraid their work is making them emotionally harder?":      ("DP", False),
            "Does the user feel full of energy?":                                    ("PA", False),
            "Does the user feel frustrated by their work?":                          ("EE", False),
            "Does the user feel they work too hard?":                                ("EE", False),
            "Is the user uninterested in what is going on with many colleagues?":    ("DP", False),
            "Does the user find direct contact with people at work too stressful?":  ("DP", False),
            "Does the user find it easy to create a relaxed work atmosphere?":       ("PA", False),
            "Does the user feel stimulated after working closely with colleagues?":   ("PA", False),
            "Has the user achieved many rewarding work objectives?":                 ("PA", False),
            "Is the user relaxed when dealing with emotional problems at work?":     ("PA", False),
            "Does the user feel colleagues blame them for their problems?":          ("DP", False),
        }

        # EE: low <16, moderate 16-26, high ≥27  (0–6 scale per item, 9 items → max 54)
        # DP: low <6, moderate 6-9, high ≥10     (max 30 with 5 items)
        # PA: high ≥40, moderate 34-39, low ≤33  (inverted — low PA = burnout, max 48)
        MBI_CUTOFFS = {
            "EE": {"high": 27, "moderate": 16},   # ≥27 high, 16-26 mod, <16 low
            "DP": {"high": 10, "moderate": 6},
            "PA": {"low": 33, "moderate": 39},    # ≤33 low (problematic), 34-39 mod, ≥40 high
        }

        def score_mbi(data: dict) -> dict:
            subscale_scores = {"EE": 0, "DP": 0, "PA": 0}
            subscale_counts = {"EE": 0, "DP": 0, "PA": 0}

            for question, response in data.items():
                if question not in MBI_ITEMS:
                    continue
                subscale, _ = MBI_ITEMS[question]
                subscale_scores[subscale] += mbi_score(response)
                subscale_counts[subscale] += 1

            def classify_EE(score):
                if score >= MBI_CUTOFFS["EE"]["high"]:     return "High"
                elif score >= MBI_CUTOFFS["EE"]["moderate"]: return "Moderate"
                else:                                         return "Low"

            def classify_DP(score):
                if score >= MBI_CUTOFFS["DP"]["high"]:     return "High"
                elif score >= MBI_CUTOFFS["DP"]["moderate"]: return "Moderate"
                else:                                         return "Low"

            def classify_PA(score):
                if score <= MBI_CUTOFFS["PA"]["low"]:      return "Low"   # problematic
                elif score <= MBI_CUTOFFS["PA"]["moderate"]: return "Moderate"
                else:                                         return "High"

            ee = subscale_scores["EE"]
            dp = subscale_scores["DP"]
            pa = subscale_scores["PA"]

            ee_level = classify_EE(ee)
            dp_level = classify_DP(dp)
            pa_level = classify_PA(pa)

            # Burnout determination: meets at least 2 of 3 critical criteria
            burnout_flags = [
                ee_level == "High",
                dp_level == "High",
                pa_level == "Low",
            ]
            burnout_count = sum(burnout_flags)

            if burnout_count >= 2:
                overall = "Burnout Present"
            elif burnout_count == 1:
                overall = "Burnout Risk (partial)"
            else:
                overall = "No Burnout Detected"

            return {
                "Emotional Exhaustion": {
                    "score": ee,
                    "max_possible": subscale_counts["EE"] * 6,
                    "level": ee_level,
                    "interpretation": f"EE score {ee} → {ee_level} emotional exhaustion.",
                },
                "Depersonalization": {
                    "score": dp,
                    "max_possible": subscale_counts["DP"] * 6,
                    "level": dp_level,
                    "interpretation": f"DP score {dp} → {dp_level} depersonalization.",
                },
                "Personal Accomplishment": {
                    "score": pa,
                    "max_possible": subscale_counts["PA"] * 6,
                    "level": pa_level,
                    "interpretation": f"PA score {pa} → {pa_level} sense of accomplishment. "
                                      f"({'Concerning — low PA contributes to burnout.' if pa_level == 'Low' else 'Adequate PA.'}) ",
                },
                "overall_burnout": overall,
                "burnout_count":burnout_count,
            }

        # Standard 17-item HAM-D
        # Items 1,2,3,7,10,11 → 0–4 scale (more nuanced symptom domains)
        # Remaining items → 0–2 scale
        # We map:
        #   0-4 items: Disagree=0, Neutral=2, Agree=4
        #   0-2 items: Disagree=0, Neutral=1, Agree=2

        HAMD_ITEMS: Dict[str, str] = {
            "Does the user experience a depressed mood such as sadness or hopelessness?": "0-4",  # item 1
            "Does the user experience feelings of guilt?":                                "0-4",  # item 2
            "Does the user experience suicidal thoughts or behaviors?":                   "0-4",  # item 3
            "Does the user have difficulty falling asleep?":                              "0-2",  # item 4
            "Does the user experience disturbed sleep during the night?":                 "0-2",  # item 5
            "Does the user wake up early due to sleep disturbance?":                      "0-2",  # item 6
            "Has the user's interest in work or activities decreased?":                   "0-4",  # item 7
            "Does the user show psychomotor slowing?":                                    "0-4",  # item 8
            "Does the user experience agitation or restlessness?":                        "0-4",  # item 9
            "Does the user experience psychological anxiety?":                            "0-4",  # item 10
            "Does the user experience physical anxiety symptoms?":                        "0-4",  # item 11
            "Does the user experience gastrointestinal symptoms?":                        "0-2",  # item 12
            "Does the user experience general physical symptoms?":                        "0-2",  # item 13
            "Does the user experience sexual or genital symptoms?":                       "0-2",  # item 14
            "Does the user show excessive concern about health?":                         "0-2",  # item 15 (hypochondriasis)
        }

        def score_hamd(data: dict) -> dict:
            total = 0
            item_breakdown = {}

            for question, response in data.items():
                if question not in HAMD_ITEMS:
                    continue
                scale = HAMD_ITEMS[question]
                score = ham_score_0_4(response) if scale == "0-4" else ham_score_0_2(response)
                total += score
                item_breakdown[question] = score

            # HAM-D severity classification (standard cutoffs)
            if total <= 7:
                severity = "None / Minimal"
                description = "No clinically significant depression detected."
            elif total <= 13:
                severity = "Mild Depression"
                description = "Mild depressive symptoms present; monitoring recommended."
            elif total <= 18:
                severity = "Moderate Depression"
                description = "Moderate depression; clinical intervention likely warranted."
            elif total <= 22:
                severity = "Severe Depression"
                description = "Severe depression; prompt clinical attention required."
            else:
                severity = "Very Severe Depression"
                description = "Very severe depression; urgent clinical intervention required."

            return {
                "total_score": total,
                "max_possible": 52,   # theoretical max for this 15-item adapted version
                "severity": severity,
                "interpretation": description,
                "item_scores": item_breakdown,
            }

        # 14 items, each scored 0–4
        # Disagree=0, Neutral=2, Agree=4
        # Two subscales: Psychic (items 1-6, 14) and Somatic (items 7-13)

        HAMA_ITEMS: Dict[str, str] = {
            "Does the user experience an anxious mood?":                            "psychic",
            "Does the user experience tension or nervousness?":                     "psychic",
            "Does the user experience fears?":                                      "psychic",
            "Does the user experience insomnia related to anxiety?":                "psychic",
            "Does the user have difficulty concentrating due to anxiety?":          "psychic",
            "Does the user experience depressed mood related to anxiety?":          "psychic",
            "Does the user experience muscular symptoms?":                          "somatic",
            "Does the user experience sensory symptoms?":                           "somatic",
            "Does the user experience cardiovascular symptoms?":                    "somatic",
            "Does the user experience respiratory symptoms?":                       "somatic",
            "Does the user experience gastrointestinal symptoms related to anxiety?": "somatic",
            "Does the user experience genitourinary symptoms related to anxiety?":  "somatic",
            "Does the user experience autonomic symptoms?":                         "somatic",  # item 13
            # Item 14 in standard HAM-A is "behavior at interview" — clinician-observed, omitted here
        }

        def score_hama(data: dict) -> dict:
            total = 0
            psychic_total = 0
            somatic_total = 0
            item_breakdown = {}

            for question, response in data.items():
                if question not in HAMA_ITEMS:
                    continue
                subscale = HAMA_ITEMS[question]
                score = ham_score_0_4(response)
                total += score
                item_breakdown[question] = score
                if subscale == "psychic":
                    psychic_total += score
                else:
                    somatic_total += score

            # HAM-A severity (standard clinical cutoffs)
            if total < 17:
                severity = "Mild Anxiety"
                description = "Mild anxiety symptoms; may not require treatment."
            elif total <= 24:
                severity = "Moderate Anxiety"
                description = "Moderate anxiety; clinical evaluation recommended."
            elif total <= 30:
                severity = "Severe Anxiety"
                description = "Severe anxiety; clinical intervention required."
            else:
                severity = "Very Severe Anxiety"
                description = "Very severe anxiety; urgent clinical attention warranted."

            return {
                "total_score": total,
                "max_possible": 52,  # 14 items × 4 (13 scored here × 4 = 52)
                "severity": severity,
                "interpretation": description,
                "psychic_subscale_score": psychic_total,
                "somatic_subscale_score": somatic_total,
                "item_scores": item_breakdown,
            }


        @dataclass
        class AssessmentResult:
            big_five: dict = field(default_factory=dict)
            burnout: dict = field(default_factory=dict)
            depression: dict = field(default_factory=dict)
            anxiety: dict = field(default_factory=dict)
            clinical_summary: dict = field(default_factory=dict)

        def generate_clinical_summary(burnout: dict, depression: dict, anxiety: dict, big_five: dict) -> dict:
            flags = []
            risk_level = "Low"

            dep_severity = depression["severity"]
            anx_severity = anxiety["severity"]
            burnout_status = burnout["overall_burnout"]

            # Flag active clinical concerns
            if "Moderate" in dep_severity or "Severe" in dep_severity:
                flags.append(f"Depression: {dep_severity}")
            if "Moderate" in anx_severity or "Severe" in anx_severity:
                flags.append(f"Anxiety: {anx_severity}")
            if "Burnout Present" in burnout_status:
                flags.append("Burnout: Active")
            elif "Risk" in burnout_status:
                flags.append("Burnout: Partial Risk")

            # Personality risk amplifiers
            neuroticism = big_five.get("Neuroticism", {})
            if neuroticism.get("level") == "high":
                flags.append("High Neuroticism: amplifies emotional distress risk")

            conscientiousness = big_five.get("Conscientiousness", {})
            if conscientiousness.get("level") == "low":
                flags.append("Low Conscientiousness: may hinder help-seeking & self-care")

            # Overall risk
            severe_count = sum([
                "Severe" in dep_severity,
                "Severe" in anx_severity,
                "Burnout Present" in burnout_status,
            ])
            if severe_count >= 2:
                risk_level = "High"
            elif len(flags) >= 2:## this might need to change
                risk_level = "Moderate"
            else:
                risk_level = "Low"
            '''
            comorbidity_note = ""
            if ("Depression" in " ".join(flags)) and ("Anxiety" in " ".join(flags)):
                comorbidity_note = (
                    "Co-occurring depression and anxiety detected. "
                    "This combination is clinically significant and associated with greater functional impairment."
                )
            '''
            return {
                "overall_risk_level": risk_level,
                "active_clinical_flags": flags,
                #"comorbidity_note": comorbidity_note,
                "recommendation": (
                    "Urgent clinical referral recommended."
                    if risk_level == "High"
                    else "Clinical evaluation recommended."
                    if risk_level == "Moderate"
                    else "Routine monitoring; no immediate intervention required."
                ),
            }

        def run_assessment(raw_data: dict) -> AssessmentResult:
            """
            Main entry point. Pass in the parsed JSON dictionary with keys:
            'Personality', 'Burnout', 'Depression', 'Anxiety'
            """
            result = AssessmentResult()
            result.big_five   = score_big_five(raw_data.get("Personality", {}))
            result.burnout    = score_mbi(raw_data.get("Burnout", {}))
            result.depression = score_hamd(raw_data.get("Depression", {}))
            result.anxiety    = score_hama(raw_data.get("Anxiety", {}))
            result.clinical_summary = generate_clinical_summary(
                result.burnout, result.depression, result.anxiety, result.big_five
            )
            return result
        data = json.loads(AI_data)
        result = run_assessment(data)
        processed_data = {"content":json.dumps(dataclasses.asdict(result), indent=2),# double content layer
                          "date": str(date.today())}
        processed_user_data ,created = UserPsycoProcessedData.objects.get_or_create(
            owner=user,
            defaults={'content': []}
        )
        history_doc, created = UserPsycoProcessedDataHistory.objects.get_or_create(
            owner=user,
            defaults={'content': []}
        )
        #old_data_list = processed_user_data.content if isinstance(processed_user_data.content, dict) else None
        processed_user_data.content = json.dumps(dataclasses.asdict(result), indent=2)
        processed_user_data.save()
        history_list = history_doc.content if isinstance(history_doc.content, list) else {}
        history_list.append(processed_data)
        history_doc.content = history_list
        history_doc.save()
        



    # personality 
    for user in users:
        User_data, created = UserPersonalityData.objects.get_or_create(
            owner=user,
            defaults={'content': {}})# it does not cause error that key of json should be in double quotes 
        old_data_list = User_data.content if isinstance(User_data.content, dict) else None
        b = []
        chats = []
        user_chats = UserChatDB.objects.filter(owner=user)
        total_words = 0
        for chat in user_chats:
            for item in chat.content:
                c = item.get("message","")
                words = c.split()
                total_words += len(words)
                estimated_tokens = math.ceil(total_words * 1.5)
                chats.append(chat)
                if estimated_tokens > 5000:
                    a = summarize_chat_history(chats)
                    chats = []
                    total_words = 0
                    b.append(a)
        
        b.append(chats)
        AI_data = assesment(b,old_data_list) 
        processed_data = {"content":[AI_data]}
        history_doc, created = UserPersonalityDataHistoric.objects.get_or_create(
            owner=user,
            defaults={'content': []}
        )
        old_data_list = processed_data["content"]
        User_data.content = old_data_list
        User_data.save()
        history_list = history_doc.content if isinstance(history_doc.content, list) else []
        history_list.append(processed_data)
        history_doc.content = history_list
        history_doc.save()
        



###############################################################33


def process_midnight_snapshots():
    users = User.objects.all()
    
    for user in users:
        chats = []
        personal_doc, created = UserDashboard.objects.get_or_create(
            owner=user,
            defaults={'content': []}
        )
        user_chats = UserChatDB.objects.filter(owner=user)
        Personal_list = personal_doc.content if isinstance(personal_doc.content, list) else []
        
        processed_data = {
            "content": Personal_list
        }
        
        DashBoardDataAI = None
        total_words = 0
        
        for chat in user_chats:
            for item in chat.content: 
                c = item.get("message", "")   
                words = c.split()
                total_words += len(words)
                estimated_tokens = math.ceil(total_words * 1.5)
                chats.append(chat)
                
                if estimated_tokens > 30000:
                    DashBoardDataAI = UserDashboard_data(chats, processed_data)
                    processed_data = {
                        "content": DashBoardDataAI.model_dump() #
                    }
                    total_words = 0
                    chats = []

        if chats:
            DashBoardDataAI = UserDashboard_data(chats, processed_data)
            processed_data = {
                "content": DashBoardDataAI.model_dump()
            }

        history_doc, created = UserDashboardHistory.objects.get_or_create(
            owner=user,
            defaults={'content': []}
        )
        
        history_list = history_doc.content if isinstance(history_doc.content, list) else []
        history_list.append(processed_data)
        history_doc.content = history_list
        history_doc.save()
        
        
        personal_doc.content = [processed_data] 
        personal_doc.save()


    
    # team dashboard
    for employee in users:
        if employee.org_node.children.exists():
            target_group_ids = get_direct_reports_ids(employee.org_node.id)
            Dahboards = []
            master_doc, created = TeamData.objects.get_or_create(
                node=employee.org_node,
                defaults={'content': []}
            )
            
            master_list = master_doc.content if isinstance(master_doc.content, list) else []            
            
            for node_id in target_group_ids:
                node = OrgNode.objects.get(id=node_id)
                user_DashBoard = UserDashboard.objects.filter(owner=node.user)
                Dahboards.append(user_DashBoard)
            
            AI_Output = TeamDashboard_data(Dahboards, master_list)
            processed_data = {
                "content": AI_Output.model_dump()
            }         
            

            history_doc, created = TeamDataHistory.objects.get_or_create(
                node=employee.org_node,
                defaults={'content': []}
            )
            
            history_list = history_doc.content if isinstance(history_doc.content, list) else []
            history_list.append(processed_data)
            history_doc.content = history_list
            history_doc.save()
            master_doc.content = [processed_data]
            master_doc.save()


 