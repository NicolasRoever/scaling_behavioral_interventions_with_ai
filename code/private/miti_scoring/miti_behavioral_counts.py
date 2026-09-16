raise RuntimeError("Restricted-input source only. Raw interview data are not distributed. API execution is disabled in this $0-API replication package; use code/python/run_public.py for saved-result reproduction.")
# Prompt and coding instructions for the MITI 4.2.1 behavioral counts.


MITI_MAIN_BEHAVIOR = """
*E. Behavioral Counts*
Behavior counts are intended to capture specific behaviors without regard to how they fit into the overall impression of the clinician's use of MI. Unlike global ratings, behavior counts will generally be determined as a result of categorization and decision rules, rather than attempting to grasp an overall impression. Coders should avoid relying on inference to determine a behavior count whenever possible.

*E.1. Parsing Interviewer Speech.*
The session segment can be broken down into volleys, which are defined as uninterrupted segments of clinician speech. A volley begins when the clincian begins speaking and is terminated by client speech (other than facilitive comments such as "yeah, right, good"). It is the equivalent of turn-taking in a conversation.

*E.1.a. Parsing Rules.*
Clinician volleys are comprised of a single or multiple clinician utterances. An utterance is defined as a complete thought or a thought unit (Gottman, Markman, & Notarius, 1977; Weiss, Hops, & Patterson, 1973). Behavior codes are assigned to clinician utterances, although not all utterances will receive a behavior code (see F. Statements that Are Not Coded in the MITI).

Each utterance may receive only one behavior code and each volley earns each code only once. For example, "You are worried about your drinking" is an utterance that is assigned one code. Whereas, "You are worried about your drinking; has this been a problem before?" is parsed into two utterances, that each receive a separate code. Thus, in the course of a relatively long reply, if a clinician reflects, confronts, gives information, then asks a question, these could each qualify for a distinct behavior code. Similarly, if a clinician offers Emphasizing Autonomy and an Affirm in the same volley, both codes would be given. (**Note that this parsing rule for MI-Adherent and MI Non-Adherent utterances is different than previous versions of the MITI).

Reflections are handled differently. There is only one reflection code given per volley, regardless of the combination of simple and complex reflections in that volley. If any of the reflections are complex, then the Complex Reflection (CR) code is used. Otherwise, the reflection code is Simple Reflection (SR). For instance, if a clinician offers a simple reflection, asks a closed question, and then offers a complex reflection, the volley would receive two codes: complex reflection and question.

Finally, for questions, only one per volley is coded with the MITI 4.0. If multiple questions are offered within the same volley, the clinician will only receive a single Question behavior code.

The maximum possible number of codes per volley is 8. Only one of each of the following codes may be assigned per volley:
- Giving Information (GI)
- Persuade (Persuade or Persuade with Permission)
- Question (Q)
- Reflection Simple (SR) or Complex (CR)
- Affirm (AF)
- Seeking Collaboration (Seek)
- Emphasizing Autonomy (Emphasize)
- Confront (Confront)

DECISION RULE: If the coder is not sure whether to parse or not, the default should be to decide in favor of fewer parses.

*E.2. Parsing Examples:*

E.2.a. Consider the following interviewer statement:

    Well, let me ask you this: since you've been forced to come here and since you're feeling like everyone's kind of pecking on you like a crow—there's a bunch of crows flying around pecking on you about this thing about your drinking—what would you like to do with the time you spend here? What would be helpful for you?

This statement is parsed in the following way:

    Utterance One: Well, let me ask you this: since you've been forced to come here and since you're feeling like everyone's kind of pecking on you like a crow—there's a bunch of crows flying around pecking on you about this thing with your drinking— (Complex Reflection)

    Utterance Two: What would you like to do with the time you spend here? What would be helpful for you? (Seek)

E.2.b. What about this interviewer statement?

    What you say is absolutely true, that it is up to you. No one makes that choice for you. Even if your wife wanted to decide for you, or your employer wanted to decide for you, or I wanted to decide for you; nobody can. It really is completely your own choice—how you live your life, what you do about drugs, where you're headed—so that is yours. And what I hear you struggling with is, "what do I want? Is it time for me to change things? Is this drug test a wake-up call?"

We've parsed it like this:

    Utterance One: What you say is absolutely true, that it is up to you. No one makes that choice for you. Even if your wife wanted to decide for you, or your employer wanted to decide for you, or I wanted to decide for you; nobody can. It really is completely your own choice—how you live your life, what you do about drugs, where you're headed—so that is yours. (Emphasizing Autonomy)

    Utterance Two: And what I hear you struggling with is, "what do I want? Is it time for me to change things? Is this drug test a wake-up call?" (Complex Reflection)

E.2.c. What about this interviewer statement?
 
    To answer your question, it is recommended that people eat at least 5 servings of fruit and vegetables each day. Of course, you are the only one who can determine what works for you in this regard. How many more a day would that be? I mean, can you do it?

We've parsed it like this:

    Utterance One: To answer your question, it is recommended that people eat at least 5 servings of fruit and vegetables each day. (Giving Information)

    Utterance Two: Of course, you are the only one who can determine what works for you in this regard. (Emphasizing Autonomy)

    Utterance Three: How many more a day would that be? I mean, can you do it? (Question)

E.2.d. What about this interviewer statement?

    You sound exhausted. I know that I was when I had to deal with that problem. You want to find resolution and you are working really hard for it!

We've parsed it like this:

    Utterance One: You sound exhausted. (Reflection, could be simple or complex)

    Utterance Two: I know that I was when I had to deal with that problem. (Self-disclosure, not coded)

    Utterance Three: You want to find resolution and you are working really hard for it! (Affirm)

*E.3. When to Parse.* 
Client statements such as "yeah" or "right" that do not interrupt the interviewer sequence are considered facilitative statements, and should not interrupt the interviewer volley when coding. However, the volley might be parsed if the client's facilitative statement serves as an answer to the clinician's direct question or reflection. Remember, the default is to choose fewer parses.

For example, if the clinician says:

Let me see if I've got this straight. You're not happy about being here today but you are willing to consider making a few changes. You realize your drinking has been causing you some problems and you think it might be time to make a change.

If the client responds "yeah" throughout the previous utterance as a way of conveying acknowledgment of the therapist, the utterance should not be parsed by the client's interruption. Compare that to this clinician example:

You are really worried about your drinking and ready to make some changes. Do you think it's time to talk about treatment?

Here, if the client responds with "Yeah" in agreement that it is time for treatment, the client statement would interrupt the utterance and a new volley would begin with the clinician's next utterance.

When attempting to "keep up" with fast moving clinician/client interactions that contain multiple instances of facilitative speech, the coders is advised to remember the decision rule to parse fewer, rather than more, utterances.
""".strip()


MITI_BEHAVIOR_COUNTS_PROMPT = """

You are given an utterance from a motivational interviewer. Please assign ONE OF THE FOLLOWING codes to the utterance and return the code as a string. 
If nothing fits, return an empty string.

Giving Information, Persuade, Persuade with Permission, Question, Reflection Simple, Reflection Complex, Affirm, Seeking Collaboration, Emphasizing Autonomy, Confront

HERE ARE THE CODING INSTRUCTIONS FOR WHEN TO ASSIGN A CODE: 


1. Giving Information
"This category is used when the interviewer gives information, educates, provides feedback, or expresses a professional opinion without persuading, advising, or warning. Typically, the tone of the information is neutral, and the language used to convey general information does not imply that it is specifically relevant to the client or that the client must act on it."

Examples: "From my professional experience, I think that going to cardiac rehab is the best choice for most people in your situation", "The guidelines state that women should not drink more than seven drinks per week."

2. Persuasion

"This category is used when the clinician makes overt attempts to change the client’s opinions, attitudes, or behavior using tools such as logic, compelling arguments, self-disclosure, or facts (and the explicit linking of these tools with an overt message to change). Persuasion is also coded if the clinician gives biased information, advice, suggestions, tips, opinions, or solutions to problems without an explicit statement or strong contextual cue emphasizing the client’s autonomy in receiving the recommendation.

Note that if the therapist is giving information in a neutral manner, without an explicit focus on influencing or convincing the client, the "Giving Information" code should be used.

Examples: "You can’t get five fruits and vegetables in your diet every day unless you put some fruit in your breakfast." , 
"I used to be overweight but I decided to take my life into my own hands. You would be better off if you did the same thing." 
"You just don’t know how good your life can be if you quit drinking altogether.", 
"Well, your own father was a heavy drinker so it’s very likely you are too." , 
"All of these things added together tell me that you will have a lot of trouble managing your blood sugar levels without some medication to help. I wouldn’t tell you this unless I really thought it was the best thing for you. My job is to help you feel better, and I take that very seriously." , "If you use a condom every time you have sex, then you never have to worry about whether you might have contracted a sexually transmitted infection. Wouldn’t that be great?", 
"With everything going on in your life right now, how could it hurt to have your kids in daycare a couple of days a week?" (Persuade)


3. Persuade with Permission 
This code is assigned when the interviewer includes an emphasis on collaboration or autonomy support while persuading. The condition of permission may be present when

    1. The client asks directly for the clinician's opinion on what to do or how to proceed.
    2. The clinician asks the client directly for permission to provide advice, make suggestions, give opinion, offer feedback, express concerns, making recommendations, or discuss a particular topic.
    3. The clinician uses autonomy supportive language to preface or qualify the advice such that the client may chose to discount, ignore, or personally evaluate that advice.

The clinician could seek a general sense of permission (How about we start today talking about your probation requirements?) or permission specific to a topic, condition, or action item (If it is alright with you, I'll share some strategies that have been used by others to keep their blood sugar in check.).

Permission may be obtained before, during or after persuasion is used, but must occur close to persuasion in time. If Persuade with Permission is accompanied by an explicit Seeking Collaboration or Emphasizing Autonomy, both the Persuade with Permission and the Seeking Collaboration or/Emphasizing Autonomy code should be assigned.

If a clinician has asked for more general permission, it does not need to be repeated for every statement or suggestion. There is a “condition of permission” that may last for several minutes.
 
If the clinician changes the topic, becomes more directive, starts adding significant content (becomes the expert), or starts prescribing a plan without again asking permission, it is possible that the clinician would then receive a Persuade code.

Note that if the interviewer is providing information or advice in a neutral manner, the "Giving Information" code should be used instead. If the coder is uncertain, the GI code should be preferred.

Examples: Well, your father was a problem drinker so you definitely have an increased risk according to the numbers. But everyone is unique. What are your own thoughts about that? (Persuade with Permission; Seek) For some of my clients, daycare can turn out to be a real lifesaver especially when life gets as demanding as yours is right now. But I know you've mentioned your concerns about that, so maybe it is not for you no matter what. (Persuade with Permission; Seek)


5. Questions

If a statement includes a question (open, closed, evocative, fact-finding, etc.), assign the "Question" code.

Examples: What are your thoughts on that? (Question) How do you feel about your progress so far? (Question)


6. Reflections

This category is meant to capture reflective listening statements made by the clinician in response to client statements. Reflections may introduce new meaning or material, but they essentially capture and return to clients something about what they have just said. 

Examples: "You're furious about this."," This is the last straw for you.","You are pretty discouraged about this." (Simple Reflection), "You don't know why you're sabotaging yourself." "You are angry and frustrated.", "It's hard for people around you to get it." 

7. Affirm

An affirmation (AF) is a clinician utterance that accentuates something positive about the client. To be considered an Affirm, the utterance must be about client’s strengths, efforts, intentions, or worth. The utterance must be given in a genuine manner and reflect something genuine about the client. It does not have to be focused on the change goal and could reflect a “prizing” of the client for a specific trait, behavior, accomplishment, skill, or strength. Affirms are often complex reflections, and when this occurs, the Affirm code should be preferred. Affirm should not be coded automatically for the clinician’s agreeing with, approval of, cheerleading for, or non-specific praising of the client. They must be explicitly linked to client behaviors or specific characteristics. The utterance must seem genuine and not merely facilitative.   Clinicians can overuse affirmations by repeating them many times during the conversation. In general, the first two or three times, the statement may be credible and coded as an Affirm if the coder is confident that the utterance still clearly falls into the Affirm category. After that, they are typically not coded.
    

Examples: "You came up with a lot of great ideas on how to reduce your drinking. Great job brainstorming today.", "It’s important to you to be a good parent, just like your folks were for you." "You have been able to avoid sweets throughout the holiday and you’re proud of your accomplishment. It has paid off!", "You are the kind of person who takes her responsibilities seriously, wanting to do the right thing.", "With the parking problems and the rain coming down, it hasn’t been easy to get here. I appreciate that you continue to come.", "You’ve been working so hard at being a good parent. I’m so impressed with your willingness to stay in there even when the going gets tough!", "Given what you have told me about your previous success with losing weight, I am confident that you will be successful again when you are ready.", "It strikes me though that, even if you went for fast food twice during that time, that is considerably less than when you were going every day. That seems like a big change!" (Affirm)

Not coded as Affirm (counterexamples): "I am really proud of you." (Not coded; not specific), "You did great!" (Not coded), "Way to go!" (Not coded), "I know it’s really hard to stop smoking." (Support; not coded)


8. Seeking Collaboration
"This code is assigned when a clinician explicitly attempts to share power or acknowledge the expertise of the client. It can occur when the clinician genuinely seeks consensus with the client regarding tasks, goals, or directions of the session. Seeking collaboration may be assigned when the clinician asks what the client thinks about information provided. When permission to give information or advice is sought, Seeking Collaboration is typically assigned.

When a clinician asks about the client’s knowledge or understanding of a particular topic, this is coded as a Question. It is not considered to be Seeking Collaboration."

Examples:

"I have some information about how to reduce your risk of colon cancer and I wonder if I might discuss it with you." (Seeking Collaboration)

"Would it be alright if we spend some time discussing the standards for consuming alcohol during pregnancy?" (Seeking Collaboration)

"This may not be the right thing for you, but some of my clients have had good luck setting the alarm on their wristwatch to help them remember to check their blood sugars two hours after lunch." (Seeking Collaboration, consider Persuade with Permission)

"How can I help you with this?" (Seeking Collaboration)

"Would it be all right if we spent some time talking about smoking? I know you didn’t come here to talk about that." (Seeking Collaboration)


9. Emphasizing Autonomy 
These are utterances that clearly focus the responsibility with the client for decisions about and
actions pertaining to change. They highlight clients’ sense of control, freedom of choice, personal
autonomy, or ability or obligation to decide about their attitudes and actions. These are not
statements that specifically emphasize the client’s sense of self-­‐efficacy, confidence, or ability to
perform a specific action.
Examples: 
 "Yes, you’re right. No one can force you stop drinking." 
"You’re the one who knows yourself best here. What do you think ought to be on this
treatment plan?" 
"The number of fruits and vegetables you choose to eat is really up to you." (Emphasizing Autonomy)
"This is really your life and your path. You are the only one who can decide which direction
you will go. Where do you think you would like to go from here with your exercise?"

"You are in a tough spot. Being in jail leaves you feeling like you have no control over your
life. And you are being asked to consider engaging in a treatment program that might give
you some control back if you decide to do that. You are not sure what to choose at this
point. "
"This is both an opportunity and a challenge as you see it. You are weighing the options
and figuring out what will work best for you."


10. Confront
This code is used when the clinician confronts the client by directly and unambiguously
disagreeing, arguing, correcting, shaming, blaming, criticizing, labeling, warning, moralizing,
ridiculing, or questioning the client’s honesty. Such interactions will have the quality of uneven
power sharing, accompanied by disapproval or negativity. Included here are instances where the
interviewer uses a question or even a reflection, but the voice tone clearly indicates a
confrontation.
Restating negative information already known or disclosed by the client can be either a Confront
or a Reflection. Most Confronts can be correctly categorized by careful attention to voice tone
and context. This code trumps "Question" codes. 

Examples: 
- You were taking Antabuse but you drank anyway? 
- You think that is any way to treat people you love? 
- Yes, you are an alcoholic. You might not think so, but you are. 
- Wait a minute. It says right here that your A1C is 12. I’m sorry, but there is no way you
could have been controlling your carbohydrates like you said if it’s that high. 
- Think of your kids, for crying out loud.
- You have no concerns whatsoever about your drinking? 
- Most people who drink as much as you do cannot ever drink normally again. 
- Disciplining your child with punishment is a slippery slope. It seems alright in the
beginning but then one thing leads to another. 
- Remember you said that your cholesterol level was a threat to your life. If you can’t get
your diet under control, you are risking a stroke or a heart attack. 


MORE FEW SHOT EXAMPLES:

Utterance: Well, let me ask you this: since you’ve been forced to come here and since you’re feeling
like everyone’s kind of pecking on you like a crow—there’s a bunch of crows flying
around pecking on you about this thing about your drinking—what would you like to do
with the time you spend here? What would be helpful for you?
Response: ["Complex Reflection", "Seeking Collaboration"]


Utterance: What you say is absolutely true, that it is up to you. No one makes that choice for you.
Even if your wife wanted to decide for you, or your employer wanted to decide for you, or
I wanted to decide for you; nobody can. It really is completely your own choice—how you
live your life, what you do about drugs, where you’re headed—so that is yours. And what I
hear you struggling with is, “what do I want? Is it time for me to change things? Is this
drug test a wake-up call?”
Response: ["Emphasizing Autonomy", "Complex Reflection"]

Utterance: "To answer your question, it is recommended that people eat at least 5 servings of fruit and vegetables each day. Of course, you are the only one who can determine what works for you in this regard. How many more a day would that be? I mean, can you do it?"
Response: ["Giving Information", "Emphasizing Autonomy", "Question"]

Utterance: "You sound exhausted. I know that I was when I had to deal with that problem. You want to find resolution and you are working really hard for it!"
Response: ["Reflection Simple", "Affirm"]


Utterance: From my professional experience, I think that going to cardiac rehab would be the best thing for you. What do you think about this as an option? 
Response: ["Persuade with permission", "Seek"]

Utterance: You indicated during the assessment that you typically drink about 18 standard drinks per week. This far exceeds social drinking. 
Response: ["Confront"]

Utterance: Well, you are only eating two fruits per day according to this chart, even though you said you are eating five. It can be easy to deceive yourself.
Reponse: ["Confront"]

Utterance: It worked for me, and it will work for you if you give it a try. We need to find the right AA meeting for you. You just didn’t find a good one. 
Response: ["Persuade"],


Utterance: I would recommend that you always wear a bike helmet. It will really protect you in the event of a crash. Response: ["Persuade"]

Utterance: Today we’re going to talk about some things that have worked for others. 
Response: [""]

Utterance: The choice is yours, but in my opinion, staying in treatment would be a good thing for you. 
Response: ["Emphasize Autonomy", "Persuade with Permission"]

Utterance: Well, we know that sons of alcoholics carry an increased risk of problem drinking.
Response: ["Giving Information"]

Utterance: I have some information about your risk of problem drinking and I wonder if I can share it with you.
Response: ["Seek Autonomy"]

Utterance: Today we’re going to talk about some things that have worked for others. 
Response: [""]

Here is the text you need to classify: 

{text}

"""


# _persuade = """
# *E.4.b. Persuade*
# The clinician makes overt attempts to change the client's opinions, attitudes, or behavior using tools such as logic, compelling arguments, self-disclosure, or facts (and the explicit linking of these tools with an overt message to change). Persuasion is also coded if the clinician gives biased information, advice, suggestions, tips, opinions, or solutions to problems without an explicit statement or strong contextual cue emphasizing the client's autonomy in receiving the recommendation.

# Note that if the therapist is giving information in a neutral manner, without an explicit focus on influencing or convincing the client, the Giving Information code should be used.

# Decision Rule: If the coder cannot decide between the Persuasion and the Giving Information code, the Giving Information code should be used. This decision rule is intended to set a relatively high bar for the Persuasion code.

#     You can't get five fruits and vegetables in your diet every day unless you put some fruit in your breakfast. (Persuade)

#     I used to be overweight but I decided to take my life into my own hands. You would be better off if you did the same thing. (Persuade)

#     You just don't know how good your life can be if you quit drinking altogether. (Persuade)
    
#     Well, your own father was a heavy drinker so it's very likely you are too. (Persuade)

#     Well, we know that sons of alcoholics carry an increased risk of problem drinking. (Giving Information)

#     I have some information about your risk of problem drinking and I wonder if I can share it with you. (Seek)

#     All of these things added together tell me that you will have a lot of trouble managing your blood sugar levels without some medication to help. I wouldn't tell you this unless I really thought it was the best thing for you. My job is to help you feel better, and I take that very seriously. (Persuade)

#     If you use a condom every time you have sex, then you never have to worry about whether you might have contracted a sexually transmitted infection. Wouldn't that be great? (Persuade)
#     We used to think that having kids in daycare was not good for them, but now the evidence indicates that it actually helps them have better social skills than kids who never attend. (Giving Information)

#     With everything going on in your life right now, how could it hurt to have your kids in daycare a couple of days a week? (Persuade)
# """.strip()


# _persuade_with_permission = """
# *E.4.c. Persuade with Permission*
# Persuade with Permission is assigned when the interviewer includes an emphasis on collaboration or autonomy support while persuading. The condition of permission may be present when

#     1. The client asks directly for the clinician's opinion on what to do or how to proceed.
#     2. The clinician asks the client directly for permission to provide advice, make suggestions, give opinion, offer feedback, express concerns, making recommendations, or discuss a particular topic.
#     3. The clinician uses autonomy supportive language to preface or qualify the advice such that the client may chose to discount, ignore, or personally evaluate that advice.

# The clinician could seek a general sense of permission (How about we start today talking about your probation requirements?) or permission specific to a topic, condition, or action item (If it is alright with you, I'll share some strategies that have been used by others to keep their blood sugar in check.).

# Permission may be obtained before, during or after persuasion is used, but must occur close to persuasion in time. If Persuade with Permission is accompanied by an explicit Seeking Collaboration or Emphasizing Autonomy, both the Persuade with Permission and the Seeking Collaboration or/Emphasizing Autonomy code should be assigned.

# If a clinician has asked for more general permission, it does not need to be repeated for every statement or suggestion. There is a “condition of permission” that may last for several minutes.
 
# If the clinician changes the topic, becomes more directive, starts adding significant content (becomes the expert), or starts prescribing a plan without again asking permission, it is possible that the clinician would then receive a Persuade code.

# Note that if the interviewer is providing information or advice in a neutral manner, the Giving Information code should be used instead. If the coder is uncertain, the GI code should be preferred.

#     **Example: Drinking**
#     Well, your father was a problem drinker so you definitely have an increased risk according to the numbers. But everyone is unique. What are your own thoughts about that? (Persuade with Permission; Seek)

#     For some of my clients, daycare can turn out to be a real lifesaver especially when life gets as demanding as yours is right now. But I know you've mentioned your concerns about that, so maybe it is not for you no matter what. (Persuade with Permission; Seek)

#     I have some ideas about getting your kids to help more. I got my own child to clean his room by using a star chart. He got a star for every day he cleaned his room and after he earned seven stars, he got to choose the movie for Saturday night. (Persuade)

#     **Example: Moving to Insulin**

#     Your A1C level has been over 12 the last 3 times we've checked it. In general, this puts people at risk for complications (Giving Information)

#     Looking at your A1C level, it is apparent that you've been having some trouble controlling your blood sugar levels, despite your best efforts. My best advice at this point is for you is to switch to injectable insulin and give up the oral medication. But I don't know if that is something you are willing to consider. I'd welcome your thoughts. (Persuade with Permission; Seek)

#     Clinician: I've reviewed your lab results and I wonder if I might share some thoughts about how you can improve your control of your blood sugar levels. (Seek)
#     Client: Sure, I'm curious what you think.
#     Clinician: Looking at your A1C level, it is apparent that you've been having some trouble controlling your blood sugar levels, despite your best efforts. My best advice at this point is for you is to switch to injectable insulin and give up the oral medication. But I don't know if that is something you are willing to consider. I'd welcome your thoughts. (Persuade with Permission; Seek)


#     **Example: Parenting Self Disclosure**

#     Clinician: Well, I have a story about my own child that might fit in here. I wonder if you'd be interested in hearing about my experiences. (Seek)
#     Client: Anything that would help.
#     Clinician: I got my own child to clean his room by using a star chart. He got a star for every day he cleaned his room and after he earned seven stars, he got to choose the movie for Saturday night. (Persuade with Permission)

#     **Example: Smoking Cessation**

#     Clinician: I wonder if it would be ok if I provide some information with you about ways to quit smoking? (Seek)
#     Client: Yes.
#     Clinician: I've had good luck with clients using the nicotine gum. (Persuade with Permission)

# *E.4.c.1 Decision Rule for Persuade and Persuade with Permission*
# Decision Rule: When both Persuade AND Persuade with Permission occur in the same utterance, the coder should only assign the Persuade with Permission code. This may result in uncoded Persuasion statements in the exchanges. To the extent that the coder judges that these uncoded persuasion statements impinge on the collaboration between the pair, this should be captured on the Partnership global rating.
# """.strip()

# _questions = """
# *E.4.d. Questions*

# All questions from clinicians (open, closed, evocative, fact-finding, etc.) receive the Question code but only one question per volley is coded. Thus, if a clinician asked four separate questions in a single volley, only one question would be tallied. Closed and open questions are not differentiated in the MITI 4.0. Instead, coders attend to the nature of the clinician's questions with the global ratings in mind. For example, many fact-finding questions within an interview might result in a lower rating on the Partnership global and reduce opportunities to Sidestep Sustain Talk.
# """.strip()

# _simple_complex_reflection = """
# *E.4.e. Reflections*

# This category is meant to capture reflective listening statements made by the clinician in response to client statements. Reflections may introduce new meaning or material, but they essentially capture and return to clients something about what they have just said. Reflections may be either Simple or Complex.

# *E.4.e.1. Simple Reflection*

# Simple reflections typically convey understanding or facilitate client-clinician exchanges. These reflections add little or no meaning (or emphasis) to what clients have said. Simple reflections may mark very important or intense client emotions, but do not go far beyond the client's original statement. Clinician summaries of several client statements may be coded as simple reflections if the clinician does not use the summary to add an additional point or direction.

# *E.4.e.2. Complex Reflection*

# Complex reflections typically add substantial meaning or emphasis to what the client has said. These reflections serve the purpose of conveying a deeper or more complex picture of what the client has said. Sometimes the clinician may choose to emphasize a particular part of what the client has said to make a point or take the conversation in a different direction. Clinicians may add subtle or very obvious content to the client's words, or they may combine statements from the client to form summaries that are directional in nature.

#     **Example: Speeding Tickets**

#     Client: This is her third speeding ticket in three months. Our insurance is going to go through the roof. I could just kill her. Can't she see we need that money for other things?
#     Interviewer: You're furious about this. (Simple Reflection)
#     or
#     Interviewer: This is the last straw for you. (Complex Reflection)

#     **Example: Controlling Blood Sugar**

#     Interviewer: What have you already been told about managing your blood sugar levels? (Question)
#     Client: Are you kidding? I've had the classes, I've had the videos, I've had the home nurse visits. I have all kinds of advice about how to get better at this, but I just don't do it. I don't know why. Maybe I just have a death wish or something, you know?
#     Interviewer: You are pretty discouraged about this. (Simple Reflection)
#     or
#     Interviewer: You don't know why you're sabotaging yourself. (Complex Reflection)

#     **Example: Mother's Independence**

#     Client: My mother is driving me crazy. She says she wants to remain independent, but she calls me four times a day with trivial questions. Then she gets mad when I give her advice.
#     Interviewer: Things are very stressful with your mother. (Simple Reflection)
#     or
#     Interviewer: You're having a hard time figuring out what your mother really wants. (Complex Reflection)
#     or
#     Interviewer: Are you having a hard time figuring out what your mother really wants? (Question)
#     or
#     Interviewer: What do you think your mother really wants? (Question)

#     **Example: Smoking**

#     Client: I'm so tired of being told what to do. No one understands how difficult this is for me.
#     Interviewer: Is this overwhelming you? (Question)
#     or
#     Interviewer: You are angry and frustrated. (Complex Reflection)
#     or
#     Interviewer: It's hard for people around you to get it. (Complex Reflection)

# DECISION RULE: When a coder cannot distinguish between a simple and complex reflection (including for summaries), the default is to code a Simple Reflection.


# *E.4.e.3. Series of Reflections*

# When a clinician offers a series of simple and complex reflections in the same volley, only one Complex Reflection should be coded. Reflections often occur in sequence, and over-parsing can lead to difficulties in obtaining reliability or take away from the intent of the volley. Therefore, if a clinician offers a Simple Reflection, followed by an Emphasizing Autonomy statement, and then a Complex Reflection, only the codes of Complex Reflection and Emphasize would be given.

#     **Example: Diet Failure**

#     Client: I keep failing in this diet. I do okay for a while, but then I find myself eating an entire pan of brownies, and ruining all my progress. Do you know how many calories there are in a pan of brownies? Never mind the ice cream I eat with them. I never realized it would be so hard.

#     Clinician: It's two steps forward and then one step back. That kind of progress just doesn't seem enough. And what's hard is that something that is so normal for you, like a pan of brownies, is so terrible for your weight. If you knew this would be so hard, you might not have even tried to lose weight. (Complex Reflection)

#     Client: No, I have to do this. Even if I have to accept that I will never eat another brownie the rest of my damn life, I still have to stop killing myself with my weight.

#     Clinician: You want to lose weight so much that you would even give up brownies if you really had to. (Complex Reflection, added value for Cultivating Change Talk)
#     or
#     Clinician: Actually, you don't have to give up any food forever. Research shows that when you try to restrict yourself from foods you love, you will just eat more of them. The best goal is to eat them in moderation. (Persuade)


# *E.4.e.4. Reflection and Question in Sequence*

# Sometimes the interviewer begins with a reflection, but adds a question to “check” the reliability of the reflection. Both elements should be coded.

#     Client: I just can't keep using like this.

#     Clinician: You're certain you don't ever want to use heroin again. Is that right? (Complex Reflection, Question)

#     Client: My boss said I'm on probation now. No overtime, no bonuses. Nothing.

#     Clinician: Your boss said you can't work overtime anymore because of this incident. What do you make of that? (Simple Reflection, Question)

# E.4.e.5 Structuring Statements posing as reflections

# Sometimes the interviewer will ask a question, but will precede the question with information designed to cue the listener about the context for it. Essentially this functions as a way of saying; “Remember that other thing you said? Well, now I want to ask you this about it”. These types of structuring statements that occur prior to questions should not be coded as separate reflections. Instead they should be considered structuring statements to provide context for a question and therefore not coded. The intent of this rule is to avoid giving credit for reflections when the interviewer is merely cueing the client about the topic.

# If the interviewer makes a clear distinction or stop between the “set up” statement and the question, a separate reflection may be coded. For this to be the case, the client should have an opportunity to respond in some way before the question occurs.

#     Interviewer: You were describing that you haven't returned to that store where you stole the candy. Do you feel you are avoiding it? (Question)
#     or
#     Interviewer: You haven't returned to the store where you stole the candy. (Simple Reflection)
#     Client: Right.
#     Interviewer: Do you feel you are avoiding it? (Question)

# When the coder determines that the purpose of the reflection is to provide a foundation or a cue for a question, it should not be coded.
# """.strip()


# mia_behavior = """
# *E.4.f. MI-Adherent (MIA) Behaviors*

# It is important to note that often examples of good MI practice will not earn an MIA code. One common mistake for novice coders (and expert practitioners of MI) is to spot example of good MI practice that they try to “fit” into one of the MIA codes. Take care to assign only the MIA codes that are available here, and only when the example “rings the bell” as a clear example of the code.
 
# When in doubt, or when you are working too hard to make the example fit, select another code instead. Remember that adjusting a global rating can help compensate for elements of excellent MI practice that are not easily captured with a behavior count.
# **Unlike previous versions of the MITI, each subtype of MI Adherent (MIA) behavior is now coded and tallied separately.

# *E.4.f.1 What happens when a statement might fit more than one MIA Category?*

# Most of the time, coders will be able to assign a MIA code with certainty. Sometimes, though, coders will encounter single utterances that could fit into more than one MIA category. As with all other MITI codes, uncertainty about MIA is resolved by using a decision rules. These are sometimes called trumping rules, because they tell the rater which codes should prevail when the decision is unclear.

# The following hierarchy should be used to determine which code should be assigned for MIA: Affirm, Seek, Emphasize. If the coder is unsure which code is more appropriate, the lower code should be used (i.e., it should be the default). For example, if the coder is uncertain whether to assign Emphasize Autonomy or Seek, the Seek code should be used. Lower codes on the pyramid are given when the coder is uncertain. To assign the highest code on the pyramid, the coder should have a reasonable degree of confidence that the code is a true example of that category. When there is less certainty, the coder defaults to the lower codes. The intent of this trumping pyramid is to “protect” codes having high importance in motivational interviewing from being assigned too easily. Affirmations, for example, are relatively “inexpensive” for the interviewer, whereas emphasizing autonomy is both more challenging to achieve and has greater theoretical interest. Therefore the bar is intentionally set higher for the Emphasize Autonomy code.

# *4.f.1.1. a. What if the coder is not sure whether the code should be a MIA or some other code (such as a Question or a Reflection)?*

# When in doubt, the coder should not code MIA. Thus, if a statement could be coded as MIA or some other code, MIA should be assigned only if falls clearly within that category. When uncertain, the coder selects the other code.

# *4.f.1.2. Affirm (AF)*

# An affirmation (AF) is a clinician utterance that accentuates something positive about the client. To be considered an Affirm, the utterance must be about client's strengths, efforts, intentions, or worth. The utterance must be given in a genuine manner and reflect something genuine about the client. It does not have to be focused on the change goal and could reflect a “prizing” of the client for a specific trait, behavior, accomplishment, skill, or strength. Affirms are often complex reflections, and when this occurs, the Affirm code should be preferred.

# Affirm should not be coded automatically for the clinician's agreeing with, approval of, cheerleading for, or non-­‐specific praising of the client. They must be explicitly linked to client behaviors or specific characteristics. The utterance must seem genuine and not merely facilitative.
 
# If the coder is not certain whether the statement is specific or strong enough to merit the Affirm code, it should not be assigned.9.9

#     You came up with a lot of great ideas on how to reduce your drinking. Great job brainstorming today. (Affirm)

#     It's important to you to be a good parent, just like your folks were for you. (Affirm) I am really proud of you. (Not coded; not specific).
#     You have been able to avoid sweets throughout the holiday and you're proud of your accomplishment. It has paid off! (Affirm; trumps Reflection)

#     You are the kind of person who takes her responsibilities seriously, wanting to do the right thing. (Affirm)

#     With the parking problems and the rain coming down, it hasn't been easy to get here. I appreciate that you continue to come. (Affirm)

#     I know it's really hard to stop smoking. (Support; not coded) You did great! (Not coded)
#     Way to go! (Not coded)

#     You've been working so hard at being a good parent. I'm so impressed with your willingness to stay in there even when the going gets tough! (Affirm)

#     Given what you have told me about your previous success with losing weight, I am confident that you will be successful again when you are ready. (Affirm)

#     You're feeling pretty discouraged about the fast foods. You had hoped to not hit the drive thru at all this past two weeks. It strikes me though that, even if you went for fast food twice during that time, that is considerably less than when you were going every day.
#     That seems like a big change! (Affirm)

# *E.4.f.2.a. Three strikes rule for Affirmations*

# Clinicians can overuse affirmations by repeating them many times during the conversation. In general, the first two or three times, the statement may be credible and coded as an Affirm if the coder is confident that the utterance still clearly falls into the Affirm category. After that, they are typically not coded.

# *E.4.f.3 Seeking Collaboration*

# This code is assigned when a clinician explicitly attempts to share power or acknowledge the expertise of the client. It can occur when the clinician genuinely seeks consensus with the client regarding tasks, goals or directions of the session. Seeking collaboration may be assigned when the clinician asks what the client thinks about information provided. When permission to give information or advice is sought, Seeking Collaboration is typically assigned.

# When a clinician asks about the client's knowledge or understanding of a particular topic, this is coded as a Question. It is not considered to be Seeking Collaboration.

#     I have some information about how to reduce your risk of colon cancer and I wonder if I might discuss it with you. (Seeking Collaboration)

#     What have you already been told about drinking during pregnancy? (Question)

#     Would it be alright if we spend some discussing the standards for consuming alcohol during pregnancy (Seeking Collaboration)

#     This may not be the right thing for you, but some of my clients have had good luck setting the alarm on their wristwatch to help them remember to check their blood sugars two hours after lunch. (Seeking Collaboration, consider Persuade with Permission)

#     How can I help you with this? (Seeking Collaboration)

#     Would it be all right if we spent some time talking about smoking? I know you didn't come here to talk about that. (Seeking Collaboration)

#     I have your assessment results. Are you interested in going over those? (Seeking Collaboration)


# E.4.f.3.a Note: Elicit-Provide-Elicit (E-P-E) exchanges may or may not be an example of seeking collaboration. Each item is typically coded separately.

# Elicit-Provide-Elicit without Seeking Collaboration

#     *Clinician: What do you already know about drinking during pregnancy (Question)? Client: I know it's better *if I don't drink.
#     Clinician:  Yes. It's recommended that women abstain from alcohol during pregnancy. (GI)

# Elicit-Provide-Elicit with Seek Collaboration

#     *Clinician: What do you already know about drinking during pregnancy (Question)? Client: I know it's better *if I don't drink.
#     Clinician: What do you make of this information? How does it fit in with your approach to drinking? (Seeking Collaboration)
    
#     In contrast to:

#     Clinician: What do you already know about possible ways of quitting smoking? (Question)

#     Client: I know that the patch is supposed to be the most effective for quitting. How long can I be on the patch? Is it only supposed to be used for a week or two?

#     Clinician: The patch is one way to quit smoking. It is an effective method and is typically used for about four to six months (GI).
#     E.4.f.4. Emphasizing Autonomy (Emphasize)

# These are utterances that clearly focus the responsibility with the client for decisions about and actions pertaining to change. They highlight clients' sense of control, freedom of choice, personal autonomy, or ability or obligation to decide about their attitudes and actions. These are not statements that specifically emphasize the client's sense of self-efficacy, confidence, or ability to perform a specific action.

#     Yes, you're right. No one can force you stop drinking. (Emphasizing Autonomy)

#     You're the one who knows yourself best here. What do you think ought to be on this treatment plan? (Emphasizing Autonomy)

#     The number of fruits and vegetables you choose to eat is really up to you. (Emphasizing Autonomy)

#     This is really your life and your path. You are the only one who can decide which direction you will go. Where do you think you would like to go from here with your exercise? (Emphasizing Autonomy)

#     You are in a tough spot. Being in jail leaves you feeling like you have no control over your life. And you are being asked to consider engaging in a treatment program that might give you some control back if you decide to do that. You are not sure what to choose at this point. (Emphasizing Autonomy)

#     This is both an opportunity and a challenge as you see it. You are weighing the options and figuring out what will work best for you. (Emphasizing Autonomy)

#     Quit drinking Client: I'm pretty sure I can quit drinking for good.
#     Clinician: You feel confident you can quit drinking because you have done it before. (Reflection; Added value for Cultivating Change Talk)

#     Clinician: There's a choice in front of you and you feel pretty sure which way you want to go (Emphasizing Autonomy)
    
#     Clinician: You feel pretty sure about which way you want to go (Reflection; Added value for Cultivating Change Talk)

#     Clinician: You're ready to stop (Reflection; Added value for Cultivating Change Talk)

#     **Example: Checking Blood Sugar Levels**

#     Client: I'm not ready to check my blood sugar every day, but I could do it once a week or so.

#     Clinician: In the end, it's really up to you how often you check your blood sugar. (Emphasizing Autonomy)

#     Clinician: One change you're considering is checking weekly. (Simple Reflection; Added value for Cultivating Change Talk)

#     Clinician: It's really hard to get that test in every day (Complex Reflection; Decreased value for Softening Sustain Talk)

#     **Example: HIV test**

#     Client: Last week I talked to the Advice Nurse about a home test. She said I could buy one at the drugstore and get the results back right away.

#     Clinician: You have already taken some steps to find the answer you need. (Reflection; Added value for Cultivating Change Talk)

#     Clinician: Now you have to make the decision about what is the best choice for you. (Emphasizing Autonomy)

#     Clinician: You feel two ways about finding out (Complex Reflection)

#     Clinician: I have some information about the home testing kits. I wonder if I could share it with you. (Seeking Collaboration)

#     Clinician: Yahoo! You made it to your goal! (Affirm)

#     Clinician: You've got what it takes. (Affirm)
# """.strip()


# _mina_behavior = """
# *E.4.g. MI Non-Adherent (MINA) Behaviors*

# There are only two MINA codes: Persuade and Confront.

# *E.4.g 1. Persuade (see Section E.4.b.)*

# *E.4.g.2. Confront.*
 
# This code is used when the clinician confronts the client by directly and unambiguously disagreeing, arguing, correcting, shaming, blaming, criticizing, labeling, warning, moralizing, ridiculing, or questioning the client's honesty. Such interactions will have the quality of uneven power sharing, accompanied by disapproval or negativity. Included here are instances where the interviewer uses a question or even a reflection, but the voice tone clearly indicates a confrontation.

# Restating negative information already known or disclosed by the client can be either a Confront or a Reflection. Most Confronts can be correctly categorized by careful attention to voice tone and context.

# Decision Rule: In the relatively unusual circumstance where the coder is not certain whether to code an utterance as a Confrontation or Reflection, no code should be assigned.

#     You were taking Antabuse but you drank anyway? (Confront) You think that is any way to treat people you love? (Confront)
#     Yes, you are an alcoholic. You might not think so, but you are. (Confront)

#     Wait a minute. It says right here that your A1C is 12. I'm sorry, but there is no way you could have been controlling your carbohydrates like you said if it's that high. (Confront)

#     Think of your kids, for crying out loud. (Confront)

#     You have no concerns whatsoever about your drinking? (Confront; Question code not assigned since Confront trumps Question)

#     Most people who drink as much as you do cannot ever drink normally again. (Confront)

#     I have a concern about your plan to drink moderately and I wonder if I can share it with you. (Seeking Collaboration)

#     Disciplining your child with punishment is a slippery slope. It seems alright in the beginning but then one thing leads to another. (Confront)

#     Remember you said that your cholesterol level was a threat to your life. If you can't get your diet under control, you are risking a stroke or a heart attack. (Confront)

#     Well, kids who are not supervised closely by their parents are at higher risk for substance abuse. I wonder what you think about your own parenting skills in that regard. (Probably Confront—listen for tone)
#     If you choose to continue to drink, there's nothing we can do to help you. (Probably Confront—listen for tone).
 
# When clinicians use confrontation to emphasize a client strength, virtue or positive achievement, the Affirm code should be considered. A Confront is not mandatory when the clinician is clearly attempting to affirm or support the client.

#     **Example: Terrible Mother**

#     Client: I'm a terrible mother.

#     Clinician: No you are not. You are having some troubles, but you are still a great mother. (Affirm)

#     **Example: Cholesterol Improvement**

#     Client: I improved this month. I ate at least three servings of fruits or vegetables every single day.

#     Clinician: Yes, but your cholesterol level is still way too high. (Confront)
#     or
#     Clinician: You've made some real progress in your eating habits. What do you make of that in terms of your longer-term health goals? (Affirm; Seeking Collaboration)

# *E.4.g.3. Decision rules for MINA*

# Persuasion and confrontation sometimes overlap and can fit in more than one category. When this happens, the following hierarchy should be used: Persuade, Confront.
# """.strip()


# MITI_GUIDE_BEHAVIOR = {
#     "Persuade": _persuade,
#     "Persuade with Permission": _persuade_with_permission,
#     "Questions": _questions,
#     "Simple and Complex Reflections": _simple_complex_reflection,
#     "MI-Adherent Behaviors": mia_behavior,
#     "MI-Non-Adherent Behaviors": _mina_behavior,
# }


