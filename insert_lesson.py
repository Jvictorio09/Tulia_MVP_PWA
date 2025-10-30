#!/usr/bin/env python3
"""
Expanded seed script for SpeakPro/Tulia lesson runner content.

Run: python insert_lessons_expanded.py

What this does (idempotent):
- Creates Levels 1–6, Units, Lessons, TipSheets, ContentBlocks, Districts, and MilestoneChallenges
- Fills each Lesson with a fun, PWA‑friendly set of Exercises (select/match/rewrite/listen/speak/scenario/fourpics)
- Uses get_or_create across all models to avoid duplication on re‑runs

Notes
- The Exercise model is assumed to support the fields used below (see original seed).
- For the custom type 'fourpics', we encode the image URLs in Exercise.options and the target word in Exercise.correct_answers[0].
- If you do not yet support 'fourpics' in your renderer, you can skip or coerce it to 'select' with image captions.

"""

import os
import sys
from pathlib import Path


def setup_django():
    project_dir = Path(__file__).parent
    sys.path.insert(0, str(project_dir))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myProject.settings')
    import django  # noqa: WPS433
    django.setup()


def upsert_district(level, name, description, image='', coach_name='', coach_description='', xp_required=0):
    from myApp.models import District
    obj, created = District.objects.get_or_create(
        level=level,
        name=name,
        defaults={
            'description': description,
            'image': image,
            'coach_name': coach_name,
            'coach_description': coach_description,
            'xp_required': xp_required,
        },
    )
    return obj, created


def upsert_milestone(level, name, description, duration_seconds, rubric, xp_reward, coins_reward):
    from myApp.models import MilestoneChallenge
    obj, created = MilestoneChallenge.objects.get_or_create(
        level=level,
        name=name,
        defaults={
            'description': description,
            'duration_seconds': duration_seconds,
            'rubric': rubric,
            'xp_reward': xp_reward,
            'coins_reward': coins_reward,
        },
    )
    return obj, created


def ensure_level(number, defaults):
    from myApp.models import Level
    level, created = Level.objects.get_or_create(number=number, defaults=defaults)
    return level, created


def ensure_unit(level, order, defaults):
    from myApp.models import Unit
    unit, created = Unit.objects.get_or_create(level=level, order=order, defaults=defaults)
    return unit, created


def ensure_lesson(unit, order, defaults):
    from myApp.models import Lesson
    lesson, created = Lesson.objects.get_or_create(unit=unit, order=order, defaults=defaults)
    return lesson, created


def ensure_tipsheet(lesson, title, content, examples=None):
    from myApp.models import TipSheet
    tips, _ = TipSheet.objects.get_or_create(
        lesson=lesson,
        defaults={
            'title': title,
            'content': content,
            'examples': examples or [],
        },
    )
    return tips


def ensure_block(lesson, order, title, content, content_type='text'):
    from myApp.models import ContentBlock
    block, _ = ContentBlock.objects.get_or_create(
        lesson=lesson,
        order=order,
        defaults={
            'title': title,
            'content': content,
            'content_type': content_type,
        },
    )
    return block


def ensure_exercise(lesson, order, ex):
    from myApp.models import Exercise
    exercise, created = Exercise.objects.get_or_create(
        lesson=lesson,
        order=order,
        defaults={
            'exercise_type': ex['exercise_type'],
            'prompt': ex['prompt'],
            'stimulus_audio': ex.get('stimulus_audio', ''),
            'stimulus_text': ex.get('stimulus_text', ''),
            'options': ex.get('options', []),
            'correct_answers': ex.get('correct_answers', []),
            'reference_rewrite': ex.get('reference_rewrite', ''),
            'feedback_correct': ex.get('feedback_correct', ''),
            'feedback_incorrect': ex.get('feedback_incorrect', ''),
            'xp_reward': ex.get('xp_reward', 5),
            'max_attempts': ex.get('max_attempts', 3),
        },
    )
    return exercise, created


def seed_level_1():
    """Level 1 — Awareness & Foundations."""
    from myApp.models import Level

    level1, _ = ensure_level(1, dict(
        name='Awareness & Foundations',
        description='Understand high-stakes moments, audience psychology, style, and clarity.',
        duration_minutes=75,
        xp_required=0,
        milestone_duration_seconds=30,
        district_name='Foundations District',
        district_description='Greek Amphitheater, Roman Forum, Medieval Market Square.',
        district_image='',
        coins_reward=50,
        gems_reward=5,
    ))

    # District & Milestone
    upsert_district(level1, 'Foundations District', 'Meet your coaches and learn the Golden Principle.', coach_name='Philosopher', coach_description='Guides debate and awareness.')
    upsert_milestone(level1, '30-Second Introduction', 'Record a clear, confident 30-second intro.', 30,
                     rubric={'weights': {'clarity': 0.3, 'structure': 0.3, 'presence': 0.2, 'influence': 0.2}},
                     xp_reward=50, coins_reward=20)

    # Unit
    unit1, _ = ensure_unit(level1, 1, dict(name='Awareness & Foundations', description='What raises the stakes; how to prepare and stay clear.', duration_minutes=30))

    # Lessons
    lessons_def = [
        dict(
            order=1,
            name='Why High‑Stakes Communication Is Different',
            description='Time Pressure × Audience Power × Emotional Charge; outcome over words.',
            duration_minutes=10,
            xp_reward=20,
            tip_sheet='Outcome > words. Prepare Message, Mind, and Moment. Keep one clear ask.',
            learning_objectives='Define high‑stakes; apply Golden Principle; prep ritual.',
            blocks=[
                (1, 'The Three Variables', 'Time, Power, Emotional Charge — awareness reduces surprise.', 'text'),
                (2, 'Short video: Why it matters', 'https://example.com/video/why-high-stakes', 'video'),
            ],
            exercises=[
                dict(order=1, exercise_type='select', prompt='Which best states the Golden Principle?', options=['Say more to show expertise.', 'Focus on the audience outcome you create.'], correct_answers=[1], feedback_correct='Yes: measure success by the audience shift.', feedback_incorrect='Hint: It is not about eloquence.'),
                dict(order=2, exercise_type='rewrite', prompt='Rewrite: "I will demonstrate my expertise thoroughly in 10 minutes."', reference_rewrite='I will help you decide quickly with one clear recommendation.', feedback_correct='Outcome‑focused!', feedback_incorrect='Aim for audience outcome.'),
                dict(order=3, exercise_type='listen', prompt='Listen and choose the phrase that aligns with outcome-focus.', stimulus_audio='', options=['Here are all the features...', 'Here is what changes for you.'], correct_answers=[1], feedback_correct='That frames the outcome.', feedback_incorrect='Try the one that signals impact.'),
                
            ],
        ),
        dict(
            order=2,
            name='Understanding Audience Psychology',
            description='Style matching and humble inquiry to reduce resistance.',
            duration_minutes=10,
            xp_reward=20,
            tip_sheet='Curiosity before advocacy: ask, reflect, then propose.',
            learning_objectives='Read styles; adapt tone; use humble inquiry.',
            blocks=[
                (1, 'Styles Overview', 'Direct/Indirect; Report/Rapport; High/Low involvement.', 'text'),
            ],
            exercises=[
                dict(order=1, exercise_type='select', prompt='Investor prefers brevity. Choose greeting.', options=['Thanks for your time — in 90 seconds, the thesis and ask.', 'Let me walk through our entire history.'], correct_answers=[0], feedback_correct='Brevity first.', feedback_incorrect='Investors reward concise clarity.'),
                dict(order=2, exercise_type='rewrite', prompt='Turn this into a humble inquiry: "We should ship feature X next week."', reference_rewrite='What outcome matters most next week, and would feature X help us reach it?', feedback_correct='Curious and aligned.', feedback_incorrect='Open with a question that reveals priorities.'),
                dict(order=3, exercise_type='scenario', prompt='Board vs Team tone?', options=['Same script for both to be fair.', 'Adapt tone and detail to each audience.'], correct_answers=[1], feedback_correct='Audience fit > uniformity.', feedback_incorrect='Different rooms, different expectations.'),
            ],
        ),
        dict(
            order=3,
            name='Communication Styles & Presence',
            description='Mindset + posture + values anchor → presence.',
            duration_minutes=8,
            xp_reward=15,
            tip_sheet='Presence = body + breath + belief. 90‑sec ritual before speaking.',
            learning_objectives='Manage arousal; project steady tone; align body with message.',
            blocks=[(1, 'Presence Drill', '4‑4‑4‑4 breathing + stance + cue word.', 'text')],
            exercises=[
                dict(order=1, exercise_type='listen', prompt='Pick the version with congruent tone to: "We are confident in this plan."', options=['Flat, rushed delivery', 'Calm, steady pace with emphasis on confident'], correct_answers=[1], feedback_correct='Tone matches message.', feedback_incorrect='Congruence builds trust.'),
                dict(order=2, exercise_type='speak', prompt='Say: "I will keep this simple and valuable for you."', feedback_correct='Grounded and clear!', feedback_incorrect='Slow down; emphasize value.'),
            ],
        ),
        dict(
            order=4,
            name='Clarity vs Jargon',
            description='Replace buzzwords with everyday language; keep one idea per sentence.',
            duration_minutes=8,
            xp_reward=15,
            tip_sheet='Prefer short words; define terms; one idea per sentence.',
            learning_objectives='Spot jargon; rewrite for clarity; choose plain options.',
            blocks=[(1, 'Why Clarity Wins', 'Clarity builds trust and speeds decisions.', 'text')],
            exercises=[
                dict(order=1, exercise_type='select', prompt='Choose the clearer line.', options=['We will operationalize synergies.', 'We will work better together.'], correct_answers=[1], feedback_correct='Simple wins.', feedback_incorrect='Short, concrete words > buzzwords.'),
                dict(order=2, exercise_type='match', prompt='Match jargon to plain English.', options=['Leverage', 'Facilitate', 'Ideate'], correct_answers=['Use', 'Help', 'Think of ideas'], feedback_correct='Nice!', feedback_incorrect='Aim for common alternatives.'),
                dict(order=3, exercise_type='rewrite', prompt='Rewrite: "Utilize the platform to ideate solutions."', reference_rewrite='Use the site to think of solutions.', feedback_correct='Crisp!', feedback_incorrect='Try use/site/think.'),
                dict(order=4, exercise_type='fourpics', prompt='4‑Pics‑1‑Word: What single word ties these images?', options=[
                    'https://images.unsplash.com/photo-1521737604893-d14cc237f11d',
                    'https://images.unsplash.com/photo-1497493292307-31c376b6e479',
                    'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4',
                    'https://images.unsplash.com/photo-1504384308090-c894fdcc538d',
                ], correct_answers=['TRUST'], feedback_correct='+10 XP — Trust is the outcome.', feedback_incorrect='Think about what clarity builds.'),
            ],
        ),
    ]

    for ldef in lessons_def:
        lesson, _ = ensure_lesson(unit1, ldef['order'], dict(
            name=ldef['name'],
            description=ldef['description'],
            duration_minutes=ldef['duration_minutes'],
            xp_reward=ldef['xp_reward'],
            tip_sheet=ldef['tip_sheet'],
            learning_objectives=ldef['learning_objectives'],
        ))
        # Blocks
        for order, title, content, ctype in ldef['blocks']:
            ensure_block(lesson, order, title, content, ctype)
        # Exercises
        for ex in ldef['exercises']:
            ensure_exercise(lesson, ex['order'], ex)


def seed_level_2():
    """Level 2 — Message Crafting."""
    level2, _ = ensure_level(2, dict(
        name='Message Crafting',
        description='Structure, hooks, and story for business impact.',
        duration_minutes=90,
        xp_required=100,
        milestone_duration_seconds=90,
        district_name='Message District',
        district_description='Lincoln Memorial, Cathedral Pulpit, Town Hall.',
        district_image='',
        coins_reward=60,
        gems_reward=6,
    ))

    upsert_district(level2, 'Message District', 'Craft compelling through-lines; earn Story Tokens.', coach_name='Storyteller', coach_description='Guides narrative rhythm.')
    upsert_milestone(level2, '90-Second Story Pitch', 'Deliver a structured 90-second story with hook and ask.', 90,
                     rubric={'weights': {'hook': 0.3, 'structure': 0.3, 'clarity': 0.25, 'purpose': 0.15}},
                     xp_reward=70, coins_reward=30)

    unit, _ = ensure_unit(level2, 1, dict(name='Message Architecture', description='Through-line, hook, story arc, close.', duration_minutes=45))

    lessons = [
        dict(order=1, name='The Through‑Line', duration=10, xp=20,
             tip='One sentence that everything serves.',
             blocks=[(1, 'Definition', 'A clean spine the audience remembers.', 'text')],
             exercises=[
                 dict(order=1, exercise_type='rewrite', prompt='Compress this 3‑sentence update into a one‑line through‑line.', reference_rewrite='We reduced churn 3% by fixing onboarding, unlocking +$120k ARR.'),
                 dict(order=2, exercise_type='select', prompt='Which through‑line works?', options=['Many things happened...', 'In 90 seconds: why this matters and the ask.'], correct_answers=[1]),
             ]),
        dict(order=2, name='The Hook (10 seconds)', duration=10, xp=20,
             tip='Lead with Why, then preview How/What.',
             blocks=[(1, 'Why‑How‑What', 'Start with Why to reduce cognitive load.', 'text')],
             exercises=[
                 dict(order=1, exercise_type='fourpics', prompt='Find the hook word.', options=[
                      'https://images.unsplash.com/photo-1504384308090-c894fdcc538d',
                      'https://images.unsplash.com/photo-1521737604893-d14cc237f11d',
                      'https://images.unsplash.com/photo-1522199710521-72d69614c702',
                      'https://images.unsplash.com/photo-1518779578993-ec3579fee39f',
                 ], correct_answers=['WHY']),
                 dict(order=2, exercise_type='rewrite', prompt='Rewrite the opener to start with Why.', reference_rewrite='Because customers churn faster than we can acquire them, we…'),
             ]),
        dict(order=3, name='Story Arc: What is → What could be', duration=12, xp=20,
             tip='Alternate current state with vision to create motion.',
             blocks=[(1, 'Arc', 'Contrast to move the room.', 'text')],
             exercises=[
                 dict(order=1, exercise_type='match', prompt='Sequence the beats.', options=['What is', 'What could be', 'Obstacle', 'Resolution'], correct_answers=['What is', 'Obstacle', 'What could be', 'Resolution']),
                 dict(order=2, exercise_type='scenario', prompt='Pick the slide that clarifies the turn.', options=['Wall of text', 'One big headline + number'], correct_answers=[1], feedback_correct='Clear visuals beat walls of text.', feedback_incorrect='One headline is clearer than many bullet points.'),
             ]),
        dict(order=4, name='Closing the Loop (Ask)', duration=8, xp=15,
             tip='One clear ask tied to Why.',
             blocks=[(1, 'Close', 'Tie back to purpose; state next step.', 'text')],
             exercises=[
                 dict(order=1, exercise_type='select', prompt='Best close?', options=['Anyway, time is up.', 'Approve 2 FTE to ship onboarding v2 by Nov 30.'], correct_answers=[1]),
                 dict(order=2, exercise_type='speak', prompt='Say your 10‑second ask tied to Why.'),
             ]),
    ]

    for item in lessons:
        lesson, _ = ensure_lesson(unit, item['order'], dict(
            name=item['name'], description=item['tip'], duration_minutes=item['duration'], xp_reward=item['xp'], tip_sheet=item['tip'], learning_objectives='Message discipline.'
        ))
        for b in item['blocks']:
            ensure_block(lesson, b[0], b[1], b[2], b[3])
        for ex in item['exercises']:
            ensure_exercise(lesson, ex['order'], ex)


def seed_level_3():
    """Level 3 — Delivery & Presence."""
    level3, _ = ensure_level(3, dict(
        name='Delivery & Presence',
        description='Voice, body, and energy control under pressure.',
        duration_minutes=90,
        xp_required=220,
        milestone_duration_seconds=120,
        district_name='Delivery District',
        district_description='Globe Theatre, Comedy Club, Parliament Chamber.',
        district_image='',
        coins_reward=70,
        gems_reward=7,
    ))

    upsert_district(level3, 'Delivery District', 'Master vocal variety, stance, and timing.', coach_name='Parliament Speaker', coach_description='Keeps pace and composure.')
    upsert_milestone(level3, '2-Minute Persuasion', 'Deliver a 2‑minute persuasive talk recorded/simulated.', 120,
                     rubric={'weights': {'tone': 0.3, 'posture': 0.25, 'timing': 0.2, 'connection': 0.25}},
                     xp_reward=80, coins_reward=35)

    unit, _ = ensure_unit(level3, 1, dict(name='Presence Mechanics', description='Voice as instrument; stance; timing.', duration_minutes=45))

    # Two punchy lessons (you can add more following the same pattern)
    lessons = [
        dict(order=1, name='Voice: Pitch, Pace, Pause, Power', duration=12, xp=20,
             tip='Slow is smooth, smooth is confident. Use pauses as punctuation.',
             blocks=[(1, 'Drill', 'Read the line with 3 different paces; record.', 'text')],
             exercises=[
                 dict(order=1, exercise_type='listen', prompt='Which version uses a purposeful pause?', options=['No pause', 'Pause before the ask'], correct_answers=[1]),
                 dict(order=2, exercise_type='speak', prompt='Say: "Here is the one change that unlocks the result."'),
             ]),
        dict(order=2, name='Body Language & Congruence', duration=10, xp=20,
             tip='Align gesture with message; eyes on the decision‑maker when asking.',
             blocks=[(1, 'Stance', 'Feet grounded, open chest, relaxed shoulders.', 'text')],
             exercises=[
                 dict(order=1, exercise_type='select', prompt='Which is more congruent for confidence?', options=['Folded arms, quick glance down', 'Open posture, steady eye contact'], correct_answers=[1]),
                 dict(order=2, exercise_type='scenario', prompt='You must deliver bad news. Choose tone guidance.', options=['Speak faster to finish quickly', 'Steady, lower pitch, slower pace'], correct_answers=[1], feedback_correct='Steady tone shows control.', feedback_incorrect='Rushed delivery undermines credibility.'),
             ]),
    ]

    for item in lessons:
        lesson, _ = ensure_lesson(unit, item['order'], dict(
            name=item['name'], description=item['tip'], duration_minutes=item['duration'], xp_reward=item['xp'], tip_sheet=item['tip'], learning_objectives='Embodied delivery.'
        ))
        for b in item['blocks']:
            ensure_block(lesson, b[0], b[1], b[2], b[3])
        for ex in item['exercises']:
            ensure_exercise(lesson, ex['order'], ex)


def seed_level_4_to_6():
    # Skeleton seeds with at least two lessons each + milestones; extend similarly as needed.
    # Level 4
    level4, _ = ensure_level(4, dict(
        name='Strategic Influence',
        description='Room reading, framing, and adaptive persuasion.',
        duration_minutes=90,
        xp_required=320,
        milestone_duration_seconds=120,
        district_name='Influence District',
        district_description='Boardroom, War Tent, UN Assembly.',
        district_image='',
        coins_reward=80,
        gems_reward=8,
    ))
    upsert_district(level4, 'Influence District', 'Read the room; choose ethical cues.', coach_name='CEO Mentor', coach_description='Frames decisions.')
    upsert_milestone(level4, 'Reframe the Proposal', 'Reframe a controversial proposal convincingly.', 120,
                     rubric={'weights': {'empathy': 0.3, 'logic': 0.3, 'ethics': 0.2, 'ask': 0.2}},
                     xp_reward=90, coins_reward=40)
    unit4, _ = ensure_unit(level4, 1, dict(name='Influence Toolkit', description='Psychology + framing.', duration_minutes=45))
    l4 = [
        dict(order=1, name='Ethos–Pathos–Logos (operational)', tip='Quick triad check before you speak.', duration=10, xp=20,
             exercises=[
                 dict(order=1, exercise_type='match', prompt='Tag each line E/P/L.', options=['Ethos', 'Pathos', 'Logos'], correct_answers=['Ethos', 'Pathos', 'Logos']),
                 dict(order=2, exercise_type='rewrite', prompt='Add Pathos without losing Logos to: "We hit 98.2% uptime."', reference_rewrite='Your teams stayed productive—98.2% uptime kept projects moving.'),
             ]),
        dict(order=2, name='Cialdini’s Influence Cues', tip='Choose ethically: authority, proof, reciprocity, liking, consistency, scarcity.', duration=10, xp=20,
             exercises=[
                 dict(order=1, exercise_type='scenario', prompt='Which cue pair fits a board update?', options=['Scarcity + Liking', 'Authority + Social proof'], correct_answers=[1], feedback_correct='Authority + proof build credibility.', feedback_incorrect='Boards trust authority, not scarcity tactics.'),
                 dict(order=2, exercise_type='select', prompt='Spot reciprocity.', options=['We offered a free audit first.', 'We demanded a commitment first.'], correct_answers=[0]),
             ]),
    ]
    for i in l4:
        lesson, _ = ensure_lesson(unit4, i['order'], dict(name=i['name'], description=i['tip'], duration_minutes=i['duration'], xp_reward=i['xp'], tip_sheet=i['tip'], learning_objectives='Influence practice.'))
        ensure_block(lesson, 1, 'Primer', i['tip'], 'text')
        for ex in i['exercises']:
            ensure_exercise(lesson, ex['order'], ex)

    # Level 5
    level5, _ = ensure_level(5, dict(
        name='Negotiation & Impact',
        description='Trust, objection handling, and principled bargaining.',
        duration_minutes=90,
        xp_required=420,
        milestone_duration_seconds=300,
        district_name='Negotiation District',
        district_description='Yalta Conference, Merchant Guild, Startup Pitch Day.',
        district_image='',
        coins_reward=90,
        gems_reward=9,
    ))
    upsert_district(level5, 'Negotiation District', 'Balance assertiveness and empathy.', coach_name='Statesman', coach_description='Diplomatic persuasion.')
    upsert_milestone(level5, '5-Min Negotiation', 'Conduct a principled 5‑minute negotiation.', 300,
                     rubric={'weights': {'interests': 0.3, 'listening': 0.25, 'options': 0.25, 'commitment': 0.2}},
                     xp_reward=110, coins_reward=50)
    unit5, _ = ensure_unit(level5, 1, dict(name='Principled Negotiation', description='Interests over positions.', duration_minutes=45))
    l5 = [
        dict(order=1, name='Interests vs Positions', tip='Ask why; trade on interests.', duration=10, xp=20,
             exercises=[
                 dict(order=1, exercise_type='select', prompt='Which is an interest?', options=['We want a 10% discount', 'We need predictable cash flow'], correct_answers=[1]),
                 dict(order=2, exercise_type='rewrite', prompt='Reframe the position into an interest.', reference_rewrite='We need predictable cash flow, so a quarterly plan works.'),
             ]),
        dict(order=2, name='Handling Objections', tip='Label emotion, validate, then respond.', duration=10, xp=20,
             exercises=[
                 dict(order=1, exercise_type='scenario', prompt='Best response to: "It's too risky."', options=['You're wrong.', 'I hear the risk. Which part worries you most?'], correct_answers=[1], feedback_correct='Validation opens dialogue.', feedback_incorrect='Defensiveness closes doors.'),
                 dict(order=2, exercise_type='speak', prompt='Say a validating line, then ask one clarifying question.'),
             ]),
    ]
    for i in l5:
        lesson, _ = ensure_lesson(unit5, i['order'], dict(name=i['name'], description=i['tip'], duration_minutes=i['duration'], xp_reward=i['xp'], tip_sheet=i['tip'], learning_objectives='Negotiation drills.'))
        ensure_block(lesson, 1, 'Primer', i['tip'], 'text')
        for ex in i['exercises']:
            ensure_exercise(lesson, ex['order'], ex)

    # Level 6
    level6, _ = ensure_level(6, dict(
        name='Integration & Mastery',
        description='Combine clarity, story, delivery, and influence into signature talks.',
        duration_minutes=100,
        xp_required=520,
        milestone_duration_seconds=240,
        district_name='Mastery District',
        district_description='TED Stage, Davos Forum, Hologram Stage.',
        district_image='',
        coins_reward=120,
        gems_reward=12,
    ))
    upsert_district(level6, 'Mastery District', 'Unite all skills in one performance.', coach_name='TED Coach', coach_description='Clarity + story + presence.')
    upsert_milestone(level6, '3–5 Minute Signature Talk', 'Deliver an integrated, inspiring talk.', 240,
                     rubric={'weights': {'purpose': 0.25, 'structure': 0.25, 'delivery': 0.25, 'influence': 0.25}},
                     xp_reward=150, coins_reward=60)
    unit6, _ = ensure_unit(level6, 1, dict(name='Signature Synthesis', description='Design and deliver your signature talk.', duration_minutes=50))
    l6 = [
        dict(order=1, name='Outcome‑Driven Communication', tip='Design backwards from audience shift.', duration=12, xp=25,
             exercises=[
                 dict(order=1, exercise_type='rewrite', prompt='State your desired audience action in ≤12 words.', reference_rewrite='Approve onboarding v2 to cut churn 3% this quarter.'),
                 dict(order=2, exercise_type='scenario', prompt='Cut sentences that don't serve the outcome.', options=['Keep all context for safety', 'Keep only what moves the action'], correct_answers=[1], feedback_correct='Every sentence serves the outcome.', feedback_incorrect='Extra context dilutes focus.'),
             ]),
        dict(order=2, name='Signature Talk Run‑through', tip='Through‑line → hook → arc → ask.', duration=15, xp=30,
             exercises=[
                 dict(order=1, exercise_type='speak', prompt='Deliver a 45‑sec preview of your talk.'),
                 dict(order=2, exercise_type='listen', prompt='Which preview has a clearer Why?', options=['Feature first', 'Why first'], correct_answers=[1]),
             ]),
    ]
    for i in l6:
        lesson, _ = ensure_lesson(unit6, i['order'], dict(name=i['name'], description=i['tip'], duration_minutes=i['duration'], xp_reward=i['xp'], tip_sheet=i['tip'], learning_objectives='Integration.'))
        ensure_block(lesson, 1, 'Primer', i['tip'], 'text')
        for ex in i['exercises']:
            ensure_exercise(lesson, ex['order'], ex)



def main():
    setup_django()
    from django.db import transaction
    from myApp.models import Level, Unit, Lesson, Exercise, TipSheet, ContentBlock, MilestoneChallenge, District

    # Wipe existing data
    print('🗑️  Clearing existing lesson data...')
    with transaction.atomic():
        Exercise.objects.all().delete()
        TipSheet.objects.all().delete()
        ContentBlock.objects.all().delete()
        Lesson.objects.all().delete()
        Unit.objects.all().delete()
        MilestoneChallenge.objects.all().delete()
        District.objects.all().delete()
        Level.objects.all().delete()
    
    print('🌱 Seeding fresh data...')

    created_counts = dict(levels=0, units=0, lessons=0, exercises=0, tips=0, blocks=0, milestones=0, districts=0)

    with transaction.atomic():
        # Seed Level 1–3 in depth, and Level 4–6 minimally (extensible pattern)
        seed_level_1()
        seed_level_2()
        seed_level_3()
        seed_level_4_to_6()

    print('\n✅ Database wiped and reseeded successfully!')
    print('Next: runserver → sign in → explore Levels 1–3 fully, 4–6 skeleton ready to extend.')


if __name__ == '__main__':
    main()
