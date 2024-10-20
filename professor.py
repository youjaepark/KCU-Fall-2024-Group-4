class Professor:
    def __init__(self, ratemyprof_id: int, first_name: str, last_name: str, num_of_ratings: int, overall_rating):
        self.ratemyprof_id = ratemyprof_id
        self.name = f"{first_name} {last_name}"
        self.first_name = first_name
        self.last_name = last_name
        self.num_of_ratings = num_of_ratings
        self.overall_rating = float(overall_rating) if num_of_ratings > 0 else 0

    def __repr__(self):
        return f"Professor({self.name}, {self.num_of_ratings} ratings, {self.overall_rating} overall)"
