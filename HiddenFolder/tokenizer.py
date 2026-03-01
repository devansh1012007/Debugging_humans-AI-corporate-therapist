import math
conversation = [
    {
        "role": "user",
        "message": " I feel very unproductive recently. I almost feel ashamed of yself for taking such a high salary and not producing a good enough output forthe team. This company gives such a comforting and open environment but I just don't deserve it."
    },
    {
        "role": "assistant",
        "message":  " I understand how challenging it can be to feel unproductive, especially when you have a high salary and responsibilities at work. It's completely normal to experience these feelings of inadequacy or shame, but please remember that your value is not solely defined by your output. It sounds like the fast-paced startup environment might be putting extra pressure on you, which can sometimes make us doubt ourselves more than we should. However, it's important to recognize that everyone has their own pace and style of working. Your comfort in an open environment doesn't diminish your worth or ability to contribute meaningfully. Let's explore some ways to help you feel more productive and valued: 1. *Set Realistic Goals*: Break down larger tasks into smaller, manageable steps. This can make the work seem less overwhelming and give you a sense of accomplishment as you complete each step.2. *Prioritize Tasks*: Focus on what truly matters for your team's success right now. Sometimes it helps to prioritize based on impact rather than urgency. 3. *Seek Feedback*: Don't hesitate to ask for feedback from your colleagues or manager. This can provide clarity on where you're excelling and areas that might need improvement. 4. *Self-Care*: Ensure you're taking care of yourself physically, emotionally, and mentally. Sometimes when we feel overwhelmed, self-care practices like exercise, meditation, or hobbies can help reset our mindset.Remember, it's okay to have off days or periods where productivity feels low. What matters is that you continue striving for growth and improvement while being kind to yourself in the process. You bring unique strengths and perspectives to your team, and those contributions are valuable regardless of output alone. Would focusing on setting realistic goals help you feel more productive? Or perhaps discussing feedback mechanisms with your manager could provide clarity? Please let me know how I can further assist or if there's anything else weighing on your mind that we haven't touched upon."
    },
    {
        "role": "user",
        "message": " i have some family issues my relations with my wife are not good."
    },
    {
        "role": "assistant",
        "message": " I'm really sorry to hear about the challenges you're facing in your personal life, especially with your relationship and family issues. It's completely understandable that these difficulties might be impacting your work performance and sense of self-worth. Firstly, let me acknowledge how brave it takes for someone like you, who values excellence and feels a strong sense of responsibility to live up to the expectations set by yourself and others in this high-pressure environment, to openly share such personal struggles. It's not easy to admit when we're feeling overwhelmed or that our performance might be slipping. Given your introverted nature and preference for calm explanations, I want you to know that it's perfectly okay to take a step back sometimes to focus on what truly matters - your well-being and the health of those closest to you. Your value isn't defined by how much output you can produce in a day or week; rather, it's about who you are as a person and the care you bring into every relationship. In terms of solutions, I would suggest: 1. *Open Communication*: Consider having an honest conversation with your wife about what you're going through. It might help to express how these issues affect not just you but also her and potentially your work dynamics. 2. *Set Boundaries at Work*: Given the high expectations in a startup environment, it's crucial to communicate clearly about what you can realistically achieve given your current circumstances. Perhaps there are ways to adjust deadlines or responsibilities temporarily until things settle down at home. 3. *Self-Care Practices*: Engage in activities that help reduce stress and bring peace into your life - whether it's meditation, exercise, hobbies, or seeking professional support like therapy. Remember, taking care of yourself isn't selfish; it's necessary for you to show up as the best version of yourself both personally and professionally. It might feel daunting now, but small steps towards addressing these issues can lead to significant improvements over time. Would focusing on open communication with your wife be something that feels manageable right now? Or would exploring self-care practices first resonate more with how you're feeling? Please remember, it's okay not to have all the answers immediately. What matters most is taking one step forward at a pace that feels comfortable for you."
    },
    {
        "role": "user",
        "message": "my wife  loves my boss and in fornt of me my boss call  my wife to meet him in hotel room. thats why in reality for me its very hard to word under this type of boss but other staff are good."
    },
    {
        "role": "assistant",
        "message": "I'm really sorry to hear that you're feeling this way, but I want you to know that it's completely normal to have ups and downs in life, especially when facing challenging situations like the ones you've mentioned. It sounds like you're dealing with a lot of stress and emotional turmoil right now. The combination of your family issues, work pressures, and interpersonal conflicts can be overwhelming. It's important to remember that these challenges don't define who you are or what you're capable of achieving. Firstly, let's address the elephant in the room - your wife loving your boss. This situation must be incredibly difficult for you, especially when it seems like others at work have a more favorable relationship with your superior. It's natural to feel jealous and insecure about this dynamic. However, try not to compare yourself too much to others or dwell on what might seem unfair. Instead of focusing solely on the negative aspects, let's explore some potential solutions that could help alleviate your stress and improve your overall well-being: 1. Open communication with your wife: It seems like there are underlying issues in your marriage that need addressing. Have an honest conversation with your spouse about how you both feel regarding this situation at work. Try to find common ground and support each other through these tough times. 2. Seek professional help if needed: If talking directly with your boss feels too uncomfortable or risky, consider seeking guidance from a therapist or counselor who can provide unbiased advice on navigating difficult workplace relationships while maintaining healthy boundaries. 3. Focus on self-care: Make sure you're taking care of yourself physically and mentally during this challenging period. Engage in activities that bring you joy, practice mindfulness techniques like meditation or deep breathing exercises, exercise regularly, eat well-balanced meals, get enough sleep each night - all these small steps contribute significantly towards improving your mental health. 4. Set realistic expectations for yourself: Remember that everyone has their own unique strengths and weaknesses; it's okay if you're not excelling at work right now due to external factors beyond your control (like family issues). Be kinder to yourself by setting achievable goals instead of comparing yourself with others who may have different circumstances than yours. 5. Consider exploring other opportunities: If staying within this company continues causing distress despite efforts made towards improvement, perhaps it might be worth considering a change in career paths or industries altogether? Sometimes stepping out into unknown territory can lead us down unexpected yet fulfilling roads we never imagined before! In conclusion (just kidding!), remember that life isn't always fair but what matters most is how we choose to respond amidst adversity. You are stronger than you think, and I believe deep down inside that things will eventually get better for you - both personally and professionally! Keep pushing forward with determination while prioritizing self-care along the way; soon enough brighter days lie ahead :)"
    },
    {
        "role": "user",
        "message": "what can i do with my physical health. i dont have enough time to take care of my physical health thats the reason my mental health is unstable."
    },
    {
        "role": "assistant",
        "message": " I understand that you're feeling overwhelmed and struggling with your physical health, which is impacting your mental well-being. It's completely normal to feel this way in a high-pressure work environment like the one you described. Given your introverted nature and preference for calm explanations, I suggest focusing on small, manageable steps to improve your physical health gradually. Here are some suggestions: 1. Start with simple exercises: Begin with short walks or gentle stretches during breaks at work. This can help reduce stress and increase energy levels without requiring a significant time commitment. 2. Prioritize sleep: Ensure you're getting enough quality sleep each night. Establish a consistent bedtime routine and create a relaxing environment in your bedroom to promote better sleep. 3. Mindful eating: Focus on nourishing your body with balanced meals and snacks throughout the day. Avoid skipping meals or relying on unhealthy convenience foods, which can lead to energy crashes and increased stress. 4. Practice relaxation techniques: Incorporate mindfulness exercises like deep breathing, meditation, or progressive muscle relaxation into your daily routine. These practices can help calm your mind and reduce anxiety. 5. Seek support: Don't hesitate to reach out to a therapist or counselor who specializes in work-related stress management. They can provide personalized guidance and coping strategies tailored to your unique situation. Remember, progress takes time, so be patient with yourself as you implement these changes. Small improvements over weeks and months will lead to significant benefits for both your physical and mental health. Is there anything specific about these suggestions that resonates with you? Or would you like me to elaborate on any particular aspect of improving your physical health in the context of your demanding work environment? How can I best support you as we explore ways to implement these changes into your daily routine?"
    }
]

total_words = 0
for chat in conversation:
    # Split message by spaces to get word count
    words = chat["message"].split()
    total_words += len(words)

# Estimate tokens
estimated_tokens = math.ceil(total_words / 0.75)
print(f"Estimated tokens: {estimated_tokens}")
'''

a = []
context_window = []
total_words = 0
for chat in current_history[::-1]:# current histroy is chat data/convo
    words = chat["content"].split()
    total_words += len(words)
    estimated_tokens = math.ceil(total_words * 1.5)
    a.append(chat)
    if estimated_tokens > 8000:
        get_chat_summary = summarize_chat_history(current_history[:-len(a)])
        context_window.append(get_chat_summary)
        break
### here v can later add depalyed summary bringing it from d
context_window.append(a)'''




        a = []
        context_window = []
        total_words = 0
        for chat in current_history[::-1]:# current histroy is chat data/convo
            words = chat.message.split()
            total_words += len(words)
            estimated_tokens = math.ceil(total_words * 1.5)
            a.append(chat)
            if estimated_tokens > 4000:
                get_chat_summary = summarize_chat_history(current_history[:-len(a)])
                context_window.append(get_chat_summary)
                break
            else:
                context_window.append(a)
        a = []
        total_words = 0
        for chat in current_history[::-1]:# current histroy is chat data/convo
            words = chat.message.split()
            total_words += len(words)
            estimated_tokens = math.ceil(total_words * 1.5)
            a.append(chat)
            if estimated_tokens > 8000:
                break
        context_window = a