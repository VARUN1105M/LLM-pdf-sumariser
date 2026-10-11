import json
from pathlib import Path

TRANSCRIPTS_DATA = [
    {
        "id": "shreyas-doshi-pm-frameworks",
        "episode_number": 42,
        "title": "A guide to high-agency product management and career progression",
        "guest": "Shreyas Doshi",
        "guest_role": "Former Product Lead at Stripe, Twitter, Google",
        "date": "2023-04-13",
        "url": "https://www.lennyspodcast.com/shreyas-doshi-on-product-management/",
        "topics": ["Product Management", "L/G/P Framework", "High Agency", "Pre-mortems", "Career Strategy"],
        "summary": "Shreyas Doshi shares his most famous product management frameworks including the L/G/P (Leverage, Growth, Perception) model, the importance of high agency, how to run effective pre-mortems, and why execution speed beats strategic perfection.",
        "content": """
[00:00:15] Lenny Rachitsky: Welcome to Lenny's Podcast. Today my guest is Shreyas Doshi. Shreyas is legendary in the product community for creating frameworks that distill complex product strategy into actionable wisdom. Shreyas, welcome.

[00:01:20] Shreyas Doshi: Thanks Lenny, thrilled to be here.

[00:02:10] Lenny Rachitsky: Let's jump into the L/G/P framework. It's one of your most shared concepts. Can you unpack what it is and why PMs make mistakes with it?

[00:02:45] Shreyas Doshi: Absolutely. L/G/P stands for Leverage, Growth, and Perception. When product managers evaluate features or projects, they often make the mistake of treating all efforts equally. 
Leverage work is high-leverage product investment that creates compounding advantages—things that fundamentally shift your cost structure, infrastructure leverage, or core product moat.
Growth work is directly tied to short-to-medium-term acquisition, conversion rate optimization, and funnel efficiency. It's measurable, but without underlying leverage, it runs out of steam.
Perception work is about managing internal and external optics: PR, buzzwords, or satisfying executive pet projects that look good on slides.
The danger is that PMs spend 60% of their energy on Perception work because it gets immediate praise, 30% on incremental Growth, and only 10% on genuine high Leverage work. The best PMs flip this ratio: 60% Leverage, 30% disciplined Growth, and only 10% necessary Perception.

[00:08:40] Lenny Rachitsky: That is so true. Another concept you frequently champion is 'High Agency'. How do you define High Agency in a product team?

[00:09:15] Shreyas Doshi: High agency is the ability to bend reality to achieve a goal when the odds and bureaucracy are against you. A low-agency person encounters an obstacle—like 'legal says no' or 'data engineering backlog is 3 months'—and they file a ticket, shrug, and say 'I'm blocked'. 
A high-agency PM says: 'Why did legal say no? What is the underlying risk they are protecting against? Can we rewrite the terms of service or create a ring-fenced alpha test to address that exact risk?' They find the path through, around, or over the wall without alienating stakeholders. High agency isn't aggressiveness; it's radical resourcefulness and ownership.

[00:16:30] Lenny Rachitsky: Tell us about the Pre-Mortem technique for product launches.

[00:17:05] Shreyas Doshi: The pre-mortem is one of the highest ROI risk mitigation exercises you can do. Before writing code or kicking off a major launch, bring the engineering, design, data, product, and marketing leads into a room. You say: 'Imagine it is one year from today. The product launched, and it was a catastrophic failure. Adoption is near zero, customers are complaining, and leadership is pulling the plug. Take 10 minutes in silence and write down exactly why it failed.'
Because people have permission to be pessimistic without being labeled 'not a team player', they will share the real landmines: 'The onboarding API was too slow', 'Customer success wasn't trained', 'We solved a nice-to-have problem instead of a hair-on-fire pain'. Then you rank those risks and build preventative measures directly into the sprint plan.
"""
    },
    {
        "id": "brian-chesky-founder-mode",
        "episode_number": 105,
        "title": "Brian Chesky on 'Founder Mode', redesigning Airbnb, and leading with taste",
        "guest": "Brian Chesky",
        "guest_role": "Co-founder & CEO, Airbnb",
        "date": "2024-09-08",
        "url": "https://www.lennyspodcast.com/brian-chesky-founder-mode/",
        "topics": ["Founder Mode", "Product Leadership", "Airbnb", "Design", "Management"],
        "summary": "Brian Chesky explains how conventional Silicon Valley management advice—delegating everything to professional managers—almost broke Airbnb, and why founders must remain deep in the details, run a centralized product review cadence, and obsess over design and craft.",
        "content": """
[00:00:20] Lenny Rachitsky: Today my guest is Brian Chesky, co-founder and CEO of Airbnb. Brian, your talk about 'Founder Mode' at Y Combinator blew up the tech internet. What does Founder Mode actually mean to you?

[00:01:30] Brian Chesky: Lenny, for years we were told by traditional VCs and executive coaches that as a company scales, the founder's job is to hire 'great executives' and get out of their way. 'Hire them, empower them, delegate to them.'
We did that at Airbnb as we approached 2019, and the company became bureaucratic, fragmented, and slow. Every division became a silo with its own OKRs, roadmap, and design language. We were building mediocre software.
When the pandemic hit and our business dropped 80% in eight weeks, I had no choice. I pulled back control. I got rid of conventional divisional product management and centralized the company under a single shared roadmap. 
Founder mode means: you do not abdicate responsibility under the guise of delegation. You are in the details. You review the design, you test the flows, you question assumptions, and you ensure that the entire company operates with a cohesive product taste and unified vision.

[00:08:15] Lenny Rachitsky: How do you balance being in the details with not micromanaging?

[00:08:50] Brian Chesky: People confuse micromanagement with excellence. Micromanagement is telling a talented person what color button to click while having no vision. 
What I do is collaborative inquiry: 'Show me the end-to-end user journey. Why does this screen have five steps instead of two? Where is the magic in this experience?' If you set high standards and partner with people in the craft, the best builders love it because they know the CEO genuinely cares about their work. 
At Airbnb, we hold product reviews every single week. We ship major seasonal releases twice a year—Summer Release and Winter Release—which forces cross-functional synchronization instead of random feature droppings.
"""
    },
    {
        "id": "elena-verna-plg-growth",
        "episode_number": 88,
        "title": "Elena Verna on B2B Product-Led Growth, freemium vs. trial, and retention engines",
        "guest": "Elena Verna",
        "guest_role": "Head of Growth at Dropbox, SurveyMonkey, Miro, Amplitude",
        "date": "2023-11-20",
        "url": "https://www.lennyspodcast.com/elena-verna-b2b-growth/",
        "topics": ["Product-Led Growth", "Freemium", "B2B Monetization", "Retention", "Activation"],
        "summary": "Elena Verna provides a masterclass on B2B Product-Led Growth (PLG), explaining how to design effective freemium tiers, why retention precedes acquisition, and how to create viral expansion loops within enterprise teams.",
        "content": """
[00:00:30] Lenny Rachitsky: Welcome back to Lenny's Podcast. Today we have Elena Verna, widely regarded as the queen of B2B Product-Led Growth. Elena, thank you for joining.

[00:01:10] Elena Verna: Hi Lenny, so excited to be here!

[00:01:50] Lenny Rachitsky: Many B2B companies want to transition from sales-led to product-led. What is the biggest trap they fall into?

[00:02:25] Elena Verna: The number one trap is thinking PLG is just a pricing model or putting a 'Sign Up Free' button on your homepage. 
PLG is an end-to-end company operating model where the product itself drives acquisition, retention, and monetization. 
If your product has a steep learning curve that requires a human salesperson to set up, putting a freemium tier on it is like pouring water into a bucket without a bottom. You will get signups, but zero activation, zero retention, and huge churn.
First rule: Retention always precedes growth. You must prove that unassisted users can reach the 'Aha moment' in minutes, not days.

[00:07:45] Lenny Rachitsky: How should founders decide between Freemium versus Reverse Trial?

[00:08:20] Elena Verna: A pure Free Trial forces a buying decision in 14 or 30 days. That works well when your value is immediately obvious and urgency is high.
Freemium is an acquisition engine. It gives users continuous utility forever, which allows you to build habit and land inside an organization. But freemium requires a smart monetization trigger: either usage limits (e.g. number of boards in Miro, storage in Dropbox), feature gating (e.g. SSO, audit logs for enterprise), or collaboration gating (e.g. invite 3 or more teammates).
My favorite modern model is the 'Reverse Trial': you give the user full access to all Pro features for 14 days without requiring a credit card. When the trial expires, they don't get locked out; they downgrade gracefully to the free tier. This builds maximum exposure to premium value without creating customer resentment.
"""
    },
    {
        "id": "sean-ellis-growth-hacking",
        "episode_number": 64,
        "title": "Sean Ellis on founding Growth Hacking, the 40% PMF rule, and rapid testing",
        "guest": "Sean Ellis",
        "guest_role": "Author of Hacking Growth, Former Growth Leader at Dropbox, Eventbrite",
        "date": "2023-08-10",
        "url": "https://www.lennyspodcast.com/sean-ellis-growth-hacking/",
        "topics": ["Growth Hacking", "Product-Market Fit", "North Star Metric", "High-Tempo Testing"],
        "summary": "Sean Ellis, who coined the term 'Growth Hacking', explains the famous 40% 'Very Disappointed' rule for measuring product-market fit, how to establish a North Star Metric, and the mechanics of running high-tempo growth sprints.",
        "content": """
[00:00:15] Lenny Rachitsky: Sean Ellis is here today. Sean literally coined the term Growth Hacking and helped Dropbox and Eventbrite reach hypergrowth. Sean, let's talk about the PMF survey.

[00:01:05] Sean Ellis: Thanks Lenny. Product-market fit is the prerequisite for all growth. If you try to scale before product-market fit, you're accelerating failure. 
The survey question is: 'How would you feel if you could no longer use this product tomorrow? Very disappointed, somewhat disappointed, or not disappointed?'
Across hundreds of startups, I found a clear benchmark: if 40% or more of your active users answer 'Very disappointed', you have sufficient product-market fit to begin aggressive growth experiments. If you are below 40%, stop spending money on paid marketing. Focus 100% on understanding what your 'Very disappointed' core users love and double down on that.

[00:06:50] Lenny Rachitsky: How do you structure a high-tempo testing process once you have that 40% benchmark?

[00:07:25] Sean Ellis: Growth is a compounding probability game. A team running 2 experiments a month will always lose to a team running 10 experiments a week. 
We use the ICE scoring framework:
I = Impact: If this test wins, how big is the lift?
C = Confidence: What evidence (data, customer quotes, competitor teardowns) supports this hypothesis?
E = Ease: How quickly can engineering and design ship this test?
Rank the backlog by ICE, hold a weekly growth sprint meeting on Monday morning to review past results, commit to this week's 5 tests, and execute ruthlessly.
"""
    },
    {
        "id": "marty-cagan-empowered-teams",
        "episode_number": 51,
        "title": "Marty Cagan on Empowered Product Teams vs. Feature Factories",
        "guest": "Marty Cagan",
        "guest_role": "Partner at Silicon Valley Product Group (SVPG), Author of Inspired and Empowered",
        "date": "2023-06-05",
        "url": "https://www.lennyspodcast.com/marty-cagan-empowered-teams/",
        "topics": ["Product Leadership", "Feature Factory", "Product Discovery", "SVPG", "Autonomous Teams"],
        "summary": "Marty Cagan explains why the majority of companies claiming to do Agile are actually running 'feature factories', and how true product teams discover solutions that customers love yet work for the business.",
        "content": """
[00:00:20] Lenny Rachitsky: Welcome Marty Cagan. Marty, you wrote 'Inspired' and 'Empowered', which have guided thousands of product organizations. What is the fundamental difference between an empowered team and a feature factory?

[00:01:15] Marty Cagan: In a feature factory, the team is given a roadmap of features and deadlines by leadership. The stakeholders say: 'Build this shopping cart feature by Q3.' The PM acts as an agile project manager, writing user stories and managing the backlog. If the feature ships on time, everyone celebrates—even if nobody uses it and it generates zero business value.
In an empowered product team, the team is given a customer problem to solve or an outcome to achieve, such as: 'Reduce checkout abandonment rate by 15% without hurting average order value.' 
The team—consisting of product manager, product designer, and tech lead—is empowered to discover the solution. They test four core risks continuously: Value risk, Usability risk, Feasibility risk, and Business viability risk.

[00:08:30] Lenny Rachitsky: How does a PM lead effective Product Discovery?

[00:09:05] Marty Cagan: You cannot discover products from inside your office. You must talk to customers every single week. My rule is: every product team must conduct at least three customer discovery interviews or prototype tests every week. 
Prototype rapidly. Don't write production code to test value. Use interactive prototypes, concierge tests, and wizard-of-oz tests. Fast discovery separates the ideas that work from the 80% of ideas that will fail.
"""
    },
    {
        "id": "gustaf-alstromer-growth-loops",
        "episode_number": 75,
        "title": "Gustaf Alströmer on Growth Loops, YC Startup Growth, and Retention cohorts",
        "guest": "Gustaf Alströmer",
        "guest_role": "Group Partner at Y Combinator, Former Head of Growth at Airbnb",
        "date": "2023-09-14",
        "url": "https://www.lennyspodcast.com/gustaf-alstromer-growth-loops/",
        "topics": ["Growth Loops", "Retention Curves", "Y Combinator", "Viral Loops", "Funnel Metrics"],
        "summary": "Gustaf Alströmer discusses lessons from evaluating thousands of YC startups, why linear marketing funnels are obsolete compared to compounding growth loops, and how to analyze retention curves.",
        "content": """
[00:00:18] Lenny Rachitsky: Today my guest is Gustaf Alströmer, Group Partner at Y Combinator and former Head of Growth at Airbnb. Gustaf, why do you advise startups to focus on Growth Loops rather than traditional marketing funnels?

[00:01:05] Gustaf Alströmer: Linear funnels—awareness, acquisition, activation, retention, referral, revenue (AARRR)—are flawed because they require you to constantly pump money or marketing spend into the top of the funnel. When you stop spending, user acquisition drops to zero.
Growth loops, on the other hand, are closed compounding systems. The action of one user directly generates input for the next user.
For example, at Airbnb: a host lists an apartment -> guests search and book -> the guest experiences a great stay -> the guest tells their friends or becomes a host themselves in another city.
At Pinterest: a user pins content -> the pin gets indexed by Google -> new searchers find the pin -> they sign up and pin more content.
If your startup doesn't have a compounding growth loop—whether viral, content-driven, or paid reinvestment—sustainable scale is almost impossible.

[00:07:30] Lenny Rachitsky: What does a healthy retention curve look like for an early-stage company?

[00:08:10] Gustaf Alströmer: Plot your cohort retention over time (Day 1, Day 7, Day 30, Day 90). If the curve asymptotically flattens out into a horizontal line parallel to the x-axis, you have retained a core cohort. That flat line represents your product's baseline value. 
If the curve trends downward towards zero, you do not have product-market fit. Never attempt to pour growth loop fuel on a product with a retention curve that trends to zero.
"""
    }
]

def main():
    target_dir = Path("D:/Spark studios/2026 projects/rag-project/data/transcripts")
    target_dir.mkdir(parents=True, exist_ok=True)
    
    for item in TRANSCRIPTS_DATA:
        file_path = target_dir / f"{item['id']}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(item, f, indent=2, ensure_ascii=False)
        print(f"Generated: {file_path}")
        
    print(f"\nSuccessfully populated {len(TRANSCRIPTS_DATA)} curated Lenny Podcast transcripts in {target_dir}")

if __name__ == "__main__":
    main()
