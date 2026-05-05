import pandas as pd
import joblib
import gradio as gr
import time
import base64

# ================= LOAD MODEL =================
model = joblib.load("ipl_prematch_rf.pkl")

# ================= TEAMS =================
teams = [
    "Chennai Super Kings","Delhi Capitals","Gujarat Titans",
    "Kolkata Knight Riders","Lucknow Super Giants",
    "Mumbai Indians","Punjab Kings","Rajasthan Royals",
    "Royal Challengers Bangalore","Sunrisers Hyderabad"
]

# ================= VENUES =================
venue_city_map = {
    "Arun Jaitley Stadium, Delhi": "Delhi",
    "Barsapara Cricket Stadium, Guwahati": "Guwahati",
    "Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium, Lucknow": "Lucknow",
    "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium, Visakhapatnam": "Visakhapatnam",
    "Eden Gardens, Kolkata": "Kolkata",
    "Himachal Pradesh Cricket Association Stadium, Dharamsala": "Dharamsala",
    "M Chinnaswamy Stadium, Bengaluru": "Bangalore",
    "MA Chidambaram Stadium, Chepauk, Chennai": "Chennai",
    "Maharaja Yadavindra Singh International Cricket Stadium, Mullanpur": "Mullanpur",
    "Maharaja Yadavindra Singh International Cricket Stadium, New Chandigarh": "Chandigarh",
    "Narendra Modi Stadium, Ahmedabad": "Ahmedabad",
    "Rajiv Gandhi International Stadium, Uppal, Hyderabad": "Hyderabad",
    "Sawai Mansingh Stadium, Jaipur": "Jaipur",
    "Wankhede Stadium, Mumbai": "Mumbai"
}

venues = list(venue_city_map.keys())

# ================= TEAM LOGOS =================
team_logo_map = {
    "Chennai Super Kings": "csk.png",
    "Royal Challengers Bangalore": "rcb.png",
    "Mumbai Indians": "mi.png",
    "Kolkata Knight Riders": "kkr.png",
    "Delhi Capitals": "dc.png",
    "Sunrisers Hyderabad": "srh.png",
    "Punjab Kings": "pk.png",
    "Rajasthan Royals": "rr.png",
    "Gujarat Titans": "gt.png",
    "Lucknow Super Giants": "lsg.png"
}

def get_logo_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()




def update_match_logos(team1, team2, winner_logo=None, winner_name=None, winner_prob=None):

    if not team1 or not team2:
        return "<div style='color:white;text-align:center;'>Select teams</div>"

    logo1 = get_logo_base64(team_logo_map[team1])
    logo2 = get_logo_base64(team_logo_map[team2])

    # 🔥 Winner section
    winner_html = ""
    if winner_logo:
        winner_html = f"""
        <div style="
            display:flex;
            flex-direction:column;
            align-items:center;
            justify-content:center;
            margin-top:25px;
            text-align:center;
        ">

            <div style="color:#00e676; font-size:18px; font-weight:600;">
                🏆 Predicted Winner
            </div>

            <img src="data:image/png;base64,{winner_logo}" 
                 style="
                 width:130px;
                 margin-top:10px;
                 filter: drop-shadow(0 0 12px gold);
                 ">

            <div style="margin-top:10px; font-size:20px; color:white; font-weight:600;">
                {winner_name}
            </div>

            <div style="font-size:18px; color:#00e676; margin-top:5px;">
                Winning Probability: {winner_prob}
            </div>

            <div style="
                margin-top:12px;
                font-size:13px;
                color:#ccc;
                max-width:320px;
                line-height:1.5;
            ">
                This prediction represents a statistical probability based on historical match data 
                and machine learning analysis. It indicates the likelihood of the team winning, 
                but actual results may vary due to match conditions, player performance, and other real-time factors.
            </div>

        </div>
        """

    return f"""
    <div style='text-align:center; margin-top:60px;'>

        <div style='display:flex; align-items:center; justify-content:center; gap:25px;'>

            <img src="data:image/png;base64,{logo1}" 
                 style="width:140px; height:140px; object-fit:contain;
                 filter: drop-shadow(0 0 10px rgba(255,255,255,0.6));">

            <span style="font-size:30px; color:white; font-weight:700;">VS</span>

            <img src="data:image/png;base64,{logo2}" 
                 style="width:140px; height:140px; object-fit:contain;
                 filter: drop-shadow(0 0 10px rgba(255,255,255,0.6));">

        </div>

        {winner_html}

    </div>
    """
def predict_match(team1, team2, venue, toss_winner, toss_decision):

    city = venue_city_map[venue]

    df = pd.DataFrame([[team1, team2, city, toss_winner, toss_decision]],
                      columns=['team1','team2','city','toss_winner','toss_decision'])

    prob = model.predict_proba(df)[0]

    t1_prob = prob[1]
    t2_prob = prob[0]

    # 🔥 Winner logic
    if t1_prob > t2_prob:
        winner = team1
        winner_prob = f"{t1_prob*100:.2f} %"
    else:
        winner = team2
        winner_prob = f"{t2_prob*100:.2f} %"

    winner_logo = get_logo_base64(team_logo_map[winner])

    return (
        f"🔥 {team1}: {t1_prob*100:.2f} %",
        f"🔥 {team2}: {t2_prob*100:.2f} %",
        winner_logo,
        winner,
        winner_prob
    )
def update_all(team1, team2, venue, toss_winner, toss_decision):

    out1, out2, winner_logo, winner, winner_prob = predict_match(
        team1, team2, venue, toss_winner, toss_decision
    )

    html = update_match_logos(
        team1,
        team2,
        winner_logo,
        winner,
        winner_prob
    )

    return out1, out2, html

# ================= PAGE SWITCH FUNCTIONS =================
def show_home():
    time.sleep(1)
    return (
        gr.update(visible=False),
        gr.update(visible=True),
        gr.update(visible=False)
    )

def go_prediction():
    return (
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=True)
    )

# ================= LOAD BACKGROUND IMAGE =================
with open("ipl.webp", "rb") as f:
    encoded_string = base64.b64encode(f.read()).decode()
# ================= LOAD PLAYER IMAGE =================
with open("cups.png", "rb") as f:
    player_img = base64.b64encode(f.read()).decode()

with open("logo.png", "rb") as f:
    logo_img = base64.b64encode(f.read()).decode()

# SKY
with open("sky.png", "rb") as f:
    sky_img = base64.b64encode(f.read()).decode()

# Virat Kohli
with open("kohli.png", "rb") as f:
    kohli_img = base64.b64encode(f.read()).decode()

# Jasprit Bumrah
with open("bumrah.png", "rb") as f:
    bumrah_img = base64.b64encode(f.read()).decode()


# ================= CUSTOM CSS =================
custom_css = f"""

/* =========================================================
   PROFESSIONAL IPL DASHBOARD BACKGROUND
========================================================= */
.gradio-container {{
    min-height: 100vh;
    font-family: 'Segoe UI', sans-serif;
    background: url("data:image/webp;base64,{encoded_string}") center center / cover no-repeat fixed !important;
    overflow-x: hidden;
    position: relative;
}}

/* Dark premium overlay */
.gradio-container::before {{
    content: "";
    position: fixed;
    inset: 0;
    background:
        linear-gradient(
            rgba(5, 10, 20, 0.70),
            rgba(5, 10, 20, 0.82)
        );
    z-index: 0;
    pointer-events: none;
}}

/* Main container spacing */
.gradio-container > div {{
    position: relative;
    z-index: 2;
    max-width: 100% !important;
    width: 100% !important;
    padding: 0 60px !important;
    margin: 0 !important;
}}

.gr-box, .gr-panel, .gr-form {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}}

/* =========================================================
   PREMIUM GLASS CARD
========================================================= */
.glass-card,
.info-card,
.stat-card,
.card {{
    background: rgba(18, 28, 45, 0.72);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    color: white;
    box-shadow:
        0 12px 35px rgba(0,0,0,0.45),
        inset 0 0 0 1px rgba(255,255,255,0.03);
    transition: all 0.3s ease;
}}

.glass-card:hover,
.info-card:hover,
.stat-card:hover,
.card:hover {{
    transform: translateY(-4px);
    box-shadow:
        0 18px 40px rgba(0,0,0,0.55),
        0 0 18px rgba(0,183,255,0.12);
}}

.glass-card {{
    padding: 22px;
}}

.info-card {{
    padding: 28px;
    margin-top: 35px;
}}

.stat-card {{
    padding: 28px;
    margin-top: 30px;
}}

.card {{
    padding: 22px;
    margin-top: 30px;
}}

/* =========================================================
   CARD TITLES
========================================================= */
.card-title {{
    font-size: 20px;
    font-weight: 700;
    color: #f4f8ff;
    margin-bottom: 18px;
    letter-spacing: 0.4px;
}}

/* =========================================================
   MATCH ROWS
========================================================= */
.match-row {{
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.05);
    padding: 14px 16px;
    border-radius: 12px;
    margin-bottom: 12px;
    font-size: 15px;
    color: #e5edf8;
    transition: all 0.25s ease;
}}

.match-row:hover {{
    background: rgba(0,183,255,0.10);
    transform: translateX(4px);
}}

/* =========================================================
   PLAYER ROWS
========================================================= */
.player-row {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
    padding: 10px 12px;
    border-radius: 12px;
    background: rgba(255,255,255,0.04);
}}

.player-row:hover {{
    background: rgba(255,255,255,0.08);
}}

.player-avatar {{
    width: 48px;
    height: 48px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid rgba(255,255,255,0.15);
    box-shadow: 0 0 12px rgba(255,255,255,0.15);
}}

.player-name {{
    font-size: 14px;
    color: #f0f4fa;
    margin-bottom: 6px;
    font-weight: 500;
}}

/* =========================================================
   PROGRESS BAR
========================================================= */
.progress-bar {{
    width: 100%;
    height: 8px;
    background: rgba(255,255,255,0.12);
    border-radius: 999px;
    overflow: hidden;
}}

.progress-fill {{
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #00c6ff, #0072ff);
    box-shadow: 0 0 12px rgba(0,183,255,0.45);
}}

.star-box {{
    color: #ffd54f;
    font-size: 18px;
    letter-spacing: 1px;
    min-width: 60px;
    text-align: right;
}}

/* =========================================================
   INTRO PAGE
========================================================= */
#intro_page {{
    text-align: center;
    margin-top: 90px;
    animation: fadeIntro 1.5s ease-in-out;
}}

#intro_page h1 {{
    font-size: 68px !important;
    color: #f5f7fa !important;
    letter-spacing: 2px;
    font-weight: 800;
}}

@keyframes fadeIntro {{
    from {{
        opacity: 0;
        transform: translateY(-20px);
    }}
    to {{
        opacity: 1;
        transform: translateY(0);
    }}
}}

/* =========================================================
   TOP LOGO
========================================================= */
.top-bar {{
    position: fixed;
    top: 18px;
    left: 35px;
    z-index: 9999;
}}

.logo-box {{
    display: flex;
    align-items: center;
    gap: 12px;
}}

.logo-box img {{
    width: 95px;
    height: 95px;
    object-fit: contain;
    filter:
        drop-shadow(0 0 10px rgba(0,183,255,0.35))
        drop-shadow(0 0 18px rgba(255,215,0,0.25));
}}

/* =========================================================
   HERO SECTION
========================================================= */
.hero {{
    text-align: center;
    margin-top: 70px;
    margin-bottom: 20px;
}}

.hero h1 {{
    font-size: 52px;
    font-weight: 800;
    color: #f5f7fa;
    text-shadow: 0 4px 18px rgba(0,0,0,0.45);
}}

.hero p {{
    margin-top: 14px;
    font-size: 18px;
    line-height: 1.7;
    color: #c7d5e6;
}}

/* =========================================================
   BUTTONS
========================================================= */
#start_btn,
#prediction_page .gr-button {{
    background: linear-gradient(135deg, #00b4db, #0077ff) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-radius: 14px !important;
    font-size: 18px !important;
    font-weight: 700 !important;
    height: 52px !important;
    box-shadow:
        0 10px 22px rgba(0,119,255,0.35),
        inset 0 1px 0 rgba(255,255,255,0.15);
    transition: all 0.3s ease !important;
}}

#start_btn {{
    width: 280px !important;
    margin: 35px auto !important;
}}

#start_btn:hover,
#prediction_page .gr-button:hover {{
    transform: translateY(-3px) scale(1.02);
    box-shadow:
        0 14px 28px rgba(0,119,255,0.45),
        0 0 18px rgba(0,183,255,0.20);
}}

/* =========================================================
   STATS
========================================================= */
.stat-card h2 {{
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 8px;
    color: #00d4ff;
}}

.stat-card p {{
    font-size: 15px;
    color: #d6e1ef;
    letter-spacing: 0.5px;
}}

/* =========================================================
   INFO CARD CONTENT
========================================================= */
.info-card h2 {{
    font-size: 28px;
    margin-bottom: 12px;
    margin-top: 28px;
    color: #00d4ff;
}}

.info-card h3 {{
    font-size: 20px;
    margin-top: 24px;
    margin-bottom: 12px;
    color: #ffd54f;
}}

.info-card p {{
    color: #d8e4f0;
    line-height: 1.9;
    font-size: 15px;
    margin-bottom: 12px;
}}

.info-card ul {{
    padding-left: 22px;
    margin-bottom: 18px;
}}

.info-card li {{
    margin-bottom: 10px;
    color: #e6eef8;
    line-height: 1.7;
}}
/* ===================== PREDICTION PAGE FULL CSS ===================== */
/* PREDICTION PAGE */
#prediction_page h1 {{
    text-align: center;
    font-size: 42px !important;
    color: white !important;
    margin-bottom: 30px;
}}

#prediction_page .gr-dropdown > div {{
    background: rgba(0,0,0,0.7) !important;
    color: white !important;
    border-radius: 8px !important;
    height: 45px !important;
    border: none !important;
}}

#prediction_page .gr-radio {{
    color: white !important;
}}

#prediction_page .gr-button {{
    display: block !important;
    margin: 30px auto !important;
    width: 220px !important;
    height: 45px !important;
    font-size: 18px !important;
    font-weight: 600;
    border-radius: 8px !important;
    background: linear-gradient(45deg,#00c6ff,#0072ff) !important;
    color: white !important;
    border: none !important;
}}


#prediction_page .gr-button:hover {{
    transform: scale(1.05);
    transition: 0.3s;
}}

/* RESULT SECTION */
#result_section {{
    margin-top: 30px !important;
}}

#result_section textarea {{
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364) !important;
    color: #ffffff !important;
    border-radius: 14px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    text-align: center !important;
    font-size: 18px !important;
    font-weight: 700 !important;
    min-height: 58px !important;
    box-shadow: 0 0 18px rgba(0,183,255,0.18);
}}

"""


# ================= GRADIO APP =================
with gr.Blocks() as app:

    # INTRO PAGE
    intro = gr.Column(visible=True, elem_id="intro_page")
    with intro:
        if logo_img:
            
           gr.Markdown(f"""
<h2 style='font-size:40px; text-align:center; display:flex; justify-content:center; align-items:center; gap:12px;'>
    <img src="data:image/png;base64,{logo_img}" style="width:300px; height:400px;">
    
</h2>
""")

# HOME
    home = gr.Column(visible=False, elem_id="home_page")
    with home:

        # 🔥 TOP LOGO BAR
        if logo_img:
            gr.Markdown(f"""
            <div class="top-bar">
                <div class="logo-box">
                    <img src="data:image/png;base64,{logo_img}" />
                    <span> </span>
                </div>
            </div>
            """)
        

        gr.Markdown("""
        
        <div class="hero">
            <h1>🏆 IPL Insights & Predictions 2025</h1>
            <p>Leveraging 16 years of data (2008–2024)<br>
            to predict the next champion</p>
        </div>
        """)

        start_btn = gr.Button("🚀 Start Match Prediction", elem_id="start_btn")

        with gr.Row():
            with gr.Column():
                gr.HTML("""
                <div class="glass-card">
                    <div class="card-title">📊 Next Matches</div>

                    <div class="match-row">CSK vs MI - Today</div>
                    <div class="match-row">SRH vs DC - Tomorrow</div>
                    <div class="match-row">RCB vs KKR - Tomorrow</div>
                    
                </div>
                """)
            with gr.Column(scale=1):
                gr.Markdown(
                    f"""
                    <div style='display:flex; justify-content:center; align-items:center; margin-top:30px;'>
                        <img src="data:image/png;base64,{player_img}"
                            style="width:250px;
                            border-radius:12px;
                            box-shadow:0 0 15px rgba(0,0,0,0.5);">
                    </div>
                    """
                )
            with gr.Column():
                gr.HTML(f"""
                <div class="glass-card">
                    <div class="card-title">🏆 Top Performers</div>
                    
                    

                    <!-- KOHLI -->
                    <div class="player-row">
                        <img class="player-avatar" src="data:image/png;base64,{kohli_img}"/>
                        
                        <div style="flex:1;">
                            <div class="player-name">Virat Kohli (Orange Cap)</div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width:85%"></div>
                            </div>
                        </div>

                        <div class="star-box">⭐⭐⭐</div>
                    </div>

                    <!-- BUMRAH -->
                    <div class="player-row">
                        <img class="player-avatar" src="data:image/png;base64,{bumrah_img}"/>
                        
                        <div style="flex:1;">
                            <div class="player-name">Jasprit Bumrah (Purple Cap)</div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width:80%"></div>
                            </div>
                        </div>

                        <div class="star-box">⭐⭐☆</div>
                    </div>
                    <!-- SKY -->
                    <div class="player-row">
                        <img class="player-avatar" src="data:image/png;base64,{sky_img}"/>
                        
                        <div style="flex:1;">
                            <div class="player-name">Suryakumar Yadav (MVP)</div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width:75%"></div>
                            </div>
                        </div>

                        <div class="star-box">⭐⭐☆</div>
                    </div>
                </div>
                """)


        with gr.Row():
            gr.HTML("""
            <div class="info-card">

            <h2>The Evolution of IPL – A Data-Driven Cricket Revolutionn</h2>
            <p>
            The Indian Premier League, since its launch in 2008, has not only entertained millions but also transformed the way cricket is played and analyzed. What started as a fast-paced T20 tournament soon became a platform where strategy, data, and player performance merged. Over the years, IPL has evolved from simple aggressive batting contests into a highly analytical game where every run, ball, and decision is backed by historical data.
            <p>
            <p>
            In the early seasons, teams relied heavily on star players and individual brilliance. For example, explosive innings like that of Brendon McCullum in the opening match set the tone for high-scoring games. However, as seasons progressed, teams began to understand that consistency and balance were more important than just star power.
            <P>
            <h3> Key Historical Insights:</h3>
            <ul>
            <li>Teams with strong middle-order stability tend to win more matches</li>
            <li>All-rounders play a crucial role in balancing both batting and bowling</li>
            <li>Toss advantage varies, but chasing teams often show higher success rates</li>
            <li>Death-over performance (last 4 overs) is a major match-deciding factor</li>
            </ul>

            <h2> Legacy of Teams and Players</h2>
           <p>Over the years, certain teams and players have defined IPL’s legacy through consistent performances. Franchises like Mumbai Indians and Chennai Super Kings have dominated the tournament due to their strategic team composition and leadership stability. Their success highlights the importance of long-term planning rather than short-term aggression.
            <p>
            <p>At the same time, iconic players have shaped the identity of IPL. Leaders like MS Dhoni demonstrated calm decision-making under pressure, while players like Virat Kohli redefined consistency in batting across seasons.
            <p>
            <h3> What Makes Champions:<h3>
            <ul>
            <li>Stable leadership and captaincy</li>
            <li>Retaining a core group of players</li>
            <li>Smart usage of player roles and matchups</li>
            <li>Strong performance in pressure situations (playoffs)</li>
            </ul>
            

            <h2> Changing Nature of the Game</h2>
            <P>IPL has seen a drastic shift in scoring patterns and gameplay strategies. Earlier, a score of 150 was considered competitive, but modern IPL matches regularly cross 180 or even 200. This change reflects not just better batting skills but also improved understanding of pitch conditions and opposition weaknesses.
            <h3>⚡ Trend Evolution:</h3>
            <ul>
            <li>2008–2012 → Balanced game (bat vs ball)</li>
            <li>2013–2018 → Rise of power hitters</li>
            <li>2019–2025 → Data-driven aggressive cricket</li>
            </ul>

            <h2>The Psychology of Winning in IPL</h2>
            <p>The Indian Premier League is not just a battle of skills—it is a game of mindset, pressure handling, and decision-making under extreme conditions. Over the years, many matches have shown that teams with the strongest mental strength often outperform even more talented squads. The difference between winning and losing in IPL is often decided in just a few deliveries, where players must stay calm despite high pressure.
            <p>Captains like MS Dhoni became legends not only because of their skills but because of their ability to make the right decisions in the most critical moments.
            <h3>Psychological Winning Factors:</h3>
            <ul>
            <li>Staying calm during last-over finishes</li>
            <li>Handling crowd pressure and expectations</li>
            <li>Making quick and effective on-field decisions</li>
            <li>Confidence built from past winning experiences</li>
            </ul>

            <h2>The Power of Momentum in T20 Cricket</h2>
            <p>In IPL history, momentum has played a crucial role in shaping match outcomes. A single over—whether it’s a 20-run batting over or a wicket-taking bowling spell—can completely change the direction of the game. Unlike longer formats, T20 matches are highly dynamic, and momentum shifts happen rapidly.
            <h3>Momentum Insights:</h3>
            <ul>
            <li>One strong over can increase win probability drastically</li>
            <li>Consecutive wickets often lead to team collapse</li>
            <li>Boundaries in powerplay build early pressure</li>
            <li>Fielding efforts (run-outs, catches) shift momentum instantly</li>
            </ul>

            <h2>The Rise of Underdogs</h2>
            <p>One of the most exciting aspects of IPL history is how underdog teams and uncapped players have surprised everyone. Many unknown players entered the league and became match-winners, proving that IPL is a platform where talent meets opportunity.
            <p>Players like Jasprit Bumrah started as emerging talents and grew into world-class performers through IPL exposure.
            <h3>Underdog Insights::</h3>
            <ul>
            <li>New players often perform fearlessly</li>   
            <li>Teams with fewer stars sometimes show better coordination</li>
            <li>Unexpected performances create match-winning moments</li>
            <li>IPL scouting systems play a huge role in discovering talent</li>
            </ul>

            <h2> Hidden Impact of Fielding</h2>
            <p>While batting and bowling get most attention, fielding has silently influenced many IPL matches. A single dropped catch or brilliant run-out can decide the outcome.
            <h3>Fielding Insights:</h3>
            <ul>
            <li>Saves 10–15 runs per match on average</li>
            <li>Direct hits increase pressure on batting team</li>
            <li>Good fielding boosts overall team energy</li>
            <li>Often the difference in close matches</li>
            </ul>

           

            <h2>Conclusion of IPL</h2>

            <p>The Indian Premier League stands as one of the most revolutionary developments in modern cricket, blending entertainment, competition, and data-driven strategy into a single global phenomenon. From its beginning in 2008 to its evolution over the years, IPL has consistently redefined how the game is played, analyzed, and experienced by fans around the world.
            <p>What makes IPL unique is not just the presence of star players or high-scoring matches, but the balance between talent, teamwork, and intelligent decision-making. Teams like Mumbai Indians and Chennai Super Kings have shown that long-term success comes from stability, planning, and adaptability rather than short-term brilliance.
            <p>At the player level, legends such as MS Dhoni and Virat Kohli have demonstrated that consistency, leadership, and the ability to perform under pressure are key to greatness in the IPL environment.

            </div>
            """)

    # PREDICTION PAGE
    prediction = gr.Column(visible=False, elem_id="prediction_page")

    with prediction:

        if logo_img:
            gr.Markdown(f"""
            <div class="top-bar">
                <div class="logo-box">
                    <img src="data:image/png;base64,{logo_img}" />
                    <span> </span>
                </div>
            </div>
            """)

    # ✅ TOP CENTER TITLE (Full Width)
        gr.Markdown(
            "<h1 style='text-align:center; margin-bottom:40px;'>🏏 IPL Match Winner Prediction</h1>"
        )

    # ✅ LEFT + RIGHT LAYOUT
        with gr.Row():

        # LEFT SIDE (For future content)
            with gr.Column(scale=1):
                match_display = gr.HTML(
                "<div style='color:white;text-align:center;margin-top:50px;'>Select teams</div>"
            )

        # RIGHT SIDE (Prediction Form)
            with gr.Column(scale=1, elem_id="right_panel"):

                with gr.Row():
                    team1 = gr.Dropdown(teams, label="Team 1")
                    team2 = gr.Dropdown(teams, label="Team 2")

                venue = gr.Dropdown(venues, label="Match Venue")

                with gr.Row():
                    toss_winner = gr.Dropdown(teams, label="Toss Winner")
                    toss_decision = gr.Radio(["bat", "field"], label="Toss Decision")

                btn = gr.Button("🔮 Predict Winner")

                with gr.Row(elem_id="result_section"):
                    out1 = gr.Textbox(label="Team 1 Win Probability")
                    out2 = gr.Textbox(label="Team 2 Win Probability")
                team1.change(update_match_logos, [team1, team2], match_display)
                team2.change(update_match_logos, [team1, team2], match_display)

                btn.click(
                    update_all,
                    inputs=[team1, team2, venue, toss_winner, toss_decision],
                    outputs=[out1, out2, match_display]
                )

          # 🔥 IMPORTANT: ADD THIS (DYNAMIC LOGO UPDATE)
    
    # PAGE SWITCH
    app.load(show_home, None, [intro, home, prediction])
    start_btn.click(go_prediction, None, [intro, home, prediction])

app.launch(
    css=custom_css,
    theme=gr.themes.Soft(),   # ✅ moved here
    allowed_paths=["."]
)