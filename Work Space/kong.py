import re

class RuleProcessor:
    def __init__(self, rules):
        self.rules = rules

    def match(self, rule, text):
        text_lower = text.lower()
        rule_type = rule[0]
        if rule_type == "AND":
            return all(self.match(word, text) if isinstance(word, list) else word.lower() in text_lower for word in rule[1:])
        elif rule_type == "OR":
            return any(self.match(word, text) if isinstance(word, list) else word.lower() in text_lower for word in rule[1:])
        elif rule_type == "NGRAM":
            return " ".join(rule[1:]).lower() in text_lower
        elif rule_type == "NOT":
            return not any(word.lower() in text_lower for word in rule[1:])
        else:
            return rule.lower() in text_lower

    def get_highlights(self, rule, text):
        text_lower = text.lower()
        if rule[0] == "NGRAM":
            phrase = " ".join(rule[1:]).lower()
            return [(m.start(), m.end()) for m in re.finditer(re.escape(phrase), text_lower)]
        elif rule[0] in ["AND", "OR", "NOT"]:
            highlights = []
            for subrule in rule[1:]:
                if isinstance(subrule, list):
                    highlights.extend(self.get_highlights(subrule, text))
                else:
                    highlights.extend([(m.start(), m.end()) for m in re.finditer(re.escape(subrule.lower()), text_lower)])
            return highlights
        return []

class TextMatcher:
    def __init__(self, rules):
        self.rule_processor = RuleProcessor(rules)

    def match_texts(self, texts):
        results = []
        for text in texts:
            matching_rules = []
            highlights = []
            for rule_id, rule in self.rule_processor.rules.items():
                if self.rule_processor.match(rule, text):
                    matching_rules.append(rule_id)
                    highlights.extend(self.rule_processor.get_highlights(rule, text))
            highlights = self.merge_highlights(highlights)
            highlight_text = self.apply_highlights(text, highlights)
            results.append({"matching_rule_ids": matching_rules, "highlights": highlight_text})
        return results

    def merge_highlights(self, highlights):
        highlights.sort()
        merged = []
        for start, end in highlights:
            if merged and start <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(merged[-1][1], end))
            else:
                merged.append((start, end))
        return merged

    def apply_highlights(self, text, highlights):
        offset = 0
        for start, end in highlights:
            text = text[:start+offset] + "**" + text[start+offset:end+offset] + "**" + text[end+offset:]
            offset += 4  # Account for added asterisks
        return text

# Example usage
rules = {
    "apple_rule": ["AND", "apple", ["OR", "computers", "computer"]],
    "nothing_rule": ["OR", ["NGRAM", "nothing", "phone"], ["NGRAM", "nothing", "ear"]]
}

texts = [
    "Quarterly results were announced by Apple computers and it had nothing special",
    "We found nothing wrong with the nothing ear 1",
    "iPhone from apple computers has had tough competition from nothing phone"
]

matcher = TextMatcher(rules)
results = matcher.match_texts(texts)
for result in results:
    print(result)