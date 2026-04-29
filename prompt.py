class Prompt:
    def __init__(self):
        self.description = ""
        self.keyword = ""
        self.is_hidden = True

    def set_prompt(self, description, keyword):
        description = description.strip()
        keyword = keyword.strip()

        if description == "" or keyword == "":
            raise ValueError("Description and keyword cannot be blank.")

        self.description = description
        self.keyword = keyword.lower()
        self.is_hidden = True

    def check_guess(self, guess):
        return guess.strip().lower() == self.keyword

    def reveal_keyword(self):
        return self.keyword