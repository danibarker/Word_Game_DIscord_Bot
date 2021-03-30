def score_card_query(event_id):
    return f"""
    /* Query to get summary */
    SELECT group_number,round_number,max, s.average,e.player_id, 
    full_name, group_id, byes, spread, wins, games, rating FROM event_attendees e
    LEFT OUTER JOIN
        (SELECT group_number, round_number, max(max) AS max, 
		  sum(score)/sum(games) AS average, player_id, r.group_id, 
		  byes,sum(spread) AS spread, sum(wins) AS wins, sum(games) as games FROM  

            (/* calculate spread for each result when each player was player 1 */
            SELECT g.group_number, g.round_number, r.group_id, r.round, 
            p.full_name,r.player1 AS player_id,max(r.score_1) as max, 
            sum(r.score_1) as score, sum(r.score_1) -  sum(r.score_2)  AS spread,  
            p.rating,
            /* count number of wins */
            COUNT(CASE WHEN r.score_1 > r.score_2 THEN 1 END) +
        
            /*count number of ties */
            COUNT(CASE WHEN r.score_1 = r.score_2 THEN 1 END)*0.5 AS wins, 
        
            /* count number of byes */
            CASE WHEN (SELECT bye FROM event_attendees 
            WHERE event_id = {event_id} AND player_id = p.id) 
            <= g.round_number THEN 1 ELSE 0 END AS byes ,

            /* count number of games */
            COUNT(1) as games
            FROM players p INNER JOIN results r 
            ON r.player1 = p.id INNER join groups g ON g.id=r.group_id 
            WHERE r.event_id = {event_id} GROUP BY player1 

            UNION
        
            /* repeat for when each player was player2 */
            SELECT g.group_number, g.round_number,r.group_id, 
            r.round, p.full_name,r.player2,
            max(r.score_2) as max, sum(r.score_2) as score,
            sum(r.score_2)-sum(r.score_1),p.rating,
            COUNT(CASE WHEN r.score_1 < r.score_2 THEN 1 END) + 
            COUNT(CASE WHEN r.score_1 = r.score_2 THEN 1 END)*0.5 ,
            CASE WHEN (SELECT bye FROM event_attendees 
            WHERE event_id = {event_id} AND player_id = p.id) 
            <= g.round_number THEN 1 ELSE 0 END,
            COUNT(1) as games
            FROM players p INNER JOIN results r
            ON r.player2 = p.id INNER join groups g ON g.id=r.group_id 
            WHERE r.event_id = {event_id} GROUP BY player2  ) r

       
        GROUP BY player_id) s
   ON s.player_id = e.player_id
   LEFT JOIN players p 
	ON p.id = e.player_id  
WHERE event_id = {event_id}
ORDER BY group_id, wins desc, spread DESC
"""