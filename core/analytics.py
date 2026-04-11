class ContributorScout:
    def calculate_value_score(self, commit_data, pr_data):
        """
        PERMANENT FIX: Logic-based scoring for 'Hardworking' employees.
        """
        # Weighted Multipliers
        WEIGHTS = {
            "complexity": 0.5,    # Hard code is worth more
            "prs": 0.3,           # Merging features is leadership
            "loc": 0.2            # Volume is secondary
        }
        
        scores = {}
        for contributor in commit_data:
            # Logic: We calculate value, not just quantity
            raw_score = (
                (contributor['avg_complexity'] * WEIGHTS['complexity']) +
                (contributor['merged_prs'] * WEIGHTS['prs']) +
                (contributor['impact_score'] * WEIGHTS['loc'])
            )
            scores[contributor['name']] = round(raw_score, 2)
            
        return scores