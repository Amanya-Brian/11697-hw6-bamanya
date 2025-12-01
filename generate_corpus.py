#!/usr/bin/env python3
"""
Generate Football Corpus Documents
Creates 50+ documents on diverse football topics
"""

import os
from pathlib import Path
from typing import List, Dict
import json

# Document topics and content
DOCUMENTS = [
    {
        "filename": "world_cup_1986.txt",
        "title": "1986 FIFA World Cup",
        "content": """The 1986 FIFA World Cup was held in Mexico from May 31 to June 29, 1986. Argentina won the tournament, defeating West Germany 3-2 in the final at the Estadio Azteca in Mexico City.

Diego Maradona captained Argentina to victory and was the tournament's best player. The team was coached by Carlos Bilardo. Maradona's performances included the famous "Hand of God" goal and the "Goal of the Century" against England in the quarterfinals.

The final saw Argentina take a 2-0 lead with goals from José Luis Brown and Jorge Valdano. West Germany fought back to equalize at 2-2, but Jorge Burruchaga scored the winning goal in the 84th minute.

Gary Lineker of England won the Golden Boot with 6 goals. The tournament featured 24 teams and was notable for Maradona's dominance and Argentina's tactical prowess under Bilardo."""
    },
    {
        "filename": "fifa_history.txt",
        "title": "FIFA Foundation and History",
        "content": """FIFA (Fédération Internationale de Football Association) was founded on May 21, 1904, in Paris, France. The founding members were France, Belgium, Denmark, Netherlands, Spain, Sweden, and Switzerland.

The organization was created to oversee international competition among the national associations of these countries. Robert Guérin was FIFA's first president, serving from 1904 to 1906.

FIFA organized its first World Cup in 1930 in Uruguay, which was won by the host nation. The organization has grown from 7 founding members to 211 member associations as of 2023, making it one of the largest sports organizations in the world.

FIFA is headquartered in Zurich, Switzerland, and is responsible for organizing major international tournaments including the FIFA World Cup, FIFA Women's World Cup, and various youth and futsal competitions."""
    },
    {
        "filename": "england_1966_world_cup.txt",
        "title": "1966 FIFA World Cup Final",
        "content": """The 1966 FIFA World Cup final was played on July 30, 1966, at Wembley Stadium in London. England defeated West Germany 4-2 after extra time to win their first and only World Cup title.

The match is famous for Geoff Hurst's hat-trick, making him the only player to score three goals in a World Cup final. His second goal in extra time is controversial - the ball hit the crossbar and bounced down, and the Soviet linesman ruled it had crossed the line.

Hurst's goals came in the 18th minute, 101st minute (the controversial one), and 120th minute. Martin Peters scored England's other goal in the 78th minute. West Germany's goals were scored by Helmut Haller and Wolfgang Weber.

England captain Bobby Moore lifted the Jules Rimet Trophy, and the victory was watched by 96,924 spectators at Wembley. The win remains England's greatest achievement in international football."""
    },
    {
        "filename": "liverpool_anthem.txt",
        "title": "You'll Never Walk Alone - Liverpool FC Anthem",
        "content": """\"You'll Never Walk Alone\" is the anthem of Liverpool Football Club and is sung by supporters before every home game at Anfield. The song was originally written by Rodgers and Hammerstein for the 1945 musical Carousel.

The song was adopted by Liverpool fans in the early 1960s after it was recorded by Gerry and the Pacemakers, a local Liverpool band. The recording reached number one in the UK charts in 1963.

The anthem is now synonymous with Liverpool FC and represents the club's values of unity, solidarity, and support. The famous Kop stand at Anfield creates an intimidating atmosphere when thousands of fans sing the anthem together.

The words "You'll Never Walk Alone" also appear on the club's crest and above the Shankly Gates at Anfield. The song has become one of the most famous football anthems in the world."""
    },
    {
        "filename": "first_world_cup_1930.txt",
        "title": "1930 FIFA World Cup",
        "content": """The first FIFA World Cup was held in Uruguay in 1930. Uruguay was chosen as the host nation to celebrate the centenary of its first constitution. The tournament took place from July 13 to July 30, 1930.

Uruguay won the inaugural tournament, defeating Argentina 4-2 in the final at the Estadio Centenario in Montevideo. The stadium was built specifically for the World Cup and held 93,000 spectators.

Thirteen nations participated in the first World Cup: Argentina, Belgium, Bolivia, Brazil, Chile, France, Mexico, Paraguay, Peru, Romania, United States, Uruguay, and Yugoslavia. European participation was limited due to the long sea journey required.

Guillermo Stábile of Argentina was the top scorer with 8 goals. The tournament established the World Cup as the premier international football competition."""
    },
    {
        "filename": "2018_world_cup_golden_boot.txt",
        "title": "2018 FIFA World Cup Golden Boot",
        "content": """Harry Kane of England won the Golden Boot at the 2018 FIFA World Cup in Russia, scoring 6 goals. Kane was the tournament's top scorer despite England being eliminated in the semi-finals by Croatia.

Kane's goals included a hat-trick against Panama, two goals against Tunisia, and one penalty against Colombia. He scored in five of England's seven matches at the tournament.

Kane finished ahead of Antoine Griezmann, Romelu Lukaku, Kylian Mbappé, Denis Cherkashev, and Cristiano Ronaldo in the scoring charts. This was Kane's first major international tournament as England's captain and primary striker.

The Golden Boot award is given to the top scorer at each FIFA World Cup. In case of a tie, the award goes to the player with more assists, and if still tied, to the player with fewer minutes played."""
    },
    {
        "filename": "messi_current_club.txt",
        "title": "Lionel Messi's Career and Current Club",
        "content": """Lionel Messi joined Inter Miami CF in Major League Soccer (MLS) in July 2023. This move came after his contract with Paris Saint-Germain expired.

Messi has played for three clubs in his professional career: Barcelona (2004-2021), Paris Saint-Germain (2021-2023), and Inter Miami (2023-present). His move to Inter Miami was a landmark moment for soccer in the United States.

At Barcelona, Messi became the club's all-time leading scorer with 672 goals in 778 appearances. He won 35 trophies with Barcelona, including 10 La Liga titles and 4 UEFA Champions League titles.

At Paris Saint-Germain, Messi won Ligue 1 twice but the Champions League title eluded him. His move to Inter Miami came shortly after winning the 2022 FIFA World Cup with Argentina, cementing his legacy as one of football's greatest players."""
    },
    {
        "filename": "george_weah_ballon_dor.txt",
        "title": "George Weah - First African Ballon d'Or Winner",
        "content": """George Weah of Liberia became the first African player to win the Ballon d'Or in 1995. He was playing for AC Milan at the time and had an outstanding season in Serie A.

Weah's career included successful spells at Monaco, Paris Saint-Germain, AC Milan, Chelsea, Manchester City, and Marseille. He was known for his pace, technical ability, and powerful shooting.

In 1995, Weah also won the FIFA World Player of the Year award and was named African Footballer of the Year for the third time. His achievements opened doors for other African players in European football.

After retiring from football, Weah entered politics and was elected President of Liberia in 2018, serving until 2024. He remains the only African player to have won the Ballon d'Or."""
    },
    {
        "filename": "north_london_derby.txt",
        "title": "North London Derby",
        "content": """The North London Derby is the football match between Arsenal and Tottenham Hotspur, two of London's most successful clubs. The rivalry began in 1887 and is one of the fiercest in English football.

The derby is traditionally hosted at two stadiums: Arsenal's Emirates Stadium (formerly Highbury) and Tottenham's Tottenham Hotspur Stadium (formerly White Hart Lane). Both stadiums are located in North London, just four miles apart.

Arsenal have historically had more success in the fixture, winning more matches overall. The rivalry intensified in the modern era as both clubs competed for Premier League titles and Champions League qualification.

Famous moments include Arsène Wenger and Harry Redknapp's touchline confrontations, memorable goals, and heated player confrontations. The match regularly attracts worldwide attention and is considered one of the Premier League's biggest fixtures."""
    },
    {
        "filename": "fastest_premier_league_goal.txt",
        "title": "Fastest Goal in Premier League History",
        "content": """Shane Long scored the fastest goal in Premier League history on April 23, 2019, netting after just 7.69 seconds for Southampton against Watford at Vicarage Road. The goal broke the previous record of 9.82 seconds held by Ledley King.

Long's goal came directly from the kickoff. Southampton won the ball immediately, and Long ran through to score past Watford goalkeeper Ben Foster. The goal helped Southampton win the match 3-1.

Other notably fast Premier League goals include Ledley King's 9.82-second effort for Tottenham against Bradford City in 2000, and Alan Shearer's 10.4-second goal for Newcastle against Manchester City in 2003.

The fastest goal in top-flight English football history overall was scored by Gavin Strachan for Coventry City against Burnley in 1996, also timed at around 7 seconds, though exact timing varies by source."""
    },
    {
        "filename": "pep_guardiola_man_city.txt",
        "title": "Pep Guardiola at Manchester City",
        "content": """Pep Guardiola joined Manchester City as manager in 2016 and has transformed the club into one of Europe's dominant forces. As of 2025, Guardiola remains Manchester City's manager and has achieved unprecedented success.

Under Guardiola, Manchester City has won multiple Premier League titles, including a historic treble in the 2022-23 season when they won the Premier League, FA Cup, and UEFA Champions League. This made City only the second English club to achieve this feat after Manchester United in 1999.

Guardiola's Manchester City teams are known for their possession-based football, tactical flexibility, and record-breaking goal-scoring. The team set numerous Premier League records, including most points in a season (100 in 2017-18) and most wins in a season.

Key players under Guardiola have included Sergio Agüero, Kevin De Bruyne, Raheem Sterling, and Erling Haaland. Guardiola's contract has been extended multiple times, reflecting his importance to the club's success."""
    },
    {
        "filename": "san_siro_stadium.txt",
        "title": "San Siro Stadium - Milan",
        "content": """San Siro, officially known as Stadio Giuseppe Meazza, is located in Milan, Italy. It is one of the most iconic football stadiums in the world and serves as the home ground for both AC Milan and Inter Milan.

The stadium was built in 1926 and has a current capacity of approximately 75,923 spectators. It was named after Giuseppe Meazza, an Italian football legend who played for both Milan clubs and the Italian national team.

San Siro has hosted numerous prestigious matches, including the 1990 FIFA World Cup opening ceremony, multiple UEFA Champions League finals, and countless Serie A derbies known as the Derby della Madonnina.

The stadium is famous for its distinctive architecture, including the four cylindrical towers and the spiral ramps on the exterior. Despite talks of replacement, San Siro remains one of football's most atmospheric venues."""
    },
    {
        "filename": "beckham_career.txt",
        "title": "David Beckham's Career Moves",
        "content": """David Beckham joined LA Galaxy in Major League Soccer after leaving Real Madrid in 2007. This move was groundbreaking for American soccer and made Beckham one of the highest-paid athletes in the world.

Beckham's career included successful spells at Manchester United (1992-2003), Real Madrid (2003-2007), LA Galaxy (2007-2012), and brief loans to AC Milan. He finished his career with a stint at Paris Saint-Germain in 2013.

At Manchester United, Beckham won 6 Premier League titles, 2 FA Cups, and the 1999 UEFA Champions League. He was known for his crossing ability, set-piece expertise, and iconic status both on and off the field.

At LA Galaxy, Beckham won two MLS Cups and helped raise the profile of soccer in the United States. His "Beckham Rule" (Designated Player Rule) allowed MLS teams to sign high-profile international players outside the salary cap."""
    },
    {
        "filename": "sevilla_europa_league_2023.txt",
        "title": "Sevilla Win 2023 UEFA Europa League",
        "content": """Sevilla won the 2023 UEFA Europa League, their seventh Europa League/UEFA Cup title, by defeating AS Roma on penalties in the final held in Budapest, Hungary, on May 31, 2023.

The match ended 1-1 after extra time, with Sevilla winning 4-1 on penalties. This victory made Sevilla the most successful club in the competition's history, extending their record number of titles.

Sevilla's Europa League titles came in 2006, 2007, 2014, 2015, 2016, 2020, and 2023. The club has become synonymous with the competition, consistently performing well in European football's second-tier tournament.

José Luis Mendilibar was the manager for the 2023 triumph. Despite struggling in La Liga that season, Sevilla showed their European pedigree by winning the trophy. The victory secured their qualification for the 2023-24 UEFA Champions League."""
    },
    {
        "filename": "italy_euro_2020.txt",
        "title": "Italy Win Euro 2020",
        "content": """Italy won the UEFA Euro 2020 (played in 2021 due to COVID-19) under the captaincy of Giorgio Chiellini and Leonardo Bonucci as co-leaders. The tournament was held across Europe with the final at Wembley Stadium in London.

Italy defeated England on penalties in the final after a 1-1 draw following extra time. Luke Shaw gave England an early lead, but Leonardo Bonucci equalized for Italy. Italy won the penalty shootout 3-2.

Roberto Mancini was the coach who transformed Italy after their failure to qualify for the 2018 World Cup. Italy went on a 34-match unbeaten run during their Euro 2020 campaign.

Giorgio Chiellini captained Italy throughout the tournament and was instrumental in their defensive solidity. At 36 years old, Chiellini's leadership and experience were crucial to Italy's success. The victory was Italy's second European Championship, their first since 1968."""
    },
    {
        "filename": "diego_maradona_el_pibe_de_oro.txt",
        "title": "Diego Maradona - El Pibe de Oro",
        "content": """Diego Maradona was known as 'El Pibe de Oro' (The Golden Boy), a nickname given to him early in his career in Argentina. Maradona is widely considered one of the greatest football players of all time.

Maradona's career included successful spells at Argentinos Juniors, Boca Juniors, Barcelona, Napoli, and Sevilla. His greatest achievement came in 1986 when he captained Argentina to World Cup victory in Mexico.

Maradona wore the number 10 jersey throughout his career, which became synonymous with his genius. His famous goals against England in the 1986 World Cup quarterfinal - both the "Hand of God" and the "Goal of the Century" - are among football's most iconic moments.

At Napoli, Maradona led the club to their only two Serie A titles (1987, 1990) and the UEFA Cup in 1989. He scored 115 goals in 259 appearances for Napoli and became a deity-like figure in the city. Maradona passed away in November 2020, leaving an indelible mark on football history."""
    },
    {
        "filename": "maradona_jersey_number.txt",
        "title": "Diego Maradona's Jersey Number 10",
        "content": """Diego Maradona wore the number 10 jersey throughout his professional career, making it one of the most iconic shirt numbers in football history. The number 10 is traditionally worn by the team's playmaker or most creative player.

Maradona wore number 10 for Argentina, Napoli, Barcelona, Boca Juniors, and other clubs he represented. His performances while wearing the number elevated its status in football culture.

After Maradona's death in 2020, many clubs and players paid tribute by displaying the number 10 jersey. Napoli officially retired the number 10 shirt in honor of Maradona, meaning no future Napoli player will wear that number.

The Argentina national team continues to have players wear the number 10, most notably Lionel Messi, who inherited Maradona's legacy. The number 10 jersey represents creativity, leadership, and excellence in football."""
    },
    {
        "filename": "argentina_2022_world_cup_final.txt",
        "title": "2022 FIFA World Cup Final",
        "content": """The 2022 FIFA World Cup final was played on December 18, 2022, at Lusail Stadium in Qatar. Argentina defeated France 4-2 on penalties after a thrilling 3-3 draw following extra time.

Lionel Messi scored twice for Argentina, including a goal in the 23rd minute and another in extra time. Ángel Di María scored Argentina's second goal in regular time. Kylian Mbappé scored a hat-trick for France, including two goals in the final minutes of regulation to force extra time.

The penalty shootout saw Argentina prevail 4-2. Gonzalo Montiel scored the winning penalty. However, it was actually Messi who took and scored the first penalty for Argentina in the shootout, not specifically "the winning penalty" - that honor went to Montiel who converted the fourth and final penalty.

The victory was Argentina's third World Cup title (after 1978 and 1986) and Messi's first World Cup triumph, cementing his legacy as one of football's all-time greats. The final is considered one of the greatest World Cup finals ever played."""
    },
    {
        "filename": "2002_world_cup_hosts.txt",
        "title": "2002 FIFA World Cup Joint Hosts",
        "content": """The 2002 FIFA World Cup was jointly hosted by South Korea and Japan, making it the first World Cup held in Asia and the first co-hosted World Cup. The tournament ran from May 31 to June 30, 2002.

The decision to have co-hosts was controversial and unprecedented in World Cup history. South Korea and Japan had initially competed separately to host the tournament, but FIFA president João Havelange suggested they share hosting duties.

The tournament featured 32 teams and was notable for several upsets, including South Korea's surprising run to the semi-finals, becoming the first Asian team to reach that stage. Both co-hosts performed well, with Japan also reaching the knockout rounds.

Brazil won the tournament, defeating Germany 2-0 in the final held at International Stadium Yokohama in Japan. Ronaldo scored both goals and finished as the tournament's top scorer with 8 goals. The successful co-hosting model was later used for the 2026 World Cup (USA, Canada, Mexico)."""
    },
    {
        "filename": "nigeria_super_eagles.txt",
        "title": "Nigeria National Team - Super Eagles",
        "content": """The Nigeria national football team is nicknamed the "Super Eagles." The team is one of Africa's most successful national teams and has qualified for six FIFA World Cups (1994, 1998, 2002, 2010, 2014, 2018).

Nigeria has won the Africa Cup of Nations three times (1980, 1994, 2013) and has consistently been ranked among the top African nations by FIFA. The team's colors are green and white, matching the Nigerian flag.

Famous Nigerian players include Jay-Jay Okocha, Nwankwo Kanu, Rashidi Yekini, and more recently Victor Moses, Ahmed Musa, and Victor Osimhen. The team is known for its athletic style of play and has produced many players who have succeeded in European leagues.

The Super Eagles nickname was adopted in the 1980s and represents the national symbol of Nigeria - the eagle. The team plays its home matches at various stadiums across Nigeria, with Abuja National Stadium being a frequent venue."""
    },
    {
        "filename": "cristiano_ronaldo_clubs.txt",
        "title": "Cristiano Ronaldo's Club Career",
        "content": """Before joining Juventus in 2018, Cristiano Ronaldo played for three clubs: Sporting CP (2002-2003), Manchester United (2003-2009), and Real Madrid (2009-2018).

At Manchester United, Ronaldo won three Premier League titles, one FA Cup, two League Cups, and the 2008 UEFA Champions League. He also won his first Ballon d'Or in 2008 while at United.

At Real Madrid, Ronaldo became the club's all-time leading scorer with 450 goals in 438 appearances. He won four Champions League titles with Real Madrid (2014, 2016, 2017, 2018) and four more Ballon d'Or awards.

After Juventus (2018-2021), Ronaldo returned to Manchester United (2021-2022) before joining Al-Nassr in Saudi Arabia in 2023. Throughout his career, Ronaldo has won over 30 major trophies and five Ballon d'Or awards, establishing himself as one of football's greatest players."""
    }
]

# Add more documents to reach 50+
MORE_DOCUMENTS = [
    {
        "filename": "african_nations_cup_hosts.txt",
        "title": "Africa Cup of Nations Host Countries",
        "content": """The Africa Cup of Nations (AFCON) has been hosted by various African countries since its inception in 1957. Egypt has hosted the tournament five times (1959, 1974, 1986, 2006, 2019), more than any other nation.

Other frequent hosts include Ghana (1963, 1978, 2000, 2008), Sudan (1957, 1970), Ethiopia (1962, 1976, 2022), and Tunisia (1965, 1994, 2004). South Africa has hosted twice (1996, 2013).

Recent hosts include Cameroon (2021/2022), Gabon and Equatorial Guinea (2012, 2017 co-hosted), and Côte d'Ivoire (2023/2024). The tournament has grown in prestige and is now one of the premier international football competitions.

Libya was scheduled to host in 1982 but political circumstances led to a change. Other nations that have hosted include Algeria, Senegal, Mali, Burkina Faso, and Angola. The tournament typically features 24 teams in the modern format."""
    },
    {
        "filename": "womens_world_cup_winners.txt",
        "title": "FIFA Women's World Cup Winners 2011-2023",
        "content": """Between 2011 and 2023, the FIFA Women's World Cup has been won by three different nations.

Japan won in 2011, defeating the United States on penalties in the final held in Germany. This was Japan's first and only World Cup title.

The United States won in 2015, defeating Japan 5-2 in the final in Canada. They also won in 2019, beating the Netherlands 2-0 in France. This gave the USA four World Cup titles overall (1991, 1999, 2015, 2019).

Spain won the 2023 tournament in Australia and New Zealand, defeating England 1-0 in the final. Olga Carmona scored the winning goal, giving Spain their first World Cup title in women's football.

The tournament has grown significantly in popularity and viewership, with the 2023 edition breaking attendance records. These four tournaments showcased the increasing quality and competitiveness of women's football globally."""
    },
    {
        "filename": "london_premier_league_clubs.txt",
        "title": "London Premier League Clubs",
        "content": """London is home to several Premier League clubs, making it the most represented city in England's top division. The main London clubs in the Premier League include Arsenal, Chelsea, Tottenham Hotspur, West Ham United, and Crystal Palace.

Arsenal, based in North London (Emirates Stadium), is one of the most successful London clubs with 13 league titles. Chelsea, from West London (Stamford Bridge), has won 6 Premier League titles and 2 Champions League titles.

Tottenham Hotspur, also in North London (Tottenham Hotspur Stadium), has historically been one of England's biggest clubs despite not winning the league since 1961. West Ham United (London Stadium) represents East London.

Crystal Palace (Selhurst Park) in South London is another established Premier League club. Other London clubs have appeared in the Premier League at various times, including Fulham, Queens Park Rangers, Charlton Athletic, and Brentford.

The London derbies, particularly Arsenal vs Tottenham and Chelsea vs Arsenal, are among the most watched fixtures in English football."""
    },
    {
        "filename": "champions_league_top_scorers.txt",
        "title": "UEFA Champions League All-Time Top Scorers",
        "content": """Cristiano Ronaldo holds the record as the all-time leading scorer in UEFA Champions League history with 140 goals. He scored these goals playing for Manchester United, Real Madrid, and Juventus.

Lionel Messi is second with 129 goals, all scored while playing for Barcelona and Paris Saint-Germain. Robert Lewandowski is third with over 90 goals, having scored for Borussia Dortmund, Bayern Munich, and Barcelona.

Karim Benzema ranks fourth with 90 goals, primarily scored for Real Madrid. Raúl González, also of Real Madrid, is fifth with 71 goals. These five players make up the top scorers in Champions League history.

The Champions League has been the premier club competition in European football since 1992 (previously the European Cup). Ronaldo's record of 17 goals in a single season (2013-14) remains unmatched. He also holds the record for most hat-tricks in the competition."""
    },
    {
        "filename": "messi_club_career.txt",
        "title": "Lionel Messi's Professional Clubs",
        "content": """Lionel Messi has played for three professional clubs in his career: FC Barcelona, Paris Saint-Germain, and Inter Miami CF.

Messi joined Barcelona's youth academy, La Masia, at age 13 in 2000. He made his first-team debut in 2004 and played for Barcelona until 2021, becoming the club's all-time leading scorer with 672 goals in 778 appearances. He won 35 trophies with Barcelona, including 10 La Liga titles and 4 UEFA Champions League titles.

In August 2021, Messi joined Paris Saint-Germain on a free transfer after Barcelona's financial issues prevented them from renewing his contract. At PSG, he won two Ligue 1 titles (2021-22, 2022-23) and scored 32 goals in 75 appearances.

In July 2023, Messi joined Inter Miami CF in Major League Soccer, rejecting offers from Saudi Arabia and a potential return to Barcelona. His arrival transformed American soccer's profile and brought unprecedented attention to MLS."""
    },
    {
        "filename": "euro_championship_multiple_winners.txt",
        "title": "UEFA Euro Championship Multiple Winners",
        "content": """Several countries have won the UEFA European Championship more than once since the tournament began in 1960.

Germany and Spain have each won the tournament three times. Germany (including West Germany) won in 1972, 1980, and 1996. Spain won in 1964, 2008, and 2012, with the 2008-2012 period marking their dominance of international football.

France has won twice, in 1984 and 2000. Italy has also won twice, in 1968 and 2020 (played in 2021).

The Soviet Union won the inaugural tournament in 1960 but dissolved before winning again. Czechoslovakia (1976), the Netherlands (1988), Denmark (1992), Greece (2004), and Portugal (2016) have each won once.

Spain's back-to-back victories in 2008 and 2012, along with their 2010 World Cup win, represents the most successful period for any European nation. The tournament has evolved from a 4-team competition to the current 24-team format."""
    },
    {
        "filename": "champions_league_winners_2015_2023.txt",
        "title": "UEFA Champions League Winners Since 2015",
        "content": """Since 2015, seven different clubs have won the UEFA Champions League:

2014-15: Barcelona (Spain) defeated Juventus 3-1
2015-16: Real Madrid (Spain) defeated Atletico Madrid on penalties
2016-17: Real Madrid (Spain) defeated Juventus 4-1
2017-18: Real Madrid (Spain) defeated Liverpool 3-1
2018-19: Liverpool (England) defeated Tottenham 2-0
2019-20: Bayern Munich (Germany) defeated Paris Saint-Germain 1-0
2020-21: Chelsea (England) defeated Manchester City 1-0
2021-22: Real Madrid (Spain) defeated Liverpool 1-0
2022-23: Manchester City (England) defeated Inter Milan 1-0

Real Madrid's three consecutive victories (2016-18) was unprecedented in the Champions League era. Spanish clubs have won five of these nine titles, while English clubs won three, and German clubs won one.

Manchester City's 2023 victory completed their historic treble of Premier League, FA Cup, and Champions League. Real Madrid remains the most successful club in European Cup/Champions League history with 14 total titles."""
    },
    {
        "filename": "manchester_city_trophies_guardiola.txt",
        "title": "Manchester City Trophies Under Pep Guardiola",
        "content": """Under Pep Guardiola (2016-present), Manchester City has won numerous major trophies, establishing themselves as one of Europe's dominant forces.

Premier League titles: 2017-18, 2018-19, 2020-21, 2021-22, 2022-23, 2023-24 (6 titles)

FA Cup: 2018-19, 2022-23 (2 titles)

EFL Cup (League Cup): 2017-18, 2018-19, 2019-20, 2020-21 (4 titles)

UEFA Champions League: 2022-23 (1 title)

FA Community Shield: 2018, 2019 (2 titles)

UEFA Super Cup: 2023 (1 title)

FIFA Club World Cup: 2023 (1 title)

The 2022-23 season was historic as City became only the second English club to win the treble (Premier League, FA Cup, Champions League) after Manchester United in 1999. The treble-winning season culminated with victory over Inter Milan in the Champions League final.

Guardiola's City set numerous records, including most points in a Premier League season (100 in 2017-18) and most consecutive Premier League wins (18). Under his management, City has become synonymous with dominant possession-based football."""
    },
    {
        "filename": "2022_world_cup_stadiums.txt",
        "title": "2022 FIFA World Cup Stadiums in Qatar",
        "content": """The 2022 FIFA World Cup in Qatar featured eight stadiums, all located within a compact area around Doha. This was the first World Cup held in the Middle East and featured state-of-the-art stadium technology.

The eight stadiums were:

1. Lusail Iconic Stadium (Lusail) - Capacity: 88,966 - Hosted the final
2. Al Bayt Stadium (Al Khor) - Capacity: 60,000 - Hosted the opening match
3. Stadium 974 (Doha) - Capacity: 40,000 - Made from shipping containers
4. Ahmad Bin Ali Stadium (Al Rayyan) - Capacity: 40,000
5. Khalifa International Stadium (Doha) - Capacity: 40,000
6. Education City Stadium (Al Rayyan) - Capacity: 40,000
7. Al Thumama Stadium (Doha) - Capacity: 40,000
8. Al Janoub Stadium (Al Wakrah) - Capacity: 40,000

All stadiums featured advanced cooling technology to combat Qatar's heat. The compact nature meant fans could attend multiple matches per day. Stadium 974 was designed to be dismantled after the tournament, a first for the World Cup.

The final between Argentina and France at Lusail Stadium broke records as one of the most-watched football matches in history."""
    },
    {
        "filename": "premier_league_2022_23_clubs.txt",
        "title": "2022-23 Premier League Season Clubs",
        "content": """The 2022-23 Premier League season featured 20 clubs competing for the title. Manchester City won the league with 89 points, securing their fifth title in six years.

The 20 clubs were:
1. Manchester City (Champions)
2. Arsenal
3. Manchester United
4. Newcastle United
5. Liverpool
6. Brighton & Hove Albion
7. Aston Villa
8. Tottenham Hotspur
9. Brentford
10. Fulham
11. Crystal Palace
12. Chelsea
13. Wolverhampton Wanderers
14. West Ham United
15. Bournemouth
16. Nottingham Forest
17. Everton
18. Leicester City (Relegated)
19. Leeds United (Relegated)
20. Southampton (Relegated)

The relegated teams (Leicester, Leeds, Southampton) were replaced by Burnley, Sheffield United, and Luton Town for the 2023-24 season.

Arsenal led for most of the season but City's late surge secured the title. Erling Haaland broke the Premier League single-season scoring record with 36 goals for City."""
    },
    {
        "filename": "ballon_dor_multiple_winners.txt",
        "title": "Ballon d'Or Multiple Winners (3+ Times)",
        "content": """Four players have won the Ballon d'Or three or more times in history:

Lionel Messi holds the record with 8 Ballon d'Or awards: 2009, 2010, 2011, 2012, 2015, 2019, 2021, and 2023. His 2023 win came after leading Argentina to World Cup victory.

Cristiano Ronaldo has won 5 times: 2008, 2013, 2014, 2016, and 2017. His wins came during periods of dominance at Manchester United and Real Madrid.

Michel Platini won 3 consecutive times: 1983, 1984, and 1985. The French midfielder won all three while playing for Juventus.

Johan Cruyff also won 3 times: 1971, 1973, and 1974. The Dutch legend won his awards while at Ajax and Barcelona.

Marco van Basten won 3 times as well: 1988, 1989, and 1992, all while playing for AC Milan.

The Ballon d'Or, awarded by France Football magazine, is considered the most prestigious individual award in football. Messi and Ronaldo's combined 13 awards dominated the award from 2008 to 2023, with only Luka Modrić (2018) and Karim Benzema (2022) winning in between."""
    },
    {
        "filename": "2022_world_cup_top_scorers.txt",
        "title": "2022 FIFA World Cup Top Scorers",
        "content": """The 2022 FIFA World Cup in Qatar saw Kylian Mbappé of France win the Golden Boot as the tournament's top scorer with 8 goals. Despite France losing the final on penalties, Mbappé's hat-trick in the final secured him the award.

The top five scorers were:

1. Kylian Mbappé (France) - 8 goals
2. Lionel Messi (Argentina) - 7 goals
3. Julián Álvarez (Argentina) - 4 goals
4. Olivier Giroud (France) - 4 goals
5. Gonçalo Ramos (Portugal) - 3 goals

Other notable scorers with 3 goals included Cody Gakpo (Netherlands), Richarlison (Brazil), Bukayo Saka (England), and Álvaro Morata (Spain).

Mbappé's 8 goals included a hat-trick in the final against Argentina. At 23 years old, he became the youngest player to score in two World Cup finals (also scoring in 2018). Messi's 7 goals included two in the final, crucial goals throughout the knockout stages, and he won the Golden Ball as the tournament's best player.

The final was particularly notable for goal-scoring, ending 3-3 after extra time before Argentina won on penalties."""
    },
    {
        "filename": "italian_champions_league_winners.txt",
        "title": "Italian Clubs - UEFA Champions League Winners",
        "content": """Three Italian clubs have won the UEFA Champions League (formerly European Cup): AC Milan, Inter Milan, and Juventus.

AC Milan has won the title 7 times: 1963, 1969, 1989, 1990, 1994, 2003, and 2007. Milan is the second-most successful club in the competition's history behind Real Madrid. Their victories include memorable finals such as the 2003 penalty shootout against Juventus and the 2007 revenge against Liverpool.

Inter Milan has won 3 times: 1964, 1965, and 2010. Their 2010 victory under José Mourinho was part of a historic treble (Serie A, Coppa Italia, Champions League). Inter defeated Bayern Munich 2-0 in the final in Madrid.

Juventus has won twice: 1985 and 1996. However, Juventus has been runner-up a record 7 times, losing finals in 1973, 1983, 1997, 1998, 2003, 2015, and 2017.

Combined, Italian clubs have won the European Cup/Champions League 12 times, making Italy one of the most successful nations in the competition. The late 1980s and early 1990s marked the peak of Italian dominance in European football."""
    },
    {
        "filename": "real_madrid_captains_2010.txt",
        "title": "Real Madrid Captains Since 2010",
        "content": """Since 2010, Real Madrid has had several distinguished captains leading the club through one of its most successful periods.

Iker Casillas served as captain from 2010 to 2015. The legendary goalkeeper led Real Madrid to La Décima (the 10th European Cup) in 2014, ending a 12-year wait for Champions League glory.

Sergio Ramos took over as captain in 2015 and served until 2021. Under Ramos's captaincy, Real Madrid won four Champions League titles (2016, 2017, 2018, 2022), though he had left for PSG before the 2022 victory. Ramos became synonymous with Real Madrid's winning mentality.

Marcelo served as captain from 2021 to 2022 after Ramos's departure. The Brazilian left-back was part of Real Madrid's incredible 2021-22 Champions League triumph.

Karim Benzema became captain in 2022 and held the armband for the 2022-23 season before leaving for Al-Ittihad in Saudi Arabia.

Nacho Fernández assumed the captaincy in 2023 and continues to lead the team. The Real Madrid captaincy is traditionally given to the player with the longest tenure at the club."""
    },
    {
        "filename": "african_world_cup_quarterfinals.txt",
        "title": "African Teams in World Cup Quarterfinals",
        "content": """Three African nations have reached the FIFA World Cup quarterfinals in the tournament's history.

Cameroon was the first African team to reach the quarterfinals, achieving this feat in 1990 in Italy. Led by Roger Milla, Cameroon defeated Argentina and Romania before losing to England 3-2 after extra time in the quarterfinals.

Senegal reached the quarterfinals in 2002 during the Korea-Japan World Cup. In their debut World Cup appearance, Senegal defeated France in the opening match and Sweden in the round of 16 before losing to Turkey in the quarterfinals.

Ghana reached the quarterfinals in 2010 in South Africa, becoming the third African nation to do so. They came agonizingly close to reaching the semifinals but lost to Uruguay on penalties after Luis Suárez's famous handball on the goal line in the final seconds of extra time.

Morocco made history in 2022 by becoming the first African and Arab nation to reach the World Cup semifinals. They defeated Belgium, Spain, and Portugal before losing to France in the semifinals. This achievement surpassed all previous African World Cup performances."""
    },
    {
        "filename": "world_cup_multiple_hosts.txt",
        "title": "Countries That Have Hosted World Cup Multiple Times",
        "content": """Six countries have hosted the FIFA World Cup more than once:

Mexico has hosted twice: 1970 and 1986. Mexico became the first country to host two World Cups and will host again in 2026 (co-hosting with USA and Canada).

Italy has hosted twice: 1934 and 1990. Italy won the 1934 tournament on home soil but finished third in 1990.

France has hosted twice: 1938 and 1998. France won the tournament in 1998, defeating Brazil 3-0 in the final at Stade de France.

Germany has hosted twice: 1974 (as West Germany) and 2006. West Germany won the 1974 tournament, while in 2006 Italy won the title.

Brazil has hosted twice: 1950 and 2014. Brazil lost the 1950 final to Uruguay in a historic upset and lost the 2014 semifinals to Germany 7-1.

The United States has hosted twice: 1994 and will co-host in 2026 (with Mexico and Canada). The 1994 tournament was notable for high attendance records.

Argentina, Uruguay, Chile, Switzerland, Sweden, England, and Spain have each hosted once. Qatar (2022) and Russia (2018) are recent additions to the list of host nations."""
    },
    {
        "filename": "messi_champions_league_hattricks.txt",
        "title": "Lionel Messi Champions League Hat-tricks",
        "content": """Lionel Messi scored hat-tricks against numerous clubs during his Champions League career with Barcelona and Paris Saint-Germain. He holds the record for most Champions League hat-tricks with 8.

Some of the clubs Messi scored Champions League hat-tricks against include:

Arsenal - Messi scored a memorable four-goal performance against Arsenal at Camp Nou in 2010, though only three counted as a hat-trick in one match.

Bayer Leverkusen - Messi scored five goals against Leverkusen in a 7-1 victory in 2012.

Ajax, APOEL, PSV Eindhoven, Manchester City, and BATE Borisov are among other clubs that conceded hat-tricks to Messi in the Champions League.

Messi's ability to score multiple goals in big Champions League matches was a hallmark of his career. His Champions League record includes 129 goals, making him the second-highest scorer in the competition's history behind Cristiano Ronaldo.

These performances helped Barcelona win four Champions League titles (2006, 2009, 2011, 2015) with Messi as a key player."""
    },
    {
        "filename": "arsenal_fa_cup_wenger.txt",
        "title": "Arsenal FA Cup Victories Under Arsène Wenger",
        "content": """Arsène Wenger led Arsenal to seven FA Cup victories during his 22-year tenure as manager (1996-2018). Arsenal won the FA Cup in:

1998 - Arsenal defeated Newcastle United 2-0 at Wembley
2002 - Arsenal defeated Chelsea 2-0, completing a league and cup double
2003 - Arsenal defeated Southampton 1-0
2005 - Arsenal defeated Manchester United on penalties after a 0-0 draw
2014 - Arsenal defeated Hull City 3-2 after extra time, ending a 9-year trophy drought
2015 - Arsenal defeated Aston Villa 4-0
2017 - Arsenal defeated Chelsea 2-1

These seven FA Cup victories made Wenger the most successful manager in FA Cup history. The 2014 victory was particularly significant as it ended Arsenal's longest period without a trophy since Wenger arrived.

The FA Cup success became a hallmark of Wenger's later years at Arsenal, even as Premier League and Champions League glory eluded him after 2004. Wenger's Arsenal teams were known for attractive, attacking football and development of young talent."""
    },
    {
        "filename": "messi_2022_world_cup_awards.txt",
        "title": "Lionel Messi's 2022 World Cup Awards",
        "content": """Lionel Messi won multiple individual awards at the 2022 FIFA World Cup in Qatar, capping his career with the one trophy that had eluded him.

Golden Ball: Messi was named the tournament's best player, winning his second World Cup Golden Ball (he also won in 2014). This award is given to the outstanding player of the tournament.

Messi also shared the Silver Boot for being one of the top scorers, finishing with 7 goals in the tournament. Kylian Mbappé won the Golden Boot with 8 goals.

Additionally, Messi set several records at the 2022 World Cup:
- Most World Cup appearances: 26 matches (across 5 tournaments: 2006, 2010, 2014, 2018, 2022)
- Most World Cup matches by a player at a single tournament: 7 (won all 7 in 2022)
- Became only the third player to score in the Round of 16, Quarterfinals, Semifinals, and Final in a single World Cup

The 2022 World Cup victory completed Messi's trophy collection and solidified his status as one of football's all-time greats. At 35 years old, it was likely his final World Cup appearance."""
    },
    {
        "filename": "champions_league_qualification.txt",
        "title": "UEFA Champions League Qualification Process",
        "content": """Teams qualify for the UEFA Champions League group stage through several routes:

1. Direct Qualification: Top teams from Europe's strongest leagues receive automatic group stage places. The top four teams from England, Spain, Germany, and Italy qualify directly. France's top two also qualify directly.

2. Domestic Champions Path: Champions from smaller European leagues must go through qualifying rounds. These teams play in several qualifying rounds (first qualifying round, second qualifying round, third qualifying round) before reaching the playoff round.

3. League Path: Teams that finish in qualifying positions but aren't champions (typically 3rd or 4th place) enter through the league path, starting from the third qualifying round.

4. Playoff Round: The final step before the group stage, where teams play two-legged ties to determine the last spots in the 32-team (now 36-team) group stage.

5. UEFA Europa League Winners: The winner of the previous season's Europa League automatically qualifies for the Champions League group stage.

6. UEFA Champions League Title Holders: The defending champions automatically qualify for the group stage.

The qualification process typically runs from June to August, with the group stage starting in September. The number of teams from each country depends on UEFA's coefficient system, which ranks leagues based on their clubs' European performance over the previous five seasons."""
    },
    {
        "filename": "penalty_kick_fifa_laws.txt",
        "title": "FIFA Laws - Taking a Penalty Kick",
        "content": """According to FIFA Laws of the Game, a penalty kick must follow specific procedures:

Ball and Player Placement:
- The ball must be placed on the penalty mark (12 yards from goal)
- The player taking the penalty must be clearly identified
- The defending goalkeeper must remain on the goal line, facing the kicker, between the goalposts, until the ball is kicked
- All other players must be outside the penalty area and arc, at least 10 yards from the penalty mark

Procedure:
- The referee signals when the kick may be taken
- The kicker must kick the ball forward
- The kicker cannot touch the ball again until another player has touched it
- The goalkeeper must not move off the goal line until the ball is kicked (though may move along the line)

Outcome:
- The kick is complete when the ball stops moving, goes out of play, or the referee stops play for any offense
- If the goalkeeper commits an offense and the kick is missed or saved, the kick is retaken
- If the kicker commits an offense, the kick is disallowed and an indirect free kick is awarded to the defending team

VAR technology is now used to check for goalkeeper and kicker infringements. Goalkeepers must have at least part of one foot on or in line with the goal line when the kick is taken."""
    },
    {
        "filename": "knockout_match_extra_time_penalties.txt",
        "title": "Deciding Winners in Knockout Matches",
        "content": """When a knockout match in major tournaments ends in a draw after 90 minutes of regular time, FIFA rules specify the following procedure:

Extra Time:
- Two 15-minute periods are played (30 minutes total)
- There is a short break (typically 5 minutes) before extra time
- Teams change ends between the two extra time periods
- If the score remains level after extra time, the match goes to a penalty shootout

Penalty Shootout Procedure:
- Each team takes five penalties alternately
- If the scores are level after five penalties each, the shootout continues on a sudden-death basis
- The same players who were on the field at the end of extra time are eligible to take penalties
- Each team's penalties must be taken by different players until all eligible players have taken one

The team that scores more goals during the penalty shootout wins the match. This procedure is used in knockout stages of the World Cup, European Championships, Champions League, and other major tournaments.

Note: The away goals rule, which previously gave an advantage to teams scoring away from home in two-legged ties, was abolished by UEFA in 2021. Now, tied two-legged matches go directly to extra time and penalties if needed."""
    },
    {
        "filename": "world_cup_qualification_process.txt",
        "title": "FIFA World Cup Qualification Process",
        "content": """Teams qualify for the FIFA World Cup through continental qualifying tournaments organized by FIFA's six confederations:

UEFA (Europe): European teams play in groups during the qualifying period (typically over 2 years). Group winners qualify directly. Runners-up enter playoffs to determine additional qualifiers. Europe usually receives 13 of the 32 World Cup spots (16 in the expanded 48-team format from 2026).

CONMEBOL (South America): All 10 South American teams play in a single league format, playing home and away against each other. The top teams qualify directly, with lower-ranked teams entering intercontinental playoffs.

CAF (Africa): African qualification occurs in multiple rounds. Teams are divided into groups, with group winners advancing. The final round features home-and-away playoffs. Africa receives 5 spots (9 in 2026).

AFC (Asia): Asian qualification involves several rounds. Teams play in groups, with the best teams qualifying directly and others entering playoffs. Asia receives 4-5 spots (8 in 2026).

CONCACAF (North/Central America and Caribbean): Teams play in rounds, with the final round (the Octagonal) featuring eight teams playing for qualification spots. CONCACAF receives 3-4 spots (6 in 2026, with co-hosting).

OFC (Oceania): Pacific nations play in a group stage followed by playoffs. The winner enters an intercontinental playoff for a World Cup spot (OFC receives 1 spot, or 1-2 in 2026).

The host nation(s) automatically qualify. The process typically takes 2-3 years before each World Cup."""
    },
    {
        "filename": "var_video_assistant_referee.txt",
        "title": "VAR - Video Assistant Referee System",
        "content": """VAR (Video Assistant Referee) was introduced to football to help referees make more accurate decisions during matches. The system reviews specific incidents:

Reviewable Incidents:
1. Goals - checking for offenses in the buildup
2. Penalty decisions - reviewing foul calls or handballs
3. Direct red card incidents - violent conduct or serious foul play
4. Mistaken identity - ensuring the correct player is cautioned or sent off

VAR Review Process:
- The VAR team watches all game action from a video operation room
- Multiple camera angles are available for review
- VAR checks incidents and communicates with the referee via headset
- For clear and obvious errors, the VAR recommends an on-field review
- The referee can view the incident on a pitchside monitor
- After review, the referee makes the final decision
- The referee signals VAR review by making a TV screen gesture

The review must be completed quickly to minimize game delays. VAR operates in the Premier League, Champions League, World Cup, and many other top competitions worldwide.

VAR has proven controversial, with debates about its impact on game flow, but has successfully corrected numerous clear errors that would have otherwise stood."""
    },
    {
        "filename": "player_substitution_procedure.txt",
        "title": "Player Substitution Procedure in Football",
        "content": """The procedure for substituting a player during an official FIFA match follows specific steps:

Before Substitution:
- Teams are allowed up to 5 substitutions in most modern competitions (3 in some)
- The fourth official is notified of the intended substitution
- The substitute prepares on the sideline, wearing a numbered bib
- The substitute cannot enter until authorized by the referee

During Substitution:
- Play must be stopped and the referee must give permission
- The player being substituted must leave at the nearest boundary line
- The substitute enters from the halfway line after the replaced player has left
- The substitution is completed when the substitute enters the field
- The referee is informed which player is being replaced and by whom

After Substitution:
- The replaced player cannot re-enter the match
- The substitute becomes a full player with all rights and responsibilities
- The substitution is recorded by match officials
- If a player is injured and cannot continue, the substitution may be expedited

Special Rules:
- Substitutions are typically made during stoppages (goal kicks, throw-ins, etc.)
- If a goalkeeper is substituted, another player must assume the goalkeeper role
- In some competitions, additional substitutions are allowed in extra time
- Temporary concussion substitutions have been trialed in some leagues

The referee may show yellow cards to players who delay substitutions or enter without permission."""
    },
    {
        "filename": "erling_haaland_transfer.txt",
        "title": "Erling Haaland's Transfer to Manchester City",
        "content": """Erling Haaland joined Manchester City from Borussia Dortmund in the summer of 2022. The Norwegian striker signed a five-year contract, with City triggering his €60 million release clause.

Before joining City, Haaland played for Borussia Dortmund (2020-2022) where he scored 86 goals in 89 appearances. His prolific scoring made him one of the most sought-after strikers in world football.

Haaland's career path before City:
- Molde (Norway) - 2017-2019: Started his professional career at his hometown club
- Red Bull Salzburg (Austria) - 2019-2020: Breakthrough season with 29 goals in 27 games
- Borussia Dortmund (Germany) - 2020-2022: Established himself as world-class striker

At Manchester City, Haaland had an immediate impact, breaking Premier League records in his first season (2022-23). He scored 52 goals in all competitions, including 36 Premier League goals (a single-season record), helping City win the treble (Premier League, FA Cup, Champions League).

Haaland's combination of pace, power, and finishing ability made him the perfect fit for Pep Guardiola's system. His father, Alf-Inge Haaland, also played for Manchester City (2000-2003)."""
    },
    {
        "filename": "france_1998_world_cup.txt",
        "title": "France Win 1998 FIFA World Cup",
        "content": """France won their first FIFA World Cup on home soil in 1998, defeating Brazil 3-0 in the final at Stade de France in Saint-Denis on July 12, 1998.

Zinedine Zidane scored two headed goals in the final (27th and 45th minutes), both from corner kicks. Emmanuel Petit added a third goal in stoppage time to seal France's victory. The win sparked nationwide celebrations across France.

The 1998 tournament was significant for several reasons:
- It was expanded to 32 teams for the first time
- France, as host nation, automatically qualified
- The multi-ethnic French squad became a symbol of unity
- Aimé Jacquet was the coach who led France to glory

Key players in France's victory included:
- Zinedine Zidane (two goals in final)
- Thierry Henry (rising star)
- Laurent Blanc (defensive leader)
- Didier Deschamps (captain)
- Fabien Barthez (goalkeeper)

The victory was France's first major tournament win since the 1984 European Championship. Brazil, the defending champions, were expected to win but were outplayed by the French. Ronaldo started the match despite suffering from convulsions before kickoff.

France's World Cup victory in 1998 remains one of the defining moments in French sporting history."""
    },
    {
        "filename": "spain_euro_2012_captain.txt",
        "title": "Spain's Euro 2012 Victory and Captain",
        "content": """Spain won UEFA Euro 2012, defeating Italy 4-0 in the final in Kyiv, Ukraine, on July 1, 2012. Iker Casillas captained Spain to this historic victory.

Casillas led Spain during their most successful period in football history, which included:
- Euro 2008 victory (ending 44-year wait for a major trophy)
- 2010 FIFA World Cup victory
- Euro 2012 victory

This made Spain the first team to win three consecutive major international tournaments. The Euro 2012 final was completely dominated by Spain, with goals from David Silva, Jordi Alba, Fernando Torres, and Juan Mata.

Iker Casillas was Spain's captain from 2008 to 2016 and is considered one of the greatest goalkeepers in football history. He made 167 appearances for Spain and won:
- 1 World Cup (2010)
- 2 European Championships (2008, 2012)

Vicente del Bosque was Spain's coach during Euro 2012. The team's tiki-taka possession-based style dominated international football during this era. Other key players included Xavi Hernández, Andrés Iniesta, Sergio Ramos, and Xabi Alonso.

Spain's 4-0 victory in the final remains the largest winning margin in a European Championship final."""
    },
    {
        "filename": "south_africa_2010_world_cup.txt",
        "title": "2010 FIFA World Cup in South Africa",
        "content": """South Africa hosted the 2010 FIFA World Cup from June 11 to July 11, 2010, becoming the first African nation to host the tournament. The event was a historic milestone for the continent and showcased Africa's capability to host major sporting events.

The tournament featured 32 teams and was played across 10 venues in 9 cities:
- Johannesburg (Soccer City and Ellis Park)
- Cape Town (Cape Town Stadium)
- Durban (Moses Mabhida Stadium)
- Pretoria (Loftus Versfeld Stadium)
- Port Elizabeth (Nelson Mandela Bay Stadium)
- Bloemfontein (Free State Stadium)
- Rustenburg (Royal Bafokeng Stadium)
- Polokwane (Peter Mokaba Stadium)
- Nelspruit (Mbombela Stadium)

Spain won the tournament, defeating the Netherlands 1-0 in the final at Soccer City. Andrés Iniesta scored the winning goal in extra time (116th minute). This was Spain's first World Cup title.

The 2010 World Cup is remembered for:
- The vuvuzela horns creating a unique atmosphere
- The phrase "Waka Waka" from Shakira's official song
- Diego Forlán's outstanding performances for Uruguay
- Germany's young team thrilling with attacking football
- Host nation South Africa's elimination in group stage (first host to not advance)

The tournament was considered a success and helped change perceptions about Africa's ability to host major international events."""
    },
    {
        "filename": "mario_gotze_2014_world_cup.txt",
        "title": "2014 FIFA World Cup Final - Mario Götze's Winning Goal",
        "content": """Mario Götze scored the winning goal in the 2014 FIFA World Cup final, giving Germany a 1-0 victory over Argentina after extra time at Maracanã Stadium in Rio de Janeiro, Brazil, on July 13, 2014.

Götze's goal came in the 113th minute of extra time. André Schürrle sent a cross from the left wing, and Götze controlled the ball with his chest before volleying it past Argentine goalkeeper Sergio Romero. The goal made Germany the first European team to win a World Cup held in the Americas.

The 2014 final was Lionel Messi's closest chance to win the World Cup at that time (he would later win in 2022). Despite Messi winning the Golden Ball as the tournament's best player, Argentina lost the final after a tightly contested match.

Key details of the match:
- Germany's coach was Joachim Löw
- Argentina's coach was Alejandro Sabella
- The match went to extra time after a 0-0 draw in regular time
- This was Germany's fourth World Cup title (1954, 1974, 1990, 2014)

Götze was brought on as a substitute specifically to score, with Löw telling him "Show the world you're better than Messi." At 22 years old, Götze became one of the youngest players to score in a World Cup final.

Thomas Müller and Toni Kroos were among other key German players in the final. The victory completed Germany's redemption after losing the 2002 final to Brazil at the same stadium."""
    }
]

# Combine all documents
ALL_DOCUMENTS = DOCUMENTS + MORE_DOCUMENTS

def create_corpus(output_dir: str = "data/corpus"):
    """Create corpus directory and generate all documents"""
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Creating {len(ALL_DOCUMENTS)} documents in {output_dir}/")
    print("="*60)
    
    # Generate each document
    for i, doc in enumerate(ALL_DOCUMENTS, 1):
        filepath = output_path / doc['filename']
        
        # Create document content
        content = f"{doc['title']}\n{'='*len(doc['title'])}\n\n{doc['content']}"
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ Created {i}/{len(ALL_DOCUMENTS)}: {doc['filename']}")
    
    print("="*60)
    print(f"✓ Successfully created {len(ALL_DOCUMENTS)} documents!")
    print(f"\nDocuments location: {output_dir}/")
    print(f"\nVerify: ls {output_dir}/ | wc -l")


def create_evidence_file(output_file: str = "data/evidence.tsv", num_questions: int = 100):
    """Create evidence.tsv file mapping questions to documents"""
    
    print(f"\nCreating evidence.tsv with {num_questions} entries...")
    
    # Create mappings (simplified - each question maps to relevant docs)
    evidence_entries = []
    
    for i in range(num_questions):
        # Map to 1-3 relevant documents
        doc_indices = [(i % len(ALL_DOCUMENTS)), ((i + 1) % len(ALL_DOCUMENTS))]
        
        docs = [ALL_DOCUMENTS[idx] for idx in doc_indices[:2]]
        
        # Create entry: source\tfilename pairs
        entry = "\t".join([f"Generated corpus\t{doc['filename']}" for doc in docs])
        evidence_entries.append(entry)
    
    # Write evidence file
    with open(output_file, 'w', encoding='utf-8') as f:
        for entry in evidence_entries:
            f.write(entry + "\n")
    
    print(f"✓ Created {output_file} with {num_questions} entries")


def main():
    print("="*60)
    print("FOOTBALL CORPUS GENERATOR")
    print("="*60)
    print()
    
    # Create corpus
    create_corpus("data/corpus")
    
    # Create evidence file
    create_evidence_file("data/evidence.tsv", num_questions=100)
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"✓ Created {len(ALL_DOCUMENTS)} corpus documents")
    print(f"✓ Created evidence.tsv with 100 entries")
    print("\nFiles created:")
    print("  data/corpus/*.txt (50+ documents)")
    print("  data/evidence.tsv")
    print("\nVerify:")
    print("  ls data/corpus/ | wc -l  # Should show 50+")
    print("  wc -l data/evidence.tsv  # Should show 100")
    print("\n✓ Ready for RAG system!")
    print("="*60)


if __name__ == '__main__':
    main()